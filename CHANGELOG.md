# Changelog

All notable changes to **Geological 3D Cross Section** are documented in this file.
Tutte le modifiche rilevanti a **Geological 3D Cross Section** sono documentate in questo file.

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
