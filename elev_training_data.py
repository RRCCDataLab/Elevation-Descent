import numpy as np
import earthly

def get_data_USGSAPI():
    # create earthly region object, define vertices
    region = earthly.Region('area_training_data')
    # add the coordinate layer with a step size of 10m
    region.add_CoordLayer(10)
    # query USGS API for elevation values
    array_size = region.Coords.shape[0] * region.Coords.shape[1]
    training_array = np.empty((array_size, 3))
    coord_array_2d = region.Coords.values
    coord_array = coord_array_2d.flatten()
    # store lat, lon, elev in n x 3 numpy array
    for i in range(array_size):
        lat = coord_array[i][0]
        lon = coord_array[i][1]
        elev = earthly.USGS10mElev(lat, lon)
        training_array[i][:] = lat, lon, elev
    # save array in .npy file
    np.save('lookoutMt', training_array)
