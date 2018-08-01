#
# MODULE FOR BUILDING TRACE OBJECTS TO BE INHERITED FROM REGION (SUBREGION IN THE FUTURE)
# OBJECTS FOR THE PURPOSE OF LEARNING PROFILE INFORMATION (ELEVATION AND GRADE) FROM A 
# SERIES OF LOCATIONS WITHIN A REGION
#
# Author: Cory Kennedy
#
# Date: 7/19/2018

import region
import trace_utils

class Trace(region.Region):

    def __init__(self, lats, lons, data='10m', **kwargs):
        '''
            lats, lons params are lists of latitude and longitude points
            of the Trace positions throughout the Region
        '''
        self.Region = region.Region(lats, lons, data=data)
        self.lats = lats
        self.lons = lons
        self.coords = list(zip(lats, lons))
        print('Generating elevation profile')
        self.elev = self.bilin_walk()
        print('Generating grade profile')
        self.grade = self.get_grade_profile()

        
    def bilinear_interp(self, lat, lon):
        [(W_lon, S_lat, SW_elev), (W_lon, N_lat, NW_elev),
        (E_lon, S_lat, SE_elev), (E_lon, N_lat, NE_elev)] = self.Region.get_points(lat, lon)
        # see formula at: http://en.wikipedia.org/wiki/Bilinear_interpolation
        # credit for original function: stackoverflow user Raymond Hettinger
        # https://stackoverflow.com/questions/8661537/how-to-perform-bilinear-interpolation-in-python
        return float(SW_elev * (E_lon - lon) * (N_lat - lat) +
                SE_elev * (lon - W_lon) * (N_lat - lat) +
                NW_elev * (E_lon - lon) * (lat - S_lat) +
                NE_elev * (lon - W_lon) * (lat - S_lat)
               ) / ((E_lon - W_lon) * (N_lat - S_lat) + 0.0) 

    def bilin_walk(self):
        elev_profile = []
        for i in range(len(self.coords)):
            elev = self.bilinear_interp(self.lats[i], self.lons[i])
            elev_profile += [elev]
        return elev_profile
	
    def grade_to_next_point(self, iterator):
        origin = self.coords[iterator]
        destination = self.coords[iterator + 1]
        rise_ft = self.elev[iterator + 1] - self.elev[iterator]
        rise = rise_ft / 3.280839895 # convert ft to meters
        run = trace_utils.haversine(origin, destination)
        # Handle edge case when vehicle hasn't moved (div by zero)
        if run == 0:
            return 0
        else:
            return ((rise / run) * 100)

    def get_grade_profile(self):
        grade_profile = []

        for i in range(len(self.coords) - 1):
            grade = self.grade_to_next_point(i)
            grade_profile += [grade]

        return grade_profile

	
