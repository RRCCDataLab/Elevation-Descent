#
# MODULE FOR MLMODEL CLASS, USED FOR BUILDING TERRAIN SURFACE MODELS, DEVELOPED
# USING A LINEAR REGRESSION CONVOLUTIONAL NEURAL NETWORK. MLMODEL IS A SUBCLASS
# OF SUBREGION.
#
# Authors: Adam Forland, Cory Kennedy
#
# Date: 7/5/2018

import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from keras.models import load_model
import subregion

class MLModel(subregion.SubRegion):
    '''
        For evaluating and studying terrain surface interpolation ML models
    '''
    def __init__(self, NW_corner, SE_corner, data='10m', **kwargs):
        '''
            NW_corner, SE_corner parameters are lat/lon tuples
	'''
        # Instantiate Region superclass
        subregion.SubRegion.__init__(self, NW_corner, SE_corner, data=data, **kwargs)
        sub = subregion.SubRegion(NW_corner, SE_corner, data=data)
        # Class attributes
        self.model_path = '../curve_fitting/models/'
        self.model_file_name = str(input('Keras model file name: '))
        print(self.model_path + self.model_file_name)
        self.model = self.__load_model()
        self.training_data_path = '../data/training_data'
        self.training_data_file_name = str(input('Training data file name: '))
        self.training_data = self.__load_training_data()
        self.validation_data_path = '../data/validation_data'
        self.validation_data_file_name = str(input('Validation data file name: '))
        self.validation_data = self.np.load( self.validation_data_path + self.validation_data_file_name )
        self.LAT_ARR_TRAIN = self.training_data[:,0]
        self.LON_ARR_TRAIN= self.training_data[:,1]
        self.ELEV_ARR_TRAIN = self.training_data[:,2]
        self.LAT_MIN_TRAIN= self.LAT_ARR[0]
        self.LAT_MAX_TRAIN = self.LAT_ARR[-1]
        self.LON_MIN_TRAIN = self.LON_ARR[0]
        self.LON_MAX_TRAIN = np.amax(self.LON_ARR[-1])
        self.ELEV_MIN_TRAIN = np.amin(self.ELEV_ARR)
        self.ELEV_MAX_TRAIN = np.amax(self.ELEV_ARR)
        self.LAT_ARR_NORM_TRAIN = self.__normalize_array('lat', 'train')
        self.LON_ARR_NORM_TRAIN= self.__normalize_array('lon', 'train')
        self.ELEV_ARR_NORM_TRAIN = self.__normalize_array('elev', 'train')
        self.LAT_MIN_VALIDATE = sub.LAT_ARR[0]
        self.LAT_MAX_VALIDATE = sub.LAT_ARR[-1]
        self.LON_MIN_VALIDATE = sub.LON_ARR[0]
        self.LON_MAX_VALIDATE = sub.LON_ARR[-1]
        self.LAT_ARR_VALIDATE = np.linspace(LAT_MIN_VALIDATE, LAT_MAX_VALIDATE, sub.LAT_ARR.size[0]*10)
        self.LON_ARR_VALIDATE = np.linspace(LON_MIN_VALIDATE, LON_MAX_VALIDATE, sub.LON_ARR.size[0]*10)
        self.ELEV_ARR_VALIDATE = self.validation_data[:,2]
        self.LAT_ARR_NORM_VALIDATE = self.__normalize_array('lat', 'validate')
        self.LON_ARR_NORM_VALIDATE = self.__normalize_array('lon', 'validate')
        self.ELEV_ARR_NORM_VALIDATE = self.__normalize_array('elev', 'validate')
        self.elev = self.surface_to_df(sub.LAT_ARR, sub.LON_ARR)

    # BACKEND METHODS TO MLMODEL CLASS

    # Load the data and normalize it for the network.
    def __load_training_data(self):
        all_data_raw = np.load( self.training_data_path + self.training_data_file_name )
        all_data = []
        
        # Remove data that is too low. (Broken points)
        for i in range(np.shape(all_data_raw)[0]):
            if all_data_raw[i][2] < 6000:
                continue
            else:
                all_data.append(all_data_raw[i])
        
        # All that data, not normalized
        all_data = np.array(all_data)
        
        # Normalize the domain space
        x_train = self.ELEV_ARR
        x_train_lat = self.LAT_ARR_NORM_TRAIN
        x_train_lon = self.LON_ARR_NORM_TRAIN
        
        # Final collection of the normalized data
        x_train = np.append(x_train_lat, x_train_lon, axis=1)
        z = self.ELEV_ARR_TRAIN

        return(x_train, z)

    # Load the model that we trained
    def __load_model(self):
        return load_model( self.model_path + self.model_file_name )

    # Normalizes a val to fit the ML domain format
    def normalize_val(self, non_normal_val, axis_name_str, data_name_str):
        '''
            Takes a int for float value and returns a normalized value between 0 and 1

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
                MIN = self.ELEV_MIN_TRAIN
                MAX = self.ELEV_MAX_TRAIN

            else: raise Exception("invalid argument; please pass either 'lat', 'lon', or 'elev'")

        else: raise Exception("invalid argument; please pass either 'train' or 'validate'")

        val = non_normal_val

        return ( (val - MIN) / (MAX - MIN) )

    # De-normalizes a val back to lat/lon coordinates
    def denormalize_val(self, normal_val, axis_name_str):
        '''
            Takes a int for float value and returns a normalized value between 0 and 1

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
                MIN = self.ELEV_MIN_TRAIN
                MAX = self.ELEV_MAX_TRAIN

            else: raise Exception("invalid argument; please pass either 'lat', 'lon', or 'elev'")

        else: raise Exception("invalid argument; please pass either 'train' or 'validate'")

        val = non_normal_val

        return ( val * (MAX - MIN) + MIN )

    # Normalizes domain arrays to fit the ML format
    def __normalize_array(self, axis_name_str):
        '''
            Takes a 1d numpy array as input and returns an array,
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
                MIN = self.ELEV_MIN_TRAIN
                MAX = self.ELEV_MAX_TRAIN
                ARRAY = self.ELEV_ARR_VALIDATE

            else: raise Exception("invalid argument; please pass either 'lat', 'lon', or 'elev'")

        else: raise Exception("invalid argument; please pass either 'train' or 'validate'")

        return ( (ARRAY - MIN) / (MAX - MIN) )

    def surface_to_df(self, lat_arr, lon_arr):
        
        # Query surface for elevation at all grid locations
        elev_list_2D = []
        for col in lon_arr:
            row_list = []
            for row in lat_arr:
                elev = self.test_one(row, col)
            elev_list_2D += row_list
    
        # Contruct DataFrame with results
        return pd.DataFrame(elev_list_2D, index=lat_arr, columns=lon_arr)


    # METHODS FOR ML ARCHITECT EVALUATION OF MLMODEL CLASS

    # Compute the differences between the given points and the network.
    def Error_assessment(self):
        x_train = self.ELEV_ARR_TRAIN
        z = self.model.predict(x_train)  # Calculate this difference

        # Plot the points and the predicted values in a histogram. 
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        ax.scatter(x_train.T[:][0], x_train.T[:][1], z, c='g', marker='o')

        ax.set_xlabel('Latitude')
        ax.set_ylabel('Longitude')
        ax.set_zlabel('Elevation')

        plt.show()

    # METHODS FOR USER EVALUATION OF MLMODEL CLASS

    # Return one elevation for a given (normalized) lat,long.
    def test_one(self, test_lat, test_lon):
        norm_test_lat = self.normalize_val(test_lat, 'lat')
        norm_test_lon = self.normalize_val(test_lon, 'lon')
        norm_elev = self.model.predict(np.array([[norm_test_lat, norm_test_lon]]))
        return self.denormalize(norm_elev, 'elev')

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
            norm_lat = self.normalize_val(lat, 'lat')
            norm_lon = self.normalize_val(lon, 'lon')
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


