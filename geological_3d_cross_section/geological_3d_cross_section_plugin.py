import os

from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication

from .geological_3d_cross_section_provider import Geological3DCrossSectionProvider


class Geological3DCrossSectionPlugin:
    """Plugin che registra il provider Processing con l'algoritmo di
    rotazione e aggiunge un pulsante in barra strumenti per lanciarlo
    rapidamente, senza dover cercare l'algoritmo nel Processing Toolbox."""

    ALG_ID = "geological_3d_cross_section:place_section_3d"

    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.action = None
        self.plugin_dir = os.path.dirname(__file__)

    def initGui(self):
        self.provider = Geological3DCrossSectionProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

        icon_path = os.path.join(self.plugin_dir, "icon.png")
        self.action = QAction(
            QIcon(icon_path), "Geological 3D Cross Section", self.iface.mainWindow()
        )
        self.action.setToolTip(
            "Place a 2D geological section in 3D between points A and B"
        )
        self.action.triggered.connect(self.run)

        # pulsante in barra degli strumenti
        self.iface.addToolBarIcon(self.action)
        # voce nel menu Plugin
        self.iface.addPluginToMenu("&Geological 3D Cross Section", self.action)

    def unload(self):
        if self.action is not None:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu("&Geological 3D Cross Section", self.action)
            self.action = None
        if self.provider is not None:
            QgsApplication.processingRegistry().removeProvider(self.provider)
            self.provider = None

    def run(self):
        """Apre la finestra standard di Processing per l'algoritmo,
        con tutti i parametri (layer, asse, angolo, perno, output)."""
        import processing

        processing.execAlgorithmDialog(self.ALG_ID, {})
