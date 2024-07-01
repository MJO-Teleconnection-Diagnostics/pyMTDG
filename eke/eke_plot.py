import xarray as xr
import numpy as np
import netCDF4
import spharm

import matplotlib.pyplot as plt
import proplot as plot
from matplotlib.markers import MarkerStyle

import glob
import os

import yaml

import sys
sys.path.insert ( 0 , '../Utils' )

from eke_util import get_model_latitude
from eke_util import get_model_longitude
from eke_util import get_model_weekly_eke_anomaly
from eke_util import get_reanalysis_weekly_eke_anomaly
from eke_util import get_model_weekly_z500_anomaly
from eke_util import get_reanalysis_weekly_z500_anomaly
from eke_util import get_z500_varname
from eke_util import get_u850_varname
from eke_util import get_v850_varname
from eke_util import if_convert_z500_unit
from eke_util import convert_ymdh_to_ymd_list
from eke_util import get_rmm_composite_list
from eke_util import get_composite
from eke_util import get_season_list
from eke_util import test_sig_np
from eke_util import calcPatCorr
from eke_util import get_plot_level_spacing
from eke_util import plot_max_level
from eke_util import plotComposites
from fcst_utils import write_output_text

###### Input from yml file ( UFS )
with open ( '../driver/config.yml' , 'r' ) as file:
    yml_input = yaml.safe_load ( file )

Model_name                   = yml_input [ 'model name' ]
Ensemble_size                = int ( yml_input [ 'Number of ensembles' ] )
Daily_Mean_Data              = yml_input [ 'model data daily-mean values' ]
Forecast_time_step_interval  = yml_input [ 'forecast time step' ]
Model_data_initial_condition = yml_input [ 'model initial conditions' ]
Smooth_climatology           = yml_input [ 'smooth climatology' ]
ERAI                         = yml_input [ 'ERAI' ]
RMM                          = yml_input [ 'RMM' ]

Model_u850_files             = yml_input [ 'Path to zonal wind at 850 hPa model data files' ]
Model_v850_files             = yml_input [ 'Path to meridional wind at 850 hPa model data files' ]
Model_z500_files             = yml_input [ 'Path to Z500 model data files for EKE' ]

###### Input from yml file (UFS)
#ERAI = True
#RMM  = True
#Model_name = "UFS5"
#Multiple_Ensemble_Members    = False
#Ensemble_size                = 1
#Daily_Mean_Data              = False
#Forecast_time_step_interval  = 6
#Model_data_initial_condition = True
#Smooth_climatology           = False
#ERAI                         = True
if (yml_input['ERAI']==True):
    reanalysis_u850_file=yml_input['DIR_IN']+'/mjo_teleconnections_data/erai/uv850/u850.19790101-20190831.nc'
    reanalysis_v850_file=yml_input['DIR_IN']+'/mjo_teleconnections_data/erai/uv850/v850.19790101-20190831.nc'
    reanalysis_z500_file=yml_input['DIR_IN']+'/mjo_teleconnections_data/erai/z500/z500.19790101-20190831.nc'
    ds_obs_name='ERAI'
if (yml_input['ERAI']==False):
    reanalysis_u850_file=yml_input['Path to zonal wind at 850 hPa observation data files']
    reanalysis_v850_file=yml_input['Path to meridional wind at 850 hPa observation data files']
    reanalysis_z500_file=yml_input['Path to Z500 observation data files for EKE']
    ds_obs_name='OBS'

#if ERAI :
#    Reanalysis_name = "ERA-I"
#    reanalysis_u850_file = "/data0/czheng/S2S-UFS/ERA-Interim/uv_850_1979-2019_1.5.nc"
#    reanalysis_v850_file = "/data0/czheng/S2S-UFS/ERA-Interim/uv_850_1979-2019_1.5.nc"
#    reanalysis_z500_file = "/data0/czheng/S2S-UFS/ERA-Interim/geopotential500_1979-2019_1.5.nc"
#    ERA_u850_file = "/data0/czheng/S2S-UFS/ERA-I_0.75/u850.19790101-20190831.nc"
#    ERA_v850_file = "/data0/czheng/S2S-UFS/ERA-I_0.75/v850.19790101-20190831.nc"
#    ERA_z500_file = "/data0/czheng/S2S-UFS/ERA-I_0.75/z500.19790101-20190831.nc"

#Model_u850_files = [ "/data0/czheng/S2S-UFS/data/6hourly/Prototype5/u_850-isobaricInhPa/u.850-isobaricInhPa.*.6hourly.nc" ]
#Model_v850_files = [ "/data0/czheng/S2S-UFS/data/6hourly/Prototype5/v_850-isobaricInhPa/v.850-isobaricInhPa.*.6hourly.nc" ]
#Model_z500_files = [ "/data0/czheng/S2S-UFS/data/6hourly/Prototype5/gh_500-isobaricInhPa/gh.500-isobaricInhPa.*.6hourly.nc" ]
#Model_u850_files = [ "/data0/czheng/S2S-UFS/data/code/0.25/Prototype5/u.850-isobaricInhPa.*.f000-840.nc" ]
#Model_v850_files = [ "/data0/czheng/S2S-UFS/data/code/0.25/Prototype5/v.850-isobaricInhPa.*.f000-840.nc" ]
#Model_z500_files = [ "/data0/czheng/S2S-UFS/data/code/0.25/Prototype5/gh.500-isobaricInhPa.*.f000-840.nc" ]
#Model_u850_files = [ "/data0/czheng/S2S-UFS/data/code/e00/Prototype5/u_850-isobaricInhPa/u.850-isobaricInhPa.*.nc" ]
#Model_v850_files = [ "/data0/czheng/S2S-UFS/data/code/e00/Prototype5/v_850-isobaricInhPa/v.850-isobaricInhPa.*.nc" ]
#Model_z500_files = [ "/data0/czheng/S2S-UFS/data/code/e00/Prototype5/gh_500-isobaricInhPa/gh.500-isobaricInhPa.*.nc" ]
#Model_z500_varname = "z"
#Model_z500_varname = "gh"

if not RMM :
    #RMM_ERA_file = "/data0/czheng/S2S-UFS/ERA-Interim/rmm/rmm_ERA-Interim.nc"
    RMM_ERA_file=yml_input['DIR_IN']+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'
 

