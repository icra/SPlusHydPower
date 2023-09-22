"""
Model exported as python.
Name : 6 WP aesthetics of waterscapes
Group : 
With QGIS : 31614
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class WpAestheticsOfWaterscapes(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('CapaLULCSWAT', 'Capa LULC SWAT', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('CaparivsSWAT', 'Capa rivs SWAT', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('CapaResultat', 'Capa resultat', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(10, model_feedback)
        results = {}
        outputs = {}

        # Buffer 500 metres canals
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 500,
            'END_CAP_STYLE': 0,
            'INPUT': parameters['CaparivsSWAT'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer500MetresCanals'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Buffer 50 metres canals
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 50,
            'END_CAP_STYLE': 0,
            'INPUT': parameters['CaparivsSWAT'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer50MetresCanals'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': '\"DN\" = 1 OR \"DN\" = 2',
            'INPUT': parameters['CapaLULCSWAT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Fix geometries
        alg_params = {
            'INPUT': outputs['ExtractByExpression']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometries'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Clip LULC urba 50 m canals
        alg_params = {
            'INPUT': outputs['FixGeometries']['OUTPUT'],
            'OVERLAY': outputs['Buffer50MetresCanals']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipLulcUrba50MCanals'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Càlcul ha de sòl urbà
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'surf',
            'FIELD_PRECISION': 5,
            'FIELD_TYPE': 0,
            'FORMULA': '($area)*0.001',
            'INPUT': outputs['ClipLulcUrba50MCanals']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClculHaDeSlUrb'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Difference
        alg_params = {
            'INPUT': outputs['Buffer500MetresCanals']['OUTPUT'],
            'OVERLAY': outputs['Buffer50MetresCanals']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Difference'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Selecció UHD
        alg_params = {
            'EXPRESSION': '\"DN\"=1',
            'INPUT': outputs['ClculHaDeSlUrb']['OUTPUT'],
            'METHOD': 0
        }
        outputs['SelecciUhd'] = processing.run('qgis:selectbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Càlcul Hpd
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Hdp',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': '\"surf\"*194.129488213811',
            'INPUT': outputs['SelecciUhd']['OUTPUT'],
            'OUTPUT': parameters['CapaResultat']
        }
        outputs['ClculHpd'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['CapaResultat'] = outputs['ClculHpd']['OUTPUT']

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Clip LULC urba 500-50 m canals
        alg_params = {
            'INPUT': outputs['FixGeometries']['OUTPUT'],
            'OVERLAY': outputs['Difference']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipLulcUrba50050MCanals'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return '6 WP aesthetics of waterscapes'

    def displayName(self):
        return '6 WP aesthetics of waterscapes'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return WpAestheticsOfWaterscapes()
