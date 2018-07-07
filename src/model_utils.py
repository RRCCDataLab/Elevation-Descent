#
# A SIMPLE MODULE FOR COMPARING ELEVATION ATTRIBUTES ACROSS MODELS:
# built more specifically for evaluating the accuracy of elevation models
#
# Author: Cory Kennedy
#
# Date: 6/28/18

# NOTE code has potential for possible efficiency improvements


import numpy as np
import pandas as pd

def get_index_or_column(df_of_interest, axis=0, **kwargs):
    '''
    Keyword argument axis= (0 or 1) is used to specify wether column or index
    values are returned.
    
    Default is axis=0

    Returns a numpy array of float values
    '''
    if axis == 0 :
        return df_of_interest.index.values
    elif axis == 1 :
        return df_of_interest.columns.values.astype(float)

def get_index_and_column(df_of_interest):
    '''
    Takes a pandas DataFrame as an argument.
    
    Returns the index and column array, (in that order,)
    as numpy arrays of float values
    '''
    index_array = get_index_or_column(df_of_interest, axis=0)
    column_array = get_index_or_column(df_of_interest, axis=1)

    return index_array, column_array


def get_nearest_index(array, value):
    return (np.abs(array - value)).argmin()

def get_nearest_value_in_df(df_of_interest, index_val, col_val):
    nearest_index = get_nearest_index(df_of_interest.index.values, index_val)
    nearest_column = get_nearest_index(df_of_interest.columns.values.astype(float), col_val)
    return df_of_interest.iloc[nearest_index, nearest_column]

def is_sorted(array_of_interest):
    for element in range(array_of_interest - 1):
        if array_of_interest[element + 1] < array_of_interest[element] :
            return False
        else:
            return True

def is_in_bounds(df_of_interest, index_val, column_val):
    index_array = df_of_interest.index.values
    column_array = df_of_interest.columns.values.astype(float)
    # check if both arrays are sorted
    if ( is_sorted(index_array) and is_sorted(column_array) ) :
        # check for values of interest outside the bounds of the index/column arrays
        if (index_val < np.amin(index_array) or
            index_val > np.amax(index_array) or
            column_val < np.amin(column_array) or
            column_val > np.amax(column_array)):
            return False
        else:
            return True

def get_df_difference_as_df(minuend_df, subtrahend_df):
    '''Argument 1 (minuend DataFrame) should be the baseline pandas DataFrame,
    to which argument 2 (subtrahend DataFrame) is being compared.

    minuend - subtrahend = difference

    Returns a DataFrame of the difference values, in the shape of the
    subtrahend DataFrame.

    NOTE:
        Any values from the subtrahend DataFrame, not within the index/column domain of
        the minuend DataFrame, will not be difference.
    
        All subtrahend values not coincident will be differenced to its nearest minuend neighbor.
    '''
    # store index and column arrays of subtrahend DataFrame
    index_array, column_array = get_index_and_column(subtrahend_df)

    # create an empty DataFrame for storing differences
    differences = pd.DataFrame(index=index_array, columns=column_array)

    # iterate through subtrahend DataFrame
    for column_val in column_array:
        for index_val in index_array:
            subtrahend_val = subtrahend_df.loc[index_val, column_val]
            minuend_val = get_nearest_value_in_df(minuend_df, index_val, column_val)
            #store the difference in it's place within the differences DataFrame
            difference = minuend_val - subtrahend_val
            differences.loc[index_val, column_val] = difference

    return differences