plot_dir = "../output/ET_Cyclone/" + Model_name + "/"
if not os.path.isdir ( plot_dir ) :
    os.mkdir ( plot_dir )

###### Input from yml file (CFSv2)
#Multiple_Ensemble_Members    = False
#Ensemble_size                = 1
#Daily_Mean_Data              = False
#Forecast_time_step_interval  = 6
#Model_data_initial_condition = False
#Smooth_climatology           = False
#ERAI                         = True
#ERA_u850_file = "/data0/czheng/S2S-UFS/ERA-Interim/uv_850_1979-2019_1.5.nc"
#ERA_v850_file = "/data0/czheng/S2S-UFS/ERA-Interim/uv_850_1979-2019_1.5.nc"
#ERA_z500_file = "/data0/czheng/S2S-UFS/ERA-Interim/geopotential500_1979-2019_1.5.nc"

#Model_u850_files = "/data0/czheng/CFSv2/wnd850/wnd850.*.regrid.nc4"
#Model_v850_files = "/data0/czheng/CFSv2/wnd850/wnd850.*.regrid.nc4"
#Model_z500_files = "/data0/czheng/CFSv2/z500/z500.*.regrid.nc4"
#Model_z500_varname = "gh"

#RMM_ERA_file = "/data0/czheng/S2S-UFS/ERA-Interim/rmm/rmm_ERA-Interim.nc"

#plot_dir = ""

###### Input from yml file (ECMWF)
#Multiple_Ensemble_Members    = True
#Ensemble_size                = 11
#Daily_Mean_Data              = False
#Forecast_time_step_interval  = 24
#Model_data_initial_condition = True
#Smooth_climatology           = False
#ERAI                         = True
#ERA_u850_file = "/data0/czheng/S2S-UFS/ERA-Interim/uv_850_1979-2019_1.5.nc"
#ERA_v850_file = "/data0/czheng/S2S-UFS/ERA-Interim/uv_850_1979-2019_1.5.nc"
#ERA_z500_file = "/data0/czheng/S2S-UFS/ERA-Interim/geopotential500_1979-2019_1.5.nc"

#Model_u850_files = "/data0/czheng/ECMWF/ECMWF_u_*.nc"
#Model_v850_files = "/data0/czheng/ECMWF/ECMWF_v_*.nc"
#Model_z500_files = "/data0/czheng/ECMWF/ECMWF_z_*.nc"
#Model_z500_varname = "gh"

#RMM_ERA_file = "/data0/czheng/S2S-UFS/ERA-Interim/rmm/rmm_ERA-Interim.nc"

###### Pre-set parameters
total_weeks = 4
composite_start_month = 11
composite_end_month   = 3
composite_start_week = 3
composite_end_week = 4
compoiste_amplitude_threshold = 1.
phase_names = [ "8-1" , "2-3" , "4-5" , "6-7" ]
bootstrap_size = 1000
test_confidence_level = 0.05
pattern_corr_north = 80.
pattern_corr_south = 20.

reanalysis_timesteps_per_day = 4

pattern_corr_regions = [ "Northern Hemisphere" , "North Pacific + North America" , "North Atlantic" ]
regions_south_north  = [ [ 20 , 80 ]           , [ 20 , 80 ]                     , [ 20 , 80 ]      ]
regions_west_east    = [ [ 0 , 360 ]           , [ 120 , 270 ]                   , [ 270 , 30 ]     ]

###### Check parameter settings
if Daily_Mean_Data :
    Forecast_time_step_interval = 24
if not ( Forecast_time_step_interval == 6 or Forecast_time_step_interval == 24 ) :
    print ( "error in Forecast_time_step_interval=" + str ( Forecast_time_step_interval ) + ", the eke calculation only support 6 or 24 hours interval now" )
    exit ( )
else :
    time_step_per_24h = 24 // Forecast_time_step_interval
#if Ensemble_size == 1 : Multiple_Ensemble_Members = False
#else: Multiple_Ensemble_Members = True

###### Get Reanalysis lat,lon
reanalysis_u850_file_in = xr.open_dataset ( reanalysis_u850_file )
reanalysis_u850_varname = get_u850_varname ( reanalysis_u850_file_in )
reanalysis_u850_in = reanalysis_u850_file_in [ reanalysis_u850_varname ] [ 4 , : , : ]
reanalysis_u850_in_dim = reanalysis_u850_in.dims
del ( reanalysis_u850_in )
reanalysis_lat_in = get_model_latitude ( reanalysis_u850_file_in , reanalysis_u850_in_dim )
reanalysis_lon_in = get_model_longitude ( reanalysis_u850_file_in , reanalysis_u850_in_dim )
reanalysis_u850_file_in.close ( )
delta_reanalysis_lat = reanalysis_lat_in [ 1 ] - reanalysis_lat_in [ 0 ]
delta_reanalysis_lon = reanalysis_lon_in [ 1 ] - reanalysis_lon_in [ 0 ]
dim_reanalysis_lat = len ( reanalysis_lat_in )
dim_reanalysis_lon = len ( reanalysis_lon_in )

reanalysis_v850_file_in = xr.open_dataset ( reanalysis_v850_file )
reanalysis_v850_varname = get_v850_varname ( reanalysis_v850_file_in )
reanalysis_v850_file_in.close ( )
reanalysis_z500_file_in = xr.open_dataset ( reanalysis_z500_file )
reanalysis_z500_varname = get_z500_varname ( reanalysis_z500_file_in )
reanalysis_z500_in = reanalysis_z500_file_in [ reanalysis_z500_varname ] [ 4 , : , : ]
CONVERT_REANALYSIS_Z500_UNIT = if_convert_z500_unit ( reanalysis_z500_in )
del ( reanalysis_z500_in )
reanalysis_z500_file_in.close ( )

