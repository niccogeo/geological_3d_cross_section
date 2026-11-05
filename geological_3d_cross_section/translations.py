"""
Traduzioni (italiano / inglese) e gestione della lingua scelta dall'utente.

La lingua viene salvata nelle impostazioni di QGIS (QgsSettings) e, alla
prima apertura, segue la lingua di QGIS: italiano se QGIS è in italiano,
inglese in tutti gli altri casi.
"""

from qgis.core import QgsApplication, QgsSettings

SETTINGS_KEY = "geological_3d_cross_section/language"
LANGUAGES = ("it", "en")
DEFAULT_LANGUAGE = "en"


def get_language():
    """Restituisce 'it' oppure 'en'."""
    lang = QgsSettings().value(SETTINGS_KEY, "", type=str)
    if lang in LANGUAGES:
        return lang
    try:
        locale = QgsApplication.locale() or ""
    except Exception:
        locale = ""
    return "it" if locale.lower().startswith("it") else DEFAULT_LANGUAGE


def set_language(lang):
    if lang in LANGUAGES:
        QgsSettings().setValue(SETTINGS_KEY, lang)


def tr(key):
    """Testo tradotto nella lingua corrente (se manca, ricade sull'inglese)."""
    lang = get_language()
    return STRINGS.get(lang, {}).get(key) or STRINGS["en"].get(key, key)


HELP_IT = """
<h3>Geological 3D Cross Section</h3>

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

<p><b>Quota da DTM (facoltativo).</b> Se indichi un <b>DTM</b>, la quota Z dei
punti A e B viene letta dal DTM e la sezione viene portata a quella quota: il
profilo superiore della sezione (la superficie topografica) in A coincide con
il DTM in A. Senza DTM la sezione resta alla quota locale del layer (più l'offset
Z). La quota locale del profilo superiore viene riconosciuta in automatico
(punto più alto della sezione ai due estremi) e puoi forzarla nei parametri
avanzati. Se il profilo della sezione non coincide con il DTM anche in B, il
messaggio nel log indica la differenza; con l'opzione <i>Adatta anche in B</i>
la differenza viene distribuita linearmente lungo la sezione (la sezione viene
leggermente deformata in verticale). Il DTM funziona al meglio con sezioni
verticali (angolo 0°).</p>

<p><b>Visualizzazione.</b> Il risultato è un layer poligonale con Z
(PolygonZ), visualizzabile con la <b>Vista Mappa 3D di QGIS</b> oppure con il
plugin <b>Qgis2threejs</b>.</p>

<p><b>Lingua.</b> Puoi passare da italiano a inglese dal menu
<i>Plugin &rarr; Geological 3D Cross Section</i>.</p>

<hr/>
<p><i>Autore: Niccolò Iandelli, con il supporto di Claude ·
info@ambientegis.com<br/>
Altri sviluppi sono già in lavorazione.</i></p>
"""

HELP_EN = """
<h3>Geological 3D Cross Section</h3>

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

<p><b>Elevation from a DTM (optional).</b> If you select a <b>DTM</b>, the
Z of points A and B is read from the DTM and the section is moved to that
elevation: the top profile of the section (the topographic surface) at A
matches the DTM at A. Without a DTM the section stays at the local elevation of
the layer (plus the Z offset). The local elevation of the top profile is
detected automatically (highest point of the section at both ends) and you can
override it in the advanced parameters. If the section profile does not match
the DTM at B as well, the log message reports the difference; with the
<i>Also fit at B</i> option the difference is spread linearly along the section
(the section is slightly stretched vertically). The DTM works best with
vertical sections (angle 0°).</p>

<p><b>Visualisation.</b> The output is a polygon layer with Z (PolygonZ), which
can be viewed with the <b>QGIS 3D Map View</b> or with the
<b>Qgis2threejs</b> plugin.</p>

<p><b>Language.</b> You can switch between Italian and English from the
<i>Plugins &rarr; Geological 3D Cross Section</i> menu.</p>

<hr/>
<p><i>Author: Niccolò Iandelli, with the support of Claude ·
info@ambientegis.com<br/>
Further developments are already in progress.</i></p>
"""

