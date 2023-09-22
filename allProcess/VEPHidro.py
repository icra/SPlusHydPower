"""
Model exported as python.
Name : Producció hidroelèctrica (VEPHidro)
Group : Aprovisionament
With QGIS : 31611
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsExpression
from qgis.core import QgsProcessingContext
from qgis.core import QgsProcessingFeedback
from qgis.core import QgsProject
from qgis.core import QgsProcessingUtils
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterString
import processing
import os


class ProducciHidroelctricaVephidro(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        
        #Get Path from folder
        cwp = r''
        cwp += os.path.dirname(os.path.realpath(__file__)).replace('\\','/')
        
        # Layer with information about hydropower stations
        self.addParameter(QgsProcessingParameterFile('CHlayers', 'Hydropower stations’ location (ROR) (Base case)', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=cwp + '\\GIS\\hydropower\\puntsCHs3.shp'))
        self.addParameter(QgsProcessingParameterFile('CHlayersSC', 'Hydropower stations’ location (ROR) (Scenario case)', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=cwp + '\\GIS\\hydropower\\puntsCHs3.shp'))
        # Layer with information about hydropower stations at reservoirs
        self.addParameter(QgsProcessingParameterFile('CHreservlayer', 'Hydropower stations’ location (Res) (Base case)', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=cwp + '\\GIS\\hydropower\\puntsCHemb.shp'))
        self.addParameter(QgsProcessingParameterFile('PuntsCHEmbCS', 'Hydropower stations’ location (Res) (Scenario case)', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=cwp + '\\GIS\\hydropower\\puntsCHemb.shp'))        # Layer of the CIC municipalities with CODIMUNI
        self.addParameter(QgsProcessingParameterFile('MUNISlayer', 'Administrative limits', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=cwp + '\\GIS\\munis\\munisbase.shp'))
        # Layer with the water extraction point to make work the HP stations. Those HP stations in tributaries out of the model are not included.
        self.addParameter(QgsProcessingParameterFile('WExtractPoints', 'Derivation points (Base case)', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=cwp + '\\GIS\\hydropower\\captacionsCH5.shp'))
        self.addParameter(QgsProcessingParameterFile('WExtractPointsSC', 'Derivation points (Scenario case)', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=cwp + '\\GIS\\hydropower\\captacionsCH5.shp'))
        # Channel output layer from SWAT. Baseline conditions
        self.addParameter(QgsProcessingParameterFile('rivs1SWATBC', 'Channels (Base case)', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=cwp + '\\GIS\\Models\\SWATPshp2\\rivs1.shp'))
        self.addParameter(QgsProcessingParameterFile('rivs1SWATSC', 'Channels (Scenario case)', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=cwp + '\\GIS\\Models\\SWATPshp2\\rivs1.shp'))
        # Channel output layer from SWAT. Scenario conditions
        self.addParameter(QgsProcessingParameterFile('sqliteoutputBC', 'SQLite database (Base case)', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=cwp + '\\GIS\\Models\\swatplus_output.sqlite'))
        self.addParameter(QgsProcessingParameterFile('sqliteoutputSC', 'SQLite database (Scenario case)', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=cwp + '\\GIS\\Models\\swatplus_output.sqlite'))
        self.addParameter(QgsProcessingParameterFeatureSink('Vephidro', 'EVHP', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        #User parameters
        self.addParameter(QgsProcessingParameterNumber('G', 'G-Acceleration of gravity (m/s^2)', type=QgsProcessingParameterNumber.Double, defaultValue=9.81))
        self.addParameter(QgsProcessingParameterNumber('HL', 'HL-Head loss coefficient', type=QgsProcessingParameterNumber.Double, defaultValue=0.925))
        self.addParameter(QgsProcessingParameterNumber('Rt', 'Rt-Turbines coefficient', type=QgsProcessingParameterNumber.Double, defaultValue=0.928))
        self.addParameter(QgsProcessingParameterNumber('Rg', 'Rg-Generator coefficient', type=QgsProcessingParameterNumber.Double, defaultValue=0.928))
        self.addParameter(QgsProcessingParameterNumber('Rs', 'Rs-Transformers coefficient', type=QgsProcessingParameterNumber.Double, defaultValue=0.928))
        self.addParameter(QgsProcessingParameterNumber('EP', 'EP-Electricity price (currency unit divided by KWh)', type=QgsProcessingParameterNumber.Double, defaultValue=0.1))
        self.addParameter(QgsProcessingParameterNumber('Year', 'Year of analysis', type=QgsProcessingParameterNumber.Integer, defaultValue=2018))
        self.addParameter(QgsProcessingParameterString('grosshead', 'HF (Gross head)', multiLine=False, defaultValue='Saltbrut'))
        self.addParameter(QgsProcessingParameterString('ftm', 'Ftm (Technical minimum flow)', multiLine=False, defaultValue='Qmt'))
        self.addParameter(QgsProcessingParameterString('QMC_jan', 'Fmef_Jan (Environmental flow on january)', multiLine=False, defaultValue='QMC_gen'))
        self.addParameter(QgsProcessingParameterString('QMC_feb', 'Fmef_Feb (Environmental flow on February)', multiLine=False, defaultValue='QMC_feb'))
        self.addParameter(QgsProcessingParameterString('QMC_mar', 'Fmef_Mar (Environmental flow on March)', multiLine=False, defaultValue='QMC_març'))
        self.addParameter(QgsProcessingParameterString('QMC_apr', 'Fmef_Apr (Environmental flow on April)', multiLine=False, defaultValue='QMC_abr'))
        self.addParameter(QgsProcessingParameterString('QMC_may', 'Fmef_May (Environmental flow on May)', multiLine=False, defaultValue='QMC_maig'))
        self.addParameter(QgsProcessingParameterString('QMC_jun', 'Fmef_June (Environmental flow on June)', multiLine=False, defaultValue='QMC_juny'))
        self.addParameter(QgsProcessingParameterString('QMC_jul', 'Fmef_Jul (Environmental flow on July)', multiLine=False, defaultValue='QMC_jul'))
        self.addParameter(QgsProcessingParameterString('QMC_aug', 'Fmef_Aug (Environmental flow on August)', multiLine=False, defaultValue='QMC_ago'))
        self.addParameter(QgsProcessingParameterString('QMC_sep', 'Fmef_Sept (Environmental flow on September)', multiLine=False, defaultValue='QMC_set'))
        self.addParameter(QgsProcessingParameterString('QMC_oct', 'Fmef_Oct (Environmental flow on October)', multiLine=False, defaultValue='QMC_oct'))
        self.addParameter(QgsProcessingParameterString('QMC_nov', 'Fmef_Nov (Environmental flow on November)', multiLine=False, defaultValue='QMC_nov'))
        self.addParameter(QgsProcessingParameterString('QMC_dec', 'Fmef_Dec (Environmental flow on january)', multiLine=False, defaultValue='QMC_dec'))

        self.addParameter(QgsProcessingParameterString('Fmac', 'Fmac (maximum flow allowed per contract) (RoR)', multiLine=False, defaultValue='CabalCon'))

        self.addParameter(QgsProcessingParameterString('HSID', 'HSID (Hydropower station ID)', multiLine=False, defaultValue='codiEntita'))
        self.addParameter(QgsProcessingParameterString('AdID', 'AdID (Administration unit ID)', multiLine=False, defaultValue='CODIMUNI'))


    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(67, model_feedback)
        results = {}
        outputs = {}

        # String concatenation - SC res
        alg_params = {
            'INPUT_1': parameters['sqliteoutputSC'],
            'INPUT_2': '|layername=reservoir_day'
        }
        outputs['StringConcatenationScRes'] = processing.run('native:stringconcatenation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # String concatenation - SC
        alg_params = {
            'INPUT_1': parameters['sqliteoutputSC'],
            'INPUT_2': '|layername=channel_sd_day'
        }
        outputs['StringConcatenationSc'] = processing.run('native:stringconcatenation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # String concatenation - BC res
        alg_params = {
            'INPUT_1': parameters['sqliteoutputBC'],
            'INPUT_2': '|layername=reservoir_day'
        }
        outputs['StringConcatenationBcRes'] = processing.run('native:stringconcatenation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Join attributes by location - CODIMUNI CH BC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['CHlayers'],
            'JOIN': parameters['MUNISlayer'],
            'JOIN_FIELDS': [parameters['AdID']],
            'METHOD': 0,
            'PREDICATE': [0],
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationCodimuniChBc'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest - Channel at codiRAcapt BC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['Channel'],
            'INPUT': parameters['WExtractPoints'],
            'INPUT_2': parameters['rivs1SWATBC'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearestChannelAtCodiracaptBc'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Extract by attribute  - Channel at codiRAcapt BC
        alg_params = {
            'FIELD': 'n',
            'INPUT': outputs['JoinAttributesByNearestChannelAtCodiracaptBc']['OUTPUT'],
            'OPERATOR': 0,
            'VALUE': '1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeChannelAtCodiracaptBc'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Join attributes by location - CODIMUNI CH SC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['CHlayersSC'],
            'JOIN': parameters['MUNISlayer'],
            'JOIN_FIELDS': [parameters['AdID']],
            'METHOD': 0,
            'PREDICATE': [0],
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationCodimuniChSc'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Extract by expression - reservoir_day SC
        # SWAT+OUTPUT-> Daily released flow results by reservoir with CH (m3/s). Scenario condition
        alg_params = {
            'EXPRESSION': f"\"yr\" = {parameters['Year']}",
            'INPUT': outputs['StringConcatenationScRes']['CONCATENATION'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionReservoir_daySc'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest - Channel at codiRAcapt SC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['Channel'],
            'INPUT': parameters['WExtractPointsSC'],
            'INPUT_2': parameters['rivs1SWATSC'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearestChannelAtCodiracaptSc'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # String concatenation - BC
        alg_params = {
            'INPUT_1': parameters['sqliteoutputBC'],
            'INPUT_2': '|layername=channel_sd_day'
        }
        outputs['StringConcatenationBc'] = processing.run('native:stringconcatenation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract by expression - channel_sd_day SC
        # SWAT+OUTPUT-> Daily flow results at channel section (m3/s). Scenario condition
        alg_params = {
            'EXPRESSION': f"\"yr\" = {parameters['Year']}",
            'INPUT': outputs['StringConcatenationSc']['CONCATENATION'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionChannel_sd_daySc'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Extract by expression - channel_sd_day BC
        # SWAT+OUTPUT-> Daily flow results at channel section (m3/s). Baseline condition
        alg_params = {
            'EXPRESSION': f"\"yr\" = {parameters['Year']}",
            'INPUT': outputs['StringConcatenationBc']['CONCATENATION'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionChannel_sd_dayBc'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - codiRAcapt to flo_outB
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'FIELD': 'gis_id',
            'FIELDS_TO_COPY': [parameters['HSID'],'codiRACapt',parameters['QMC_jan'],parameters['QMC_feb'],parameters['QMC_mar'],parameters['QMC_apr'],parameters['QMC_may'],parameters['QMC_jun'],parameters['QMC_jul'],parameters['QMC_aug'],parameters['QMC_sep'],parameters['QMC_oct'],parameters['QMC_nov'],parameters['QMC_dec'],'QPdG_gen','QPdG_feb','QPdG_març','QPdG_abr','QPdG_maig','QPdG_juny','QPdG_jul','QPdG_ago','QPdG_set','QPdG_oct','QPdG_nov','QPdG_des',parameters['Fmac'],parameters['grosshead'],parameters['ftm']],
            'FIELD_2': 'Channel',
            'INPUT': outputs['ExtractByExpressionChannel_sd_dayBc']['OUTPUT'],
            'INPUT_2': outputs['ExtractByAttributeChannelAtCodiracaptBc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueCodiracaptToFlo_outb'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Extract by expression - reservoir_day BC
        # SWAT+OUTPUT-> Daily released flow results by reservoir with CH (m3/s). Baseline condition
        alg_params = {
            'EXPRESSION': f"\"yr\" = {parameters['Year']}",
            'INPUT': outputs['StringConcatenationBcRes']['CONCATENATION'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionReservoir_dayBc'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Join attributes by location - CODIMUNI CHEmb BC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['CHreservlayer'],
            'JOIN': parameters['MUNISlayer'],
            'JOIN_FIELDS': [parameters['AdID']],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREDICATE': [0],  # intersects
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationCodimuniChembBc'] = processing.run('native:joinattributesbylocation', alg_params, context=context,feedback=feedback, is_child_algorithm=True)
        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Join attributes by location - CODIMUNI CHEmb SC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['PuntsCHEmbCS'],
            'JOIN': parameters['MUNISlayer'],
            'JOIN_FIELDS': [parameters['AdID']],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREDICATE': [0],  # intersects
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationCodimuniChembSc'] = processing.run('native:joinattributesbylocation',
                                                                            alg_params, context=context,
                                                                            feedback=feedback, is_child_algorithm=True)
        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}


        # Join attributes by field value - DEmbDFlowS with CHEmb
        alg_params = {
            'DISCARD_NONMATCHING': False,# Join attributes by field value - DEmbDFlowB with CHEmb BC

            'FIELD': 'gis_id',
            'FIELDS_TO_COPY': [parameters['Fmac'],parameters['grosshead'],parameters['ftm'],parameters['AdID']],
            'FIELD_2': 'gis_id',
            'INPUT': outputs['ExtractByExpressionReservoir_daySc']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByLocationCodimuniChembSc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueDembdflowsWithChemb'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - DEmbDFlowB with CHEmb BC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'gis_id',
            'FIELDS_TO_COPY': [parameters['Fmac'],parameters['grosshead'],parameters['ftm'],parameters['AdID']],
            'FIELD_2': 'gis_id',
            'INPUT': outputs['ExtractByExpressionReservoir_dayBc']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByLocationCodimuniChembBc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueDembdflowbWithChembBc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Extract by attribute  - Channel at codiRAcapt SC
        alg_params = {
            'FIELD': 'n',
            'INPUT': outputs['JoinAttributesByNearestChannelAtCodiracaptSc']['OUTPUT'],
            'OPERATOR': 0,
            'VALUE': '1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeChannelAtCodiracaptSc'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Field calculator - Qdisp calc BC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'Qdisp',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': f'case\r\nwhen \"mon\" = 1 then MAX (0,(\"flo_out\"-{parameters["QMC_jan"]})) \r\nwhen \"mon\" = 2 then MAX (0,(\"flo_out\"-{parameters["QMC_feb"]}))\r\nwhen \"mon\" = 3 then MAX (0,(\"flo_out\"-{parameters["QMC_mar"]}))\r\nwhen \"mon\" = 4 then MAX (0,(\"flo_out\"-{parameters["QMC_apr"]})) \r\nwhen \"mon\" = 5 then MAX (0,(\"flo_out\"-{parameters["QMC_may"]}))\r\nwhen \"mon\" = 6 then MAX (0,(\"flo_out\"-{parameters["QMC_jun"]}))\r\nwhen \"mon\" = 7 then MAX (0,(\"flo_out\"-{parameters["QMC_jul"]}))\r\nwhen \"mon\" = 8 then MAX (0,(\"flo_out\"-{parameters["QMC_aug"]}))\r\nwhen \"mon\" = 9 then MAX (0,(\"flo_out\"-{parameters["QMC_sep"]}))\r\nwhen month(\"Date\") = 10 then MAX (0,(\"flo_out\"-{parameters["QMC_oct"]}))\r\nwhen \"mon\" = 11 then MAX (0,(\"flo_out\"-{parameters["QMC_nov"]}))\r\nelse MAX (0,(\"flo_out\"-{parameters["QMC_dec"]}))\r\nend  \r\n',
            'INPUT': outputs['JoinAttributesByFieldValueCodiracaptToFlo_outb']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorQdispCalcBc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Field calculator - "DEmbDFlowS" double for res6
        #alg_params = {
        #    'FIELD_LENGTH': 15,
        #    'FIELD_NAME': 'DEmbDFlowS2',
        #    'FIELD_PRECISION': 3,
        #    'FIELD_TYPE': 0,
        #    'FORMULA': 'case\r\nwhen \"gis_id\"=\'6\' then \"flo_out\"*2\r\nelse \"flo_out\"\r\nend',
        #    'INPUT': outputs['JoinAttributesByFieldValueDembdflowsWithChemb']['OUTPUT'],
        #    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        #}
        #outputs['FieldCalculatorDembdflowsDoubleForRes6'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)


        # Field calculator - QPTurb calc BC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'QPTurb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': f'min({parameters["Fmac"]}, \"Qdisp\")',
            'INPUT': outputs['FieldCalculatorQdispCalcBc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorQpturbCalcBc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Field calculator - Daily ID by CH (CodiCHDia) BC
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'CodiCHDia',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,
            'FORMULA': f'concat ({parameters["HSID"]},\'_\',\"day\", \"mon\")',
            'INPUT': outputs['FieldCalculatorQpturbCalcBc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDailyIdByChCodichdiaBc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - codiRAcapt to FlowS
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'FIELD': 'gis_id',
            'FIELDS_TO_COPY': [parameters['HSID'],'codiRACapt',parameters['QMC_jan'],parameters['QMC_feb'],parameters['QMC_mar'],parameters['QMC_apr'],parameters['QMC_may'],parameters['QMC_jun'],parameters['QMC_jul'],parameters['QMC_aug'],parameters['QMC_sep'],parameters['QMC_oct'],parameters['QMC_nov'],parameters['QMC_dec'],'QPdG_gen','QPdG_feb','QPdG_març','QPdG_abr','QPdG_maig','QPdG_juny','QPdG_jul','QPdG_ago','QPdG_set','QPdG_oct','QPdG_nov','QPdG_des',parameters['Fmac'],parameters['grosshead'],parameters['ftm']],
            'FIELD_2': 'Channel',
            'INPUT': outputs['ExtractByExpressionChannel_sd_daySc']['OUTPUT'],
            'INPUT_2': outputs['ExtractByAttributeChannelAtCodiracaptSc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueCodiracaptToFlows'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Field calculator - DEVhpEmb SC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'DEVhpEmb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': f"case\r\nwhen \"flo_out\" >= {parameters['ftm']} then ({parameters['G']}*min(\"flo_out\",{parameters['Fmac']})*({parameters['HL']})*{parameters['Rt']}*{parameters['Rg']}*{parameters['Rs']}*24*{parameters['EP']})\r\nelse 0\r\nend",
            'INPUT': outputs['JoinAttributesByFieldValueDembdflowsWithChemb']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDevhpembSc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Field calculator - "DEmbDFlowB" double for res6
        #alg_params = {
        #    'FIELD_LENGTH': 15,
        #    'FIELD_NAME': 'DEmbDFlowB2',
        #    'FIELD_PRECISION': 3,
        #    'FIELD_TYPE': 0,
        #    'FORMULA': 'case\r\nwhen \"gis_id\"=\'6\' then \"flo_out\"*2\r\nelse \"flo_out\"\r\nend',
        #    'INPUT': outputs['JoinAttributesByFieldValueDembdflowbWithChembBc']['OUTPUT'],
        #    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        #}
        #outputs['FieldCalculatorDembdflowbDoubleForRes6'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - QPTurb at CodiCHDia BC
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['CodiCHDia'],
            'INPUT': outputs['FieldCalculatorDailyIdByChCodichdiaBc']['OUTPUT'],
            'VALUES_FIELD_NAME': 'QPTurb',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesQpturbAtCodichdiaBc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - EVhpEmb SC
        alg_params = {
            'CATEGORIES_FIELD_NAME': [parameters['AdID']],
            'INPUT': outputs['FieldCalculatorDevhpembSc']['OUTPUT'],
            'VALUES_FIELD_NAME': 'DEVhpEmb',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesEvhpembSc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Field calculator - Qdisp calc SC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'Qdisp',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': f'case\r\nwhen \"mon\" = 1 then MAX (0,(\"flo_out\"- MAX({parameters["QMC_jan"]},\"QPdG_gen\"))) \r\nwhen \"mon\" = 2 then MAX (0,(\"flo_out\"- MAX({parameters["QMC_feb"]},\"QPdG_feb\")))\r\nwhen \"mon\" = 3 then MAX (0,(\"flo_out\"- MAX({parameters["QMC_mar"]},\"QPdG_març\")))\r\nwhen \"mon\" = 4 then MAX (0,(\"flo_out\"- MAX({parameters["QMC_apr"]},\"QPdG_abr\"))) \r\nwhen \"mon\" = 5 then MAX (0,(\"flo_out\"- MAX({parameters["QMC_may"]},\"QPdG_maig\")))\r\nwhen \"mon\" = 6 then MAX (0,(\"flo_out\"- MAX({parameters["QMC_jun"]},\"QPdG_juny\")))\r\nwhen \"mon\" = 7 then MAX (0,(\"flo_out\"- MAX({parameters["QMC_jul"]},\"QPdG_jul\")))\r\nwhen \"mon\" = 8 then MAX (0,(\"flo_out\"- MAX({parameters["QMC_aug"]},\"QPdG_ago\")))\r\nwhen \"mon\" = 9 then MAX (0,(\"flo_out\"- MAX({parameters["QMC_sep"]},\"QPdG_set\")))\r\nwhen month(\"Date\") = 10 then MAX (0,(\"flo_out\"- MAX({parameters["QMC_oct"]},\"QPdG_oct\")))\r\nwhen \"mon\" = 11 then MAX (0,(\"flo_out\"- MAX({parameters["QMC_nov"]},\"QPdG_nov\")))\r\nelse MAX (0,(\"flo_out\"- MAX({parameters["QMC_dec"]},\"QPdG_des\")))\r\nend  \r\n',
            'INPUT': outputs['JoinAttributesByFieldValueCodiracaptToFlows']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorQdispCalcSc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Field calculator - QPTxSB BC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'QPTxSB',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': f"{parameters['grosshead']}*\"QPTurb\"",
            'INPUT': outputs['FieldCalculatorDailyIdByChCodichdiaBc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorQptxsbBc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Field calculator - QPTurb calc SC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'QPTurb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': f'min({parameters["Fmac"]}, \"Qdisp\")',
            'INPUT': outputs['FieldCalculatorQdispCalcSc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorQpturbCalcSc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Field calculator - DEVhpEmb BC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'DEVhpEmb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': f'case\r\nwhen \"flo_out\" >= {parameters["ftm"]} then ({parameters["G"]} * min(\"flo_out\",{parameters["Fmac"]})*({parameters["grosshead"]}*{parameters["HL"]})*{parameters["Rt"]}*{parameters["Rg"]}*{parameters["Rs"]}*24*{parameters["EP"]})\r\nelse 0\r\nend',
            'INPUT': outputs['JoinAttributesByFieldValueDembdflowbWithChembBc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDevhpembBc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - codiEntita at CodiCHdia level BC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'CodiCHdia',
            'FIELDS_TO_COPY': [parameters['HSID'],parameters['ftm']],
            'FIELD_2': 'CodiCHdia',
            'INPUT': outputs['StatisticsByCategoriesQpturbAtCodichdiaBc']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorDailyIdByChCodichdiaBc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueCodientitaAtCodichdiaLevelBc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Field calculator - QTurb BC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'QTurb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': f'case\r\nwhen \"sum\">={parameters["ftm"]} then \"sum\"\r\nelse 0\r\nend',
            'INPUT': outputs['JoinAttributesByFieldValueCodientitaAtCodichdiaLevelBc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorQturbBc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - EVhpEmb BC
        alg_params = {
            'CATEGORIES_FIELD_NAME': [parameters['AdID']],
            'INPUT': outputs['FieldCalculatorDevhpembBc']['OUTPUT'],
            'VALUES_FIELD_NAME': 'DEVhpEmb',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesEvhpembBc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - QPTxSB at CodiCHDia BC
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['CodiCHDia'],
            'INPUT': outputs['FieldCalculatorQptxsbBc']['OUTPUT'],
            'VALUES_FIELD_NAME': 'QPTxSB',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesQptxsbAtCodichdiaBc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Field calculator - Daily ID by CH (CodiCHDia) SC
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'CodiCHDia',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,
            'FORMULA': f'concat ({parameters["HSID"]},\'_\',\"day\", \"mon\")',
            'INPUT': outputs['FieldCalculatorQpturbCalcSc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDailyIdByChCodichdiaSc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Field calculator - QPTxSB SC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'QPTxSB',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': f'{parameters["grosshead"]}*\"QPTurb\"',
            'INPUT': outputs['FieldCalculatorDailyIdByChCodichdiaSc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorQptxsbSc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - QPTurb at CodiCHDia SC
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['CodiCHDia'],
            'INPUT': outputs['FieldCalculatorDailyIdByChCodichdiaSc']['OUTPUT'],
            'VALUES_FIELD_NAME': 'QPTurb',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesQpturbAtCodichdiaSc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(37)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - codiEntita at CodiCHdia level SC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'CodiCHdia',
            'FIELDS_TO_COPY': [parameters['HSID'],parameters['ftm']],
            'FIELD_2': 'CodiCHdia',
            'INPUT': outputs['StatisticsByCategoriesQpturbAtCodichdiaSc']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorDailyIdByChCodichdiaSc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueCodientitaAtCodichdiaLevelSc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(38)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - QPTurb to calc SaltBrut BC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'CodiCHDia',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': 'CodiCHDia',
            'INPUT': outputs['StatisticsByCategoriesQptxsbAtCodichdiaBc']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesQpturbAtCodichdiaBc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': 'QPT_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueQpturbToCalcSaltbrutBc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(39)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - QPTxSB at CodiCHDia SC
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['CodiCHDia'],
            'INPUT': outputs['FieldCalculatorQptxsbSc']['OUTPUT'],
            'VALUES_FIELD_NAME': 'QPTxSB',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesQptxsbAtCodichdiaSc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(40)
        if feedback.isCanceled():
            return {}

        # Field calculator - QTurb SC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'QTurb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': f'case\r\nwhen \"sum\">={parameters["ftm"]} then \"sum\"\r\nelse 0\r\nend',
            'INPUT': outputs['JoinAttributesByFieldValueCodientitaAtCodichdiaLevelSc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorQturbSc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(41)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - QPTurb to calc SaltBrut SC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'CodiCHDia',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': 'CodiCHDia',
            'INPUT': outputs['StatisticsByCategoriesQptxsbAtCodichdiaSc']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesQpturbAtCodichdiaSc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': 'QPT_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueQpturbToCalcSaltbrutSc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(42)
        if feedback.isCanceled():
            return {}

        # Field calculator - SaltBrut at CodiCHDia (SaltBrutCH) BC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'SaltBrutCH',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'case\r\nwhen (\"sum\"/\"QPT_sum\") is null then 0\r\nelse (\"sum\"/\"QPT_sum\")\r\nend\r\n',
            'INPUT': outputs['JoinAttributesByFieldValueQpturbToCalcSaltbrutBc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSaltbrutAtCodichdiaSaltbrutchBc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(43)
        if feedback.isCanceled():
            return {}

        # Field calculator - SaltBrut at CodiCHDia (SaltBrutCH) SC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'SaltBrutCH',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'case\r\nwhen (\"sum\"/\"QPT_sum\") is null then 0\r\nelse (\"sum\"/\"QPT_sum\")\r\nend\r\n',
            'INPUT': outputs['JoinAttributesByFieldValueQpturbToCalcSaltbrutSc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSaltbrutAtCodichdiaSaltbrutchSc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(44)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - SaltBrutCH and QTurb SC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'CodiCHDia',
            'FIELDS_TO_COPY': ['SaltBrutCH'],
            'FIELD_2': 'CodiCHDia',
            'INPUT': outputs['FieldCalculatorQturbSc']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorSaltbrutAtCodichdiaSaltbrutchSc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueSaltbrutchAndQturbSc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(45)
        if feedback.isCanceled():
            return {}

        # Field calculator - DEVhp SC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'DEVhp',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': f"{parameters['G']}*\"QTurb\"*(\"SaltBrutCH\"*{parameters['HL']})*{parameters['Rt']}*{parameters['Rg']}*{parameters['Rs']}*24*{parameters['EP']}\r\n",
            'INPUT': outputs['JoinAttributesByFieldValueSaltbrutchAndQturbSc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDevhpSc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(46)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - SaltBrutCH and QTurb BC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'CodiCHDia',
            'FIELDS_TO_COPY': ['SaltBrutCH'],
            'FIELD_2': 'CodiCHDia',
            'INPUT': outputs['FieldCalculatorQturbBc']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorSaltbrutAtCodichdiaSaltbrutchBc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueSaltbrutchAndQturbBc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(47)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - EVhp at CH level SC
        alg_params = {
            'CATEGORIES_FIELD_NAME': [parameters['HSID']],
            'INPUT': outputs['FieldCalculatorDevhpSc']['OUTPUT'],
            'VALUES_FIELD_NAME': 'DEVhp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesEvhpAtChLevelSc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(48)
        if feedback.isCanceled():
            return {}

        # Field calculator - DEVhp BC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'DEVhp',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': f"{parameters['G']}*\"QTurb\"*(\"SaltBrutCH\"*{parameters['HL']})*{parameters['Rt']}*{parameters['Rg']}*{parameters['Rs']}*24*{parameters['EP']}\r\n",
            'INPUT': outputs['JoinAttributesByFieldValueSaltbrutchAndQturbBc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDevhpBc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(49)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - EVhp at muni SC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': f'{parameters["HSID"]}',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': f'{parameters["HSID"]}',
            'INPUT': outputs['JoinAttributesByLocationCodimuniChSc']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesEvhpAtChLevelSc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': 'EVhp_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueEvhpAtMuniSc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(50)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - EVhp at CH level BC
        alg_params = {
            'CATEGORIES_FIELD_NAME': [parameters['HSID']],
            'INPUT': outputs['FieldCalculatorDevhpBc']['OUTPUT'],
            'VALUES_FIELD_NAME': 'DEVhp',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesEvhpAtChLevelBc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(51)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - EVhp at muni SC
        alg_params = {
            'CATEGORIES_FIELD_NAME': [parameters['AdID']],
            'INPUT': outputs['JoinAttributesByFieldValueEvhpAtMuniSc']['OUTPUT'],
            'VALUES_FIELD_NAME': 'EVhp_sum',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesEvhpAtMuniSc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(52)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - EVhp to muni SC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': f'{parameters["AdID"]}',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': f'{parameters["AdID"]}',
            'INPUT': parameters['MUNISlayer'],
            'INPUT_2': outputs['StatisticsByCategoriesEvhpAtMuniSc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': 'EVhp_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueEvhpToMuniSc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(53)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - EVhp at muni BC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': f'{parameters["HSID"]}',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': f'{parameters["HSID"]}',
            'INPUT': outputs['JoinAttributesByLocationCodimuniChBc']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesEvhpAtChLevelBc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': 'EVhp_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueEvhpAtMuniBc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(54)
        if feedback.isCanceled():
            return {}

        # Field calculator - EVhp at muni SC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'EVhp',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'case\r\nwhen \"EVhp_sum\" is null then 0\r\nelse \"EVhp_sum\"\r\nend',
            'INPUT': outputs['JoinAttributesByFieldValueEvhpToMuniSc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorEvhpAtMuniSc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(55)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - EVhp at muni BC
        alg_params = {
            'CATEGORIES_FIELD_NAME': [parameters['AdID']],
            'INPUT': outputs['JoinAttributesByFieldValueEvhpAtMuniBc']['OUTPUT'],
            'VALUES_FIELD_NAME': 'EVhp_sum',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesEvhpAtMuniBc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(56)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - EVhp with EVhpEmb SC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': f'{parameters["AdID"]}',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': f'{parameters["AdID"]}',
            'INPUT': outputs['FieldCalculatorEvhpAtMuniSc']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesEvhpembSc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': 'EVhpEmb_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueEvhpWithEvhpembSc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(57)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - EVhp to muni BC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': f'{parameters["AdID"]}',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': f'{parameters["AdID"]}',
            'INPUT': parameters['MUNISlayer'],
            'INPUT_2': outputs['StatisticsByCategoriesEvhpAtMuniBc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': 'EVhp_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueEvhpToMuniBc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(58)
        if feedback.isCanceled():
            return {}

        # Field calculator - EVhp at muni BC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'EVhp',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'case\r\nwhen \"EVhp_sum\" is null then 0\r\nelse \"EVhp_sum\"\r\nend',
            'INPUT': outputs['JoinAttributesByFieldValueEvhpToMuniBc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorEvhpAtMuniBc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(59)
        if feedback.isCanceled():
            return {}

        # Field calculator - EVhpEmb at muni SC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'EVhpEmb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'case\r\nwhen \"EVhpEmb_sum\" is null then 0\r\nelse \"EVhpEmb_sum\"\r\nend',
            'INPUT': outputs['JoinAttributesByFieldValueEvhpWithEvhpembSc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorEvhpembAtMuniSc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(60)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - EVhp with EVhpEmb BC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': f'{parameters["AdID"]}',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': f'{parameters["AdID"]}',
            'INPUT': outputs['FieldCalculatorEvhpAtMuniBc']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesEvhpembBc']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': 'EVhpEmb_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueEvhpWithEvhpembBc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(61)
        if feedback.isCanceled():
            return {}

        # Field calculator - EVhpEmb at muni BC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'EVhpEmb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'case\r\nwhen \"EVhpEmb_sum\" is null then 0\r\nelse \"EVhpEmb_sum\"\r\nend',
            'INPUT': outputs['JoinAttributesByFieldValueEvhpWithEvhpembBc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorEvhpembAtMuniBc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(62)
        if feedback.isCanceled():
            return {}

        # Field calculator - VEPHidro_CB
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'EVHP_CB',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '\"EVhp\" + \"EVhpEmb\"',
            'INPUT': outputs['FieldCalculatorEvhpembAtMuniBc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVephidro_cb'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)


        feedback.setCurrentStep(63)
        if feedback.isCanceled():
            return {}

        # Field calculator - VEPHidro_CS
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'EVHP_SC',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '\"EVhp\" + \"EVhpEmb\"',
            'INPUT': outputs['FieldCalculatorEvhpembAtMuniSc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVephidro_cs'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(64)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - EVhpS and EVhpB
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': f'{parameters["AdID"]}',
            'FIELDS_TO_COPY': ['EVHP_SC'],
            'FIELD_2': f'{parameters["AdID"]}',
            'INPUT': outputs['FieldCalculatorVephidro_cb']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorVephidro_cs']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueEvhpsAndEvhpb'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(65)
        if feedback.isCanceled():
            return {}

        # Field calculator - VEPHidro
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'EVHP',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'EVHP_SC - EVHP_CB',
            'INPUT': outputs['JoinAttributesByFieldValueEvhpsAndEvhpb']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVephidro'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(66)
        if feedback.isCanceled():
            return {}

        # Drop field(s) - VEPHidro
        alg_params = {
            'COLUMN': [f'{parameters["HSID"]}','EVhp_sum','EVhp','EVhpEmb_sum','EVhpEmb',''],
            'INPUT': outputs['FieldCalculatorVephidro']['OUTPUT'],
            'OUTPUT': parameters['Vephidro']
        }
        outputs['DropFieldsVephidro'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Vephidro'] = outputs['DropFieldsVephidro']['OUTPUT']

        if 'TEMPORARY_OUTPUT' in parameters['Vephidro'].sink.asExpression():
            context.layerToLoadOnCompletionDetails(results['Vephidro']).name = "EVHP"

        return results

    def name(self):
        return 'Producció hidroelèctrica (VEPHidro)'

    def displayName(self):
        return 'Producció hidroelèctrica (VEPHidro)'

    def group(self):
        return 'Aprovisionament'

    def groupId(self):
        return 'Aprovisionament'

    def createInstance(self):
        return ProducciHidroelctricaVephidro()
