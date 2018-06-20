import earthly as ea
from math import sqrt

def distance_between_points(pnt_1, pnt_2):
    lon_dist = ea.parallelDistance(pnt_1[0], pnt_2[0])
    lat_dist = ea.meridianDistance(pnt_1[0], pnt_1[1], pnt_2[0], pnt_2[1])
    return sqrt(lat_dist**2 + lon_dist**2)


