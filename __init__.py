# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ServeisEcosistemics
                                 A QGIS plugin
 Genera uns seguit de capes per a la visualització dels beneficis dels servesi ecosistemics.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-01-25
        copyright            : (C) 2022 by ICRA
        email                : ariu@icra.cat
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

__author__ = 'ICRA'
__date__ = '2022-01-01'
__copyright__ = '(C) 2022 by ICRA'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ServeisEcosistemics class from file ServeisEcosistemics.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .serveis_eco import ServeisEcosistemicsPlugin
    return ServeisEcosistemicsPlugin(iface)