###### Read model u,v data
model_u_file_list = glob.glob ( Model_u850_files )
model_u_file_list.sort ( )
yyyymmddhh_list = [ ]
u_files_head = Model_u850_files.split ( "*" , 1 )
file_yyyymmddhh_str1 = model_u_file_list [ 0 ].replace ( u_files_head [ 0 ] , "" )
file_yyyymmddhh_str2 = file_yyyymmddhh_str1.replace ( u_files_head [ 1 ] , "" )
file_yyyymmddhh_str  = file_yyyymmddhh_str2.split ( "_" , 1 )
if len ( file_yyyymmddhh_str [ 0 ] ) == 10 : INCLUDE_HOUR = True
elif len ( file_yyyymmddhh_str [ 0 ] ) == 8 : INCLUDE_HOUR = False
else :
    print ( "error in " + model_u_file_list [ 0 ] + " format not matching yyyymmddhh or yyyymmddhh_exx" )
if INCLUDE_HOUR:
    for file_n in model_u_file_list :
        file_yyyymmddhh_str1 = file_n.replace ( u_files_head [ 0 ] , "" )
        file_yyyymmddhh_str2 = file_yyyymmddhh_str1.replace ( u_files_head [ 1 ] , "" )
        file_yyyymmddhh_str  = file_yyyymmddhh_str2.split ( "_" , 1 )
        if len ( file_yyyymmddhh_str [ 0 ] ) == 10 :
            yyyymmddhh_integer = int ( file_yyyymmddhh_str [ 0 ] )
            mm = yyyymmddhh_integer // 10000 % 100
            if mm > 12 :
                print ( "error in file:" + file_n + " month=" + str ( mm ) )
                exit ( )
            dd = yyyymmddhh_integer // 100 % 100
            if dd > 31 :
                print ( "error in file:" + file_n + " day=" + str ( dd ) )
                exit ( )
            hh = yyyymmddhh_integer % 100
            if hh > 18 or hh % 6 != 0 :
                print ( "error in file:" + file_n + " only support 00, 06, 12 and 18 for initial hours" )
                exit ( )
            if yyyymmddhh_integer not in yyyymmddhh_list :
                yyyymmddhh_list.append ( yyyymmddhh_integer )
        else:
            print ( "error in " + file_n + " format not matching yyyymmddhh or yyyymmddhh_exx" )
else :
    for file_n in model_u_file_list :
        file_yyyymmddhh_str1 = file_n.replace ( u_files_head [ 0 ] , "" )
        file_yyyymmddhh_str2 = file_yyyymmddhh_str1.replace ( u_files_head [ 1 ] , "" )
        file_yyyymmddhh_str  = file_yyyymmddhh_str2.split ( "_" , 1 )
        if len ( file_yyyymmddhh_str [ 0 ] ) == 8 :
            yyyymmddhh_integer = int ( file_yyyymmddhh_str [ 0 ] )
            mm = yyyymmddhh_integer // 100 % 100
            if mm > 12 :
                print ( "error in file:" + file_n + " month=" + str ( mm ) )
                exit ( )
            dd = yyyymmddhh_integer % 100
            if dd > 31 :
                print ( "error in file:" + file_n + " day=" + str ( dd ) )
                exit ( )
            yyyymmddhh_integer = yyyymmddhh_integer * 100
            if yyyymmddhh_integer not in yyyymmddhh_list :
                yyyymmddhh_list.append ( yyyymmddhh_integer )
        else:
            print ( "error in " + file_n + " format not matching yyyymmdd or yyyymmdd_exx" )

yyyymmddhh_list.sort ( )
yyyymmdd_list = convert_ymdh_to_ymd_list ( yyyymmddhh_list )
if INCLUDE_HOUR : files_dates_list = yyyymmddhh_list
else : files_dates_list = yyyymmdd_list
v_files_head = Model_v850_files.split ( "*" , 1 )

######read the first model u file to get lat and lon dimension
#if Multiple_Ensemble_Members : ens_string = "_e00"
#else : ens_string = ""
ens_string = "_e00"
model_u850_file0 = xr.open_dataset ( u_files_head [ 0 ] + str ( files_dates_list [ 0 ] ) + ens_string + u_files_head [ 1 ] )
Model_u850_varname = get_u850_varname ( model_u850_file0 )
model_u850_in = model_u850_file0 [ Model_u850_varname ]
model_u850_in_dim = model_u850_in.dims
model_lat_in = get_model_latitude ( model_u850_file0 , model_u850_in_dim )
model_lon_in = get_model_longitude ( model_u850_file0 , model_u850_in_dim )
model_u850_file0.close ( )
model_input_u = np.array ( model_u850_in )
model_v850_file0 = xr.open_dataset ( v_files_head [ 0 ] + str ( files_dates_list [ 0 ] ) + ens_string + v_files_head [ 1 ] )
Model_v850_varname = get_v850_varname ( model_v850_file0 )
model_v850_file0.close ( )

######regrid set-up
delta_model_lat = model_lat_in [ 1 ] - model_lat_in [ 0 ]
delta_model_lon = model_lon_in [ 1 ] - model_lon_in [ 0 ]
dim_model_lat = len ( model_lat_in )
dim_model_lon = len ( model_lon_in )
REGRID_MODEL = False
REGRID_REANALYSIS = False
if dim_model_lat > dim_reanalysis_lat :
    REGRID_MODEL = True
elif dim_model_lat < dim_reanalysis_lat :
    REGRID_REANALYSIS = True
else:
    if dim_model_lon > dim_reanalysis_lon :
        REGRID_MODEL = True
    elif dim_model_lon < dim_reanalysis_lon :
        REGRID_REANALYSIS = True
if delta_model_lat * delta_reanalysis_lat < 0 : REVERSE_REANALYSIS_LAT = True
else : REVERSE_REANALYSIS_LAT = False
if REGRID_MODEL :
    ingrid = spharm.Spharmt ( len ( model_lon_in ) , len ( model_lat_in ) , gridtype='regular' )
    outgrid = spharm.Spharmt ( len ( reanalysis_lon_in ) , len ( reanalysis_lat_in ) , gridtype='regular' )
    data_lat_in = reanalysis_lat_in
    data_lon_in = reanalysis_lon_in
else:
    ingrid = spharm.Spharmt ( len ( reanalysis_lon_in ) , len ( reanalysis_lat_in ) , gridtype='regular' )
    outgrid = spharm.Spharmt ( len ( model_lon_in ) , len ( model_lat_in ) , gridtype='regular' )
    data_lat_in = model_lat_in
    data_lon_in = model_lon_in

