import numpy as np
import urllib.request
import simplejson


topLeftLatLon = [39.724788, -105.154405]
botRightLatLon = [39.721670, -105.151328]

# N to S range (.00005 or 1/20000 increments are ~5m steps)
parallelRange = (np.arange(botRightLatLon[0], topLeftLatLon[0], (1/20000)))

# E to W range
meridianRange = (np.arange(topLeftLatLon[1], botRightLatLon[1], (1/20000)))

# Create empty 3d tensor (lat, lon, elevation)
domain = np.zeros((np.shape(parallelRange)[0],np.shape(meridianRange)[0],3))

m = 0 # Rows
n = 0 # Columns

while m < (np.shape(parallelRange)[0]): # Iterate through rows
    n = 0 # Reset column count
    while n < (np.shape(meridianRange)[0]): # Iterate through columns
        domain[m][n][1] = meridianRange[n]
        domain[m][n][0] = parallelRange[m]

        # long = str(meridianRange[m]) # Prepare iterative requests to...
        # lat = str(parallelRange[n]) # google's API

        # Make request for elevation data
        # response = urllib.request.urlopen("https://maps.googleapis.com/maps/api/elevation/json?locations=" + str(lat) + "," + str(long) + "&key=AIzaSyCehLK-fJxEZbT9Zej6kKLk8pTAz_iXkp8")
        # data = simplejson.load(response)
        domain[m][n][2] = 3 # data["results"][0]["elevation"]

        n = n + 1
    m = m + 1

print(np.shape(domain))
