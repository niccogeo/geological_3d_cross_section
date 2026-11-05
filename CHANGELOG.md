# Changelog

All notable changes to **Geological 3D Cross Section** are documented in this file.
Tutte le modifiche rilevanti a **Geological 3D Cross Section** sono documentate in questo file.

## [1.2] - 2026-11-05

### English
**Added**
- Optional **DTM** parameter: the elevation of points A and B is read from the DTM (band 1) and the section is moved to that real elevation. Before, the section stayed at its local elevation while the DTM was at its real height in the 3D view.
- The top profile of the section (topographic surface) is detected automatically at both ends; it can be set manually in the advanced parameters.
- *Also fit at B* option: the difference between the DTM and the section profile at B is spread linearly along the section.
- The processing log reports the DTM elevations, the local reference values and the difference at B.

**Notes**
- Without a DTM the behaviour is unchanged.
- The DTM works best with vertical sections (angle 0°).

### Italiano
**Aggiunto**
- Parametro **DTM** facoltativo: la quota dei punti A e B viene letta dal DTM (banda 1) e la sezione viene portata a quella quota reale. Prima la sezione restava alla quota locale mentre il DTM stava alla sua altezza reale nella vista 3D.
- Il profilo superiore della sezione (superficie topografica) viene riconosciuto in automatico ai due estremi; si può indicare a mano nei parametri avanzati.
- Opzione *Adatta anche in B*: la differenza tra DTM e profilo della sezione in B viene distribuita linearmente lungo la sezione.
- Il log di elaborazione riporta le quote del DTM, i valori locali di riferimento e la differenza in B.

**Note**
- Senza DTM il comportamento resta invariato.
- Il DTM funziona al meglio con sezioni verticali (angolo 0°).

## [1.1] - 2026-10-06

### English
**Added**
- Selectable interface language (Italian / English) from the *Plugins → Geological 3D Cross Section* menu.
- On first run the plugin follows the QGIS language, then remembers the user's choice.
- Processing dialog (parameters, drop-down lists), help text, group name and toolbar tooltip are translated.

**Changed**
- Errors in the Processing dialog (e.g. points A and B coincide) are now shown as clear messages instead of a Python traceback.
- The help text shows only the selected language.

**Fixed**
- Qt6 compatibility: `QAction` is imported from `QtGui` with a fallback to `QtWidgets` for Qt5.
- Qt6 compatibility: fully qualified enums for `QgsWkbTypes` and `QgsProcessingParameterNumber`.

### Italiano
**Aggiunto**
- Lingua dell'interfaccia selezionabile (italiano / inglese) dal menu *Plugin → Geological 3D Cross Section*.
- Alla prima apertura il plugin segue la lingua di QGIS, poi ricorda la scelta dell'utente.
- Finestra di Processing (parametri, menu a tendina), Help, nome del gruppo e tooltip del pulsante sono tradotti.

**Modificato**
- Gli errori nella finestra di Processing (per esempio punti A e B coincidenti) sono mostrati come messaggi chiari invece del traceback di Python.
- L'Help mostra solo la lingua selezionata.

**Corretto**
- Compatibilità Qt6: `QAction` viene importato da `QtGui`, con ripiego su `QtWidgets` per Qt5.
- Compatibilità Qt6: enum completi per `QgsWkbTypes` e `QgsProcessingParameterNumber`.

## [1.0] - 2026-09-30

### English
First public release.
- Places a 2D geological cross-section into real-world 3D space between point A (left end) and point B (right end).
- Vertical tilt around the A-B line.
- Vertical exaggeration: x1, x2, x2.5, x5, x10 or custom.
- Z offset.
- Toolbar button, Plugins menu entry and Processing algorithm.
- Bilingual help (IT/EN).

### Italiano
Prima versione pubblica.
- Posiziona una sezione geologica 2D nello spazio 3D reale tra il punto A (estremo sinistro) e il punto B (estremo destro).
- Inclinazione verticale attorno alla linea A-B.
- Esagerazione verticale: x1, x2, x2.5, x5, x10 o personalizzata.
- Offset di quota Z.
- Pulsante in barra strumenti, voce nel menu Plugin e algoritmo di Processing.
- Help bilingue (IT/EN).