######read model u,v data and calculate eke anomaly
model_eke850_forecast_anomaly = np.full ( ( len ( yyyymmdd_list ) , total_weeks , len ( data_lat_in ) , len ( data_lon_in ) ) , np.nan , dtype=model_input_u.dtype )
del ( model_input_u )
del ( model_u850_in )
for week_n in range ( total_weeks ) :
    model_eke850_forecast_anomaly [ : , week_n , : , : ] = get_model_weekly_eke_anomaly ( u_files_head , v_files_head , Model_u850_varname , Model_v850_varname , yyyymmddhh_list , files_dates_list , week_n , Ensemble_size , data_lat_in , data_lon_in , model_eke850_forecast_anomaly.dtype , time_step_per_24h , Model_data_initial_condition , Smooth_climatology , REGRID_MODEL , ingrid , outgrid )

###### Read model z500 data
#potential issue with data type of z500,uv850
#potential issue with missing files in uv850 or z500
#potential issue with data frequency (6hourly vs daily mean) of z500,uv850
z_files_head = Model_z500_files.split ( "*" , 1 )
ens_string = "_e00"
model_z500_file0 = xr.open_dataset ( z_files_head [ 0 ] + str ( files_dates_list [ 0 ] ) + ens_string + z_files_head [ 1 ] )
Model_z500_varname = get_z500_varname ( model_z500_file0 )
model_z500_in = model_z500_file0 [ Model_z500_varname ]
CONVERT_MODEL_Z500_UNIT = if_convert_z500_unit ( model_z500_in )
model_z500_file0.close ( )
model_input_z = np.array ( model_z500_in )
model_z500_forecast_anomaly = np.full ( ( len ( yyyymmdd_list ) , total_weeks , len ( data_lat_in ) , len ( data_lon_in ) ) , np.nan , dtype=model_input_z.dtype )
del ( model_input_z )
del ( model_z500_in )
for week_n in range ( total_weeks ) :
    model_z500_forecast_anomaly [ : , week_n , : , : ] = get_model_weekly_z500_anomaly ( z_files_head , Model_z500_varname , yyyymmddhh_list , files_dates_list , week_n , Ensemble_size , data_lat_in , data_lon_in , model_z500_forecast_anomaly.dtype , time_step_per_24h , Model_data_initial_condition , Smooth_climatology , Daily_Mean_Data , REGRID_MODEL , ingrid , outgrid , CONVERT_MODEL_Z500_UNIT )

##### read reanalysis data for eke
#potential issue with data type of erai/reanalysis
reanlaysis_eke850_forecast_anomaly = np.full ( ( len ( yyyymmdd_list ) , total_weeks , len ( data_lat_in ) , len ( data_lon_in ) ) , np.nan , dtype=model_eke850_forecast_anomaly.dtype )
reanlaysis_z500_forecast_anomaly = np.full ( ( len ( yyyymmdd_list ) , total_weeks , len ( data_lat_in ) , len ( data_lon_in ) ) , np.nan , dtype=model_z500_forecast_anomaly.dtype )
for week_n in range ( total_weeks ) :
    reanlaysis_eke850_forecast_anomaly [ : , week_n , : , : ] = get_reanalysis_weekly_eke_anomaly ( reanalysis_u850_file , reanalysis_v850_file , reanalysis_u850_varname , reanalysis_v850_varname , yyyymmddhh_list , week_n , data_lat_in , data_lon_in , model_eke850_forecast_anomaly.dtype , time_step_per_24h , Daily_Mean_Data , Smooth_climatology , reanalysis_timesteps_per_day , REGRID_REANALYSIS , ingrid , outgrid , REVERSE_REANALYSIS_LAT )
    reanlaysis_z500_forecast_anomaly [ : , week_n , : , : ] = get_reanalysis_weekly_z500_anomaly ( reanalysis_z500_file , reanalysis_z500_varname , yyyymmddhh_list , week_n , data_lat_in , data_lon_in , model_z500_forecast_anomaly.dtype , time_step_per_24h , Daily_Mean_Data , Smooth_climatology , reanalysis_timesteps_per_day , REGRID_REANALYSIS , ingrid , outgrid , REVERSE_REANALYSIS_LAT , CONVERT_REANALYSIS_Z500_UNIT )

##### read rmm index
rmm_file = xr.open_dataset ( RMM_ERA_file )
rmm_time_in = rmm_file [ 'time' ]
#tvalue = netCDF4.num2date ( rmm_time_in , rmm_time_in.units )
tvalue = netCDF4.num2date ( rmm_time_in , rmm_time_in.units.replace ( "after" , "since" ) )
#rmm_yyyymmdd = np.array ( rmm_time_in.dt.year * 10000 + rmm_time_in.dt.month * 100 + rmm_time_in.dt.day )
rmm_yyyymmdd = np.full ( len ( rmm_time_in ) , np.nan , dtype='int64' )
for time_n in range ( len ( rmm_time_in ) ) : rmm_yyyymmdd [ time_n ] = tvalue [ time_n ].year * 10000 + tvalue [ time_n ].month * 100 + tvalue [ time_n ].day
rmm_phase_in = np.full ( len ( rmm_time_in ) , np.nan , dtype='int64' )
for time_n in range ( len ( rmm_time_in ) ) : rmm_phase_in [ time_n ] = int ( rmm_file [ 'phase' ] [ time_n ] )
rmm_amplitude_in = np.array ( rmm_file [ 'amplitude' ] )
rmm_file.close ( )
rmm_list = get_rmm_composite_list ( phase_names , yyyymmdd_list , rmm_yyyymmdd , rmm_phase_in , rmm_amplitude_in , compoiste_amplitude_threshold , composite_start_month , composite_end_month )

