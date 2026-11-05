"""
Geological 3D Cross Section
---------------------------
Posiziona una sezione 2D (poligoni) nello spazio 3D reale ancorandola a due
punti A (estremo sinistro) e B (estremo destro).

Un asse locale della sezione esprime la distanza orizzontale, l'altro la
quota. La sezione viene posizionata in modo che:

- l'estremo sinistro coincida con il Punto A;
- l'estremo destro coincida con il Punto B;
- possa essere inclinata attorno alla linea A-B (angolo di rotazione);
- la quota possa essere esagerata (esagerazione verticale) e traslata (offset Z);
- facoltativamente la quota sia presa da un DTM in A e in B.
"""

import math

from qgis.core import (
    QgsCoordinateTransform,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessingParameterPoint,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsWkbTypes,
    QgsPolygon,
    QgsMultiPolygon,
    QgsMultiLineString,
    QgsLineString,
    QgsPoint,
)

try:
    from qgis.core import NULL
except ImportError:  # pragma: no cover
    NULL = None

from .section_math import dtm_anchor, edge_top
from .translations import tr


def _advanced_flag():
    """Flag 'avanzato' compatibile con le diverse versioni di QGIS."""
    try:
        return QgsProcessingParameterDefinition.Flag.FlagAdvanced
    except AttributeError:
        return QgsProcessingParameterDefinition.FlagAdvanced


# oltre questo valore la 'quota' trovata è quasi certamente una coordinata di mappa
LIMITE_QUOTA_LOCALE = 1e5

# inclinazione laterale minima (frazione della quota) per Qgis2threejs
LEAN_THREEJS = 0.002


