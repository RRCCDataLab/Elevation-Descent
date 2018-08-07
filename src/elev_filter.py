import numpy as np
import pylab as mp
import math as math
from scipy import stats
from scipy.interpolate import interp1d
from scipy import integrate
import warnings
warnings.simplefilter('ignore')

def elev_filter(pnts):

    time_sec = np.copy(pnts['time_rel'])
    speed_mph = np.copy(pnts['gpsspeed'])
    elevation_ft = np.copy(pnts['bilin_elev'])
    functional_class = [1]*len(time_sec)

    bin_size_ft = 100.0
    window_size_list = [5,7,5,5,5,5]
    while_accept_val_lst = [9,3,5,5,9,9]

    t_s = np.asarray(time_sec)
    spd_mph = np.asarray(speed_mph)
    elev_ft = np.asarray(elevation_ft)
    fc_ind = mp.find(np.equal(np.asarray(functional_class),None))
    func_class = np.asarray(functional_class)
    func_class[fc_ind] = 0
    wav_lst = np.zeros((len(t_s),1))
    for i in range(len(wav_lst)):
        wav_lst[i] = while_accept_val_lst[func_class[i]]

    dist_ft = 5280.0*integrate.cumtrapz( spd_mph, x=(t_s/3600.0) , initial=0)
    ## Down-sample the raw data at uniformly spaced points (by distance)
    dist_ft_uni, elev_ft_uni, func_class_uni, wav_lst_uni = get_uniform_data( dist_ft, elev_ft, func_class, wav_lst, bin_size_ft )

    ## Smooth the elevation profile
    elev_ft_uni_new, elev_ft_uni_new_adj = smoothing_filter(elev_ft_uni, func_class_uni, window_size_list, bin_size_ft)

    ## Discard and backfill outlier points
    while_cnt = 0
    retention_index_prev = np.asarray(range(len(elev_ft_uni_new_adj)))
    no_change = 0
    while np.any(np.greater(abs(np.diff(elev_ft_uni_new_adj)),wav_lst_uni[1:])) and no_change==0:
        while_cnt += 1
        test_values = np.diff(elev_ft_uni_new_adj)
        test_values = np.insert(test_values, 0, 0)
        retention_index = mp.find( np.greater(wav_lst_uni,abs(test_values)) )
        if retention_index[0] != 0:
            retention_index = np.insert(retention_index, 0, 0)
        if retention_index[-1] != len(elev_ft_uni_new_adj)-1:
            retention_index = np.append(retention_index, len(elev_ft_uni_new_adj)-1)

        retention_index = np.intersect1d(retention_index,retention_index_prev)
        if np.array_equal(retention_index,retention_index_prev):
            no_change=1
        retention_index_prev = np.copy(retention_index)

        elev_ft_func = interp1d( dist_ft_uni[retention_index], elev_ft_uni[retention_index], kind=1  )
        elev_ft_uni = elev_ft_func(dist_ft_uni)
        elev_ft_uni_new, elev_ft_uni_new_adj = smoothing_filter(elev_ft_uni, func_class_uni, window_size_list, bin_size_ft)

    ## Interpolate on the smoothed elevation profile at the original distance points
    if len(dist_ft_uni) > 1:
        new_elev_ft_func = interp1d( dist_ft_uni, elev_ft_uni_new, kind=1  )
        new_elev_ft = new_elev_ft_func(dist_ft)
    else:
        new_elev_ft  = elevation_ft
    new_grade = get_grade(dist_ft, new_elev_ft)
    pnts['bilin_elev'] = np.copy(new_elev_ft)
    pnts['bilin_grade_filter'] = np.copy(new_grade)

    # Calculate error (deviation) from old and new elevation series
    elev_filter_error = np.sum(np.absolute(new_elev_ft - elevation_ft))/len(elevation_ft)
    return pnts#, while_cnt, elev_filter_error


def get_uniform_data(*args):

    # internally define variables
    dist_old = args[0]
    elev_old = args[1]
    func_class_old = args[2]
    wav_lst_old = args[3]
    nom_dist_window = args[4]

    window_cnt = mp.ceil(max(dist_old)/nom_dist_window)
    act_dist_window = max(dist_old)/window_cnt

    dist_new = mp.linspace(0.0, dist_old[-1], window_cnt+1)
    elev_new = np.asarray([-1.0]*len(dist_new))
    func_class_new = np.zeros(len(dist_new)) - 1.0
    wav_lst_new = np.zeros(len(dist_new)) - 1.0

    for i in range(len(dist_new)):
        logical1 = dist_old >= (dist_new[i]-act_dist_window/2.0)
        logical2 = dist_old <= (dist_new[i]+act_dist_window/2.0)
        ind = mp.find( np.bitwise_and(logical1, logical2) )
        if len(ind) != 0:
            y0 = elev_old[ind]
            elev_new[i] = mp.median(y0)
            func_class_mode, func_class_mode_cnt = stats.mode( func_class_old[ind] )
            func_class_new[i] = np.copy(func_class_mode)
            wav_mode, wav_mode_cnt = stats.mode( wav_lst_old[ind] )
            wav_lst_new[i] = np.copy(wav_mode)

    elev_new[0] = 1.0*elev_old[0]
    elev_new[-1] = 1.0*elev_old[-1]

    ind = mp.find(elev_new != -1.0)
    if len(ind) > 1:
        elev_new_func = interp1d( dist_new[ind], elev_new[ind], kind=1 )
        elev_new = elev_new_func(dist_new)

    ind = mp.find(func_class_new != -1.0)
    if len(ind) > 1:
        fc_new_func = interp1d( dist_new[ind], func_class_new[ind], kind=0 )
        func_class_new = fc_new_func(dist_new)

    ind = mp.find(wav_lst_new != -1.0)
    if len(ind) > 1:
        wav_new_func = interp1d( dist_new[ind], wav_lst_new[ind], kind=0 )
        wav_lst_new = wav_new_func(dist_new)

    return dist_new, elev_new, func_class_new, wav_lst_new


