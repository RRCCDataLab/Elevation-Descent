import numpy as np
from keras.models import Sequential
from keras import optimizers
from keras.layers.core import Dense, Activation, Dropout, Lambda
from matplotlib import pyplot as plt
from itertools import product 
from mpl_toolkits.mplot3d import Axes3D
from keras import regularizers
from datetime import datetime

# Read in all the data
all_data_raw = np.load('./data/theM_1m.npy')

# Cut the elevations that are too low
all_data = []
for i in range(np.shape(all_data_raw)[0]):
    if all_data_raw[i][2] < 6000:
        continue
    else:
        all_data.append(all_data_raw[i])

# Make the new all_data without the 
# low points
all_data = np.array(all_data)

# Make raw x_train
x_train = all_data[:,:2]

# Normalize x_train
x_train_lat = (all_data[:,0:1] - np.min(all_data[:,0:1]))/(np.max(all_data[:,0:1]) -  np.min(all_data[:,0:1])) 
x_train_long = (all_data[:,1:2] - np.min(all_data[:,1:2]))/(np.max(all_data[:,1:2]) -  np.min(all_data[:,1:2]))

# Bring all of x_train together.
x_train = np.append(x_train_lat, x_train_long, axis = 1)

# Normalize z
z = all_data[:,2:]
# z = (z - np.min(z))/(np.max(z)-np.min(z))

# Build the model 
model = Sequential([Dense(output_dim=20, input_dim=2),
                Activation("sigmoid") ,
                Dense(output_dim=10, input_dim=20),
                Activation("tanh"),
                Dense(output_dim=10, input_dim=10),
                Activation("relu"),
                Dense(output_dim=10, input_dim=10),
                Activation("relu"),
                Dense(output_dim=1, input_dim=10),
                Activation('relu')])


# Optimizers
sgd = optimizers.SGD(lr=0.01, momentum=0.5, nesterov=True)
adam = optimizers.Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=.1, decay=0.0, amsgrad=False)

# Compile the models
model.compile(loss='mae', optimizer=adam)

# Run the model
model.fit(x_train, z, nb_epoch=10000)

# Save the model
model.save('./models/elevation_model_real_data'+ datetime.now().strftime('%Y-%m-%d_%H:%M:%S')  + '.h5')

# Make the prediction data for the points between the given information.
z_predicted = model.predict(x_train)

# Plot the points and the predicted values. 
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(x_train.T[:][0], x_train.T[:][1], z, c='g', marker='o')
ax.scatter(x_train.T[:][0], x_train.T[:][1], z_predicted, c='r', marker='o')

ax.set_xlabel('Latitude')
ax.set_ylabel('Longitude')
ax.set_zlabel('Elevation')

plt.show()

