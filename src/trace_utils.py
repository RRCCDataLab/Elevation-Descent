#
# A MODULE FOR TILE CLASS UTILITIES
#
# Author: Cory Kennedy
#
# Date: 7/19/2018

from math import radians, sin, cos, asin, sqrt

def haversine(origin, destination):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # extract lats/lons from trace
    lat1, lon1 = origin
    lat2, lon2 = destination
    
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers.
    dist_km =  c * r
    dist_m = dist_km * 1000
    return dist_m
