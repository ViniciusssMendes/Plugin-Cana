# -*- coding: utf-8 -*-

"""
/***************************************************************************
 FalhaDePlantio
                                 A QGIS plugin
 Pluing utilizado para mapeamento de falha de plantio na cultura de cana-de-açúcar
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-09-25
        copyright            : (C) 2022 by Thiago Silva
        email                : email
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Thiago Silva'
__date__ = '2022-09-25'
__copyright__ = '(C) 2022 by Thiago Silva'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication



class FalhaDePlantioAlgorithm(QgsProcessingAlgorithm):  




    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('gligreenleafindex', 'Raster', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('linhaplantio', 'Linha de plantio', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('quadra', 'Contorno', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('FalhaDePlantio', 'Falha de plantio', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
    
    
    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(13, model_feedback)
        results = {}
        outputs = {}

        parameters['FalhaDePlantio'].destinationName = 'Falha de plantio'

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 1,
            'END_CAP_STYLE': 0,  # Arredondado
            'INPUT': parameters['quadra'],
            'JOIN_STYLE': 0,  # Arredondado
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Recortar o vetor pela camada de máscara
        alg_params = {
            'INPUT': parameters['linhaplantio'],
            'MASK': outputs['Buffer']['OUTPUT'],
            'OPTIONS': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RecortarOVetorPelaCamadaDeMscara'] = processing.run('gdal:clipvectorbypolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Recortar raster RBG
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,  # Use Camada de entrada Tipo Dado
            'EXTRA': '',
            'INPUT': parameters['gligreenleafindex'],
            'KEEP_RESOLUTION': False,
            'MASK': outputs['Buffer']['OUTPUT'],
            'MULTITHREADING': False,
            'NODATA': -1,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': 'ProjectCrs',
            'TARGET_CRS': None,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RecortarRasterRbg'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Aritmética de bandas
        # Calculo de indeci
        alg_params = {
            'ALPHA': True,
            'FORMULA': '(2*b2 - b1 - b3)/(2*b2 + b1 + b3)',
            'INPUT': outputs['RecortarRasterRbg']['OUTPUT'],
            'OPEN': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AritmticaDeBandas'] = processing.run('lftools:bandarithmetic', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Calculadora raster
        # Calculo de pix max e pix min
        alg_params = {
            'BAND_A': 1,
            'BAND_B': None,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTRA': '',
            'FORMULA': '(A <= 0) *0 +  (A > 0) * 1',
            'INPUT_A': outputs['AritmticaDeBandas']['OUTPUT'],
            'INPUT_B': None,
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': -1,
            'OPTIONS': '',
            'RTYPE': 5,  # Float32
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculadoraRaster'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # r.to.vect
        alg_params = {
            '-b': False,
            '-s': False,
            '-t': False,
            '-v': False,
            '-z': False,
            'GRASS_OUTPUT_TYPE_PARAMETER': 0,  # auto
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'GRASS_VECTOR_DSCO': '',
            'GRASS_VECTOR_EXPORT_NOCAT': False,
            'GRASS_VECTOR_LCO': '',
            'column': 'DN',
            'input': outputs['CalculadoraRaster']['OUTPUT'],
            'type': 2,  # area
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Rtovect'] = processing.run('grass7:r.to.vect', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Extrair por atributo
        alg_params = {
            'FIELD': 'DN',
            'INPUT': outputs['Rtovect']['output'],
            'OPERATOR': 0,  # =
            'VALUE': '0',
            'FAIL_OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairPorAtributo'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Excluir buracos
        alg_params = {
            'INPUT': outputs['ExtrairPorAtributo']['OUTPUT'],
            'MIN_AREA': 0.05,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExcluirBuracos'] = processing.run('native:deleteholes', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Suavização
        alg_params = {
            'INPUT': outputs['ExtrairPorAtributo']['FAIL_OUTPUT'],
            'ITERATIONS': 1,
            'MAX_ANGLE': 180,
            'OFFSET': 0.25,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Suavizao'] = processing.run('native:smoothgeometry', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Simplificar
        alg_params = {
            'INPUT': outputs['ExtrairPorAtributo']['FAIL_OUTPUT'],
            'METHOD': 0,  # Distância (Douglas-Peucker)
            'TOLERANCE': 0.05,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Simplificar'] = processing.run('native:simplifygeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Diferença
        alg_params = {
            'INPUT': outputs['RecortarOVetorPelaCamadaDeMscara']['OUTPUT'],
            'OVERLAY': outputs['Simplificar']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Diferena'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Multipartes para partes simples
        alg_params = {
            'INPUT': outputs['Diferena']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartesParaPartesSimples'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Calc_Linha_falha
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Comprimento',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': ' $length ',
            'INPUT': outputs['MultipartesParaPartesSimples']['OUTPUT'],
            'OUTPUT': parameters['FalhaDePlantio']
        }
        outputs['Calc_linha_falha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['FalhaDePlantio'] = outputs['Calc_linha_falha']['OUTPUT']
        return results

    def name(self):
        return 'Falha de plantio'

    def displayName(self):
        return 'Falha de plantio'

    def group(self):
        return 'Análise'

    def groupId(self):
        return 'Análise'

    def icon (self):
        return QIcon(r'''C:\Users\Usuario-ASUS\Desktop\Automaçao\UBV\MODELOS\Script\Logo\martinho.png''')
        

    def createInstance(self):
        return FalhaDePlantioAlgorithm()



class MapeamentoDePlantasInvasorasFolhaLargaMedia(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('contorno', 'Contorno', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('gligreenleafindex', 'Raster', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Daninhas', 'Daninhas', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(11, model_feedback)
        results = {}
        outputs = {}
        
        parameters['Daninhas'].destinationName = 'Daninhas'
        # Recortar raster pela camada de máscara
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,  # Use Camada de entrada Tipo Dado
            'EXTRA': '',
            'INPUT': parameters['gligreenleafindex'],
            'KEEP_RESOLUTION': False,
            'MASK': parameters['contorno'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RecortarRasterPelaCamadaDeMscara'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Aritmética de bandas
        alg_params = {
            'ALPHA': True,
            'FORMULA': '(2*b2 - b1 - b3)/(2*b2 + b1 + b3)',
            'INPUT': outputs['RecortarRasterPelaCamadaDeMscara']['OUTPUT'],
            'OPEN': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AritmticaDeBandas'] = processing.run('lftools:bandarithmetic', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Calculadora raster
        alg_params = {
            'BAND_A': 1,
            'BAND_B': None,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTRA': '',
            'FORMULA': '(A <=0.15) *0 + (A >0.15) * 1',
            'INPUT_A': outputs['AritmticaDeBandas']['OUTPUT'],
            'INPUT_B': None,
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': -1,
            'OPTIONS': '',
            'RTYPE': 5,  # Float32
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculadoraRaster'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Raster para vetor (poligonizar)
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': outputs['CalculadoraRaster']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RasterParaVetorPoligonizar'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Multipartes para partes simples
        alg_params = {
            'INPUT': outputs['RasterParaVetorPoligonizar']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartesParaPartesSimples'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Corrigir geometrias
        alg_params = {
            'INPUT': outputs['MultipartesParaPartesSimples']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CorrigirGeometrias'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Extrair por atributo
        alg_params = {
            'FIELD': 'DN',
            'INPUT': outputs['CorrigirGeometrias']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': '1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairPorAtributo'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Excluir buracos
        alg_params = {
            'INPUT': outputs['ExtrairPorAtributo']['OUTPUT'],
            'MIN_AREA': 150,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExcluirBuracos'] = processing.run('native:deleteholes', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Calculadora de campo
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Area_m²',
            'FIELD_PRECISION': 25,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': ' $area ',
            'INPUT': outputs['ExcluirBuracos']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculadoraDeCampo'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Extrair final
        alg_params = {
            'FIELD': 'Area_m²',
            'INPUT': outputs['CalculadoraDeCampo']['OUTPUT'],
            'OPERATOR': 3,  # ≥
            'VALUE': '1.5',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairFinal'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': 4.3,
            'END_CAP_STYLE': 2,  # Quadrado
            'INPUT': outputs['ExtrairFinal']['OUTPUT'],
            'JOIN_STYLE': 1,  # Pontiagudo
            'MITER_LIMIT': 2,
            'SEGMENTS': 1,
            'OUTPUT': parameters['Daninhas']
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Daninhas'] = outputs['Buffer']['OUTPUT']
        return results

    def name(self):
        return 'Sniper Daninhas'

    def displayName(self):
        return 'Sniper Daninhas'

    def group(self):
        return 'Análise'

    def groupId(self):
        return 'Análise'
    
    def icon (self):
        return QIcon(r'''C:\Users\Usuario-ASUS\Desktop\Automaçao\UBV\MODELOS\Script\Logo\martinho.png''')

    def createInstance(self):
        return MapeamentoDePlantasInvasorasFolhaLargaMedia()
