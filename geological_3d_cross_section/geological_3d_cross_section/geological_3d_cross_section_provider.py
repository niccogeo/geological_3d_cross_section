from qgis.core import QgsProcessingProvider
from .geological_3d_cross_section_algorithm import Geological3DCrossSectionAlgorithm


class Geological3DCrossSectionProvider(QgsProcessingProvider):

    def id(self):
        return "geological_3d_cross_section"

    def name(self):
        return "Geological 3D Cross Section"

    def icon(self):
        return QgsProcessingProvider.icon(self)

    def loadAlgorithms(self):
        self.addAlgorithm(Geological3DCrossSectionAlgorithm())
