##Usage: In the main code add from eke_util import *

import numpy as np
import xarray as xr

from fcst_utils import calcAnom

def convert_to_daily ( data , steps_per_day , total_days ) :
    if steps_per_day == 1 : return data
    else :
        data_daily = np.zeros ( ( total_days , data.shape [ 1 ] , data.shape [ 2 ] ) , dtype=data.dtype )
        for step in range ( steps_per_day ) :
            data_daily = data_daily + data [ step : steps_per_day * total_days : steps_per_day , : , : ]
        data_daily = data_daily * ( 1 / steps_per_day )
        return data_daily

def calcEke ( u , v , steps_per_day , total_days ) :
# step_per_day: how many time steps each day, for daily mean data step_per_day=1, 6-hourly data step_per_day=4
# input numpy arrays for u and v
    u_diff = np.empty ( ( ( total_days + 1 ) * steps_per_day , u.shape [ 1 ] , u.shape [ 2 ] ) , dtype=u.dtype )
    u_diff = u [ steps_per_day : ( total_days + 1 ) * steps_per_day , : , : ] - u [ : total_days * steps_per_day , : , : ]
    v_diff = np.empty ( ( ( total_days + 1 ) * steps_per_day , v.shape [ 1 ] , v.shape [ 2 ] ) , dtype=v.dtype )
    v_diff = v [ steps_per_day : ( total_days + 1 ) * steps_per_day , : , : ] - v [ : total_days * steps_per_day , : , : ]
    eke = np.empty ( ( total_days * steps_per_day , u.shape [ 1 ] , u.shape [ 2 ] ) , dtype=u.dtype )
    eke = 0.5 * ( u_diff * u_diff + v_diff * v_diff )
    if steps_per_day > 1 : return convert_to_daily ( eke , steps_per_day , total_days )
    else : return eke

def weighted_mean ( x , w ) :
    return np.sum ( x * w ) / np.sum ( w )
def weighted_cov ( x , y , w ) :
#    return np.sum ( w * ( x - weighted_mean ( x , w ) ) * ( y - weighted_mean ( y , w ) ) ) / np.sum ( w )
    return np.sum ( w * x * y ) / np.sum ( w )
def weighted_corr ( x , y , w ) :
    return weighted_cov ( x , y , w ) / np.sqrt ( weighted_cov ( x , x , w ) * weighted_cov ( y , y , w ) )

def get_weighted_field ( lat , lon ) :
    weight_field = np.empty ( ( len ( lat ) , len ( lon ) ) , dtype='float32' )
    for lat_n in range ( len ( lat ) ) : weight_field [ lat_n , : ] = np.cos ( lat [ lat_n ] * np.pi / 180 )
    return weight_field

def calcPatCorr ( data1 , data2 , lat , lat_south , lat_north , lon , lon_west , lon_east ) :
    weights = get_weighted_field ( lat , lon )
    lon_list = [ ]
    if lon_west < lon_east :
        for lon_n in range ( len ( lon ) ) :
            if lon [ lon_n ] >= lon_west and lon [ lon_n ] <= lon_east : lon_list.append ( lon_n )
    else :
        for lon_n in range ( len ( lon ) ) :
            if lon [ lon_n ] >= lon_west or lon [ lon_n ] <= lon_east : lon_list.append ( lon_n )
    if lat [ 1 ] > lat [ 0 ] : 
        lat_south_index = 0
        while lat [ lat_south_index ] < lat_south : lat_south_index = lat_south_index + 1
        lat_north_index = lat_south_index
        while lat_north_index < len ( lat ) and lat [ lat_north_index ] < lat_north : lat_north_index = lat_north_index + 1
        lat_north_index = lat_north_index - 1
        return weighted_corr ( data1 [ lat_south_index : lat_north_index , lon_list ] , data2 [ lat_south_index : lat_north_index , lon_list ] , weights [ lat_south_index : lat_north_index , lon_list ] )
    else :
        lat_north_index = 0
        while lat [ lat_north_index ] > lat_north : lat_north_index = lat_north_index + 1
        lat_south_index = lat_north_index
        while lat_south_index < len ( lat ) and lat [ lat_south_index ] > lat_south : lat_south_index = lat_south_index + 1
        lat_south_index = lat_south_index - 1
        return weighted_corr ( data1 [ lat_north_index : lat_south_index , lon_list ] , data2 [ lat_north_index : lat_south_index , lon_list ] , weights [ lat_north_index : lat_south_index , lon_list ] )
    
