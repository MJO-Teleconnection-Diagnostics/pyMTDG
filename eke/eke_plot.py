import xarray as xr
import numpy as np
import netCDF4
import Ngl

import glob
import os

import yaml

from eke_util import get_model_latitude
from eke_util import get_model_longitude
from eke_util import get_model_weekly_eke_anomaly
from eke_util import get_erai_weekly_eke_anomaly
from eke_util import get_model_weekly_z500_anomaly
from eke_util import get_erai_weekly_z500_anomaly
from eke_util import convert_ymdh_to_ymd_list
from eke_util import get_rmm_composite_list
from eke_util import get_composite
from eke_util import get_season_list
from eke_util import test_sig_np
from eke_util import calcPatCorr
from eke_util import get_plot_level_spacing
from eke_util import plot_max_level

###### Input from yml file ( UFS )
with open ( 'config.yml' , 'r' ) as file:
    yml_input = yaml.safe_load ( file )

Model_name                   = yml_input [ 'model name' ]
Ensemble_size                = int ( yml_input [ 'Number of ensembles:' ] )
Daily_Mean_Data              = yml_input [ 'Model input file daily mean:' ]
Forecast_time_step_interval  = yml_input [ 'forecast time step' ]
Model_data_initial_condition = yml_input [ 'model initial conditions' ]
Smooth_climatology           = yml_input [ 'smooth climatology:' ]
ERAI                         = yml_input [ 'ERAI:' ]
RMM                          = yml_input [ 'RMM:' ]

Model_u850_files             = yml_input [ 'Path to zonalwind850 date files' ]
Model_v850_files             = yml_input [ 'Path to meridional wind at 850 hPa date files' ]
Model_z500_files             = yml_input [ 'Path to z500 date files' ]

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
if ERAI :
    ERA_u850_file = "/data0/czheng/S2S-UFS/ERA-Interim/uv_850_1979-2019_1.5.nc"
    ERA_v850_file = "/data0/czheng/S2S-UFS/ERA-Interim/uv_850_1979-2019_1.5.nc"
    ERA_z500_file = "/data0/czheng/S2S-UFS/ERA-Interim/geopotential500_1979-2019_1.5.nc"

#Model_u850_files = [ "/data0/czheng/S2S-UFS/data/6hourly/Prototype5/u_850-isobaricInhPa/u.850-isobaricInhPa.*.6hourly.nc" ]
#Model_v850_files = [ "/data0/czheng/S2S-UFS/data/6hourly/Prototype5/v_850-isobaricInhPa/v.850-isobaricInhPa.*.6hourly.nc" ]
#Model_z500_files = [ "/data0/czheng/S2S-UFS/data/6hourly/Prototype5/gh_500-isobaricInhPa/gh.500-isobaricInhPa.*.6hourly.nc" ]
Model_z500_varname = "z"

if RMM :
    RMM_ERA_file = "/data0/czheng/S2S-UFS/ERA-Interim/rmm/rmm_ERA-Interim.nc"

plot_dir = "../output/Eke/" + Model_name + "/"
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

RMM_ERA_file = "/data0/czheng/S2S-UFS/ERA-Interim/rmm/rmm_ERA-Interim.nc"

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

ERAI_timesteps_per_day = 4

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
if Ensemble_size == 1 : Multiple_Ensemble_Members = False
else: Multiple_Ensemble_Members = True

