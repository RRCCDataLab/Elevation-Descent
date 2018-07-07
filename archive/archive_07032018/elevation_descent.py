import numpy as np
import urllib.request
import simplejson
import pandas as pd
import itertools

''' Maybe make region a class (this would eliminate any questions
    about datatypes of regions) as in the function below '''
def region_as_nparray():
    topLeftLatLon = (float(input("top left latitude:")), float(input("top left longitude:")))
    botRightLatLon = (float(input("bottom right lattitude:")), float(input("bottom right longitude:")))
    # N to S range (.00005 or 1/20000 increments are ~5m steps)
    parallelRange = (np.arange(botRightLatLon[0], topLeftLatLon[0], (1/20000)))
    # E to W range
    meridianRange = (np.arange(topLeftLatLon[1], botRightLatLon[1], (1/20000)))
    global domainSpace
    domainSpace = np.zeros((np.shape(parallelRange)[0],np.shape(meridianRange)[0],2))
    row = 0
    while row < np.shape(parallelRange)[0]:
        column = 0
        while column < np.shape(meridianRange)[0]:
            domainSpace[row][column][0] = parallelRange[row]
            domainSpace[row][column][1] = meridianRange[column]
            column += 1
        row += 1
    return domainSpace


def region_to_csv():
    topLeftLatLon = (float(input("top left latitude:")), float(input("top left longitude:")))
    botRightLatLon = (float(input("bottom right lattitude:")), float(input("bottom right longitude:")))
    #topLeftLatLon = (39.720993, -105.151754)
    #botRightLatLon = (39.720761, -105.151258)
    stepSize = float(input("step size:"))
    # N to S range (.00005 or 1/20000 increments are ~5m steps)
    latitudeRange = list(np.arange(botRightLatLon[0], topLeftLatLon[0], stepSize))
    # E to W range
    longitudeRange = list(np.arange(topLeftLatLon[1], botRightLatLon[1], stepSize))
    # Create 1D list of tuples with all unique lat/lon combos
    latLonArrs = [latitudeRange, longitudeRange]
    latLonTuples = list(itertools.product(latitudeRange, longitudeRange))
    # Convert 1D to 2D list for DataFrame
    LatLonList2D = []
    rowList = []
    for tuple in latLonTuples:
        rowList += [tuple(tuple)]
        if len(rowList) == len(longitudeRange):
            LatLonList2D += [rowList]
            rowList = []
    # Generate DataFrame
    tuplesDF = pd.DataFrame(LatLonList2D)
    # Write to csv file
    tuplesDF.to_csv(str(input("region name:"))+'.csv', index=False)


def elevation_to_npy():
    print("Warning: This function will request elevation data from google's elevation API.")
    print("\tPlease familiarize yourself with its policies and limitations.")
    region()
    # Create empty 3d tensor (lat, lon, elevation)
    dataCube = np.resize(domainSpace, (np.shape(domainSpace)[0], np.shape(domainSpace)[1], np.shape(domainSpace)[2]+1))
    row = 0 # Rows
    while row < (np.shape(domainSpace)[0]): # Iterate through rows
        column = 0 # RColumns
        while column < ((np.shape(domainSpace)[1])): # Iterate through columns
            lat = str(domainSpace[row][column][0])
            lon = str(domainSpace[row][column][1])
            # Make request for elevation data
            response = urllib.request.urlopen("https://maps.googleapis.com/maps/api/elevation/json?locations=" + str(lat) + "," + str(lon) + "&key=AIzaSyCehLK-fJxEZbT9Zej6kKLk8pTAz_iXkp8")
            data = simplejson.load(response)
            dataCube[row][column][2] = data["results"][0]["elevation"]
            column += 1
        row += 1
    np.save(str(input("region name:")), dataCube)

''' UNDER CONTRUCTION '''
def elevation_to_csv():
    # Create empty 3d tensor (lat, lon, elevation)
    dataCube = np.resize(domainSpace, (np.shape(domainSpace)[0], np.shape(domainSpace)[1], np.shape(domainSpace)[2]+1))
    row = 0 # Rows
    while row < (np.shape(domainSpace)[0]): # Iterate through rows
        column = 0 # RColumns
        while column < ((np.shape(domainSpace)[1])): # Iterate through columns
            lat = str(domainSpace[row][column][0])
            lon = str(domainSpace[row][column][1])
            # Make request for elevation data
            response = urllib.request.urlopen("https://maps.googleapis.com/maps/api/elevation/json?locations=" + str(lat) + "," + str(lon) + "&key=AIzaSyCehLK-fJxEZbT9Zej6kKLk8pTAz_iXkp8")
            data = simplejson.load(response)
            dataCube[row][column][2] = data["results"][0]["elevation"]
            column += 1
        row += 1
    elevDF = pd.DataFrame(data=dataCube)

    # FINISHME: add array to dataframe and dataeframe to csv
