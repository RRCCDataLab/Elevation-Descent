#
# MODULE FOR NAMING TRAINING, VALIDATION, AND MODEL DATA FILES
#
# Author: Cory Kennedy
#
# date: 07/11/2018


import datetime

def get_file_name(unique_code, more_info, filetype=None):
    '''
        example use: get_file_name('a0', 'lookoutMt', filetype='training_data')
                    returns: 'a0_trainingData_lookoutMt_Jul-11-2018.npy'

                    filetype keyword arguments include: 'training_data',
                                                'validation_data', and 'model'
    '''
    # 2 digit code for pairing a model with it's training/validation data
    month = datetime.date.today().strftime("%B")[0:3]
    day = datetime.date.today().strftime("%d")
    # make day 03 instead of 3
    if len(day) == 1: day = '0' + day
    year = datetime.date.today().strftime("%Y")
    date = month + '-' + day + '-' + year

    if filetype == 'training_data':
        data_type = 'trainingData'
        file_ext = '.npy'
    elif filetype == 'model':
        data_type = 'model'
        file_ext = '.h5'
    elif filetype == 'validation_data':
        data_type = 'validationData'
        file_ext = '.npy'
    elif filetype == None:
        raise Exception("filetype keyword must be specified:\n\t'training_data', 'validation_data', or 'model'")
    else:
        raise Exception("invalid filetype keyword")

    return "%s_%s_%s_%s%s" % (unique_code, data_type,
                            more_info, date, file_ext)

