# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 15:26:27 2015

@author: eburton

Modified 6/6/18 - 8/10/18

by: Cory Kennedy
"""

import os
import gdal
import numpy as np
import region_utils
import sys
# NOTE point the path below at your gdal installation (gdal_merge.py)
sys.path.append('/Users/ckennedy/miniconda2/envs/tensorflow/bin/')
import gdal_merge

# XXX temporary
# TODO: add get_path function to allow different 1m data tiles to be retrieved
#path_1m_data = '/mnt/e/DEM_Database/NED_1m/x47y440/USGS_NED_one_meter_x47y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015.img'
path_1m_data = '/Volumes/Fleet Storage/DEM_Database/NED_1m/x47y440/USGS_NED_one_meter_x47y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015.img'
#path_1m_data = '/mnt/e/DEM_Database/NED_1m/x48y440/USGS_NED_one_meter_x48y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015.img'
#path_1m_meta = '/mnt/e/DEM_Database/NED_1m/x47y440/USGS_NED_one_meter_x47y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015_meta.xml'
path_1m_meta = '/Volumes/Fleet Storage/DEM_Database/NED_1m/x47y440/USGS_NED_one_meter_x47y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015_meta.xml'
#path_1m_meta = '/mnt/e/DEM_Database/NED_1m/x48y440/USGS_NED_one_meter_x48y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015_meta.xml'
#path_10m_data = '/mnt/e/DEM_Database/NED_13/grid/n40w106/grdn40w106_13/w001001.adf'
path_10m_data = '/Volumes/Fleet Storage/DEM_Database/NED_13/grid/n40w106/grdn40w106_13/w001001.adf'

raster_data_loc = '../data/raster_data/'

# TODO: add kwarg for getting 1m data path
def get_raster_path(grid_ref):
    sub_path = 'grd' + grid_ref + '_13'
    #raster_path = '/mnt/e/DEM_Database/NED_13/grid/' + grid_ref + '/' + sub_path + '/w001001.adf'
    raster_path = '/Volumes/Fleet Storage/DEM_Database/NED_13/grid/' + grid_ref + '/' + sub_path + '/w001001.adf'
    return raster_path


def get_grid_refs(lats, lons):  # lats and lons are lists
    grid_refs = []

    for index in range(len(lons)):
        if lats[index] > 0.0 and lons[index] < 0.0: # if lat is N and lon is W, isolate degree value and add 1
            latVal = str(int(abs(lats[index])//1 + 1))
            lonVal = str(int(abs(lons[index])//1 + 1))

            if len(lonVal) < 3:
                lonVal = '0' + lonVal # if degree val only has 2 digits, prepend 0 to front
            grid_refs.append('n' + latVal + 'w' + lonVal) # prepend directions and stitch together

        else:
            grid_refs.append('0')

    return list(set(grid_refs))


def get_elev_data(grid_ref, lats, lons): # grid_ref is a single string, from build_grid_refs(arg, arg)
    elevation = []
    print('Retreiving Path to Raster Data...')
    raster_path = get_raster_path(grid_ref)

    if not os.path.exists(raster_path): # checks if data exists
        elevation = [np.nan]*len(lons) # populates whole elev list with nan
        raise Exception('Incorrect FilePath to Raster Database, or data does not exist.')

    else: # path is correct
        xOrigin, yOrigin, pixelWidth, pixelHeight, bands, rows, cols, data = get_raster_data(raster_path)
        xOffset = [int((v - xOrigin) / pixelWidth) if v < 0.0 else 'nan' for v in np.float64(lons)]
        yOffset = [int((v - yOrigin) / pixelHeight) if v > 0.0 else 'nan' for v in np.float64(lats)]

        for val in range(len(lons)):
            if xOffset[val] == 'nan':
                print('passed')
                elevation.append(np.nan)

            else:
                for j in range(bands):
                    band = data.GetRasterBand(j+1) # 1-based index
                    raster_data = band.ReadAsArray(xOffset[val], yOffset[val], 1, 1)

                    if raster_data != None:
                        elev = float(raster_data[0,0]) * 3.28084
                        elevation.append(elev)

                    else:
                        print('passed')
                        elevation.append(np.nan)

        del data
    print('Returning Elevation Value(s)')
    return elevation


# TODO: add ability to pull different tiles based on coordinate argument
# TODO: get file path by calling get_path function instead of as an arg
# converst USGS 1m raster data from tiled coord system to pandas dataframe in lat/lon coord systm
def get_1m_data(path_1m_data):
    # get metadata and data from osgeo.gdal.open(IMGfile); NOTE boundary metadata isn't lat/lon
    xOrigin, yOrigin, pixelWidth, pixelHeight, bands, rows, cols, data = get_raster_data(path_1m_data)

    # convert origin coordinate and pixel size to lat/lon using xml metadata file
    N, S, E, W = region_utils.get_bounds_from_meta(path_1m_meta)
    xOrigin, yOrigin = W, N
    pixelHeight = abs(N - S) / float(rows) * -1
    pixelWidth = abs(E - W) / float(cols) # pixel width in lat/lon
    raster_data_1m = [xOrigin, yOrigin, pixelWidth, pixelHeight, bands, rows, cols, data]
    return raster_data_1m


def get_raster_data(raster_path):
    data = gdal.Open(raster_path)

    if data != None:
        print('Geotransforming Elevation Data...')
        # get geotransform data from osgeo.gdal.Dataset.GetGeoTransform()
        geotransform = data.GetGeoTransform()
        xOrigin = geotransform[0]
        yOrigin = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]
        print('Unpacking Grid...')
        cols = data.RasterXSize # number of pixel columns in raster tile
        rows = data.RasterYSize # number of pixel rows in raster tile
        bands = data.RasterCount # number of raster bands (~layers)

    else:
        print('Grid Does not Exist')
        xOrigin = None
        yOrigin = None
        pixelWidth = None
        pixelHeight = None
        bands = None
        rows = None
        cols = None

    return xOrigin, yOrigin, pixelWidth, pixelHeight, bands, rows, cols, data


def return_elevation_profiles(lats, lons):
    if type(lons) == list:
        lons = np.array(lons)
        lats = np.array(lats)
    elevation_full  =[]
    ts_full = []
    grid_refs = build_grid_refs(lats, lons)
    grid_refs = np.array(grid_refs)
    uni_grid_refs = list(set(grid_refs))
    row_col = np.arange(0,len(lons))

    for gr in uni_grid_refs:
        ts = list(row_col[(grid_refs == gr)])
        elevation = get_elev_data(gr, lats[(grid_refs == gr)], lons[(grid_refs == gr)])
        elevation_full += list(elevation)
        ts_full += list(ts)

    ts_full, elevation_full = [list(x) for x in zip(*sorted(zip(ts_full, elevation_full), key=lambda pair: pair[0]))]
    elevation_full = np.array(elevation_full)
    return elevation_full

def merge_rasters(grid_refs, raster_paths):
    print('Finding multiple raster files...')
    # Get file name for storage of raster files
    txt_filename = name_raster_file(grid_refs, filetype='txt')
    # Store the location of all the raster files to be merged
    rasterfiles_to_txt(grid_refs, raster_paths, raster_data_loc + txt_filename)
    # Get file name for the merged raster file
    merged_filename = name_raster_file(grid_refs, filetype='adf')
    # Merge the raster files; gdal_merge parses args starting at 1
    print('Merging multiple raster files...')
    gdal_merge.main(['', '-o', raster_data_loc + merged_filename, '-v', '--optfile',
                    raster_data_loc + txt_filename ])

def rasterfiles_to_txt(grid_refs, raster_paths, filename):
    f = open(filename, 'w')

    # Writes "path/to/raster/filename" (return) to a txt file
    to_file = '' # intitialize empty string before appending
    for path in raster_paths:
        to_file += ('\"' + path + '\"' + '\n')

    f.write(to_file)
    f.close()

def name_raster_file(grid_refs, filetype='txt', **kwarg):
    file_str = '' # intitialize empty string before appending
    for string in grid_refs:
        file_str += string
    file_str += '.' + filetype
    return file_str


# LONG TERM STORAGE

    # raster_path = 'E:\\DEM_Database\\NED_13\\grid\\' + grid_ref + '\\' + sub_path + '\\w001001.adf'
    # sub_path = 'grd' + grid_ref + '_13'
    # raster_path = '/mnt/e/DEM_Database/NED_13/grid/' + grid_ref + '/' + sub_path + '/w001001.adf'

    # os.environ['PATH'] = "c:\\Program Files\\GDAL" + ';' + os.environ['PATH']
    # os.environ['GDAL_DRIVER_PATH'] = "c:\\Program Files\GDAL\gdal\\plugins-optional"
    # os.environ['GDAL_DATA'] = "c:\\Program Files\\GDAL\\gdal-data"