##### make composites
model_eke850_composite = np.full ( ( len ( phase_names ) , len ( data_lat_in ) , len ( data_lon_in ) ) , np.nan , dtype=model_eke850_forecast_anomaly.dtype )
model_z500_composite = np.full ( ( len ( phase_names ) , len ( data_lat_in ) , len ( data_lon_in ) ) , np.nan , dtype=model_z500_forecast_anomaly.dtype )
reanalysis_eke850_composite = np.full ( ( len ( phase_names ) , len ( data_lat_in ) , len ( data_lon_in ) ) , np.nan , dtype=reanlaysis_eke850_forecast_anomaly.dtype )
reanalysis_z500_composite = np.full ( ( len ( phase_names ) , len ( data_lat_in ) , len ( data_lon_in ) ) , np.nan , dtype=reanlaysis_z500_forecast_anomaly.dtype )
for phase_n in range ( len ( phase_names ) ) :
    model_eke850_composite [ phase_n , : , : ]      = get_composite ( model_eke850_forecast_anomaly , rmm_list [ phase_n ] , composite_start_week , composite_end_week )
    model_z500_composite [ phase_n , : , : ]        = get_composite ( model_z500_forecast_anomaly , rmm_list [ phase_n ] , composite_start_week , composite_end_week )
    reanalysis_eke850_composite [ phase_n , : , : ] = get_composite ( reanlaysis_eke850_forecast_anomaly , rmm_list [ phase_n ] , composite_start_week , composite_end_week )
    reanalysis_z500_composite [ phase_n , : , : ]   = get_composite ( reanlaysis_z500_forecast_anomaly , rmm_list [ phase_n ] , composite_start_week , composite_end_week )

##### test significance
season_list = get_season_list ( yyyymmdd_list , composite_start_month , composite_end_month )
model_eke850_season = np.nanmean ( model_eke850_forecast_anomaly [ season_list , composite_start_week - 1 : composite_end_week , : , : ] , axis=1 )
model_eke850_significance = np.full ( model_eke850_composite.shape , np.nan , dtype=model_eke850_forecast_anomaly.dtype )
model_z500_season = np.nanmean ( model_z500_forecast_anomaly [ season_list , composite_start_week - 1 : composite_end_week , : , : ] , axis=1 )
model_z500_significance = np.full ( model_z500_composite.shape , np.nan , dtype=model_z500_forecast_anomaly.dtype )
reanalysis_eke850_season = np.nanmean ( reanlaysis_eke850_forecast_anomaly [ season_list , composite_start_week - 1 : composite_end_week , : , : ] , axis=1 )
reanalysis_eke850_significance = np.full ( reanalysis_eke850_composite.shape , np.nan , dtype=reanlaysis_eke850_forecast_anomaly.dtype )
reanalysis_z500_season = np.nanmean ( reanlaysis_z500_forecast_anomaly [ season_list , composite_start_week - 1 : composite_end_week , : , : ] , axis=1 )
reanalysis_z500_significance = np.full ( reanalysis_z500_composite.shape , np.nan , dtype=reanlaysis_z500_forecast_anomaly.dtype )
for phase_n in range ( len ( phase_names ) ) :
    model_eke850_significance [ phase_n , : , : ]      = test_sig_np ( model_eke850_season , model_eke850_composite [ phase_n ] , bootstrap_size , len ( rmm_list [ phase_n ] ) )
    model_z500_significance [ phase_n , : , : ]        = test_sig_np ( model_z500_season , model_z500_composite [ phase_n ] , bootstrap_size , len ( rmm_list [ phase_n ] ) )
    reanalysis_eke850_significance [ phase_n , : , : ] = test_sig_np ( reanalysis_eke850_season , reanalysis_eke850_composite [ phase_n ] , bootstrap_size , len ( rmm_list [ phase_n ] ) )
    reanalysis_z500_significance [ phase_n , : , : ]   = test_sig_np ( reanalysis_z500_season , reanalysis_z500_composite [ phase_n ] , bootstrap_size , len ( rmm_list [ phase_n ] ) )

##### pattern correlation
pattern_correlation_eke850 = np.empty ( ( len ( pattern_corr_regions ) , len ( phase_names ) ) , dtype=model_eke850_composite.dtype )
pattern_correlation_z500   = np.empty ( ( len ( pattern_corr_regions ) , len ( phase_names ) ) , dtype=model_z500_composite.dtype )
for region_n in range ( len ( pattern_corr_regions ) ) :
    for phase_n in range ( len ( phase_names ) ) :
        pattern_correlation_eke850 [ region_n , phase_n ] = calcPatCorr ( reanalysis_eke850_composite [ phase_n , : , : ] , model_eke850_composite [ phase_n , : , : ] , np.array ( data_lat_in ) , regions_south_north [ region_n ] [ 0 ] , regions_south_north [ region_n ] [ 1 ] , np.array ( data_lon_in ) , regions_west_east [ region_n ] [ 0 ] , regions_west_east [ region_n ] [ 1 ] )
        pattern_correlation_z500 [ region_n , phase_n ] = calcPatCorr ( reanalysis_z500_composite [ phase_n , : , : ] , model_z500_composite [ phase_n , : , : ] , np.array ( data_lat_in ) , regions_south_north [ region_n ] [ 0 ] , regions_south_north [ region_n ] [ 1 ] , np.array ( data_lon_in ) , regions_west_east [ region_n ] [ 0 ] , regions_west_east [ region_n ] [ 1 ] )

##### make plots
colors  = [ "blue" , "red" , "orange" , "magenta" ]

fig, axs = plt.subplots ( 1 , len ( pattern_corr_regions ) , figsize=( 14 , 4 ) )
fig.suptitle ( "pattern correlation" , size=14 )
for region_n in range ( len ( pattern_corr_regions ) ) :
    for phase_n in range ( len ( phase_names ) ) :    
        m = MarkerStyle ( 'o' )
        axs [ region_n ].plot ( pattern_correlation_z500 [ region_n , phase_n ] , pattern_correlation_eke850 [ region_n , phase_n ] , marker=m , color=colors [ phase_n ] )
        axs [ region_n ].text ( pattern_correlation_z500 [ region_n , phase_n ] , pattern_correlation_eke850 [ region_n , phase_n ] - 0.1 , phase_names [ phase_n ] , color=colors [ phase_n ] )
    axs [ region_n ].set_xlabel ( "z500 pattern correlation" )
    axs [ region_n ].set_ylabel ( "eke850 pattern correlation" )
    axs [ region_n ].set_xlim ( -1 , 1 )
    axs [ region_n ].set_ylim ( -1 , 1 )
    axs [ region_n ].set_title ( pattern_corr_regions [ region_n ] )
