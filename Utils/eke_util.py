##Usage: In the main code add from eke_util import *

smoothing_harmonics_num = 4
g0 = 9.801

import numpy as np
import xarray as xr
from os import path

def get_model_latitude ( file_in , file_dims ) :
    return file_in [ file_dims [ len ( file_dims ) - 2 ] ]

def get_model_longitude ( file_in , file_dims ) :
    return file_in [ file_dims [ len ( file_dims ) - 1 ] ]

def get_model_data_timestep ( file_heads , yyyymmddhh , ens_string , timestep , var_name ) :
    model_file  = xr.open_dataset ( file_heads [ 0 ] + str ( yyyymmddhh ) + ens_string + file_heads [ 1 ] )
    model_in    = model_file [ var_name ] [ timestep , : , : ]
    model_file.close ( )
    model_in_np = np.array ( model_in )
    return model_in_np

def get_model_eke_timestep ( u_file_heads , v_file_heads , yyyymmddhh , ens_string , timestep , interval ) :
    u_0    = get_model_data_timestep ( u_file_heads , yyyymmddhh , ens_string , timestep , 'u' )
    u_24   = get_model_data_timestep ( u_file_heads , yyyymmddhh , ens_string , timestep + interval , 'u' )
    u_diff = np.full ( len ( u_0 ) , np.nan , dtype=u_0.dtype )
    u_diff = u_24 - u_0
    v_0    = get_model_data_timestep ( v_file_heads , yyyymmddhh , ens_string , timestep , 'v' )
    v_24   = get_model_data_timestep ( v_file_heads , yyyymmddhh , ens_string , timestep + interval , 'v' )
    v_diff = np.full ( len ( v_0 ) , np.nan , dtype=v_0.dtype )
    v_diff = v_24 - v_0
    eke_0  = np.full ( len ( u_diff ) , np.nan , dtype=u_diff.dtype )
    eke_0  = 0.5 * ( u_diff * u_diff + v_diff * v_diff )
    return ( eke_0 )

def smooth_cli ( input_cli , harmonics ) :
    day_num = input_cli.shape [ 0 ]
    cli_fft = np.fft.rfft ( input_cli , axis=0 )
    cli_fft [ harmonics + 1 : day_num - harmonics - 1 , : , : ] = 0.
    output_cli = np.fft.irfft ( cli_fft , n=day_num , axis=0 )
    return ( output_cli )                  

def cal_anom ( raw_field , ymd_list , if_smooth ) :
    mmdd_list = [ ]
    for ymd in ymd_list :
        mmdd_now = ymd % 10000
        if mmdd_now not in mmdd_list :
            mmdd_list.append ( mmdd_now )
    mmdd_list.sort ( )
    data_mmdd_list = [ ]
    for mmdd_n in range ( len ( mmdd_list ) ) :
        data_mmdd_list.append ( [ ] )
    for ymd_n in range ( len ( ymd_list ) ) :
        mmdd_now = ymd_list [ ymd_n ] % 10000
        index = mmdd_list.index ( mmdd_now )
        data_mmdd_list [ index ].append ( ymd_n )
    cli_shape_list = list ( raw_field.shape )
    cli_shape_list [ 0 ] = len ( mmdd_list )
    cli_shape_tuple = tuple ( cli_shape_list )
    cli_field = np.full ( cli_shape_tuple , np.nan , dtype=raw_field.dtype )
    for mmdd_n in range ( len ( mmdd_list ) ) :
        cli_field [ mmdd_n , : , : ] = np.nanmean ( raw_field [ data_mmdd_list [ mmdd_n ] , : , : ] , axis=0 )
    cli_smooth = np.full ( cli_field.shape , np.nan , dtype=cli_field.dtype )
    if if_smooth :
        cli_smooth = smooth_cli ( cli_field , smoothing_harmonics_num )
    else :
        cli_smooth = cli_field
    del ( cli_field )
    anomaly_field = np.full ( raw_field.shape , np.nan , dtype=raw_field.dtype )
    for ymd_n in range ( len ( ymd_list ) ) :
        mmdd_now = ymd_list [ ymd_n ] % 10000
        index = mmdd_list.index ( mmdd_now )
        anomaly_field [ ymd_n , : , : ] = raw_field [ ymd_n , : , : ] - cli_smooth [ index , : , : ]