STRINGS = {
    "it": {
        # plugin / menu
        "action_tooltip": "Posiziona una sezione geologica 2D in 3D tra i punti A e B",
        "lang_it": "Lingua / Language: Italiano",
        "lang_en": "Lingua / Language: English",
        "lang_changed": "Lingua impostata: Italiano. Si applica alla prossima apertura della finestra.",
        "plugin_title": "Geological 3D Cross Section",
        # algoritmo
        "alg_name": "Posiziona sezione 2D in 3D (punti A/B)",
        "group": "Geologia",
        "p_input": "Sezione 2D (poligoni)",
        "p_axis": "Asse orizzontale della sezione nel layer originale",
        "axis_x": "X esprime la distanza lungo la sezione (Y è la quota)",
        "axis_y": "Y esprime la distanza lungo la sezione (X è la quota)",
        "p_point_a": "Punto A (estremo sinistro della sezione)",
        "p_point_b": "Punto B (estremo destro della sezione)",
        "p_angle": (
            "Angolo di rotazione verticale attorno alla linea A-B "
            "(gradi, 0 = sezione verticale, 90 = sezione sdraiata)"
        ),
        "p_exag": "Esagerazione verticale (applicata alla quota prima della rotazione)",
        "exag_none": "x1 (nessuna)",
        "exag_custom": "Personalizzata...",
        "p_exag_val": (
            "Valore esagerazione personalizzata (usato solo se sopra è "
            "selezionato 'Personalizzata...')"
        ),
        "p_zoffset": "Offset di quota Z (aggiunto dopo la rotazione)",
        "p_dtm": "DTM per la quota dei punti A e B (facoltativo)",
        "p_ref_a": (
            "Quota locale del profilo superiore in A (facoltativo, "
            "altrimenti automatica)"
        ),
        "p_ref_b": (
            "Quota locale del profilo superiore in B (facoltativo, "
            "altrimenti automatica)"
        ),
        "p_fit_b": (
            "Adatta anche in B alla quota del DTM (deforma la sezione "
            "in verticale)"
        ),
        "log_dtm_ab": "DTM: quota in A = {za:.3f}, quota in B = {zb:.3f}",
        "log_dtm_ref": (
            "Profilo superiore della sezione (quota locale): in A = {ra:.3f}, "
            "in B = {rb:.3f}"
        ),
        "log_dtm_base": "Spostamento verticale applicato dal DTM: {zbase:.3f}",
        "log_dtm_mismatch": (
            "Differenza tra DTM e profilo della sezione in B: {m:.3f} "
            "(positivo = il DTM è più alto della sezione)"
        ),
        "log_dtm_fit": "La differenza in B è stata distribuita lungo la sezione.",
        "log_dtm_tilt": (
            "Attenzione: con una sezione inclinata il DTM è letto nei punti "
            "A e B, ma il profilo superiore si sposta in orizzontale."
        ),
        "err_dtm_sample": (
            "Il DTM non ha un valore valido nel punto {nome} "
            "(fuori dall'estensione o senza dato)."
        ),
        "err_dtm_edge": (
            "Non riesco a riconoscere il profilo superiore della sezione in "
            "{nome}: indica la quota locale nei parametri avanzati."
        ),
        "p_output": "Sezione ruotata 3D",
        "err_exag": (
            "Il valore di esagerazione verticale personalizzata deve "
            "essere maggiore di zero."
        ),
        "err_ab": (
            "Il Punto A e il Punto B coincidono: la sezione non ha una "
            "direzione definita."
        ),
        "err_width": (
            "L'estensione della sezione lungo l'asse orizzontale scelto "
            "è nulla: controlla il parametro 'Asse orizzontale'."
        ),
        "help": HELP_IT,
    },
    "en": {
        "action_tooltip": "Place a 2D geological section in 3D between points A and B",
        "lang_it": "Lingua / Language: Italiano",
        "lang_en": "Lingua / Language: English",
        "lang_changed": "Language set to English. It will apply the next time the dialog is opened.",
        "plugin_title": "Geological 3D Cross Section",
        "alg_name": "Place 2D section in 3D (points A/B)",
        "group": "Geology",
        "p_input": "2D section (polygons)",
        "p_axis": "Horizontal axis of the section in the source layer",
        "axis_x": "X is the distance along the section (Y is elevation)",
        "axis_y": "Y is the distance along the section (X is elevation)",
        "p_point_a": "Point A (left end of the section)",
        "p_point_b": "Point B (right end of the section)",
        "p_angle": (
            "Vertical rotation angle around the A-B line "
            "(degrees, 0 = vertical section, 90 = lying flat)"
        ),
        "p_exag": "Vertical exaggeration (applied to elevation before rotation)",
        "exag_none": "x1 (none)",
        "exag_custom": "Custom...",
        "p_exag_val": (
            "Custom exaggeration value (only used if 'Custom...' is "
            "selected above)"
        ),
        "p_zoffset": "Z offset (added after rotation)",
        "p_dtm": "DTM for the elevation of points A and B (optional)",
        "p_ref_a": (
            "Local elevation of the top profile at A (optional, "
            "otherwise automatic)"
        ),
        "p_ref_b": (
            "Local elevation of the top profile at B (optional, "
            "otherwise automatic)"
        ),
        "p_fit_b": (
            "Also fit at B to the DTM elevation (stretches the section "
            "vertically)"
        ),
        "log_dtm_ab": "DTM: elevation at A = {za:.3f}, elevation at B = {zb:.3f}",
        "log_dtm_ref": (
            "Top profile of the section (local elevation): at A = {ra:.3f}, "
            "at B = {rb:.3f}"
        ),
        "log_dtm_base": "Vertical shift applied from the DTM: {zbase:.3f}",
        "log_dtm_mismatch": (
            "Difference between the DTM and the section profile at B: "
            "{m:.3f} (positive = the DTM is higher than the section)"
        ),
        "log_dtm_fit": "The difference at B was spread along the section.",
        "log_dtm_tilt": (
            "Warning: with a tilted section the DTM is read at points A and "
            "B, but the top profile moves horizontally."
        ),
        "err_dtm_sample": (
            "The DTM has no valid value at point {nome} "
            "(outside the extent or no data)."
        ),
        "err_dtm_edge": (
            "Cannot detect the top profile of the section at {nome}: set "
            "the local elevation in the advanced parameters."
        ),
        "p_output": "Rotated 3D section",
        "err_exag": "The custom vertical exaggeration value must be greater than zero.",
        "err_ab": (
            "Point A and Point B are the same: the section has no "
            "defined direction."
        ),
        "err_width": (
            "The extent of the section along the chosen horizontal axis "
            "is zero: check the 'Horizontal axis' parameter."
        ),
        "help": HELP_EN,
    },
}
