#
# MODULE FOR MLMODEL CLASS, USED FOR BUILDING TERRAIN SURFACE MODELS, DEVELOPED
# USING A LINEAR REGRESSION CONVOLUTIONAL NEURAL NETWORK. MLMODEL IS A SUBCLASS
# OF SUBREGION.
#
# Authors: Adam Forland, Cory Kennedy
#
# Date: 7/5/2018

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from keras.models import load_model
import subregion
import ml_model_utils

import pdb

class MLModel(subregion.SubRegion):
    '''
        For evaluating and studying terrain surface interpolation ML models
    '''
    def __init__(self, NW_corner, SE_corner, data='10m', **kwargs):
        '''
            NW_corner, SE_corner parameters are lat/lon tuples
	'''
        # Instantiate Region superclass
        #subregion.SubRegion.__init__(self, NW_corner, SE_corner, data=data, **kwargs)
        self.SubRegion = subregion.SubRegion(NW_corner, SE_corner, data=data)

        # Class attributes
        # Model Data
        self.model_path = '../data/models/'
        # TODO add failsafes for all input prompts
        self.model_file_name = str(input('Keras model file name: '))
        self.model = self.__load_model()

        # Training Data
        self.training_data_path = '../data/training_data/'
        self.training_data_file_name = str(input('Training data file name: '))
        training_data = np.load(self.training_data_path + self.training_data_file_name)
        # TODO make below a function
        # Delete all data points with elev values below 5000ft (they are errant)
        self.training_data = np.delete(training_data, np.where(training_data[:,2] < 5000), axis=0)
        self.LAT_ARR_TRAIN = self.training_data[:,0]
        self.LON_ARR_TRAIN= self.training_data[:,1]
        self.ELEV_ARR_TRAIN = self.training_data[:,2]
        self.LAT_MIN_TRAIN= self.LAT_ARR_TRAIN[0]
        self.LAT_MAX_TRAIN = self.LAT_ARR_TRAIN[-1]
        self.LON_MIN_TRAIN = self.LON_ARR_TRAIN[0]
        self.LON_MAX_TRAIN = self.LON_ARR_TRAIN[-1]
        self.ELEV_MIN_TRAIN = np.amin(self.ELEV_ARR_TRAIN)
        self.ELEV_MAX_TRAIN = np.amax(self.ELEV_ARR_TRAIN)

        # x_train data; normalized and errant elevations removed
        self.XTRAIN, _ = self.__load_training_data()
        self.LAT_ARR_XTRAIN = self.XTRAIN[:,0]
        self.LON_ARR_XTRAIN= self.XTRAIN[:,1]
        self.ELEV_ARR_XTRAIN = self.XTRAIN[:,2]
        self.LAT_MIN_XTRAIN= self.LAT_ARR_XTRAIN[0]
        self.LAT_MAX_XTRAIN = self.LAT_ARR_XTRAIN[-1]
        self.LON_MIN_XTRAIN = self.LON_ARR_XTRAIN[0]
        self.LON_MAX_XTRAIN = self.LON_ARR_XTRAIN[-1]
        self.ELEV_MIN_XTRAIN = np.amin(self.ELEV_ARR_XTRAIN)
        self.ELEV_MAX_XTRAIN = np.amax(self.ELEV_ARR_XTRAIN)

        # Validation Data
        self.validation_data_path = '../data/validation_data/'
        self.validation_data_file_name = str(input('Validation data file name: '))
        validation_data = np.load(self.validation_data_path + self.validation_data_file_name)
        # Delete all data points with elev values below 5000ft (they are errant)
        self.validation_data = np.delete(validation_data, np.where(validation_data[:,2] < 5000), axis=0)
        self.LAT_ARR_VALIDATE = self.validation_data[:,0]
        self.LON_ARR_VALIDATE = self.validation_data[:,1]
        self.ELEV_ARR_VALIDATE = self.validation_data[:,2]
        self.LAT_MIN_VALIDATE = self.LAT_ARR_VALIDATE[0]
        self.LAT_MAX_VALIDATE = self.LAT_ARR_VALIDATE[-1]
        self.LON_MIN_VALIDATE = self.LON_ARR_VALIDATE[0]
        self.LON_MAX_VALIDATE = self.LON_ARR_VALIDATE[-1]
        self.ELEV_MIN_VALIDATE = np.amin(self.ELEV_ARR_VALIDATE)
        self.ELEV_MAX_VALIDATE = np.amax(self.ELEV_ARR_VALIDATE)
        self.LAT_ARR_NORM_VALIDATE = self.__normalize_axarray('lat', 'validate')
        self.LON_ARR_NORM_VALIDATE = self.__normalize_axarray('lon', 'validate')
        self.ELEV_ARR_NORM_VALIDATE = self.__normalize_axarray('elev', 'validate')
        
        # Build model geo-grid
        sub = self.SubRegion
        model_lat_array = np.linspace(sub.LAT_ARR[0], sub.LAT_ARR[-1], sub.LAT_ARR.shape[0] * 10)
        model_lon_array = np.linspace(sub.LON_ARR[0], sub.LON_ARR[-1], sub.LON_ARR.shape[0] * 10)

        # Results
        self.elev = self.surface_to_df(model_lat_array, model_lon_array)

    # BACKEND METHODS TO MLMODEL CLASS ----------------------------------[

    # Load the data and normalize it for the network.
    def __load_training_data(self):
        all_data_raw = self.training_data
        all_data = []
        
        # Remove data that is too low. (Broken points)
        for i in range(np.shape(all_data_raw)[0]):
            if all_data_raw[i][2] < 5000:
                continue
            else:
                all_data.append(all_data_raw[i])
        
        # All that data, normalized
        all_data = np.array(all_data)
        x_train_elevs = ml_model_utils.normalize_array(all_data[:,2])
        x_train_lats = ml_model_utils.normalize_array(all_data[:,0])
        x_train_lons = ml_model_utils.normalize_array(all_data[:,1])

        # Reformat as x_train
        x_train = np.stack([x_train_elevs, x_train_lats, x_train_lons], axis=1)
        z = x_train[:,0]

        return(x_train, z)

    # Load the model that we trained
    def __load_model(self):
        return load_model( self.model_path + self.model_file_name )

    # Normalizes an axis val to fit the ML domain format
    def __normalize_axval(self, non_normal_val, axis_name_str, data_name_str):
        '''
            Takes a int for float value, from along an axis, and returns a
            normalized value between 0 and 1

            Parameters: value_to_be_normalized, axis_name ('lat', 'lon', or 'elev')
                        data_name ('train', 'validate')
        '''
        if data_name_str == 'train' :

            if axis_name_str == 'lat' :
                MIN = self.LAT_MIN_TRAIN
                MAX = self.LAT_MAX_TRAIN

            elif axis_name_str == 'lon' :
                MIN = self.LON_MIN_TRAIN
                MAX = self.LON_MAX_TRAIN

            elif axis_name_str == 'elev' :
                MIN = self.ELEV_MIN_TRAIN
                MAX = self.ELEV_MAX_TRAIN

            else: raise Exception("invalid argument; please pass either 'lat', 'lon', or 'elev'")

        elif data_name_str == 'validate' :

            if axis_name_str == 'lat' :
                MIN = self.LAT_MIN_VALIDATE
                MAX = self.LAT_MAX_VALIDATE

            elif axis_name_str == 'lon' :
                MIN = self.LON_MIN_VALIDATE
                MAX = self.LON_MAX_VALIDATE

            elif axis_name_str == 'elev' :
                MIN = self.ELEV_MIN_VALIDATE
                MAX = self.ELEV_MAX_VALIDATE

            else: raise Exception("invalid argument; please pass either 'lat', 'lon', or 'elev'")

        else: raise Exception("invalid argument; please pass either 'train' or 'validate'")

        val = non_normal_val

        return ( (val - MIN) / (MAX - MIN) )

    # De-normalizes an axis val back to lat/lon coordinates
    def __denormalize_axval(self, normal_val, axis_name_str, data_name_str):
        '''
            Takes a normalized int or float value, from along an axis, and returns a
            de-normalized value from the original range/domain

            Parameters: value_to_be_normalized, axis_name ('lat', 'lon', or 'elev')
                        data_name ('train', 'validate')
        '''
        if data_name_str == 'train' :

            if axis_name_str == 'lat' :
                MIN = self.LAT_MIN_TRAIN
                MAX = self.LAT_MAX_TRAIN

            elif axis_name_str == 'lon' :
                MIN = self.LON_MIN_TRAIN
                MAX = self.LON_MAX_TRAIN

            elif axis_name_str == 'elev' :
                MIN = self.ELEV_MIN_TRAIN
                MAX = self.ELEV_MAX_TRAIN

            else: raise Exception("invalid argument; please pass either 'lat', 'lon', or 'elev'")

        elif data_name_str == 'validate' :

            if axis_name_str == 'lat' :
                MIN = self.LAT_MIN_VALIDATE
                MAX = self.LAT_MAX_VALIDATE

            elif axis_name_str == 'lon' :
                MIN = self.LON_MIN_VALIDATE
                MAX = self.LON_MAX_VALIDATE

            elif axis_name_str == 'elev' :
                MIN = self.ELEV_MIN_VALIDATE
                MAX = self.ELEV_MAX_VALIDATE

            else: raise Exception("invalid argument; please pass either 'lat', 'lon', or 'elev'")

        else: raise Exception("invalid argument; please pass either 'train' or 'validate'")

        return ( normal_val * (MAX - MIN) + MIN )

    # Normalizes axis arrays to fit the ML format
    def __normalize_axarray(self, axis_name_str, data_name_str):
        '''
            Takes a 1d numpy array, from an axis, as input and returns an array,
            normalized between 0 and 1, of the same size.

            Parameters: value_to_be_normalized, axis_name ('lat', 'lon', or 'elev')
                        data_name ('train', 'validate')
        '''
        if data_name_str == 'train' :

            if axis_name_str == 'lat' :
                MIN = self.LAT_MIN_TRAIN
                MAX = self.LAT_MAX_TRAIN
                ARRAY = self.LAT_ARR_TRAIN

            elif axis_name_str == 'lon' :
                MIN = self.LON_MIN_TRAIN
                MAX = self.LON_MAX_TRAIN
                ARRAY = self.LON_ARR_TRAIN

            elif axis_name_str == 'elev' :
                MIN = self.ELEV_MIN_TRAIN
                MAX = self.ELEV_MAX_TRAIN
                ARRAY = self.ELEV_ARR_TRAIN

            else: raise Exception("invalid argument; please pass either 'lat', 'lon', or 'elev'")

        elif data_name_str == 'validate' :

            if axis_name_str == 'lat' :
                MIN = self.LAT_MIN_VALIDATE
                MAX = self.LAT_MAX_VALIDATE
                ARRAY = self.LAT_ARR_VALIDATE

            elif axis_name_str == 'lon' :
                MIN = self.LON_MIN_VALIDATE
                MAX = self.LON_MAX_VALIDATE
                ARRAY = self.LON_ARR_VALIDATE

            elif axis_name_str == 'elev' :
                MIN = self.ELEV_MIN_VALIDATE
                MAX = self.ELEV_MAX_VALIDATE
                ARRAY = self.ELEV_ARR_VALIDATE

            else: raise Exception("invalid argument; please pass either 'lat', 'lon', or 'elev'")

        else: raise Exception("invalid argument; please pass either 'train' or 'validate'")

        return ( (ARRAY - MIN) / (MAX - MIN) )

    def surface_to_df(self, lat_arr, lon_arr):
        
        # Query surface for elevation at all grid locations
        elev_list_2D = []
        for row in lat_arr:
            row_list = []
            for col in lon_arr:
                elev = float(self.test_one(row, col)[0])
                row_list += [elev]
            elev_list_2D += [row_list]

            lat_arr_flip = np.flip(lat_arr, 0)

        # Contruct DataFrame with results
        return pd.DataFrame(elev_list_2D, index=lat_arr_flip, columns=lon_arr)


    # METHODS FOR ML ARCHITECT EVALUATION OF MLMODEL CLASS --------------------

    # Compute the differences between the given points and the network.
    def Error_assessment(self):
        x_train = self.XTRAIN
        z = self.model.predict(x_train)  # Calculate this difference

        # Plot the points and the predicted values in a histogram. 
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        ax.scatter(x_train.T[:][0], x_train.T[:][1], z, c='g', marker='o')

        ax.set_xlabel('Latitude')
        ax.set_ylabel('Longitude')
        ax.set_zlabel('Elevation')

        plt.show()

    # METHODS FOR USER EVALUATION OF MLMODEL CLASS ----------------------------

    # Return one elevation for a given (normalized) lat,long.
    def test_one(self, test_lat, test_lon):
        norm_test_lat = self.__normalize_axval(test_lat, 'lat', 'train')
        norm_test_lon = self.__normalize_axval(test_lon, 'lon', 'train')
        #norm_elev = self.model.predict(np.array([[norm_test_lat, norm_test_lon]]))
        elev = self.model.predict(np.array([[norm_test_lat, norm_test_lon]]))
        # NOTE suspect maybe not normalized
        #return self.__denormalize_axval(norm_elev, 'elev', 'train')
        return elev

    def batch_test(self):
        all_raw_training_data = self.training_data
        validate_step = self.validation_data
        model = self.model
       
        # Cut the elevations that are too low
        training_step = []
        for i in range(np.shape(all_raw_training_data)[0]):
            if all_raw_training_data[i][2] < 3000:
                continue
            else:
                training_step.append(all_raw_training_data[i])
        
        training_step = np.array(training_step)

        lat_max = self.LAT_MAX_TRAIN
        lat_min = self.LAT_MIN_TRAIN

        lon_max = self.LON_MAX_TRAIN
        lon_min = self.LON_MIN_TRAIN

        info = []
        for i in range(np.shape(small_step)[0]):
            lat = small_step[i][0]
            lon = small_step[i][1]
            norm_lat = self.__normalize_axval(lat, 'lat', 'train')
            norm_lon = self.__normalize_axval(lon, 'lon', 'train')
            z_predicted = model.predict(np.array([[norm_lat, norm_lon]]))       
            diff = small_step[i][2] - z_pre
            info.append(diff)

        bar, bins = np.histogram(info, bins=20)
        plt.bar(bins[:-1], bar, width=10)
        plt.show()



# Running the methods.
#x_train, z, LatN, LongN = backend.load_data()
#model = self.backend.__load_model()

#print(model.predict(np.array([[LatN,LongN]])))
#user_evaluation.batch_test()


#elevation = user_evaluation.test_one(1, model, MIN, MAX)
#print(elevation[0][0])

#network_evaluation.Error_assessment(model, x_train, z)



