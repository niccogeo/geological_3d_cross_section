# Geological 3D Cross Section

QGIS plugin · **v1.1**  
Author: **Niccolò Iandelli**, with the support of Claude · info@ambientegis.com

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-niccogeo-FFDD00?logo=buymeacoffee&logoColor=black)](https://www.buymeacoffee.com/niccogeo)

---

## English

Places a **2D geological cross-section** (polygon layer drawn on the XY plane) into real-world 3D space between two points picked on the map: **A** (left end) and **B** (right end). Azimuth and horizontal scale are computed automatically.

**Options**
- Point A / Point B (pick on the map or type coordinates)
- Rotation angle around the A-B line (0° = vertical, 90° = lying flat)
- Vertical exaggeration: x1, x2, x2.5, x5, x10 or custom
- Z offset

**Input section.** It can be created with the **Geoscience** plugin, or digitised from **scanned raster sections**. In both cases it must be **geometrically correct and to scale** (same unit on both axes). The A-B distance should match the real length of the section, otherwise it will be distorted horizontally.

**Visualisation.** The output is a PolygonZ layer: use the **QGIS 3D Map View** or the **Qgis2threejs** plugin.

**Where to find it.** Toolbar button, *Plugins → Geological 3D Cross Section*, or Processing Toolbox.

**Language.** The interface and help can be switched between Italian and English from the *Plugins → Geological 3D Cross Section* menu. On first run the plugin follows the QGIS language.

🚧 Further developments are already in progress.

## Italiano

Posiziona una **sezione geologica 2D** (poligoni disegnati sul piano XY) nello spazio 3D reale tra due punti scelti sulla mappa: **A** (estremo sinistro) e **B** (estremo destro). Azimuth e scala orizzontale sono calcolati automaticamente.

**Opzioni**
- Punto A / Punto B (selezione sulla mappa o coordinate)
- Angolo di rotazione attorno alla linea A-B (0° = verticale, 90° = sdraiata)
- Esagerazione verticale: x1, x2, x2.5, x5, x10 o personalizzata
- Offset di quota Z

**Sezione di partenza.** Può essere realizzata con il plugin **Geoscience**, oppure disegnata a partire da **sezioni scannerizzate in raster**. In entrambi i casi deve essere **geometricamente corretta e in scala** (stessa unità sui due assi). La distanza A-B deve corrispondere alla lunghezza reale della sezione, altrimenti risulterà deformata in orizzontale.

**Visualizzazione.** Il risultato è un layer PolygonZ: usa la **Vista Mappa 3D di QGIS** oppure il plugin **Qgis2threejs**.

**Dove si trova.** Pulsante in barra strumenti, *Plugin → Geological 3D Cross Section*, oppure Processing Toolbox.

**Lingua.** Interfaccia e Help si possono cambiare tra italiano e inglese dal menu *Plugin → Geological 3D Cross Section*. Alla prima apertura il plugin segue la lingua di QGIS.

🚧 Altri sviluppi sono già in lavorazione.

## License
GPL-2.0-or-later
