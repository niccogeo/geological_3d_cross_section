"""
Geological 3D Cross Section - sezione 2D ancorata a due punti reali A (sinistra) e B (destra)
-----------------------------------------------------------------------------
Prende un layer di poligoni 2D che rappresenta una sezione (un asse locale
esprime la distanza orizzontale lungo la sezione, l'altro la quota/elevazione)
e la posiziona nello spazio 3D reale in modo che:

- l'estremo sinistro della sezione coincida con il Punto A;
- l'estremo destro della sezione coincida con il Punto B;
- l'intera sezione venga eventualmente inclinata (angolo di rotazione
  verticale) attorno alla linea A-B, come una cerniera;
- un offset di quota (Z) sposti l'intera sezione su/giù.

Azimuth e scala orizzontale vengono calcolati automaticamente dalla
distanza e direzione reale tra A e B: non serve inserirli a mano.
"""

import math

from qgis.core import (
    QgsProcessingAlgorithm,
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

    ASSI = [
        "X esprime la distanza lungo la sezione (Y è la quota)",
        "Y esprime la distanza lungo la sezione (X è la quota)",
    ]

    ESAGERAZIONI = ["x1 (nessuna)", "x2", "x2.5", "x5", "x10", "Personalizzata..."]
    VALORI_ESAGERAZIONE = [1.0, 2.0, 2.5, 5.0, 10.0, None]

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(self.INPUT, "Sezione 2D (poligoni)")
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ASSE_ORIZZONTALE,
                "Asse orizzontale della sezione nel layer originale",
                options=self.ASSI,
                defaultValue=0,
            )
        )
        self.addParameter(
            QgsProcessingParameterPoint(
                self.PUNTO_A, "Punto A (estremo sinistro della sezione)"
            )
        )
        self.addParameter(
            QgsProcessingParameterPoint(
                self.PUNTO_B, "Punto B (estremo destro della sezione)"
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.ANGOLO,
                "Angolo di rotazione verticale attorno alla linea A-B "
                "(gradi, 0 = sezione verticale, 90 = sezione sdraiata)",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.0,
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ESAGERAZIONE,
                "Esagerazione verticale (applicata alla quota prima della rotazione)",
                options=self.ESAGERAZIONI,
                defaultValue=0,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.ESAGERAZIONE_VAL,
                "Valore esagerazione personalizzata (usato solo se sopra è "
                "selezionato 'Personalizzata...')",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1.0,
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.ZOFFSET,
                "Offset di quota Z (aggiunto dopo la rotazione)",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.0,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, "Sezione ruotata 3D")
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
        if esagerazione is None:  # "Personalizzata..."
            esagerazione = self.parameterAsDouble(
                parameters, self.ESAGERAZIONE_VAL, context
            )
            if esagerazione <= 0:
                raise ValueError(
                    "Il valore di esagerazione verticale personalizzata deve "
                    "essere maggiore di zero."
                )

        crs = layer.sourceCrs()
        punto_a = self.parameterAsPoint(parameters, self.PUNTO_A, context, crs)
        punto_b = self.parameterAsPoint(parameters, self.PUNTO_B, context, crs)

        ax, ay = punto_a.x(), punto_a.y()
        bx, by = punto_b.x(), punto_b.y()
        dx, dy = bx - ax, by - ay
        lunghezza_reale = math.hypot(dx, dy)
        if lunghezza_reale == 0:
            raise ValueError(
                "Il Punto A e il Punto B coincidono: la sezione non ha una "
                "direzione definita."
            )
        hx, hy = dx / lunghezza_reale, dy / lunghezza_reale  # versore A->B

        extent = layer.extent()
        if asse_h == 0:
            u_min, u_max = extent.xMinimum(), extent.xMaximum()
        else:
            u_min, u_max = extent.yMinimum(), extent.yMaximum()

        larghezza_locale = u_max - u_min
        if larghezza_locale == 0:
            raise ValueError(
                "L'estensione della sezione lungo l'asse orizzontale scelto "
                "è nulla: controlla il parametro 'Asse orizzontale'."
            )
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
            QgsWkbTypes.MultiPolygon25D,
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
        return "Place 2D section in 3D (points A/B)"

    def group(self):
        return "Geologia"

    def groupId(self):
        return "geologia"

    def shortHelpString(self):
        return """
<h3>Geological 3D Cross Section</h3>

<h4>🇮🇹 Italiano</h4>
<p>Posiziona una <b>sezione geologica 2D</b> (poligoni) nello spazio 3D reale
tra due punti scelti sulla mappa: <b>A</b> (estremo sinistro) e
<b>B</b> (estremo destro). Azimuth e scala orizzontale vengono calcolati
automaticamente da A e B.</p>

<p><b>Preparazione della sezione.</b> La sezione deve essere disegnata nel
<b>piano XY</b>: un asse rappresenta la distanza orizzontale lungo la
sezione, l'altro la quota. Può essere:</p>
<ul>
<li>una sezione realizzata con il plugin <b>Geoscience</b>;</li>
<li>una sezione digitalizzata a partire da <b>sezioni scansionate in
raster</b> (georiferite nel piano XY).</li>
</ul>
<p>In entrambi i casi la sezione deve essere <b>geometricamente corretta e in
scala</b> (stessa unità di misura sui due assi). La distanza A-B dovrebbe
corrispondere alla lunghezza reale della sezione: la larghezza viene
adattata alla distanza A-B, mentre la quota no (se le due misure non
coincidono la sezione risulterà deformata).</p>

<p><b>Parametri.</b> Asse orizzontale del layer (X o Y) · Punto A e Punto B
(selezionabili con un click sulla mappa) · Angolo di rotazione attorno alla
linea A-B (0° = verticale, 90° = sdraiata) · Esagerazione verticale
(x1, x2, x2.5, x5, x10 o personalizzata) · Offset di quota Z.</p>

<p><b>Visualizzazione.</b> Il risultato è un layer poligonale con Z
(PolygonZ), visualizzabile con la <b>Vista Mappa 3D di QGIS</b> oppure con il
plugin <b>Qgis2threejs</b>.</p>

<hr/>
<h4>🇬🇧 English</h4>
<p>Places a <b>2D geological cross-section</b> (polygons) into real-world 3D
space between two points picked on the map: <b>A</b> (left end) and
<b>B</b> (right end). Azimuth and horizontal scale are computed automatically
from A and B.</p>

<p><b>Preparing the section.</b> The section must be drawn on the
<b>XY plane</b>: one axis is the horizontal distance along the section, the
other is elevation. It can be:</p>
<ul>
<li>a section created with the <b>Geoscience</b> plugin;</li>
<li>a section digitised from <b>scanned raster sections</b> (georeferenced on
the XY plane).</li>
</ul>
<p>In both cases the section must be <b>geometrically correct and to
scale</b> (same unit on both axes). The A-B distance should match the real
length of the section: the width is fitted to the A-B distance while
elevation is not (if the two do not match, the section will be
distorted).</p>

<p><b>Parameters.</b> Horizontal axis of the layer (X or Y) · Point A and
Point B (can be picked with a click on the map) · Rotation angle around the
A-B line (0° = vertical, 90° = lying flat) · Vertical exaggeration
(x1, x2, x2.5, x5, x10 or custom) · Z offset.</p>

<p><b>Visualisation.</b> The output is a polygon layer with Z (PolygonZ), which
can be viewed with the <b>QGIS 3D Map View</b> or with the
<b>Qgis2threejs</b> plugin.</p>

<hr/>
<p><i>Author / Autore: Niccolò Iandelli, with the support of Claude ·
info@ambientegis.com<br/>
Further developments are already in progress / Altri sviluppi sono già in
lavorazione.</i></p>
"""

    def createInstance(self):
        return Geological3DCrossSectionAlgorithm()