###### Read model u,v data
model_u_file_list = glob.glob ( Model_u850_files [ 0 ] )
model_u_file_list.sort ( )
yyyymmddhh_list = [ ]
u_files_head = Model_u850_files [ 0 ].split ( "*" , 1 )
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
yyyymmddhh_list.sort ( )
yyyymmdd_list = convert_ymdh_to_ymd_list ( yyyymmddhh_list )
v_files_head = Model_v850_files [ 0 ].split ( "*" , 1 )
#read the first model file to get lat and lon dimension
if Multiple_Ensemble_Members : ens_string = "_e00"
else : ens_string = ""
model_u850_file0 = xr.open_dataset ( u_files_head [ 0 ] + str ( yyyymmddhh_list [ 0 ] ) + ens_string + u_files_head [ 1 ] )
model_u850_in = model_u850_file0 [ 'u' ]
model_u850_in_dim = model_u850_in.dims
model_lat_in = get_model_latitude ( model_u850_file0 , model_u850_in_dim )
model_lon_in = get_model_longitude ( model_u850_file0 , model_u850_in_dim )
model_u850_file0.close ( )
model_input_u = np.array ( model_u850_in )
#read model data and calculate eke anomaly
model_eke850_forecast_anomaly = np.full ( ( len ( yyyymmdd_list ) , total_weeks , len ( model_lat_in ) , len ( model_lon_in ) ) , np.nan , dtype=model_input_u.dtype )
del ( model_input_u )
del ( model_u850_in )
for week_n in range ( total_weeks ) :
    model_eke850_forecast_anomaly [ : , week_n , : , : ] = get_model_weekly_eke_anomaly ( u_files_head , v_files_head , yyyymmddhh_list , week_n , Ensemble_size , Multiple_Ensemble_Members , model_lat_in , model_lon_in , model_eke850_forecast_anomaly.dtype , time_step_per_24h , Model_data_initial_condition , Smooth_climatology )

###### Read model z500 data
#potential issue with data type of z500,uv850
#potential issue with missing files in uv850 or z500
#potential issue with data frequency (6hourly vs daily mean) of z500,uv850
z_files_head = Model_z500_files [ 0 ].split ( "*" , 1 )
if Multiple_Ensemble_Members : ens_string = "_e00"
else : ens_string = ""
model_z500_file0 = xr.open_dataset ( z_files_head [ 0 ] + str ( yyyymmddhh_list [ 0 ] ) + ens_string + z_files_head [ 1 ] )
model_z500_in = model_z500_file0 [ Model_z500_varname ]
model_z500_file0.close ( )
model_input_z = np.array ( model_z500_in )
model_z500_forecast_anomaly = np.full ( ( len ( yyyymmdd_list ) , total_weeks , len ( model_lat_in ) , len ( model_lon_in ) ) , np.nan , dtype=model_input_z.dtype )
del ( model_input_z )
del ( model_z500_in )
for week_n in range ( total_weeks ) :
    model_z500_forecast_anomaly [ : , week_n , : , : ] = get_model_weekly_z500_anomaly ( z_files_head , Model_z500_varname , yyyymmddhh_list , week_n , Ensemble_size , Multiple_Ensemble_Members , model_lat_in , model_lon_in , model_z500_forecast_anomaly.dtype , time_step_per_24h , Model_data_initial_condition , Smooth_climatology , Daily_Mean_Data )

