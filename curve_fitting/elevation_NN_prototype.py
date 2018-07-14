'''
Author: Adam Forland Data_Lab @ Red Rocks Community College
'''

import numpy as np
import sys
from matplotlib import pyplot as plt
from matplotlib import cm
import yaml

from keras.models import model_from_yaml
from keras import regularizers
from mpl_toolkits.mplot3d import Axes3D
from keras.models import Sequential
from keras import optimizers
from keras.layers.core import Dense, Activation, Dropout, Lambda
from keras import regularizers

from itertools import product 
from datetime import datetime


sys.path.append('../src')
import file_name_utils 

ID = sys.argv[1]
EPOCH_NUM = int(sys.argv[2])
arch = sys.argv[3]

# Load the model from storage
yaml_model = open('../data/architectures/' + arch + '.yml', "r+").read()
model = model_from_yaml(yaml_model)

# Read in all the data
all_data_raw = np.load('../data/training_data/theM_10m_3.npy') 

# Cut the elevations that are too low
all_data = []
for i in range(np.shape(all_data_raw)[0]):
    if all_data_raw[i][2] < 5000:
        continue
    else:
        all_data.append(all_data_raw[i])

# Make the new all_data without the low points
all_data = np.array(all_data)

# Make raw x_train
x_train = all_data[:, :2]

# Normalize x_train
x_train_lat = (all_data[:, 0:1] - np.min(all_data[:, 0:1]))/(np.max(all_data[:, 0:1]) -  np.min(all_data[:, 0:1])) 
x_train_long = (all_data[:, 1:2] - np.min(all_data[:, 1:2]))/(np.max(all_data[:, 1:2]) -  np.min(all_data[:, 1:2]))

# Bring all of x_train together.
x_train = np.append(x_train_lat, x_train_long, axis=1)                

# Make high resolution data.
high_res = np.arange(0, 1, .01)

high_res_mesh = []
for j in range(np.shape(high_res)[0]):
    x = high_res[j]
    for k in range(np.shape(high_res)[0]):
        y = high_res[k]    
        high_res_mesh.append([x, y])
        
high_res_mesh = np.asarray(high_res_mesh)

# Normalize z
z = all_data[:,2:]

# Optimizers
sgd = optimizers.SGD(lr=0.01, momentum=0.5, nesterov=True)
adam = optimizers.Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=.1, decay=0.0, amsgrad=True)

# Compile the models
model.compile(loss='mae', optimizer=adam)

'''
val = model.to_yaml()
with open(arch + '.yml', 'w') as outfile:
        outfile.write(val)
'''

# Run the model
model.fit(x_train, z, nb_epoch=EPOCH_NUM)

# Running Cory's custom namer
name = file_name_utils.get_file_name(ID, str(EPOCH_NUM), filetype="model") 

# Running Cory's custom namer
name_w = file_name_utils.get_file_name(ID + '_W', str(EPOCH_NUM), filetype="model") 

# Save the model
model.save("../data/models/" + name)

# Save the weights
model.save_weights("../data/weights/" + name_w)

# Make the prediction data for the points between the given information.
z_predicted = model.predict(x_train)
z_predicted_HR =  model.predict(high_res_mesh)

# Plot the points and the predicted values. 
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(x_train.T[:][0], x_train.T[:][1], z, c=z, marker='o')
ax.scatter(x_train.T[:][0], x_train.T[:][1], z_predicted, c='r' , marker='o')
#ax.scatter(high_res_mesh.T[:][0], high_res_mesh.T[:][1], z_predicted_HR, c='b', marker='o')

ax.set_xlabel('Latitude')
ax.set_ylabel('Longitude')
ax.set_zlabel('Elevation')

plt.show()

