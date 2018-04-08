import numpy as np
import pandas as pd
import itertools
from math import sin, cos, sqrt, atan2, radians

def parallelDistance(lat1, lat2):
    # Calculate the distance of the parallel span
    R = 6373.0 # approximate radius of earth in km
    dlon = 0
    dlat = abs(lat2 - lat1)
    a = sin(dlat / 2)**2 + cos(lat2) * cos(lat1) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    parallel_distance = R * c
    return parallel_distance

def meridianDistance(lat1, lon1, lat2, lon2):
    # Calculate the distance of the meridian span
    R = 6373.0 # approximate radius of earth in km
    dlon = abs(lon2 - lon1)
    dlat = 0
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    meridian_distance = R * c
    return meridian_distance


class Region:

    def __init__(self, name):
        self.name = name
        NW_lat = float(input("NW corner latitude: "))
        NW_lon = float(input("NW corner longitude: "))
        SE_lat = float(input("SE corner latitude: "))
        SE_lon = float(input("SE corner longitude: "))
        self.perim = (NW_lat, NW_lon, SE_lat, SE_lon)
        self.Coords = pd.DataFrame()

    '''Creates a pandas DataFrame of the latitude/longitude coordinates for the region. Step Size (stepSize) is in meters (great circle.)'''
    def add_CoordLayer(self, stepSize):
        
        NW_lat = self.perim[0]
        NW_lon = self.perim[1]
        SE_lat = self.perim[2]
        SE_lon = self.perim[3]

        NW_lat_rad = radians(NW_lat)
        NW_lon_rad = radians(NW_lon)
        SE_lat_rad = radians(SE_lat)
        SE_lon_rad = radians(SE_lon)
 
        # Calculate the number of steps for the parallel span
        parallel_distance = parallelDistance(NW_lat_rad, SE_lat_rad) * 1000
        parallel_steps = parallel_distance / stepSize

        # Calculate the number of steps for the meridian span
        meridian_distance = meridianDistance(NW_lat_rad, NW_lon_rad, SE_lat_rad, SE_lon_rad) * 1000
        meridian_steps = meridian_distance / stepSize

        # N to S range
        parallelRange = np.linspace(SE_lat, NW_lat, parallel_steps)
        # E to W range
        meridianRange = np.linspace(NW_lon, SE_lon, meridian_steps)

        # Create 1D list of tuples with all unique lat/lon combos
        latLonTuples = list(itertools.product(parallelRange, meridianRange))

        # Convert 1D to 2D list for DataFrame
        latLonList2D = []
        rowList = []
        for tuples in latLonTuples:
            rowList += [tuples]
            if len(rowList) == len(meridianRange):
                latLonList2D += [rowList]
                rowList = []

        # Generate DataFrame
        coordMatrix = pd.DataFrame(latLonList2D)
        self.Coords = self.Coords.append(coordMatrix)
        #return self.Coords
