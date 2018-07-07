#
# A MODULE FOR THE SUBREGION CLASS, INHERITED FROM THE REGION CLASS, USED FOR BUILDING
# TERRAIN SURFACE INTERPOLATION MODELS
#
# Author: Cory Kennedy
#
# Date: 6/16/2018

import region

# SubRegion class is a subclass of Region class from region.py
class SubRegion(region.Region):
    
    def __init__(self, NW_corner, SE_corner, data='10m', **kwargs):
        '''
            NW_corner, SE_corner parameters are lat/lon tuples
        '''
        region.Region.__init__(self, NW_corner[0], NW_corner[1], data=data, **kwargs)
        reg = region.Region(NW_corner[0], NW_corner[1], data=data)
        self.elev = reg.slice_subregion(NW_corner, SE_corner)
        self.LAT_ARR = self.elev.index.values.astype(float)
        self.LON_ARR = self.elev.columns.values.astype(float)
