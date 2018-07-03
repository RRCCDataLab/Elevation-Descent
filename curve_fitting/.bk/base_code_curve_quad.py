import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from matplotlib import pyplot as plt


high_res = np.arange(0, 5, .001)

def f(t):
    return t**2 + 3 * np.sin(t)

model = Sequential([Dense(output_dim=80, input_dim=1),
                Activation("tanh"),
                Dense(output_dim=80, input_dim=80),
                Activation("sigmoid"),
                Dense(output_dim=40, input_dim=80),
                Activation("sigmoid"),
                Dense(output_dim=1, input_dim=40)])

model.compile(loss='mse', optimizer='nadam')

X = np.arange(0,6,1)
y = np.array([(x)**2 + 3 * np.sin(x) for x in X])

model.fit(X, y, nb_epoch=5000)
y_predicted = model.predict(high_res) 
plt.scatter(X, y)
plt.plot(high_res , y_predicted)
plt.plot(high_res, f(high_res)) 
plt.show()
