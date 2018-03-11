import numpy as np
import pandas as pd
import urllib.request
import simplejson
import itertools

# tuples that store region info
topLeftLatLon = (39.720993, -105.151754)
botRightLatLon = (39.720761, -105.151258)

# N to S range (.00005 or 1/20000 increments are ~5m steps)
latitudeRange = list(np.arange(botRightLatLon[0], topLeftLatLon[0], (1/20000)))
# E to W range
longitudeRange = list(np.arange(topLeftLatLon[1], botRightLatLon[1], (1/20000)))

# Create MultiIndex for DataFrame
latLonArrs = [latitudeRange, longitudeRange]
latLonTuples = list(itertools.product(latitudeRange, longitudeRange))
latLonIndex = pd.MultiIndex.from_tuples(latLonTuples, names=['Latitude', 'Longitude'])

elevationList = []
for lat, lon in latLonTuples:
    # Make request for elevation data
    response = urllib.request.urlopen("https://maps.googleapis.com/maps/api/elevation/json?locations=" + str(lat) + "," + str(lon) + "&key=AIzaSyCehLK-fJxEZbT9Zej6kKLk8pTAz_iXkp8")
    data = simplejson.load(response)
    elevationList += [data["results"][0]["elevation"]]

terrainDF = pd.DataFrame({'Elevations' : elevationList}, index=latLonIndex)

terrainDF



''' UNDER CONTRUCTION
terrainDF.index

len(terrainDF.index.levels[0])

GS = pd.Series

idx = pd.IndexSlice
terrainDF.iloc[idx[:, 1], :]
'''