def get_season_list ( model_yyyymmdd , start_month , end_month ) :
    season_list = [ ]
    if start_month > end_month :
        for time_step in range ( len ( model_yyyymmdd ) ) :
            month_now = model_yyyymmdd [ time_step ] // 100 % 100
            if month_now >= start_month or month_now <= end_month :
                season_list.append ( time_step )
    else :
        for time_step in range ( len ( model_yyyymmdd ) ) :
            month_now = model_yyyymmdd [ time_step ] // 100 % 100
            if month_now >= start_month and month_now <= end_month :
                season_list.append ( time_step )

def get_rmm_composite_list ( composite_phase_names , model_yyyymmdd , rmm_yyyymmdd , rmm_phase_in , rmm_amplitude_in , amplitude_threshold , start_month , end_month ) :
    rmm_list = [ ]
    for phase_n in range ( len ( composite_phase_names ) ) : rmm_list.append ( [ ] )
    if start_month > end_month :
        for time_step in range ( len ( model_yyyymmdd ) ) :
            month_now = model_yyyymmdd [ time_step ] // 100 % 100
            if month_now >= start_month or month_now <= end_month :
                time_n = 0
                while rmm_yyyymmdd [ time_n ] < model_yyyymmdd [ time_step ] : time_n = time_n + 1
                if rmm_amplitude_in [ time_n ] > amplitude_threshold :
                    rmm_list [ rmm_phase_in [ time_n ] // 2 % 4 ].append ( time_step )
    else :
        for time_step in range ( len ( model_yyyymmdd ) ) :
            month_now = model_yyyymmdd [ time_step ] // 100 % 100
            if month_now >= start_month and month_now <= end_month :
                time_n = 0
                while rmm_yyyymmdd [ time_n ] < model_yyyymmdd [ time_step ] : time_n = time_n + 1
                if rmm_amplitude_in [ time_n ] > amplitude_threshold :
                    rmm_list [ rmm_phase_in [ time_n ] // 2 % 4 ].append ( time_step )
    return rmm_list

def get_all_anomalies ( data_in , time_name , time ) :
    data_xr = xr.DataArray ( data=data_in , dims=[ time_name , "forecast_time" , "latitude" , "longitude" ] )
    data_xr [ time_name ] = time
    data_xr.name = "variable"
    data_anomaly = np.empty ( data_in.shape , dtype=data_in.dtype )
    for forecast_n in range ( data_in.shape [ 1 ] ) :
        data_anomaly [ : , forecast_n , : , : ] = np.array ( calcAnom ( data_xr [ : , forecast_n , : , : ] , data_xr.name ) )
    return data_anomaly

def get_ts_one_forecast_model ( file_in , var_name , file_dims , time_n , ensemble_n ) :
    if file_dims == 4 : data = np.array ( file_in [ var_name ] [ time_n , : , : , : ] )
    elif file_dims == 5 : data = np.array ( file_in [ var_name ] [ time_n , ensemble_n , : , : , : ] )
    return data

def get_ts_ERA ( file_in , var_name , time_n , total_days , if_model_daily_mean , ERA_timesteps_per_day ) :
    data = np.array ( file_in [ var_name ] [ time_n : time_n + total_days * ERA_timesteps_per_day , : , : ] )
    if if_model_daily_mean and ERA_timesteps_per_day > 1 : return convert_to_daily ( data , ERA_timesteps_per_day , total_days )
    else : return data

def get_ensemble_size ( file_in , file_dims ) :
    if len ( file_dims ) == 4 : return 1
    elif len ( file_dims ) == 5 : return len ( ( file_in [ file_dims [ 1 ] ] ) )

def get_model_latitude ( file_in , file_dims ) :
    return file_in [ file_dims [ len ( file_dims ) - 2 ] ]

def get_model_longitude ( file_in , file_dims ) :
    return file_in [ file_dims [ len ( file_dims ) - 1 ] ]

def test_sig_np ( data_season , data_composite , N_samples , m_cases ) :
    # data_season shape: ( time , ... , ... )
    season_size = data_season.shape [ 0 ]
    data_distribution = np.empty ( ( N_samples , data_season.shape [ 1 ] , data_season.shape [ 2 ] ) , dtype=data_season.dtype )
    rng = np.random.default_rng ( )
    for n in range ( N_samples ) :
        random_numbers = rng.choice ( season_size , size=m_cases , replace=False )
        data_distribution [ n , : , : ] = np.nanmean ( data_season [ random_numbers , : , : ] , axis=0 )
    data_sort = np.sort ( data_distribution , axis=0 , kind='stable' )
    del ( data_distribution )
    data_sig = np.empty ( ( data_season.shape [ 1 ] , data_season.shape [ 2 ] ) , dtype=data_season.dtype )
    for i in range ( data_season.shape [ 1 ] ) :
        for j in range ( data_season.shape [ 2 ] ) :
            data_sig [ i , j ] = np.searchsorted ( data_sort [ : , i , j ] , data_composite [ i , j ] ) / N_samples
    return data_sig