#    del ( raw_field )
#    del ( cli_smooth )
#    del ( mmdd_list )
#    del ( data_mmdd_list )
    return anomaly_field

def convert_ymdh_to_ymd_list ( ymdh_list ) :
    ymd_list = [ ]
    for ymdh_n in range ( len ( ymdh_list ) ) :
        yyyymmdd_now = ymdh_list [ ymdh_n ] // 100
        if yyyymmdd_now not in ymd_list :
            ymd_list.append ( yyyymmdd_now )
    return ymd_list
                        
def get_model_weekly_eke_anomaly ( u_file_heads , v_file_heads , ymdh_list , file_list , week_n , ensemble_total , if_multi_members , lat , lon , data_type , interval_per_24h , if_include_ic , if_smooth ) :
    ymd_list = convert_ymdh_to_ymd_list ( ymdh_list )
    eke_week_anomaly = np.full ( ( len ( ymd_list ) , 7 , len ( lat ) , len ( lon ) ) , np.nan , dtype=data_type )
    for day in range ( 7 ) :
        eke_day = np.full ( ( len ( ymd_list ) , 4 , ensemble_total , interval_per_24h , len ( lat ) , len ( lon ) ) , np.nan , dtype=data_type )
        for interval_n in range ( interval_per_24h ) :
            print ( week_n , day , interval_n )
            for ymdh_n in range ( len ( ymdh_list ) ) :
                yyyymmdd_now = ymdh_list [ ymdh_n ] // 100
                ymd_index = ymd_list.index ( yyyymmdd_now )
                hh = ymdh_list [ ymdh_n ] % 100
                hh_n = hh // ( 24 // interval_per_24h )
                if interval_per_24h > 1 :
                    timestep = ( week_n * 7 + day ) * interval_per_24h - hh_n + interval_n
                    # possible future development: use reanalysis data to replace model initial condition when model intial condition is unavailable
                    if not if_include_ic : timestep = timestep - 1
                else :
                    timestep = ( week_n * 7 + day ) * interval_per_24h + interval_n
                    # possible future development: use reanalysis data to replace model initial condition when model intial condition is unavailable
                    if ( not if_include_ic ) and hh == 0 : timestep = timestep - 1
                if timestep >= 0 :
                    for ens_n in range ( ensemble_total ) :
                        if if_multi_members : ens_string = "_e" + str ( ens_n ).zfill ( 2 )
                        else : ens_string = ""
                        eke_day [ ymd_index , hh_n , ens_n , interval_n , : , : ] = get_model_eke_timestep ( u_file_heads , v_file_heads , file_list [ ymdh_n ] , ens_string , timestep , interval_per_24h )
        eke_day_mean = np.nanmean ( eke_day , axis=(1,2,3) )
        eke_week_anomaly [ : , day , : , : ] = cal_anom ( eke_day_mean , ymd_list , if_smooth )
#    del ( eke_day_mean )
#    del ( eke_day )
    eke_week_anomaly_mean = np.nanmean ( eke_week_anomaly , axis=1 )
#    del ( eke_week_anomaly )
    return eke_week_anomaly_mean