plt.savefig ( plot_dir + "pattern_corr.jpg" , dpi=500 )

##### save correlations
file_name="pattern_corr"
    
for region_n in range ( len ( pattern_corr_regions ) ):
    write_output_text( plot_dir+file_name+'_'+pattern_corr_regions[region_n],
                       np.insert(phase_names,0,''),
                       [np.insert(np.array(pattern_correlation_eke850[ region_n , : ],dtype=object),0,'eke850'),
                        np.insert(np.array(pattern_correlation_z500[region_n,:],dtype=object),0,'z500')]
                     )           

plot_levels = 8
fig_title_names = [ "Reanalysis" , Model_name ]
cmap='bwr'

cnLevelSpacingF = get_plot_level_spacing ( reanalysis_eke850_composite , plot_levels , pattern_corr_south , pattern_corr_north , np.array ( data_lat_in ) )
cnMaxLevelValF  = plot_max_level ( plot_levels , cnLevelSpacingF )
cnLevels = np.arange ( - cnMaxLevelValF , cnMaxLevelValF + cnLevelSpacingF , cnLevelSpacingF )
for phase_n in range ( len ( phase_names ) ) :
    wks_name = plot_dir + "eke850_phase" + phase_names [ phase_n ]
    plot_data = np.empty ( ( 2 , len ( data_lat_in ) , len ( data_lon_in ) ) , dtype=type ( model_eke850_composite ) )
    plot_data [ 0 , : , : ] = reanalysis_eke850_composite [ phase_n , : , : ]
    plot_data [ 1 , : , : ] = model_eke850_composite [ phase_n , : , : ]
    sig_data = np.empty ( ( 2 , len ( data_lat_in ) , len ( data_lon_in ) ) , dtype=type ( model_eke850_significance ) )
    sig_data [ 0 , : , : ] = reanalysis_eke850_significance [ phase_n , : , : ]
    sig_data [ 1 , : , : ] = model_eke850_significance [ phase_n , : , : ]
    for plot_n in range ( 2 ) :
        for lat_n in range ( len ( data_lat_in ) ) :
            for lon_n in range ( len ( data_lon_in ) ) :
                if sig_data [ plot_n , lat_n , lon_n ] > ( test_confidence_level * .5 ) and sig_data [ plot_n , lat_n , lon_n ] < ( 1 - test_confidence_level * .5 ) : sig_data [ plot_n , lat_n , lon_n ] = -1
                else : sig_data [ plot_n , lat_n , lon_n ] = 0.5
#    sig_data = np.where ( logical_and ( sig_data > ( test_confidence_level * .5 ) , sig_data < ( 1 - test_confidence_level * .5 ) ) , - 1. , 0.5 )
    plotComposites ( plot_data , data_lat_in , data_lon_in , fig_title_names , cnLevels , cmap , sig_data , pattern_correlation_eke850 [ 0 , phase_n ] , wks_name , "eke850 phase" + phase_names [ phase_n ] , "eke850 m2/s2" ) 

cnLevelSpacingF = get_plot_level_spacing ( reanalysis_z500_composite , plot_levels , pattern_corr_south , pattern_corr_north , np.array ( data_lat_in ) )
cnMaxLevelValF  = plot_max_level ( plot_levels , cnLevelSpacingF )
cnLevels = np.arange ( - cnMaxLevelValF , cnMaxLevelValF + cnLevelSpacingF , cnLevelSpacingF )
for phase_n in range ( len ( phase_names ) ) :
    wks_name = plot_dir + "z500_phase" + phase_names [ phase_n ]
    plot_data = np.empty ( ( 2 , len ( data_lat_in ) , len ( data_lon_in ) ) , dtype=type ( model_z500_composite ) )
    plot_data [ 0 , : , : ] = reanalysis_z500_composite [ phase_n , : , : ]
    plot_data [ 1 , : , : ] = model_z500_composite [ phase_n , : , : ]
    sig_data = np.empty ( ( 2 , len ( data_lat_in ) , len ( data_lon_in ) ) , dtype=type ( model_z500_significance ) )
    sig_data [ 0 , : , : ] = reanalysis_z500_significance [ phase_n , : , : ]
    sig_data [ 1 , : , : ] = model_z500_significance [ phase_n , : , : ]
    for plot_n in range ( 2 ) :
        for lat_n in range ( len ( data_lat_in ) ) :
            for lon_n in range ( len ( data_lon_in ) ) :
                if sig_data [ plot_n , lat_n , lon_n ] > ( test_confidence_level * .5 ) and sig_data [ plot_n , lat_n , lon_n ] < ( 1 - test_confidence_level * .5 ) : sig_data [ plot_n , lat_n , lon_n ] = -1
                else : sig_data [ plot_n , lat_n , lon_n ] = 0.5
#    sig_data = np.where ( logical_and ( sig_data > ( test_confidence_level * .5 ) , sig_data < ( 1 - test_confidence_level * .5 ) ) , - 1. , 0.5 )
    plotComposites ( plot_data , data_lat_in , data_lon_in , fig_title_names , cnLevels , cmap , sig_data , pattern_correlation_z500 [ 0 , phase_n ] , wks_name , "z500 phase" + phase_names [ phase_n ] , "z500 m" ) 

exit ( )

##### make plots
mpres                       = Ngl.Resources()
mpres.nglDraw               = False
mpres.nglFrame              = False
mpres.nglMaximize           = False
mpres.vpXF                  = 0.05
mpres.vpYF                  = 0.88
mpres.vpWidthF              = 0.45
mpres.vpHeightF             = 0.45
mpres.mpProjection          = 'Stereographic'
mpres.mpEllipticalBoundary  = True
mpres.mpDataSetName         = 'Earth..4'
mpres.mpDataBaseVersion     = 'MediumRes'
mpres.mpLimitMode           = 'LatLon'
mpres.mpMaxLatF             = 90.
mpres.mpMinLatF             = 20.
mpres.mpCenterLatF          = 90.
mpres.mpGridAndLimbOn       = False
mpres.pmTickMarkDisplayMode = 'Never'

