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
- la quota possa essere esagerata (esagerazione verticale) e traslata (offset Z).

Azimuth e scala orizzontale sono calcolati da A e B.
"""

import math

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterPoint,
    QgsProcessingParameterFeatureSink,
    QgsFeature,
    QgsGeometry,
    QgsWkbTypes,
    QgsPolygon,
    QgsMultiPolygon,
    QgsLineString,
    QgsPoint,
)

from .translations import tr


class Geological3DCrossSectionAlgorithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    ASSE_ORIZZONTALE = "ASSE_ORIZZONTALE"
    PUNTO_A = "PUNTO_A"
    PUNTO_B = "PUNTO_B"
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
            QgsProcessingParameterNumber(
                self.ZOFFSET,
                tr("p_zoffset"),
                type=QgsProcessingParameterNumber.Type.Double,
                defaultValue=0.0,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, tr("p_output"))
        )

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

        cos_a, sin_a = math.cos(angolo), math.sin(angolo)

        def ruota_punto(px, py):
            if asse_h == 0:
                u, v = px, py
            else:
                u, v = py, px

            v = v * esagerazione  # esagerazione verticale, prima della rotazione

            d = (u - u_min) * scala  # distanza reale da A lungo A-B
            avanzamento = d + v * sin_a  # spostamento lungo la linea A-B
            X = ax + hx * avanzamento
            Y = ay + hy * avanzamento
            Z = z_offset + v * cos_a
            return X, Y, Z

        fields = layer.fields()
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.Type.MultiPolygon25D,
            crs,
        )

        total = layer.featureCount() or 1
        for i, feat in enumerate(layer.getFeatures()):
            if feedback.isCanceled():
                break

            geom = feat.geometry()
            if geom is None or geom.isEmpty():
                continue

            ring_groups = (
                geom.asMultiPolygon() if geom.isMultipart() else [geom.asPolygon()]
            )

            polys3d = []
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
                polys3d.append(poly)

            if len(polys3d) == 1:
                new_geom = QgsGeometry(polys3d[0])
            else:
                mp = QgsMultiPolygon()
                for p in polys3d:
                    mp.addGeometry(p)
                new_geom = QgsGeometry(mp)

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
