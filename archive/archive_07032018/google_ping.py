import numpy as np
import urllib.request
import simplejson

def googleElevReq():
    sure = str(input("Using google's elevation API may cost Adam money.\n"
                     "Are you sure you want to continue? (y/n)"))
    if sure == 'y':
        topLeftLatLon = [float(input("top left latitude:")), float(input("top left longitude:"))]
        botRightLatLon = [float(input("bottom right lattitude:")), float(input("bottom right longitude:"))]
        # N to S range (.00005 or 1/20000 increments are ~5m steps)
        parallelRange = (np.arange(botRightLatLon[0], topLeftLatLon[0], (1/20000)))
        # E to W range
        meridianRange = (np.arange(topLeftLatLon[1], botRightLatLon[1], (1/20000)))
        # Create empty 3d tensor (lat, lon, elevation)
        datacube = np.zeros((np.shape(parallelRange)[0],np.shape(meridianRange)[0],3))
        m = 0 # Rows
        n = 0 # Columns
        while m < (np.shape(parallelRange)[0]): # Iterate through rows
            n = 0 # Reset column count
            while n < ((np.shape(meridianRange)[0])): # Iterate through columns
                datacube[m][n][1] = meridianRange[n]
                datacube[m][n][0] = parallelRange[m]
                lon = str(meridianRange[n]) # Prepare iterative requests to...
                lat = str(parallelRange[m]) # google's API
                # Make request for elevation data
                response = urllib.request.urlopen("https://maps.googleapis.com/maps/api/elevation/json?locations=" + str(lat) + "," + str(lon) + "&key=AIzaSyCehLK-fJxEZbT9Zej6kKLk8pTAz_iXkp8")
                data = simplejson.load(response)
                datacube[m][n][2] = data["results"][0]["elevation"]
                n = n + 1
            m = m + 1
        np.save(str(input("region name:")), datacube)
    else:
        print("Adam thanks you")
