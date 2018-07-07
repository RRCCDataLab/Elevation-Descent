from rasterDB import get_raster_data
import region
import region_utils
import numpy as np

# Lookout Mt area vertices
# n40w106 from 10m USGS dataset
# x47y440 from 1m USGS dataset
NW_pnt_lookout = (39.746620, -105.241833)
SE_pnt_lookout = (39.744586, -105.237280)

# Mt Evans area vertices
# n40w106 from 1m USGS dataset
NW_pnt_evans = (39.602595, -105.693718)
SE_pnt_evans = (39.558016, -105.610281)

# TODO: add get_path function to allow different 1m data tiles to be retrieved
#path_1m_data = '/mnt/e/DEM_Database/NED_1m/x47y440/USGS_NED_one_meter_x47y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015.img'
path_1m_data = '/Volumes/Fleet Storage/DEM_Database/NED_1m/x47y440/USGS_NED_one_meter_x47y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015.img'
#path_1m_data = '/mnt/e/DEM_Database/NED_1m/x48y440/USGS_NED_one_meter_x48y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015.img'
path_1m_meta = '/Volumes/Fleet Storage/DEM_Database/NED_1m/x47y440/USGS_NED_one_meter_x47y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015_meta.xml'    
#path_1m_meta = '/mnt/e/DEM_Database/NED_1m/x47y440/USGS_NED_one_meter_x47y440_CO_SoPlatteRiver_Lot5_2013_IMG_2015_meta.xml'    
path_10m_data = '/Volumes/Fleet Storage/DEM_Database/NED_13/grid/n40w106/grdn40w106_13/w001001.adf'
#path_10m_data = '/mnt/e/DEM_Database/NED_13/grid/n40w106/grdn40w106_13/w001001.adf'
data_store_path = '/Users/ckennedy/projects/RoadGrade_Cory/data/'
#data_store_path = '/home/ckennedy/repos/RoadGrade_Cory/data/'


''' 1m dataset '''
# get elevation dataframe
lookoutMt_tile_1m = region.Region(NW_pnt_lookout[0], NW_pnt_lookout[1], data='1m')
print(lookoutMt_tile_1m.Elev)

# slice area of interest
theM_1m_df = lookoutMt_tile_1m.slice_subregion(NW_pnt_lookout, SE_pnt_lookout)
print(theM_1m_df)

# save df to a csv file
theM_1m_df.to_csv(data_store_path + 'theM_1m.csv')

# convert Dataframe to 2d numpy array
theM_1m_2d = theM_1m_df.values

# flatten array
theM_1m_1d = theM_1m_2d.flatten()

# create n x 3 numpy array (lat, lon, elev)
lats_arr = np.array(theM_1m_df.index.values)
lons_arr = np.array(theM_1m_df.columns.values)
row_num = theM_1m_df.shape[0]
col_num = theM_1m_df.shape[1]
element_num = theM_1m_1d.shape[0]
training_array = np.empty((element_num, 3)) # create training array (n,3)

# populate training_array
element = 0
for lat in lats_arr:
    for lon in lons_arr:
        elev = theM_1m_1d[element]
        training_array[element][:] = lat, lon, elev
        element += 1

print(training_array)        

# save array as .npy file
np.save(data_store_path + 'theM_1m.npy', training_array)



''' 10m dataset '''
# get elevation dataframe
lookoutMt_tile_10m = region.Region(NW_pnt_lookout[0], NW_pnt_lookout[1], data='10m')
print(lookoutMt_tile_10m.Elev)

# slice area of interest
theM_10m_df = lookoutMt_tile_10m.slice_subregion(NW_pnt_lookout, SE_pnt_lookout)
print(theM_10m_df)

# save df to a csv file
theM_10m_df.to_csv(data_store_path + 'theM_10m.csv')

# convert Dataframe to 2d numpy array
theM_10m_2d = theM_10m_df.values

# flatten array
theM_10m_1d = theM_10m_2d.flatten()

# create n x 3 numpy array (lat, lon, elev)
lats_arr = np.array(theM_10m_df.index.values)
lons_arr = np.array(theM_10m_df.columns.values)
row_num = theM_10m_df.shape[0]
col_num = theM_10m_df.shape[1]
element_num = theM_10m_1d.shape[0]
training_array = np.empty((element_num, 3)) # create training array (n,3)

# populate training_array
element = 0
for lat in lats_arr:
    for lon in lons_arr:
        elev = theM_10m_1d[element]
        training_array[element][:] = lat, lon, elev
        element += 1

print(training_array)        

# save array as .npy file
np.save(data_store_path + 'theM_10m.npy', training_array)