##### read reanalysis data for eke
#potential issue with data type of erai/reanalysis
if ERAI :
    reanlaysis_eke850_forecast_anomaly = np.full ( ( len ( yyyymmdd_list ) , total_weeks , len ( model_lat_in ) , len ( model_lon_in ) ) , np.nan , dtype=model_eke850_forecast_anomaly.dtype )
    reanlaysis_z500_forecast_anomaly = np.full ( ( len ( yyyymmdd_list ) , total_weeks , len ( model_lat_in ) , len ( model_lon_in ) ) , np.nan , dtype=model_z500_forecast_anomaly.dtype )
    for week_n in range ( total_weeks ) :
        reanlaysis_eke850_forecast_anomaly [ : , week_n , : , : ] = get_erai_weekly_eke_anomaly ( ERA_u850_file , ERA_v850_file , yyyymmddhh_list , week_n , model_lat_in , model_lon_in , model_eke850_forecast_anomaly.dtype , time_step_per_24h , Daily_Mean_Data , Smooth_climatology , ERAI_timesteps_per_day )
        reanlaysis_z500_forecast_anomaly [ : , week_n , : , : ] = get_erai_weekly_z500_anomaly ( ERA_z500_file , yyyymmddhh_list , week_n , model_lat_in , model_lon_in , model_z500_forecast_anomaly.dtype , time_step_per_24h , Daily_Mean_Data , Smooth_climatology , ERAI_timesteps_per_day )

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
model_eke850_composite = np.full ( ( len ( phase_names ) , len ( model_lat_in ) , len ( model_lon_in ) ) , np.nan , dtype=model_eke850_forecast_anomaly.dtype )
model_z500_composite = np.full ( ( len ( phase_names ) , len ( model_lat_in ) , len ( model_lon_in ) ) , np.nan , dtype=model_z500_forecast_anomaly.dtype )
reanalysis_eke850_composite = np.full ( ( len ( phase_names ) , len ( model_lat_in ) , len ( model_lon_in ) ) , np.nan , dtype=reanlaysis_eke850_forecast_anomaly.dtype )
reanalysis_z500_composite = np.full ( ( len ( phase_names ) , len ( model_lat_in ) , len ( model_lon_in ) ) , np.nan , dtype=reanlaysis_z500_forecast_anomaly.dtype )
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
        pattern_correlation_eke850 [ region_n , phase_n ] = calcPatCorr ( reanalysis_eke850_composite [ phase_n , : , : ] , model_eke850_composite [ phase_n , : , : ] , np.array ( model_lat_in ) , regions_south_north [ region_n ] [ 0 ] , regions_south_north [ region_n ] [ 1 ] , np.array ( model_lon_in ) , regions_west_east [ region_n ] [ 0 ] , regions_west_east [ region_n ] [ 1 ] )
        pattern_correlation_z500 [ region_n , phase_n ] = calcPatCorr ( reanalysis_z500_composite [ phase_n , : , : ] , model_z500_composite [ phase_n , : , : ] , np.array ( model_lat_in ) , regions_south_north [ region_n ] [ 0 ] , regions_south_north [ region_n ] [ 1 ] , np.array ( model_lon_in ) , regions_west_east [ region_n ] [ 0 ] , regions_west_east [ region_n ] [ 1 ] )

##### make plots
res_polar_color                      = Ngl.Resources ( )
res_polar_color.nglFrame             = False
res_polar_color.nglDraw              = False
res_polar_color.cnFillOn             = True
res_polar_color.cnLinesOn            = False
res_polar_color.cnLineLabelsOn       = False
res_polar_color.cnFillPalette        = "NCV_blue_red"
res_polar_color.lbOrientation        = "horizontal"
res_polar_color.mpMinLatF            = 20.
res_polar_color.mpMaxLatF            = 80.
res_polar_color.mpCenterLonF         = 180.
res_polar_color.mpGridAndLimbOn      = False
res_polar_color.mpLimitMode          = "LatLon"
res_polar_color.mpGeophysicalLineColor = "gray50"
res_polar_color.mpOutlineBoundarySets  = "Geophysical"
res_polar_color.cnLevelSelectionMode = "ManualLevels"
#res_polar_color.cnMinLevelValF       = -34.
#res_polar_color.cnMaxLevelValF       = 34.
#res_polar_color.cnLevelSpacingF      = 4.
res_polar_color.sfXArray             = np.array ( model_lon_in )
res_polar_color.sfYArray             = np.array ( model_lat_in )

res_significance                     = Ngl.Resources ( )
res_significance.nglFrame            = False
res_significance.nglDraw             = False
res_significance.cnFillOn            = False
res_significance.cnLinesOn           = True
res_significance.cnLineLabelsOn      = False
res_significance.cnLevelSelectionMode = "ManualLevels"
res_significance.cnMinLevelValF      = test_confidence_level * .5
res_significance.cnMaxLevelValF      = 1 - test_confidence_level * .5
res_significance.cnLevelSpacingF     = res_significance.cnMaxLevelValF - res_significance.cnMinLevelValF
res_significance.sfXArray            = np.array ( model_lon_in )
res_significance.sfYArray            = np.array ( model_lat_in )
res_significance.cnInfoLabelOn       = False
res_significance.cnLineThicknessF    = 1.5