def smoothing_filter(*args):

    # internally define variables
    speed = args[0]
    fc_lst = args[1]
    window_cnt_lst = args[2]
    bin_size_ft = args[3]

    ### hold initial and final values at start and end of arrays
    buffer_data0 = np.asarray([speed[0]]*((max(window_cnt_lst)-1)/2))
    buffer_data1 = np.asarray([speed[-1]]*((max(window_cnt_lst)-1)/2))
    speed = np.insert(speed, [0]*len(buffer_data0), buffer_data0)
    speed = np.append(speed, buffer_data1)

    speed_adjustment = np.zeros( len(speed) )

    buffer_data0 = np.asarray([fc_lst[0]]*((max(window_cnt_lst)-1)/2))
    buffer_data1 = np.asarray([fc_lst[-1]]*((max(window_cnt_lst)-1)/2))
    fc_lst = np.insert(fc_lst, [0]*len(buffer_data0), buffer_data0)
    fc_lst = np.append(fc_lst, buffer_data1)

    # identify segments to convolve
    fc_lst_diff = np.diff(fc_lst)
    interval_end = np.asarray(mp.find(fc_lst_diff != 0))
    interval_start = interval_end+1
    interval_end = np.append(interval_end, len(fc_lst)-1-(max(window_cnt_lst)-1)/2)
    interval_start = np.insert(interval_start, 0, (max(window_cnt_lst)-1)/2)

    for fa in range(len(interval_start)):
        window = np.array([window_cnt_lst[int(fc_lst[interval_start[fa]])]])-1
        speed_sub0 = np.copy( speed[int(interval_start[fa]-window/2):int(interval_end[fa]+1+window/2)] )

        # determine number of points for filtering
        n_points = np.arange(0, window + 1)
        binomial_coefficients = []
        for i in n_points: # calculate binomial filter coefficients
            binomial_coefficients.append(float(math.factorial(window)/
            (math.factorial(window-i)*math.factorial(i))))

        binomial_coefficients =  np.divide(binomial_coefficients,
                                           np.sum(binomial_coefficients))

        # Determine the Savitsky Golay Filter Coefficients assuming 3 order
        order_range = range(3+1)
        b = np.mat([[k**i for i in order_range] for k in range(-window/2, window/2+1)])
        m = np.linalg.pinv(b).A[0]

        # perform the SG convolution on the speed data
        speed_sub = np.convolve(m, speed_sub0, mode = 'valid')

        # now that we have the binomial filter coefficients we can convolve the
        # speed data with the filter to get binomial filter smoothed values
        speed_sub = np.convolve(binomial_coefficients, np.r_[ speed_sub0[0:int(window/2)] , speed_sub , speed_sub0[len(speed_sub0)-int(window/2):] ], mode = 'valid')

        ### insert filtered speed subsegment back into complete array
        speed[interval_start[fa]:interval_end[fa]+1] = np.copy(speed_sub)
        speed_adjustment[int(interval_start[fa]):int(interval_end[fa]+1)] = speed_sub0[int(window/2):int(-window/2)] - speed_sub

    ### adjust elevation at intersection of smoothed segments
    for fa in range(len(interval_start)-1):
        gr0 = (speed[interval_end[fa]]-speed[interval_end[fa]-1]) / bin_size_ft
        gr1 = (speed[interval_start[fa+1]+1]-speed[interval_start[fa+1]]) / bin_size_ft
        avg_grd = (gr0+gr1) / 2.0
        target_trans_elev = speed[interval_end[fa]] + avg_grd*bin_size_ft
        elev_adj = target_trans_elev - speed[interval_start[fa+1]]
        speed[interval_start[fa+1]:] = speed[interval_start[fa+1]:] + elev_adj

    ## Remove buffer data on either end of array
    buff_len = len(buffer_data0)
    speed = speed[buff_len:-buff_len]
    speed_adjustment = speed_adjustment[buff_len:-buff_len]

    return speed, speed_adjustment


def get_grade(dist_ft, elev_ft):
    d_dist = np.diff(dist_ft)
    d_elev = np.diff(elev_ft)
    grade = d_elev / d_dist
    grade = np.insert( grade, 0, 0 )
    grade = np.round( grade, decimals=4 )
    for a in range(len(grade)-1):
        if np.isinf(grade[a+1]) or np.isnan(grade[a+1]):
            grade[a+1] = grade[a]

    return grade
