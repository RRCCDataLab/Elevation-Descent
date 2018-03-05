'''Program seems to be working but takes a very long to run'''

import numpy as np

elevTensor = np.load('RRCC_gulch.npy')

# Strips core matrix from elevTensor
elevMatrix = np.transpose(np.transpose(elevTensor)[2][:])

numElevMatrixRows = np.shape(elevMatrix)[0] # Number of rows
numElevMatrixCols = np.shape(elevMatrix)[1] # Number of columns

# Create shell matrix. 
shellMatrix = np.full(((numElevMatrixRows + 2), (numElevMatrixCols + 2)), -50000.0, dtype=float)

# Put the shellMatrix around the core matrix
row = 1
while row <= numElevMatrixRows :
    column = 1
    while column <= numElevMatrixCols:
        shellMatrix[row][column] = elevMatrix[row-1][column-1]
        column += 1
    row += 1

gradTensor = np.resize(elevTensor, (numElevMatrixRows, numElevMatrixCols, 11))

# Take all the differences
row = 1 # Row counter
while row <= numElevMatrixRows + 1:
    column = 1 # Column counter
    while column <= numElevMatrixCols + 1:
        height = 0
        while height < 8:
            GN = shellMatrix[row][column] - shellMatrix[row-1][column] #Up
            GNE = shellMatrix[row][column] - shellMatrix[row-1][column+1] #Diagonal Up Right
            GE = shellMatrix[row][column] - shellMatrix[row][column+1] #Right
            GSE = shellMatrix[row][column] - shellMatrix[row+1][column+1] #Diagonal Down Right
            GS = shellMatrix[row][column] - shellMatrix[row+1][column] #Down
            GSW = shellMatrix[row][column] - shellMatrix[row+1][column-1] #Diagonal Down Left
            GW = shellMatrix[row][column] - shellMatrix[row][column-1] #Left
            GNW = shellMatrix[row][column] - shellMatrix[row-1][column-1] #Diagonal Up Left
            gradList = [GN, GNE, GE, GSE, GS, GSW, GW, GNW]
            gradTensor[row-1][column-1][height] = gradList[height+3]
            height += 1
        column += 1
    row += 1

gradTensor

np.save(str(input("region name:")+"_grad"), gradTensor)
