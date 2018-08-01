#
# CONFIG FILE FOR TSDC SERVER
#
# Modify and store your own, untracked version to use locally
#
# 08/01/2018

from os import path

path_to_DEMs = path.join('Z:', 'DEM_Database')

TSDC_CONFIG = {
}

CFDS_CONFIG = {
        'path_10m_data': path.join(path_to_DEMs, 'NED_13', 'grid'),
        'path_1m_data': path.join(path_to_DEMs, 'NED_1m'),
        'path_1m_meta': path.join(path_to_DEMs, 'NED_1m'),
}

GDAL_CONFIG = {
        'path_to_gdal_merge': path.join('C:', 'Program Files (x86)', 'GDAL')
}
