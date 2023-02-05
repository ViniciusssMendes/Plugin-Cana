# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FalhaDePlantio
                                 A QGIS plugin
 Pluing utilizado para mapeamento de falha de plantio na cultura de cana de açúcar
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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Thiago Silva'
__date__ = '2022-09-25'
__copyright__ = '(C) 2022 by Thiago Silva'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FalhaDePlantio class from file FalhaDePlantio.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Falhadeplantio import FalhaDePlantioPlugin
    return FalhaDePlantioPlugin()
    
    
    from .Falhadeplantio import MapeamentoDePlantasInvasorasFolhaLargaMediaPlugin
    return MapeamentoDePlantasInvasorasFolhaLargaMediaPlugin()
