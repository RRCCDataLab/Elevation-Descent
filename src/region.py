#
# MODULE FOR BUILDING REGION OBJECTS TO BE INHERITED BY SUBREGION OBJECTS AND EVENTUALL
# MODEL OBJECTS FOR THE PURPOSE OF STUDYING TERRAIN SURFACE INTERPOLATION TECHNIQUES
#
# Author: Cory Kennedy
#
# Date: 6/12/2018

import numpy as np
import pandas as pd
import raster_utils
import region_utils

# XXX temporary:
#path_to_1m_data = '/mnt/e/DEM_Database/NED_1m/x47y440/USGS_NED_one_meter_x47y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015.img'
path_to_1m_data = '/Volumes/Fleet Storage/DEM_Database/NED_1m/x47y440/USGS_NED_one_meter_x47y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015.img'

#path_to_1m_data = '/mnt/e/DEM_Database/NED_1m/x48y440/USGS_NED_one_meter_x48y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015.img'

class Region(object):

    def __init__(self, lat, lon, data='10m', **kwargs):
        if data == '1m':
            # TODO: add ability to pass lat lon to get_1m_data to select various tiles
            print('retrieving raster data...')
            self.raster_data = raster_utils.get_1m_data(path_to_1m_data)

        elif data == '10m':
            print('building grid reference string...')
            self.grid_refs = raster_utils.build_grid_refs([lat], [lon])
            print('generating file path to raster data...')
            self.raster_path = raster_utils.get_raster_path(self.grid_refs[0])
            print('retrieving raster data...')
            self.raster_data = raster_utils.get_raster_data(self.raster_path)
            
        else:
            raise Exception('invalid data source selection')

        print('defining raster data parameters...')
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
        self.start_lon = self.W_bound + x_offset # center of first col of pixels
        self.end_lat = self.start_lat + (self.pixel_height * (self.num_rows - 1)) # center of last row
        self.end_lon = self.start_lon + (self.pixel_width * (self.num_cols - 1)) # center of last col
        self.band = self.raster_data[4]
        print('generating lat/lon domain arrays...')
        self.lat_array = np.linspace(self.start_lat, self.end_lat, num=self.num_rows, endpoint=True)
        self.lon_array = np.linspace(self.start_lon, self.end_lon, num=self.num_cols, endpoint=True)
        print('storing raster data...')
        self.elev_data = self.raster_data[7]
        print('generating elevation DataFrame...')
        data = self.elev_data.ReadAsArray()
        self.elev = pd.DataFrame(data=data, index=self.lat_array, columns=self.lon_array)
        self.elev = self.elev * 3.280839895 # converts DF from meters to feet

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
        elev = self.Elev.iloc[lat_index, lon_index]
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