res_polar_color_z500                      = Ngl.Resources ( )
res_polar_color_z500.nglFrame             = False
res_polar_color_z500.nglDraw              = False
res_polar_color_z500.cnFillOn             = True
res_polar_color_z500.cnLinesOn            = False
res_polar_color_z500.cnLineLabelsOn       = False
res_polar_color_z500.cnFillPalette        = "NCV_blue_red"
res_polar_color_z500.lbOrientation        = "horizontal"
res_polar_color_z500.mpMinLatF            = 20.
res_polar_color_z500.mpMaxLatF            = 80.
res_polar_color_z500.mpCenterLonF         = 180.
res_polar_color_z500.mpGridAndLimbOn      = False
res_polar_color_z500.mpLimitMode          = "LatLon"
res_polar_color_z500.mpGeophysicalLineColor = "gray50"
res_polar_color_z500.mpOutlineBoundarySets  = "Geophysical"
res_polar_color_z500.cnLevelSelectionMode = "ManualLevels"
#res_polar_color_z500.cnMinLevelValF       = -125
#res_polar_color_z500.cnMaxLevelValF       = 125.
#res_polar_color_z500.cnLevelSpacingF      = 10.
res_polar_color_z500.sfXArray             = np.array ( model_lon_in )
res_polar_color_z500.sfYArray             = np.array ( model_lat_in )

#wks_model = Ngl.open_wks ( "pdf" , plot_dir + "model" )
#wks_reanalysis = Ngl.open_wks ( "pdf" , plot_dir + "reanalysis" )

plot_levels = 8
res_polar_color.cnLevelSpacingF = get_plot_level_spacing ( reanalysis_eke850_composite , plot_levels , res_polar_color.mpMinLatF , res_polar_color.mpMaxLatF , np.array ( model_lat_in ) )
res_polar_color.cnMaxLevelValF  = plot_max_level ( plot_levels , res_polar_color.cnLevelSpacingF )
res_polar_color.cnMinLevelValF  = - res_polar_color.cnMaxLevelValF
res_polar_color_z500.cnLevelSpacingF = get_plot_level_spacing ( reanalysis_z500_composite , plot_levels , res_polar_color_z500.mpMinLatF , res_polar_color_z500.mpMaxLatF , np.array ( model_lat_in ) )
res_polar_color_z500.cnMaxLevelValF  = plot_max_level ( plot_levels , res_polar_color_z500.cnLevelSpacingF )
res_polar_color_z500.cnMinLevelValF  = - res_polar_color_z500.cnMaxLevelValF

for phase_n in range ( len ( phase_names ) ) :
    wks_reanalysis = Ngl.open_wks ( "png" , plot_dir + "reanalysis_eke850_" + phase_names [ phase_n ] )
    res_polar_color.tiMainString = "reanalysis eke850 phase" + phase_names [ phase_n ]
    plot = Ngl.contour_map ( wks_reanalysis , reanalysis_eke850_composite [ phase_n , : , : ] , res_polar_color )
    plot1 = Ngl.contour ( wks_reanalysis , reanalysis_eke850_significance [ phase_n , : , : ] , res_significance )
    Ngl.overlay ( plot , plot1 )
    Ngl.draw ( plot )
    Ngl.frame ( wks_reanalysis )
    Ngl.delete_wks ( wks_reanalysis )
    wks_model = Ngl.open_wks ( "png" , plot_dir + "model_eke850_" + phase_names [ phase_n ] )
    res_polar_color.tiMainString = "model eke850 phase" + phase_names [ phase_n ]
    plot = Ngl.contour_map ( wks_model , model_eke850_composite [ phase_n , : , : ] , res_polar_color )
    plot1 = Ngl.contour ( wks_model , model_eke850_significance [ phase_n , : , : ] , res_significance )
    Ngl.overlay ( plot , plot1 )
    Ngl.draw ( plot )
    Ngl.frame ( wks_model )
    Ngl.delete_wks ( wks_model )

