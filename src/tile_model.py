#
# MODULE FOR TILEMODEL CLASS, USED FOR BUILDING A TILED MODEL OF A TERRAIN SURFACE.
# TILEMODEL IS A SUBCLASS OF SUBREGION.
#
# Author: Cory Kennedy
#
# Date: 7/6/2018

import numpy as np
import pandas as pd
import subregion

class TileModel(subregion.SubRegion):

    def __init__(self, NW_corner, SE_corner, data='10m', **kwargs):
        '''
            NW_corner, SE_corner parameters are lat/lon tuples
        '''
        self.SubRegion = subregion.SubRegion(NW_corner, SE_corner, data=data)
        z_arr = self.SubRegion.elev.values
        z_stretched_arr = np.repeat(z_arr, 10, axis=0)
        z_tiled_arr = np.repeat(z_stretched_arr, 10, axis=1)
        self.LAT_ARR = np.linspace(self.SubRegion.LAT_ARR[0], self.SubRegion.LAT_ARR[-1], z_tiled_arr.shape[0])
        self.LON_ARR = np.linspace(self.SubRegion.LON_ARR[0], self.SubRegion.LON_ARR[-1], z_tiled_arr.shape[1])
        self.elev = pd.DataFrame(z_tiled_arr, index=self.LAT_ARR, columns=self.LON_ARR)

