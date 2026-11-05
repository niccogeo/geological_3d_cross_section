# Geological 3D Cross Section

QGIS plugin · **v1.2**  
Author: **Niccolò Iandelli**, with the support of Claude · info@ambientegis.com

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-niccogeo-FFDD00?logo=buymeacoffee&logoColor=black)](https://www.buymeacoffee.com/niccogeo)

---

### English
**Added**
- **Viewer** option (QGIS 3D native / Qgis2threejs): for Qgis2threejs the section is leaned sideways by 0.2% of the elevation so that polygons are triangulated correctly. Geometries are also fixed (invalid geometries, duplicate vertices) before the transformation.
- **Keep proportions (uniform scale)** option: elevation is multiplied by the same factor as the A-B distance. Use it when the scanned section was georeferenced at too small a scale (A-B much longer than the section width).
- The section layer can contain **lines** as well as polygons.
- Clear error if the section layer is in map coordinates instead of local coordinates.
- Optional **DTM** parameter: the elevation of points A and B is read from the DTM (band 1) and the section is moved to that real elevation. Before, the section stayed at its local elevation while the DTM was at its real height in the 3D view.
- The top profile of the section (topographic surface) is detected automatically at both ends; it can be set manually in the advanced parameters.
- *Also fit at B* option: the difference between the DTM and the section profile at B is spread linearly along the section.
- The processing log reports the DTM elevations, the local reference values and the difference at B.

**Notes**
- Without a DTM the behaviour is unchanged.
- The DTM works best with vertical sections (angle 0°).

### Italiano
**Aggiunto**
- Opzione **Visualizzatore** (Vista 3D nativa di QGIS / Qgis2threejs): per Qgis2threejs la sezione viene inclinata lateralmente dello 0,2% della quota così i poligoni vengono triangolati correttamente. Le geometrie vengono anche corrette (non valide, vertici duplicati) prima della trasformazione.
- Opzione **Mantieni le proporzioni (scala uniforme)**: la quota viene moltiplicata per lo stesso fattore della distanza A-B. Da usare quando la sezione scansionata è stata georiferita in scala troppo piccola (A-B molto più lungo della larghezza della sezione).
- Il layer della sezione può contenere **linee** oltre ai poligoni.
- Errore chiaro se il layer della sezione è in coordinate di mappa invece che locali.
- Parametro **DTM** facoltativo: la quota dei punti A e B viene letta dal DTM (banda 1) e la sezione viene portata a quella quota reale. Prima la sezione restava alla quota locale mentre il DTM stava alla sua altezza reale nella vista 3D.
- Il profilo superiore della sezione (superficie topografica) viene riconosciuto in automatico ai due estremi; si può indicare a mano nei parametri avanzati.
- Opzione *Adatta anche in B*: la differenza tra DTM e profilo della sezione in B viene distribuita linearmente lungo la sezione.
- Il log di elaborazione riporta le quote del DTM, i valori locali di riferimento e la differenza in B.

**Note**
- Senza DTM il comportamento resta invariato.
- Il DTM funziona al meglio con sezioni verticali (angolo 0°).

## License
GPL-2.0-or-later
