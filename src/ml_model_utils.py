#
# HELPER FUNCTIONS FOR THE MLMODEL CLASS
#
# Author: Cory Kennedy
#
# Date: 7/9/2018

import numpy as np

# Normalizes any array to values between 0 and 1
def normalize_array(non_normal_array):

    min_val = np.amin(non_normal_array)
    max_val = np.amax(non_normal_array)

    return ( (non_normal_array - min_val) / (max_val - min_val) )