res_polar_color                      = Ngl.Resources ( )
res_polar_color.nglFrame             = False
res_polar_color.nglDraw              = False
res_polar_color.cnFillOn             = True
res_polar_color.cnLinesOn            = False
res_polar_color.cnLineLabelsOn       = False
res_polar_color.cnFillPalette        = "NCV_blue_red"
res_polar_color.cnLevelSelectionMode = "ManualLevels"
res_polar_color.lbOrientation        = "horizontal"
res_polar_color.sfYArray             = np.array ( data_lat_in )

res_significance                     = Ngl.Resources ( )
res_significance.nglFrame            = False
res_significance.nglDraw             = False
res_significance.cnFillOn            = False
res_significance.cnLinesOn           = True
res_significance.cnLineLabelsOn      = False
res_significance.cnLevelSelectionMode = "ManualLevels"
res_significance.cnMonoLineColor     = True
res_significance.cnLineColor         = "darkgreen"
res_significance.cnMinLevelValF      = test_confidence_level * .5
res_significance.cnMaxLevelValF      = 1 - test_confidence_level * .5
res_significance.cnLevelSpacingF     = res_significance.cnMaxLevelValF - res_significance.cnMinLevelValF
res_significance.cnInfoLabelOn       = False
res_significance.cnLineThicknessF    = 3.
res_significance.sfYArray            = np.array ( data_lat_in )

res_polar_color_z500                      = Ngl.Resources ( )
res_polar_color_z500.nglFrame             = False
res_polar_color_z500.nglDraw              = False
res_polar_color_z500.cnFillOn             = True
res_polar_color_z500.cnLinesOn            = False
res_polar_color_z500.cnLineLabelsOn       = False
res_polar_color_z500.cnFillPalette        = "NCV_blue_red"
res_polar_color_z500.cnLevelSelectionMode = "ManualLevels"
res_polar_color_z500.lbOrientation        = "horizontal"
res_polar_color_z500.sfYArray             = np.array ( data_lat_in )

lnres                   = Ngl.Resources()
lnres.gsLineColor       = "black"
lnres.gsLineThicknessF  = 1.0
lnres.gsLineDashPattern = 0

plot_levels = 8
res_polar_color.cnLevelSpacingF = get_plot_level_spacing ( reanalysis_eke850_composite , plot_levels , pattern_corr_south , pattern_corr_north , np.array ( data_lat_in ) )
res_polar_color.cnMaxLevelValF  = plot_max_level ( plot_levels , res_polar_color.cnLevelSpacingF )
res_polar_color.cnMinLevelValF  = - res_polar_color.cnMaxLevelValF
res_polar_color_z500.cnLevelSpacingF = get_plot_level_spacing ( reanalysis_z500_composite , plot_levels , pattern_corr_south , pattern_corr_north , np.array ( data_lat_in ) )
res_polar_color_z500.cnMaxLevelValF  = plot_max_level ( plot_levels , res_polar_color_z500.cnLevelSpacingF )
res_polar_color_z500.cnMinLevelValF  = - res_polar_color_z500.cnMaxLevelValF

for phase_n in range ( len ( phase_names ) ) :
    wks_model = Ngl.open_wks ( "png" , plot_dir + "eke850_phase" + phase_names [ phase_n ] )
    mpres.vpXF = 0.025             #-- viewport x-position
    map1 = Ngl.map ( wks_model , mpres )                        #-- create base map
    Ngl.draw ( map1 )                                   #-- draw map
    lines = []
    lines.append ( Ngl.add_polyline ( wks_model , map1 , [ - 180 , 0 , 180 ] , [ mpres.mpMinLatF , mpres.mpMinLatF , mpres.mpMinLatF ] ,lnres ) )
    plot_cyclic , lon_cyclie       = Ngl.add_cyclic ( model_eke850_composite [ phase_n , : , : ] , data_lon_in )
    plot_significance , lon_cyclie = Ngl.add_cyclic ( model_eke850_significance [ phase_n , : , : ] , data_lon_in )
    res_polar_color.sfXArray       = lon_cyclie
    res_significance.sfXArray      = lon_cyclie
    res_polar_color.tiMainString = Model_name + " eke850 phase" + phase_names [ phase_n ]
    plot = Ngl.contour ( wks_model , plot_cyclic , res_polar_color )
    plot1 = Ngl.contour ( wks_model , plot_significance , res_significance )
    Ngl.overlay ( map1 , plot )
    Ngl.overlay ( map1 , plot1 )
    Ngl.draw ( map1 )
    mpres.vpXF = 0.525             #-- viewport x-position
    map2 = Ngl.map ( wks_model , mpres )                        #-- create base map
    Ngl.draw ( map2 )                                   #-- draw map
    lines = []
    lines.append ( Ngl.add_polyline ( wks_model , map2 , [ - 180 , 0 , 180 ] , [ mpres.mpMinLatF , mpres.mpMinLatF , mpres.mpMinLatF ] ,lnres ) )
    plot_cyclic , lon_cyclie       = Ngl.add_cyclic ( reanalysis_eke850_composite [ phase_n , : , : ] , data_lon_in )
    plot_significance , lon_cyclie = Ngl.add_cyclic ( reanalysis_eke850_significance [ phase_n , : , : ] , data_lon_in )
    res_polar_color.sfXArray       = lon_cyclie
    res_significance.sfXArray      = lon_cyclie
    res_polar_color.tiMainString = Reanalysis_name + " eke850 phase" + phase_names [ phase_n ]
    plot = Ngl.contour ( wks_model , plot_cyclic , res_polar_color )
    plot1 = Ngl.contour ( wks_model , plot_significance , res_significance )
    Ngl.overlay ( map2 , plot )
    Ngl.overlay ( map2 , plot1 )
    Ngl.draw ( map2 )
    Ngl.frame ( wks_model )
    Ngl.delete_wks ( wks_model )

