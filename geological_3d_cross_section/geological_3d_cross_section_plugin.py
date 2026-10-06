import os

try:  # Qt6 / QGIS recenti
    from qgis.PyQt.QtGui import QAction
except ImportError:  # Qt5
    from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication

from .geological_3d_cross_section_provider import Geological3DCrossSectionProvider
from .translations import get_language, set_language, tr

MENU_TITLE = "&Geological 3D Cross Section"


class Geological3DCrossSectionPlugin:
    """Registra il provider Processing, aggiunge un pulsante in barra
    strumenti per aprire l'algoritmo e due voci di menu per scegliere
    la lingua (italiano / inglese)."""

    ALG_ID = "geological_3d_cross_section:place_section_3d"

    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.action = None
        self.action_it = None
        self.action_en = None
        self.plugin_dir = os.path.dirname(__file__)

    # ------------------------------------------------------------------ GUI
    def initGui(self):
        self._add_provider()

        icon_path = os.path.join(self.plugin_dir, "icon.png")
        self.action = QAction(
            QIcon(icon_path), tr("plugin_title"), self.iface.mainWindow()
        )
        self.action.setToolTip(tr("action_tooltip"))
        self.action.triggered.connect(self.run)

        self.action_it = QAction(tr("lang_it"), self.iface.mainWindow())
        self.action_it.setCheckable(True)
        self.action_it.triggered.connect(lambda: self.change_language("it"))

        self.action_en = QAction(tr("lang_en"), self.iface.mainWindow())
        self.action_en.setCheckable(True)
        self.action_en.triggered.connect(lambda: self.change_language("en"))

        self._update_language_checks()

        # pulsante in barra degli strumenti
        self.iface.addToolBarIcon(self.action)
        # voci nel menu Plugin
        self.iface.addPluginToMenu(MENU_TITLE, self.action)
        self.iface.addPluginToMenu(MENU_TITLE, self.action_it)
        self.iface.addPluginToMenu(MENU_TITLE, self.action_en)

    def unload(self):
        if self.action is not None:
            self.iface.removeToolBarIcon(self.action)
        for act in (self.action, self.action_it, self.action_en):
            if act is not None:
                self.iface.removePluginMenu(MENU_TITLE, act)
        self.action = self.action_it = self.action_en = None
        self._remove_provider()

    # ------------------------------------------------------------- provider
    def _add_provider(self):
        self.provider = Geological3DCrossSectionProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def _remove_provider(self):
        if self.provider is not None:
            QgsApplication.processingRegistry().removeProvider(self.provider)
            self.provider = None

    # -------------------------------------------------------------- lingua
    def _update_language_checks(self):
        lang = get_language()
        self.action_it.setChecked(lang == "it")
        self.action_en.setChecked(lang == "en")

    def change_language(self, lang):
        set_language(lang)
        self._update_language_checks()
        if self.action is not None:
            self.action.setToolTip(tr("action_tooltip"))
        # ricarico il provider per aggiornare i nomi nel Processing Toolbox
        self._remove_provider()
        self._add_provider()
        self.iface.messageBar().pushInfo(tr("plugin_title"), tr("lang_changed"))

    # ------------------------------------------------------------ esecuzione
    def run(self):
        """Apre la finestra standard di Processing per l'algoritmo."""
        import processing

        processing.execAlgorithmDialog(self.ALG_ID, {})