def get_model_weekly_z500_anomaly ( z500_file_heads , var_name , ymdh_list , file_list , week_n , ensemble_total , if_multi_members , lat , lon , data_type , interval_per_24h , if_include_ic , if_smooth , if_daily_mean ) :
    ymd_list = convert_ymdh_to_ymd_list ( ymdh_list )
    z500_week_anomaly = np.full ( ( len ( ymd_list ) , 7 , len ( lat ) , len ( lon ) ) , np.nan , dtype=data_type )
    for day in range ( 7 ) :
        z500_day = np.full ( ( len ( ymd_list ) , 4 , ensemble_total , interval_per_24h , len ( lat ) , len ( lon ) ) , np.nan , dtype=data_type )
        for interval_n in range ( interval_per_24h ) :
            for ymdh_n in range ( len ( ymdh_list ) ) :
                yyyymmdd_now = ymdh_list [ ymdh_n ] // 100
                ymd_index = ymd_list.index ( yyyymmdd_now )
                hh = ymdh_list [ ymdh_n ] % 100
                hh_n = hh // ( 24 // interval_per_24h )
                if interval_per_24h > 1 :
                    timestep = ( week_n * 7 + day ) * interval_per_24h - hh_n + interval_n
                    # possible future development: use reanalysis data to replace model initial condition when model intial condition is unavailable
                    if not if_include_ic : timestep = timestep - 1
                else :
                    timestep = ( week_n * 7 + day ) * interval_per_24h + interval_n
                    # possible future development: use reanalysis data to replace model initial condition when model intial condition is unavailable
                    if ( not if_daily_mean ) and ( not if_include_ic ) and hh == 0 : timestep = timestep - 1
                if timestep >= 0 :
                    for ens_n in range ( ensemble_total ) :
                        if if_multi_members : ens_string = "_e" + str ( ens_n ).zfill ( 2 )
                        else : ens_string = ""
                        file_now = z500_file_heads [ 0 ] + str ( ymdh_list [ ymdh_n ] ) + ens_string + z500_file_heads [ 1 ]
                        if path.exists ( file_now ) :
                            z500_day [ ymd_index , hh_n , ens_n , interval_n , : , : ] = get_model_data_timestep ( z500_file_heads , file_list [ ymdh_n ] , ens_string , timestep , var_name )

        z500_day_mean = np.nanmean ( z500_day , axis=(1,2,3) )
        z500_week_anomaly [ : , day , : , : ] = cal_anom ( z500_day_mean , ymd_list , if_smooth )
#    del ( z500_day_mean )
#    del ( z500_day )
    z500_week_anomaly_mean = np.nanmean ( z500_week_anomaly , axis=1 )
#    del ( z500_week_anomaly )
    return z500_week_anomaly_mean

def get_ts_erai ( file_in , var_name , time_n , total_days , eari_timesteps_per_day ) :
    data = np.array ( file_in [ var_name ] [ time_n : time_n + total_days * eari_timesteps_per_day , : , : ] )
    data1 = np.array ( file_in [ var_name ] [ time_n : time_n + 1 , : , : ] )
    return data