for phase_n in range ( len ( phase_names ) ) :    
    wks_model = Ngl.open_wks ( "png" , plot_dir + "z500_phase" + phase_names [ phase_n ] )
    mpres.vpXF = 0.025             #-- viewport x-position
    map1 = Ngl.map ( wks_model , mpres )                        #-- create base map
    Ngl.draw ( map1 )                                   #-- draw map
    lines = []
    lines.append ( Ngl.add_polyline ( wks_model , map1 , [ - 180 , 0 , 180 ] , [ mpres.mpMinLatF , mpres.mpMinLatF , mpres.mpMinLatF ] ,lnres ) )
    plot_cyclic , lon_cyclie       = Ngl.add_cyclic ( model_z500_composite [ phase_n , : , : ] , data_lon_in )
    plot_significance , lon_cyclie = Ngl.add_cyclic ( model_z500_significance [ phase_n , : , : ] , data_lon_in )
    res_polar_color_z500.sfXArray  = lon_cyclie
    res_significance.sfXArray      = lon_cyclie
    res_polar_color_z500.tiMainString = Model_name + " z500 phase" + phase_names [ phase_n ]
    plot = Ngl.contour ( wks_model , plot_cyclic , res_polar_color_z500 )
    plot1 = Ngl.contour ( wks_model , plot_significance , res_significance )
    Ngl.overlay ( map1 , plot )
    Ngl.overlay ( map1 , plot1 )
    Ngl.draw ( map1 )
    mpres.vpXF = 0.525             #-- viewport x-position
    map2 = Ngl.map ( wks_model , mpres )                        #-- create base map
    Ngl.draw ( map2 )                                   #-- draw map
    lines = []
    lines.append ( Ngl.add_polyline ( wks_model , map2 , [ - 180 , 0 , 180 ] , [ mpres.mpMinLatF , mpres.mpMinLatF , mpres.mpMinLatF ] ,lnres ) )
    plot_cyclic , lon_cyclie       = Ngl.add_cyclic ( reanalysis_z500_composite [ phase_n , : , : ] , data_lon_in )
    plot_significance , lon_cyclie = Ngl.add_cyclic ( reanalysis_z500_significance [ phase_n , : , : ] , data_lon_in )
    res_polar_color_z500.sfXArray  = lon_cyclie
    res_significance.sfXArray      = lon_cyclie
    res_polar_color_z500.tiMainString = Reanalysis_name + " z500 phase" + phase_names [ phase_n ]
    plot = Ngl.contour ( wks_model , plot_cyclic , res_polar_color_z500 )
    plot1 = Ngl.contour ( wks_model , plot_significance , res_significance )
    Ngl.overlay ( map2 , plot )
    Ngl.overlay ( map2 , plot1 )
    Ngl.draw ( map2 )
    Ngl.frame ( wks_model )
    Ngl.delete_wks ( wks_model )

colors  = [ "blue" , "red" , "orange" , "magenta" ]

res1                    = Ngl.Resources ( )
res1.vpXF               = 0.03
res1.vpYF               = 0.88
res1.vpWidthF           = 0.27
res1.vpHeightF          = 0.27
res1.nglFrame           = False
res1.nglDraw            = False
res1.nglMaximize           = False
res1.xyLineThicknesses  = 1
res1.xyMarkLineModes    = [ "Lines" , "Markers" ,"Markers" ]
res1.xyMarkers          = [ 0       , 4         , 4        ]               #-- marker type of each line
res1.xyMarkerSizeF      = 0.02                   #-- default is 0.01
res1.xyMarkerThicknessF = 5
res1.xyMarkerColors     = [ "red"   , "red"     ,"blue"    ] #-- set marker colors
res1.trXMaxF = 1.
res1.trYMaxF = 1.
res1.trXMinF = -1.
res1.trYMinF = -1.
res1.tiMainFontHeightF  = 0.012

gsres                   = Ngl.Resources ( )
gsres.gsMarkerIndex     = 16       # dots
gsres.gsMarkerSizeF     = 0.01    # twice normal size
gsres.gsMarkerThicknessF = 2

txres               = Ngl.Resources()
txres.txFontHeightF = 0.012
txres.txJust        = "BottomCenter"

wks_pattern_cc = Ngl.open_wks ( "png" , plot_dir + "pattern_corr" )
for region_n in range ( len ( pattern_corr_regions ) ) :
    res1.vpXF = 0.08 + 0.04 * ( region_n ) + res1.vpWidthF * region_n
    one_to_one = np.array ( [ pattern_correlation_eke850 [ region_n , 0 ] , pattern_correlation_eke850 [ region_n , 1 ] , res1.trXMinF , res1.trXMaxF ] )
    res1.tiXAxisString = "z500 pattern correlation"
    if region_n == 0 :
        res1.tiYAxisString = "eke850 pattern correlation"
        res1.tiMainString = pattern_corr_regions [ region_n ] + " " + str ( regions_south_north [ region_n ] [ 0 ] ) + "-" + str ( regions_south_north [ region_n ] [ 1 ] ) + "N"
    else :
        res1.tiYAxisString = ""
        if regions_west_east [ region_n ] [ 0 ] < 180 : east_str = str ( regions_west_east [ region_n ] [ 0 ] ) + "E"
        else : east_str = str ( regions_west_east [ region_n ] [ 0 ] ) + "W"
        if regions_west_east [ region_n ] [ 1 ] < 180 : west_str = str ( regions_west_east [ region_n ] [ 1 ] ) + "E"
        else : west_str = str ( regions_west_east [ region_n ] [ 1 ] ) + "W"
        res1.tiMainString = pattern_corr_regions [ region_n ] + " " + str ( regions_south_north [ region_n ] [ 0 ] ) + "-" + str ( regions_south_north [ region_n ] [ 1 ] ) + "N " + east_str + "-" + west_str
    plot = Ngl.xy ( wks_pattern_cc , one_to_one , one_to_one , res1 )
    for phase_n in range ( len ( phase_names ) ) :
        gsres.gsMarkerColor = colors [ phase_n ]
        prim6 = Ngl.add_polymarker ( wks_pattern_cc , plot , pattern_correlation_z500 [ region_n , phase_n ] , pattern_correlation_eke850 [ region_n , phase_n ] , gsres )
        txres.txFontColor   = colors [ phase_n ]
        text1 = Ngl.add_text ( wks_pattern_cc , plot , "phase" + phase_names [ phase_n ] , pattern_correlation_z500 [ region_n , phase_n ] , pattern_correlation_eke850 [ region_n , phase_n ] - .15 , txres )
    Ngl.draw ( plot )
Ngl.frame ( wks_pattern_cc )
Ngl.delete_wks ( wks_pattern_cc )