for phase_n in range ( len ( phase_names ) ) :
    wks_reanalysis = Ngl.open_wks ( "png" , plot_dir + "reanalysis_z500_" + phase_names [ phase_n ] )
    res_polar_color_z500.tiMainString = "reanalysis z500 phase" + phase_names [ phase_n ]
    plot = Ngl.contour_map ( wks_reanalysis , reanalysis_z500_composite [ phase_n , : , : ] , res_polar_color_z500 )
    plot1 = Ngl.contour ( wks_reanalysis , reanalysis_z500_significance [ phase_n , : , : ] , res_significance )
    Ngl.overlay ( plot , plot1 )
    Ngl.draw ( plot )
    Ngl.frame ( wks_reanalysis )
    Ngl.delete_wks ( wks_reanalysis )
    wks_model = Ngl.open_wks ( "png" , plot_dir + "model_z500_" + phase_names [ phase_n ] )
    res_polar_color_z500.tiMainString = "model z500 phase" + phase_names [ phase_n ]
    plot = Ngl.contour_map ( wks_model , model_z500_composite [ phase_n , : , : ] , res_polar_color_z500 )
    plot1 = Ngl.contour ( wks_model , model_z500_significance [ phase_n , : , : ] , res_significance )
    Ngl.overlay ( plot , plot1 )
    Ngl.draw ( plot )
    Ngl.frame ( wks_model )
    Ngl.delete_wks ( wks_model )
#Ngl.delete_wks ( wks_reanalysis )
#Ngl.delete_wks ( wks_model )

#wks_pattern_cc = Ngl.open_wks ( "png" , plot_dir + "pattern_corr" )

res1                    = Ngl.Resources ( )
res1.nglFrame           = False
res1.nglDraw            = False
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
res1.tiMainFontHeightF  = 0.02

gsres                   = Ngl.Resources ( )
gsres.gsMarkerIndex     = 16       # dots
gsres.gsMarkerSizeF     = 0.025    # twice normal size
gsres.gsMarkerThicknessF = 5

txres               = Ngl.Resources()
txres.txFontHeightF = 0.02
txres.txJust        = "BottomCenter"

colors  = [ "blue" , "red" , "orange" , "magenta" ]

for region_n in range ( len ( pattern_corr_regions ) ) :
    wks_pattern_cc = Ngl.open_wks ( "png" , plot_dir + "pattern_corr " + pattern_corr_regions [ region_n ] )
    one_to_one = np.array ( [ pattern_correlation_eke850 [ region_n , 0 ] , pattern_correlation_eke850 [ region_n , 1 ] , res1.trXMinF , res1.trXMaxF ] )
    res1.tiMainString = pattern_corr_regions [ region_n ] + " " + str ( regions_south_north [ region_n ] [ 0 ] ) + "-" + str ( regions_south_north [ region_n ] [ 1 ] ) + "N " + str ( regions_west_east [ region_n ] [ 0 ] ) + "-" + str ( regions_west_east [ region_n ] [ 1 ] )
    res1.tiXAxisString = "z500 pattern correlation"
    res1.tiYAxisString = "eke850 pattern correlation"
    plot = Ngl.xy ( wks_pattern_cc , one_to_one , one_to_one , res1 )
    for phase_n in range ( len ( phase_names ) ) :
        gsres.gsMarkerColor = colors [ phase_n ]
        prim6 = Ngl.add_polymarker ( wks_pattern_cc , plot , pattern_correlation_z500 [ region_n , phase_n ] , pattern_correlation_eke850 [ region_n , phase_n ] , gsres )
        txres.txFontColor   = colors [ phase_n ]
        text1 = Ngl.add_text ( wks_pattern_cc , plot , "phase" + phase_names [ phase_n ] , pattern_correlation_z500 [ region_n , phase_n ] , pattern_correlation_eke850 [ region_n , phase_n ] - .15 , txres )
    Ngl.draw ( plot )
    Ngl.frame ( wks_pattern_cc )
    Ngl.delete_wks ( wks_pattern_cc )

#Ngl.delete_wks ( wks_pattern_cc )