def get_erai_weekly_eke_anomaly ( era_u_file , era_v_file, ymdh_list , week_n , lat , lon , data_type , interval_per_24h , if_daily_mean , if_smooth , eari_timesteps_per_day ) :
    ymd_list = convert_ymdh_to_ymd_list ( ymdh_list )
    ERA_u850_file = xr.open_dataset ( era_u_file )
    ERA_u_time_in  = ERA_u850_file [ 'time' ]
    ERA_u_yyyymmdd = np.array ( ERA_u_time_in.dt.year * 10000 + ERA_u_time_in.dt.month * 100 + ERA_u_time_in.dt.day )
    ERA_v850_file = xr.open_dataset ( era_v_file )
    ERA_v_time_in  = ERA_v850_file [ 'time' ]
    ERA_v_yyyymmdd = np.array ( ERA_v_time_in.dt.year * 10000 + ERA_v_time_in.dt.month * 100 + ERA_v_time_in.dt.day )
    u_ts = get_ts_erai ( ERA_u850_file , 'u' , 0 , 2 , eari_timesteps_per_day )
    eke_week_anomaly = np.full ( ( len ( ymd_list ) , 7 , len ( lat ) , len ( lon ) ) , np.nan , dtype=u_ts.dtype )
    for day in range ( 7 ) :
        eke_day = np.full ( ( len ( ymd_list ) , len ( lat ) , len ( lon ) ) , np.nan , dtype=eke_week_anomaly.dtype )
        for ymd_n in range ( len ( ymd_list ) ) :
            index = np.where ( ERA_u_yyyymmdd == ymd_list [ ymd_n ] ) [ 0 ] [ 0 ]
            u_ts = get_ts_erai ( ERA_u850_file , 'u' , index + ( week_n * 7 + day ) * eari_timesteps_per_day , 2 , eari_timesteps_per_day )
            index = np.where ( ERA_v_yyyymmdd == ymd_list [ ymd_n ] ) [ 0 ] [ 0 ]
            v_ts = get_ts_erai ( ERA_v850_file , 'v' , index + ( week_n * 7 + day ) * eari_timesteps_per_day , 2 , eari_timesteps_per_day )
            if if_daily_mean :
                u_diff = np.full ( u_ts [ 0 , : , : ].shape , np.nan , dtype=u_ts.dtype )
                u_diff = np.nanmean ( u_ts [ 0 : eari_timesteps_per_day , : , : ] , axis=0 ) - np.nanmean ( u_ts [ eari_timesteps_per_day : eari_timesteps_per_day * 2 , : , : ] , axis=0 )
                v_diff = np.full ( u_ts [ 0 , : , : ].shape , np.nan , dtype=v_ts.dtype )
                v_diff = np.nanmean ( v_ts [ 0 : eari_timesteps_per_day , : , : ] , axis=0 ) - np.nanmean ( v_ts [ eari_timesteps_per_day : eari_timesteps_per_day * 2 , : , : ] , axis=0 )
                eke_day [ ymd_n , : , : ] = 0.5 * ( u_diff * u_diff + v_diff * v_diff )
            else :
                u_diff = np.full ( u_ts [ : interval_per_24h , : , : ].shape , np.nan  , dtype=u_ts.dtype )
                v_diff = np.full ( v_ts [ : interval_per_24h , : , : ].shape , np.nan  , dtype=v_ts.dtype )
                for interval_n in range ( interval_per_24h ) :
                    u_diff [ interval_n , : , : ] = u_ts [ interval_n * ( eari_timesteps_per_day // interval_per_24h ) , : , : ] - u_ts [ interval_n * ( eari_timesteps_per_day // interval_per_24h ) + eari_timesteps_per_day , : , : ]
                    v_diff [ interval_n , : , : ] = v_ts [ interval_n * ( eari_timesteps_per_day // interval_per_24h ) , : , : ] - v_ts [ interval_n * ( eari_timesteps_per_day // interval_per_24h ) + eari_timesteps_per_day , : , : ]
                eke_day [ ymd_n , : , : ] = np.nanmean ( 0.5 * ( u_diff * u_diff + v_diff * v_diff ) , axis=0 )
        eke_week_anomaly [ : , day , : , : ] = cal_anom ( eke_day , ymd_list , if_smooth )
#    del ( eke_day )
    eke_week_anomaly_mean = np.nanmean ( eke_week_anomaly , axis=1 )
#    del ( eke_week_anomaly )
    ERA_u850_file.close ( )
    ERA_v850_file.close ( )
    return eke_week_anomaly_mean.astype ( data_type )

def get_erai_weekly_z500_anomaly ( era_z_file , ymdh_list , week_n , lat , lon , data_type , interval_per_24h , if_daily_mean , if_smooth , eari_timesteps_per_day ) :
    ymd_list = convert_ymdh_to_ymd_list ( ymdh_list )
    ERA_z500_file = xr.open_dataset ( era_z_file )
    ERA_z_time_in  = ERA_z500_file [ 'time' ]
    ERA_z_yyyymmdd = np.array ( ERA_z_time_in.dt.year * 10000 + ERA_z_time_in.dt.month * 100 + ERA_z_time_in.dt.day )
    z500_ts = get_ts_erai ( ERA_z500_file , 'z' , 0 , 1 , eari_timesteps_per_day )
    z500_week_anomaly = np.full ( ( len ( ymd_list ) , 7 , len ( lat ) , len ( lon ) ) , np.nan , dtype=z500_ts.dtype )
    for day in range ( 7 ) :
        z500_day = np.full ( ( len ( ymd_list ) , len ( lat ) , len ( lon ) ) , np.nan , dtype=z500_week_anomaly.dtype )
        for ymd_n in range ( len ( ymd_list ) ) :
            index = np.where ( ERA_z_yyyymmdd == ymd_list [ ymd_n ] ) [ 0 ] [ 0 ]
            z500_ts = get_ts_erai ( ERA_z500_file , 'z' , index + ( week_n * 7 + day ) * eari_timesteps_per_day , 1 , eari_timesteps_per_day )
            z500_day [ ymd_n , : , : ] = np.nanmean ( z500_ts , axis=0 )
        z500_week_anomaly [ : , day , : , : ] = cal_anom ( z500_day , ymd_list , if_smooth )
#    del ( z500_day )
    z500_week_anomaly_mean = np.nanmean ( z500_week_anomaly , axis=1 ) * ( 1. / g0 ) 
#    del ( z500_week_anomaly )
    ERA_z500_file.close ( )
    return z500_week_anomaly_mean.astype ( data_type )

def get_rmm_composite_list ( composite_phase_names , model_yyyymmdd , rmm_yyyymmdd , rmm_phase_in , rmm_amplitude_in , amplitude_threshold , start_month , end_month ) :
    rmm_list = [ ]
    for phase_n in range ( len ( composite_phase_names ) ) : rmm_list.append ( [ ] )
    if start_month > end_month :
        for time_step in range ( len ( model_yyyymmdd ) ) :
            month_now = model_yyyymmdd [ time_step ] // 100 % 100
            if month_now >= start_month or month_now <= end_month :
                time_n = np.where ( rmm_yyyymmdd == model_yyyymmdd [ time_step ] ) [ 0 ] [ 0 ]
                if rmm_amplitude_in [ time_n ] > amplitude_threshold :
                    rmm_list [ rmm_phase_in [ time_n ] // 2 % 4 ].append ( time_step )
    else :
        for time_step in range ( len ( model_yyyymmdd ) ) :
            month_now = model_yyyymmdd [ time_step ] // 100 % 100
            if month_now >= start_month and month_now <= end_month :
                time_n = np.where ( rmm_yyyymmdd == model_yyyymmdd [ time_step ] ) [ 0 ] [ 0 ]
                if rmm_amplitude_in [ time_n ] > amplitude_threshold :
                    rmm_list [ rmm_phase_in [ time_n ] // 2 % 4 ].append ( time_step )
    return rmm_list

def get_composite ( input_data , composite_index , start_week , end_week ) :
    return np.nanmean ( input_data [ composite_index , start_week - 1 : end_week , : , : ] , axis=(0,1) )

def get_season_list ( model_yyyymmdd , start_month , end_month ) :
    out_list = [ ]
    if start_month > end_month :
        for time_step in range ( len ( model_yyyymmdd ) ) :
            month_now = model_yyyymmdd [ time_step ] // 100 % 100
            if month_now >= start_month or month_now <= end_month :
                out_list.append ( time_step )
    else :
        for time_step in range ( len ( model_yyyymmdd ) ) :
            month_now = model_yyyymmdd [ time_step ] // 100 % 100
            if month_now >= start_month and month_now <= end_month :
                out_list.append ( time_step )
    return out_list

def test_sig_np ( data_season , data_composite , N_samples , m_cases ) :
    season_size = data_season.shape [ 0 ]
    data_distribution = np.full ( ( N_samples , data_season.shape [ 1 ] , data_season.shape [ 2 ] ) , np.nan , dtype=data_season.dtype )
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

def get_lat_north_south_index ( lat_south , lat_north , lat ) :
    if lat [ 1 ] > lat [ 0 ] : 
        lat_south_index = 0
        while lat [ lat_south_index ] < lat_south : lat_south_index = lat_south_index + 1
        lat_north_index = lat_south_index
        while lat_north_index < len ( lat ) and lat [ lat_north_index ] < lat_north : lat_north_index = lat_north_index + 1
        lat_north_index = lat_north_index - 1
        return ( lat_south_index , lat_north_index )
    else :
        lat_north_index = 0
        while lat [ lat_north_index ] > lat_north : lat_north_index = lat_north_index + 1
        lat_south_index = lat_north_index
        while lat_south_index < len ( lat ) and lat [ lat_south_index ] > lat_south : lat_south_index = lat_south_index + 1
        lat_south_index = lat_south_index - 1
        return ( lat_north_index , lat_south_index )

def calcPatCorr ( data1 , data2 , lat , lat_south , lat_north , lon , lon_west , lon_east ) :
    weights = get_weighted_field ( lat , lon )
    lon_list = [ ]
    if lon_west < lon_east :
        for lon_n in range ( len ( lon ) ) :
            if lon [ lon_n ] >= lon_west and lon [ lon_n ] <= lon_east : lon_list.append ( lon_n )
    else :
        for lon_n in range ( len ( lon ) ) :
            if lon [ lon_n ] >= lon_west or lon [ lon_n ] <= lon_east : lon_list.append ( lon_n )
#    if lat [ 1 ] > lat [ 0 ] : 
#        lat_south_index = 0
#        while lat [ lat_south_index ] < lat_south : lat_south_index = lat_south_index + 1
#        lat_north_index = lat_south_index
#        while lat_north_index < len ( lat ) and lat [ lat_north_index ] < lat_north : lat_north_index = lat_north_index + 1
#        lat_north_index = lat_north_index - 1
#        return weighted_corr ( data1 [ lat_south_index : lat_north_index , lon_list ] , data2 [ lat_south_index : lat_north_index , lon_list ] , weights [ lat_south_index : lat_north_index , lon_list ] )
#    else :
#        lat_north_index = 0
#        while lat [ lat_north_index ] > lat_north : lat_north_index = lat_north_index + 1
#        lat_south_index = lat_north_index
#        while lat_south_index < len ( lat ) and lat [ lat_south_index ] > lat_south : lat_south_index = lat_south_index + 1
#        lat_south_index = lat_south_index - 1
#        return weighted_corr ( data1 [ lat_north_index : lat_south_index , lon_list ] , data2 [ lat_north_index : lat_south_index , lon_list ] , weights [ lat_north_index : lat_south_index , lon_list ] )
    ( lat_south_index , lat_north_index ) = get_lat_north_south_index ( lat_south , lat_north , lat )
    return weighted_corr ( data1 [ lat_south_index : lat_north_index , lon_list ] , data2 [ lat_south_index : lat_north_index , lon_list ] , weights [ lat_south_index : lat_north_index , lon_list ] )

def plot_max_level ( levels , interval ) :
    return interval // 2 * ( levels * 2 + 1 )

def get_plot_level_spacing ( data , levels , lat_south , lat_north , lat ) :
    ( lat_south_index , lat_north_index ) = get_lat_north_south_index ( lat_south , lat_north , lat )
    plot_max = max ( abs ( data [ : , lat_south_index : lat_north_index ].max ( ) ) , abs ( data [ : , lat_south_index : lat_north_index ].min ( ) ) )
    interval = 2
    while plot_max_level ( levels , interval ) < plot_max :
        interval = interval + 2
    return interval

