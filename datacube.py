'''
The M array will be the elevation data. The program here makes a "Shell"
of zeros around the given elevation array so that all the differences
can be computed eight times even for the edges. The Delta_Vectors
is an array that collects these differences. The first two entries will
tell us the location of the pixel in the elevation array (M) and the
other entries will be the differences starting with the cell to the
right and working counter-clockwise.
'''

import numpy as np

M = np.array([[1,2,3],[1,1,1],[3,4,5]]) # Core matrix
Shell = np.zeros((np.shape(M)[0] + 2,np.shape(M)[1] + 2)) # Shell martix

# Empty delta collection
Delta_Vectors = np.zeros((np.shape(M)[0]*np.shape(M)[1],10))

# Put the shell around the core matrix
i = 1
while i < 4 :
    j = 1
    while j < 4:
        Shell[i][j] = M[i-1][j-1]
        j = j + 1
    i = i + 1

# Take all the differences
k = 0 # Index for all the entries in the matrix
i = 1 # Row counter
while k < 9:
    while i < 4 :
        j = 1 # Column counter
        while j < 4:
            G1 = Shell[i][j] - Shell[i][j+1] #Right
            G2 = Shell[i][j] - Shell[i-1][j+1] #Diagonal Up Right
            G3 = Shell[i][j] - Shell[i-1][j] #Up Center
            G4 = Shell[i][j] - Shell[i-1][j-1] #Diagonal Up Left
            G5 = Shell[i][j] - Shell[i][j-1] #Left
            G6 = Shell[i][j] - Shell[i+1][j-1] #Diagonal Down Left
            G7 = Shell[i][j] - Shell[i+1][j] #Down
            G8 = Shell[i][j] - Shell[i-1][j+1] #Diagonal Down Right

            k = k + 1

            # Make delta vector [Row,Column, (8 changes)]
            Delta_Vectors[k-1] = [i,j,G1,G2,G3,G4,G5,G6,G7,G8]

            j = j + 1

        i = i + 1

print(Delta_Vectors)
