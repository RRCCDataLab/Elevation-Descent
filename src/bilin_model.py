#
# MODULE FOR BILINMODEL CLASS, USED FOR BUILDING A BILINEARLY INTERPOLATED MODEL
# OF A TERRAIN SURFACE. BILINMODEL IS A SUBCLASS OF SUBREGION.
#
# Author: Cory Kennedy
#
# Date: 7/6/2018

import numpy as np
import pandas as pd
from scipy.interpolate import interp2d
import subregion

class BilinModel(subregion.SubRegion):

    def __init__(self, NW_corner, SE_corner, data='10m', **kwargs):
        '''
            NW_corner, SE_corner parameters are lat/lon tuples
	'''
	subregion.SubRegion.__init__(self, NW_corner, SE_corner, data=data, **kwargs)
	sub = subregion.SubRegion(NW_corner, SE_corner, data=data)
	X = sub.LON_ARR # array of longitude vals W > E
	Y = np.flip(sub.LAT_ARR, 0) # flipped to accomadate builtin interp method
	Z = sub.elev.values # elevation vals as a 2d array

	# Build the function for bilinear interpolation
	newfunc = interp2d(X, Y, Z, kind='linear')

	# Domain space now has 10x the values within the same region
	xnew = np.linspace(np.amin(X), np.amax(X), X.shape[0]*10)
	ynew = np.linspace(np.amax(Y), np.amin(Y), Y.shape[0]*10)

	# Get bilin interpolated 2d array from function
	z_bilin = newfunc(xnew, ynew)
        self.LAT_ARR = np.flip(ynew, 0) # flip y axis back after interpolation
        self.LON_ARR = xnew
        self.elev = pd.DataFrame(z_bilin, index=self.LAT_ARR, columns=self.LON_ARR)
