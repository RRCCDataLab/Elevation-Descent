#
# MODULE FOR BUILDING REGION OBJECTS TO BE INHERITED BY SUBREGION OBJECTS AND EVENTUALL
# MODEL OBJECTS FOR THE PURPOSE OF STUDYING TERRAIN SURFACE INTERPOLATION TECHNIQUES
#
# Author: Cory Kennedy
#
# Date: 6/12/2018

import numpy as np
import pandas as pd
from os import path
import raster_utils
import region_utils
#import config

pathx47y440 = path.join('x47y440', 'USGS_NED_one_meter_x47y440_CO_SoPlatteRiver_lot5_2013_IMG_2015.img')
#path_to_1m_data = path.join(config.CFDS_CONFIG['path_1m_data'], pathx47y440)

path_to_raster_data = path.join('..', 'data', 'raster_data')

class Region(object):

    def __init__(self, lats, lons, data='10m', **kwargs):
        if data == '1m':
            # TODO: add ability to pass lat lon to get_1m_data to select various tiles
            print('Retrieving raster data...')
            self.raster_data = raster_utils.get_1m_data(path_to_1m_data)

        elif data == '10m':

            # if lats (and lons) is a list
            # indicates child object is a Trace object
            if (isinstance(lats, list) and len(lats) > 1):
                print('Building grid reference string(s)...')
                self.grid_refs = raster_utils.get_grid_refs(lats, lons)

                print('Generating file path(s) to raster data...')
                self.raster_paths = []
                for grid_ref in self.grid_refs:
                    raster_path = raster_utils.get_raster_path(grid_ref)
                    self.raster_paths += [raster_path]

            # if lats (and lons) is a single element
            # indicates child object is a SubRegion object
            else:
                lat = lats
                lon = lons
                print('building grid reference string...')
                self.grid_refs = raster_utils.get_grid_refs([lat], [lon])
                print('generating file path to raster data...')
                self.raster_path = raster_utils.get_raster_path(self.grid_refs[0])
                print('retrieving raster data...')
                self.raster_data = raster_utils.get_raster_data(self.raster_path)


            print('Retrieving raster data...')
            # Merge tiles if there are multiple
            if (len(self.grid_refs) > 1) :
                # Get file name of merged raster to be created
                name_raster = raster_utils.name_raster_file
                merged_filename = name_raster(self.grid_refs, filetype='adf')
                # Create the merge raster
                raster_utils.merge_rasters(self.grid_refs, self.raster_paths)
                merged_raster_path = path.join(path_to_raster_data, merged_filename)
                # Store data from the merged raster
                self.raster_data = raster_utils.get_raster_data(merged_raster_path)

            else:
                single_raster_path = self.raster_path[0]
                self.raster_data = raster_utils.get_raster_data(single_raster_path)

        else:
            raise Exception('invalid data source selection')

        print('Defining raster data parameters...')
        self.pixel_width = self.raster_data[2]
        self.pixel_height = self.raster_data[3]
        self.num_rows = self.raster_data[5]
        self.num_cols = self.raster_data[6]
        self.N_bound = self.raster_data[1]
        self.S_bound = self.N_bound + self.pixel_height * self.num_rows
        self.W_bound = self.raster_data[0]
        self.E_bound = self.W_bound + self.pixel_width * self.num_cols
        x_offset = self.pixel_width / 2.0 # match column vals with horizontal center of pixel
        y_offset = self.pixel_height / 2.0 # match index vals with vertical center of pixel
        self.start_lat = self.N_bound + y_offset # center of first row of pixels
        self.start_lon = self.W_bound + x_offset # center of first col of pixel
        # center of last rows
        self.end_lat = self.start_lat + (self.pixel_height * (self.num_rows - 1))
        # center of last col
        self.end_lon = self.start_lon + (self.pixel_width * (self.num_cols - 1))
        self.band = self.raster_data[4]
        print('Generating lat/lon domain arrays...')
        self.lat_array = np.linspace(self.start_lat, self.end_lat, num=self.num_rows, endpoint=True)
        self.lon_array = np.linspace(self.start_lon, self.end_lon, num=self.num_cols, endpoint=True)
        print('Storing raster data...')
        self.elev_data = self.raster_data[7]
        print('Generating elevation DataFrame...')
        data = self.elev_data.ReadAsArray()
        # Resulting DataFrame in meters
        self.elev = pd.DataFrame(data=data, index=self.lat_array, columns=self.lon_array)

    def lat_index(self, lat):
        nearest_lat_index = region_utils.find_nearest(self.lat_array, lat)
        # if that element is the first element
        if nearest_lat_index == 0:
            below_index = nearest_lat_index # below index is 0
            above_index = below_index + 1 # above index is 1
        # or else, if that element is the last element
        elif self.lat_array[nearest_lat_index] == self.lat_array[-1]:
            below_index = nearest_lat_index - 1 # below index is 2nd-to-last element
            above_index = nearest_lat_index # above index is last element
        # otherwise
        else:
            # if element at nearest index is less than element of interest
            if self.lat_array[nearest_lat_index] < lat:
                below_index = nearest_lat_index # below index is the nearest element
                above_index = below_index + 1 # above index is the next element
            # otherwise
            else:
                above_index = nearest_lat_index # above index is the nearest element
                below_index = above_index - 1 # below index is the previous element
        return below_index, above_index

    def lon_index(self, lon):
        nearest_lon_index = region_utils.find_nearest(self.lon_array, lon)
        # if that element is the first element
        if nearest_lon_index == 0:
            below_index = nearest_lon_index # below index is 0
            above_index = below_index + 1 # above index is 1
        # or else, if that element is the last element
        elif self.lon_array[nearest_lon_index] == self.lon_array[-1]:
            below_index = nearest_lon_index - 1 # below index is 2nd-to-last element
            above_index = nearest_lon_index # above index is last element
        # otherwise
        else:
            # if element at nearest index is less than element of interest
            if self.lon_array[nearest_lon_index] < lon:
                below_index = nearest_lon_index # below index is the nearest element
                above_index = below_index + 1 # above index is the next element
            # otherwise
            else:
                above_index = nearest_lon_index
                below_index = above_index - 1
        return below_index, above_index

    def get_indices(self, lat, lon):
        S, N = self.lat_index(lat)
        W, E = self.lon_index(lon)
        return N, S, E, W

    def return_point_data(self, lat_index, lon_index):
        lon = float(self.elev.iloc[:, lon_index].name)
        lat = float(self.elev.iloc[lat_index].name)
        elev = self.elev.iloc[lat_index, lon_index]
        return (lon, lat, elev)

    def get_points(self, lat, lon):
        N_index, S_index, E_index, W_index = self.get_indices(lat, lon)
        NW_pnt = self.return_point_data(N_index, W_index)
        SW_pnt = self.return_point_data(S_index, W_index)
        NE_pnt = self.return_point_data(N_index, E_index)
        SE_pnt = self.return_point_data(S_index, E_index)
        return [SW_pnt, NW_pnt, SE_pnt, NE_pnt]

    def slice_subregion(self, NW_coord, SE_coord):
        N_index, _, _, W_index = self.get_indices(NW_coord[0], NW_coord[1])
        _, S_index, E_index, _ = self.get_indices(SE_coord[0], SE_coord[1])
        df = self.elev.iloc[ (N_index+1):S_index, (W_index+1):E_index ]
        return df

