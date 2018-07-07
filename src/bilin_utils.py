#
# A MODULE FOR BIILINEAR INTERPOLATION UTILITIES
#
# Author: Cory Kennedy
#
# Date: 6/17/2018

def bilinear_interp(self, lat, lon):
    [(W_lon, S_lat, SW_elev), (W_lon, N_lat, NW_elev),
    (E_lon, S_lat, SE_elev), (E_lon, N_lat, NE_elev)] = self.get_points(lat, lon)
    # see formula at: http://en.wikipedia.org/wiki/Bilinear_interpolation
    # credit for original function: stackoverflow user Raymond Hettinger
    # https://stackoverflow.com/questions/8661537/how-to-perform-bilinear-interpolation-in-python
    return float(SW_elev * (E_lon - lon) * (N_lat - lat) +
            SE_elev * (lon - W_lon) * (N_lat - lat) +
            NW_elev * (E_lon - lon) * (lat - S_lat) +
            NE_elev * (lon - W_lon) * (lat - S_lat)
           ) / ((E_lon - W_lon) * (N_lat - S_lat) + 0.0) 

def elev_walk(self, trace):
    for i in range(len(trace)):
        elev = self.bilinear_interp(trace[i][0], trace[i][1])
        trace[i] = [trace[i][0], trace[i][1], elev]
    return trace