class Geological3DCrossSectionAlgorithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    ASSE_ORIZZONTALE = "ASSE_ORIZZONTALE"
    PUNTO_A = "PUNTO_A"
    PUNTO_B = "PUNTO_B"
    DTM = "DTM"
    REF_A = "REF_A"
    REF_B = "REF_B"
    FIT_B = "FIT_B"
    UNIFORME = "UNIFORME"
    VISUALIZZATORE = "VISUALIZZATORE"
    ANGOLO = "ANGOLO"
    ESAGERAZIONE = "ESAGERAZIONE"
    ESAGERAZIONE_VAL = "ESAGERAZIONE_VAL"
    ZOFFSET = "ZOFFSET"
    OUTPUT = "OUTPUT"

    VALORI_ESAGERAZIONE = [1.0, 2.0, 2.5, 5.0, 10.0, None]  # None = personalizzata

    def initAlgorithm(self, config=None):
        assi = [tr("axis_x"), tr("axis_y")]
        esagerazioni = [
            tr("exag_none"),
            "x2",
            "x2.5",
            "x5",
            "x10",
            tr("exag_custom"),
        ]

        self.addParameter(
            QgsProcessingParameterVectorLayer(self.INPUT, tr("p_input"))
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ASSE_ORIZZONTALE,
                tr("p_axis"),
                options=assi,
                defaultValue=0,
            )
        )
        self.addParameter(QgsProcessingParameterPoint(self.PUNTO_A, tr("p_point_a")))
        self.addParameter(QgsProcessingParameterPoint(self.PUNTO_B, tr("p_point_b")))
        self.addParameter(
            QgsProcessingParameterRasterLayer(self.DTM, tr("p_dtm"), optional=True)
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.FIT_B, tr("p_fit_b"), defaultValue=False
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.ANGOLO,
                tr("p_angle"),
                type=QgsProcessingParameterNumber.Type.Double,
                defaultValue=0.0,
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ESAGERAZIONE,
                tr("p_exag"),
                options=esagerazioni,
                defaultValue=0,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.ESAGERAZIONE_VAL,
                tr("p_exag_val"),
                type=QgsProcessingParameterNumber.Type.Double,
                defaultValue=1.0,
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.UNIFORME, tr("p_uniform"), defaultValue=False
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.VISUALIZZATORE,
                tr("p_viewer"),
                options=[tr("viewer_native"), tr("viewer_threejs")],
                defaultValue=0,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.ZOFFSET,
                tr("p_zoffset"),
                type=QgsProcessingParameterNumber.Type.Double,
                defaultValue=0.0,
            )
        )

        # parametri avanzati: quota locale del profilo superiore in A e in B
        for nome, chiave in ((self.REF_A, "p_ref_a"), (self.REF_B, "p_ref_b")):
            param = QgsProcessingParameterNumber(
                nome,
                tr(chiave),
                type=QgsProcessingParameterNumber.Type.Double,
                optional=True,
            )
            param.setFlags(param.flags() | _advanced_flag())
            self.addParameter(param)

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, tr("p_output"))
        )

    # ------------------------------------------------------------------ aiuti
    @staticmethod
    def _is_set(value):
        if value is None or value == "":
            return False
        if NULL is not None:
            try:
                if value == NULL:
                    return False
            except Exception:
                pass
        return True

    def _optional_double(self, parameters, name, context):
        """Valore numerico facoltativo: None se il campo è vuoto."""
        if not self._is_set(parameters.get(name)):
            return None
        return self.parameterAsDouble(parameters, name, context)

    @staticmethod
    def _sample_dtm(raster, point, point_crs, context, nome):
        """Legge la quota del DTM (banda 1) nel punto indicato."""
        pt = point
        if raster.crs() != point_crs:
            trasformazione = QgsCoordinateTransform(
                point_crs, raster.crs(), context.transformContext()
            )
            pt = trasformazione.transform(point)
        valore, ok = raster.dataProvider().sample(pt, 1)
        if not ok or valore is None or math.isnan(valore):
            raise QgsProcessingException(tr("err_dtm_sample").format(nome=nome))
        return float(valore)

    @staticmethod
    def _pulisci_poligoni(geom):
        """Corregge la geometria e toglie i vertici duplicati.

        Restituisce None se dopo la correzione non restano poligoni.
        """
        try:
            if not geom.isGeosValid():
                geom = geom.makeValid()
            geom.removeDuplicateNodes()
            parti = [
                p
                for p in geom.asGeometryCollection()
                if "polygon" in QgsWkbTypes.displayString(p.wkbType()).lower()
            ]
        except Exception:
            return geom
        if not parti:
            return None
        if len(parti) == 1:
            return parti[0]
        return QgsGeometry.collectGeometry(parti)

    # ------------------------------------------------------------- algoritmo
    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        asse_h = self.parameterAsEnum(parameters, self.ASSE_ORIZZONTALE, context)
        angolo = math.radians(
            self.parameterAsDouble(parameters, self.ANGOLO, context)
        )
        z_offset = self.parameterAsDouble(parameters, self.ZOFFSET, context)

        esag_idx = self.parameterAsEnum(parameters, self.ESAGERAZIONE, context)
        esagerazione = self.VALORI_ESAGERAZIONE[esag_idx]
        if esagerazione is None:  # personalizzata
            esagerazione = self.parameterAsDouble(
                parameters, self.ESAGERAZIONE_VAL, context
            )
            if esagerazione <= 0:
                raise QgsProcessingException(tr("err_exag"))

        # tipo di geometria del layer: poligoni oppure linee
        tipo_layer = QgsWkbTypes.displayString(layer.wkbType())
        if "polygon" in tipo_layer.lower():
            modo_geom = "poligoni"
            tipo_out = QgsWkbTypes.Type.MultiPolygon25D
        elif "line" in tipo_layer.lower():
            modo_geom = "linee"
            tipo_out = QgsWkbTypes.Type.MultiLineString25D
        else:
            raise QgsProcessingException(tr("err_geom_type").format(tipo=tipo_layer))

        crs = layer.sourceCrs()
        punto_a = self.parameterAsPoint(parameters, self.PUNTO_A, context, crs)
        punto_b = self.parameterAsPoint(parameters, self.PUNTO_B, context, crs)

        ax, ay = punto_a.x(), punto_a.y()
        bx, by = punto_b.x(), punto_b.y()
        dx, dy = bx - ax, by - ay
        lunghezza_reale = math.hypot(dx, dy)
        if lunghezza_reale == 0:
            raise QgsProcessingException(tr("err_ab"))
        hx, hy = dx / lunghezza_reale, dy / lunghezza_reale  # versore A->B

        extent = layer.extent()
        if asse_h == 0:
            u_min, u_max = extent.xMinimum(), extent.xMaximum()
        else:
            u_min, u_max = extent.yMinimum(), extent.yMaximum()

        larghezza_locale = u_max - u_min
        if larghezza_locale == 0:
            raise QgsProcessingException(tr("err_width"))
        scala = lunghezza_reale / larghezza_locale

        # scala uniforme: la quota viene scalata come la distanza orizzontale
        # (utile se la sezione è stata georiferita in scala troppo piccola)
        uniforme = self.parameterAsBool(parameters, self.UNIFORME, context)
        if uniforme:
            esagerazione = esagerazione * scala
            feedback.pushInfo(
                tr("log_uniform").format(scala=scala, esag=esagerazione)
            )

        cos_a, sin_a = math.cos(angolo), math.sin(angolo)

        # Qgis2threejs triangola in pianta (XY): una sezione perfettamente
        # verticale ha area nulla in pianta e dà triangoli sbagliati. Si
        # aggiunge un'inclinazione laterale minima, proporzionale alla quota
        # relativa (0,2% = circa 0,1 gradi).
        threejs = self.parameterAsEnum(parameters, self.VISUALIZZATORE, context) == 1
        inclinazione = LEAN_THREEJS if threejs else 0.0
        v_min = (extent.yMinimum() if asse_h == 0 else extent.xMinimum()) * esagerazione
        px_, py_ = -hy, hx  # perpendicolare ad A-B in pianta
        if threejs:
            feedback.pushInfo(tr("log_lean").format(k=inclinazione * 100))

        # --- quota dal DTM (facoltativa) -----------------------------------
        z_base = 0.0
        shear = 0.0
        dtm = self.parameterAsRasterLayer(parameters, self.DTM, context)
        if dtm is not None:
            fit_b = self.parameterAsBool(parameters, self.FIT_B, context)

            z_a = self._sample_dtm(dtm, punto_a, crs, context, "A")
            z_b = self._sample_dtm(dtm, punto_b, crs, context, "B")

            ref_a = self._optional_double(parameters, self.REF_A, context)
            ref_b = self._optional_double(parameters, self.REF_B, context)
            auto_a, auto_b = ref_a is None, ref_b is None
            if ref_a is None or ref_b is None:
                vertici = []
                for feat in layer.getFeatures():
                    geom = feat.geometry()
                    if geom is None or geom.isEmpty():
                        continue
                    for v in geom.vertices():
                        if asse_h == 0:
                            vertici.append((v.x(), v.y()))
                        else:
                            vertici.append((v.y(), v.x()))
                if ref_a is None:
                    ref_a = edge_top(vertici, u_min, larghezza_locale)
                    if ref_a is None:
                        raise QgsProcessingException(
                            tr("err_dtm_edge").format(nome="A")
                        )
                if ref_b is None:
                    ref_b = edge_top(vertici, u_max, larghezza_locale)
                    if ref_b is None:
                        raise QgsProcessingException(
                            tr("err_dtm_edge").format(nome="B")
                        )

            for nome, valore, auto in (("A", ref_a, auto_a), ("B", ref_b, auto_b)):
                if auto and abs(valore) > LIMITE_QUOTA_LOCALE:
                    raise QgsProcessingException(
                        tr("err_dtm_coords").format(nome=nome, valore=valore)
                    )

            z_base, shear, mismatch = dtm_anchor(
                z_a, z_b, ref_a, ref_b, esagerazione, cos_a, fit_b
            )

            feedback.pushInfo(tr("log_dtm_ab").format(za=z_a, zb=z_b))
            feedback.pushInfo(tr("log_dtm_ref").format(ra=ref_a, rb=ref_b))
            feedback.pushInfo(tr("log_dtm_base").format(zbase=z_base))
            feedback.pushInfo(tr("log_dtm_mismatch").format(m=mismatch))
            if fit_b:
                feedback.pushInfo(tr("log_dtm_fit"))
            if abs(math.degrees(angolo)) > 1e-9:
                feedback.pushWarning(tr("log_dtm_tilt"))

        def ruota_punto(px, py):
            if asse_h == 0:
                u, v = px, py
            else:
                u, v = py, px

            v = v * esagerazione  # esagerazione verticale, prima della rotazione

            frazione = (u - u_min) / larghezza_locale  # 0 in A, 1 in B
            d = (u - u_min) * scala  # distanza reale da A lungo A-B
            avanzamento = d + v * sin_a  # spostamento lungo la linea A-B
            X = ax + hx * avanzamento
            Y = ay + hy * avanzamento
            lateral = (v - v_min) * inclinazione
            X += px_ * lateral
            Y += py_ * lateral
            Z = z_base + z_offset + v * cos_a + shear * frazione
            return X, Y, Z

        fields = layer.fields()
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            tipo_out,
            crs,
        )

        total = layer.featureCount() or 1
        for i, feat in enumerate(layer.getFeatures()):
            if feedback.isCanceled():
                break

            geom = feat.geometry()
            if geom is None or geom.isEmpty():
                continue

            if modo_geom == "poligoni":
                geom = self._pulisci_poligoni(geom)
                if geom is None or geom.isEmpty():
                    continue
                ring_groups = (
                    geom.asMultiPolygon() if geom.isMultipart() else [geom.asPolygon()]
                )
                parti = []
                for rings in ring_groups:
                    new_rings = []
                    for ring in rings:
                        new_pts = []
                        for pt in ring:
                            X, Y, Z = ruota_punto(pt.x(), pt.y())
                            new_pts.append(QgsPoint(X, Y, Z))
                        new_rings.append(new_pts)

                    poly = QgsPolygon()
                    poly.setExteriorRing(QgsLineString(new_rings[0]))
                    for hole in new_rings[1:]:
                        poly.addInteriorRing(QgsLineString(hole))
                    parti.append(poly)
                contenitore = QgsMultiPolygon
            else:
                linee = (
                    geom.asMultiPolyline() if geom.isMultipart() else [geom.asPolyline()]
                )
                parti = []
                for linea in linee:
                    new_pts = []
                    for pt in linea:
                        X, Y, Z = ruota_punto(pt.x(), pt.y())
                        new_pts.append(QgsPoint(X, Y, Z))
                    parti.append(QgsLineString(new_pts))
                contenitore = QgsMultiLineString

            if len(parti) == 1:
                new_geom = QgsGeometry(parti[0])
            else:
                multi = contenitore()
                for parte in parti:
                    multi.addGeometry(parte)
                new_geom = QgsGeometry(multi)

            new_feat = QgsFeature(fields)
            new_feat.setAttributes(feat.attributes())
            new_feat.setGeometry(new_geom)
            sink.addFeature(new_feat)

            feedback.setProgress(int(100 * i / total))

        return {self.OUTPUT: dest_id}

    def name(self):
        return "place_section_3d"

    def displayName(self):
        return tr("alg_name")

    def group(self):
        return tr("group")

    def groupId(self):
        return "geology"

    def shortHelpString(self):
        return tr("help")

    def createInstance(self):
        return Geological3DCrossSectionAlgorithm()
