import xarray as xr
import numpy as np
import netCDF4
import Ngl

from eke_util import calcEke
from eke_util import calcPatCorr
from eke_util import convert_to_daily
from eke_util import get_ts_one_forecast_model
from eke_util import get_ts_ERA
from eke_util import get_ensemble_size
from eke_util import get_model_latitude
from eke_util import get_model_longitude
from eke_util import get_all_anomalies
from eke_util import get_rmm_composite_list
from eke_util import get_season_list
from eke_util import test_sig_np

##### input directories and files
#DIR_IN = "/data0/czheng/S2S-UFS/data/combine/Prototype5/"
#U850_DIR = DIR_IN + "u.850-isobaricInhPa.2011040100-2018031500.f000-840.nc"
#V850_DIR = DIR_IN + "v.850-isobaricInhPa.2011040100-2018031500.f000-840.nc"
#Z500_DIR = DIR_IN + "gh.500-isobaricInhPa.2011040100-2018031500.f000-840.nc"
#ERA_IN = "/data0/czheng/S2S-UFS/ERA-Interim/"
#U850_ERA_DIR = ERA_IN + "uv_850_1979-2019_1.5.nc"
#V850_ERA_DIR = ERA_IN + "uv_850_1979-2019_1.5.nc"
#Z500_ERA_DIR = ERA_IN + "geopotential500_1979-2019_1.5.nc"
#RMM_IN = "/data0/czheng/S2S-UFS/ERA-Interim/rmm/"
#RMM_DIR = RMM_IN + "rmm_ERA-Interim.nc"

##### output plots directories and files
#PLOT_OUT = ""
#PLOT_DIR = PLOT_OUT + "test"

##### data frequency 6hourly or daily
# needs input from DAILY_MEAN_DATA
MODEL_TIME_STEPS_PER_DAY = 4 ## for 6 hourly
MODEL_DAILY_MEAN_DATA = False
if MODEL_TIME_STEPS_PER_DAY > 1 :
    MODEL_DAILY_MEAN_DATA = False
REANALYSIS_TIME_STEPS_PER_DAY = 4

##### parameters setup
composite_start_month = 11
composite_end_month   = 3
compoiste_amplitude_threshold = 1.
phase_names = [ "8-1" , "2-3" , "4-5" , "6-7" ]
total_weeks = 4
start_week = 3
end_week = 4
test_confidence_level = 0.10
bootstrap_size = 1000
g0 = 9.801

pattern_corr_regions = [ "Northern Hemisphere" , "North Pacific + North America" , "North Atlantic" ]
regions_south_north  = [ [ 20 , 80 ]           , [ 20 , 80 ]                     , [ 20 , 80 ]      ]
regions_west_east    = [ [ 0 , 360 ]           , [ 120 , 270 ]                   , [ 270 , 30 ]     ]

##### read model data for eke
model_u850_file = xr.open_dataset ( U850_DIR )
model_u850_in = model_u850_file [ 'u' ]
model_u850_in_dim = model_u850_in.dims
time_dim_name = model_u850_in_dim [ 0 ]
model_u850time_in = model_u850_file [ time_dim_name ]
model_yyyymmdd = np.array ( model_u850time_in.dt.year * 10000 + model_u850time_in.dt.month * 100 + model_u850time_in.dt.day )
ensemble_size = get_ensemble_size ( model_u850_file , model_u850_in_dim )
model_lat_in = get_model_latitude ( model_u850_file , model_u850_in_dim )
model_lon_in = get_model_longitude ( model_u850_file , model_u850_in_dim )
del ( model_u850_in )
model_v850_file = xr.open_dataset ( V850_DIR )

u_one_forecast = get_ts_one_forecast_model ( model_u850_file , 'u' , len ( model_u850_in_dim ) , 0 , 1 )
model_eke850_one_ensemble_forecast = np.empty ( ( ensemble_size , total_weeks * 7 , len ( model_lat_in ) , len ( model_lon_in ) ) , dtype=u_one_forecast.dtype )
model_eke850_ensemble_mean = np.empty ( ( len ( model_u850time_in ) , total_weeks * 7 , len ( model_lat_in ) , len ( model_lon_in ) ) , dtype=u_one_forecast.dtype )
del ( u_one_forecast )
for time_n in range ( len ( model_u850time_in ) ) :
    for ensemble_n in range ( ensemble_size ) :
        model_eke850_one_ensemble_forecast [ ensemble_n , : , : , : ] = calcEke ( get_ts_one_forecast_model ( model_u850_file , 'u' , len ( model_u850_in_dim ) , time_n , ensemble_n ) , get_ts_one_forecast_model ( model_v850_file , 'v' , len ( model_u850_in_dim ) , time_n , ensemble_n ) , MODEL_TIME_STEPS_PER_DAY , total_weeks * 7 )
    model_eke850_ensemble_mean [ time_n , : , : , : ] = np.nanmean ( model_eke850_one_ensemble_forecast , axis=0 )
model_eke850_anomaly = get_all_anomalies ( model_eke850_ensemble_mean , time_dim_name , model_u850time_in )
del ( model_eke850_ensemble_mean )

##### read reanalysis data for eke
ERA_u850_file = xr.open_dataset ( U850_ERA_DIR )
ERA_time_in  = ERA_u850_file [ 'time' ]
ERA_yyyymmdd = np.array ( ERA_time_in.dt.year * 10000 + ERA_time_in.dt.month * 100 + ERA_time_in.dt.day )
ERA_example = get_ts_ERA ( ERA_u850_file , 'u' , 0 , 10 , MODEL_DAILY_MEAN_DATA , REANALYSIS_TIME_STEPS_PER_DAY )
ERA_eke850 = np.empty ( model_eke850_anomaly.shape , dtype=ERA_example.dtype )
del ( ERA_example )
ERA_v850_file = xr.open_dataset ( V850_ERA_DIR )
ERA_steps_daily = REANALYSIS_TIME_STEPS_PER_DAY
if MODEL_DAILY_MEAN_DATA : ERA_steps_daily = 1
for time_n in range ( len ( model_yyyymmdd ) ) :
    time_step = 0
    while ERA_yyyymmdd [ time_step ] < model_yyyymmdd [ time_n ] : time_step = time_step + 1
    ERA_eke850 [ time_n , : , : , : ] = calcEke ( get_ts_ERA ( ERA_u850_file , 'u' , time_step , total_weeks * 7 + 2 , MODEL_DAILY_MEAN_DATA , REANALYSIS_TIME_STEPS_PER_DAY ) , get_ts_ERA ( ERA_v850_file , 'v' , time_step , total_weeks * 7 + 2 , MODEL_DAILY_MEAN_DATA , REANALYSIS_TIME_STEPS_PER_DAY ) , ERA_steps_daily , total_weeks * 7 )
ERA_eke850_anomaly = get_all_anomalies ( ERA_eke850 , time_dim_name , model_u850time_in )
del ( ERA_eke850 )

##### read model data for z500
model_z500_file = xr.open_dataset ( Z500_DIR )
model_z500_in = model_z500_file [ 'gh' ]
model_z500_in_dim = model_z500_in.dims
time_dim_name = model_z500_in_dim [ 0 ]
model_z500time_in = model_z500_file [ time_dim_name ]
z500_one_forecast = get_ts_one_forecast_model ( model_z500_file , 'gh' , len ( model_z500_in_dim ) , 0 , 1 )
model_z500_one_ensemble_forecast = np.empty ( ( ensemble_size , total_weeks * 7 , len ( model_lat_in ) , len ( model_lon_in ) ) , dtype=z500_one_forecast.dtype )
model_z500_ensemble_mean = np.empty ( ( len ( model_z500time_in ) , total_weeks * 7 , len ( model_lat_in ) , len ( model_lon_in ) ) , dtype=z500_one_forecast.dtype )
del ( z500_one_forecast )
for time_n in range ( len ( model_z500time_in ) ) :
    for ensemble_n in range ( ensemble_size ) :
        model_z500_one_ensemble_forecast [ ensemble_n , : , : , : ] = convert_to_daily ( get_ts_one_forecast_model ( model_z500_file , 'gh' , len ( model_z500_in_dim ) , time_n , ensemble_n ) , MODEL_TIME_STEPS_PER_DAY , total_weeks * 7 )
    model_z500_ensemble_mean [ time_n , : , : , : ] = np.nanmean ( model_z500_one_ensemble_forecast , axis=0 )
model_z500_anomaly = get_all_anomalies ( model_z500_ensemble_mean , time_dim_name , model_z500time_in )
del ( model_z500_ensemble_mean )

##### read reanalysis data for z500
ERA_z500_file = xr.open_dataset ( Z500_ERA_DIR )
ERA_time_in  = ERA_u850_file [ 'time' ]
ERA_yyyymmdd = np.array ( ERA_time_in.dt.year * 10000 + ERA_time_in.dt.month * 100 + ERA_time_in.dt.day )
ERA_example = get_ts_ERA ( ERA_z500_file , 'z' , 0 , 10 , MODEL_DAILY_MEAN_DATA , REANALYSIS_TIME_STEPS_PER_DAY )
ERA_z500 = np.empty ( model_z500_anomaly.shape , dtype=ERA_example.dtype )
del ( ERA_example )
ERA_steps_daily = REANALYSIS_TIME_STEPS_PER_DAY
if MODEL_DAILY_MEAN_DATA : ERA_steps_daily = 1
for time_n in range ( len ( model_yyyymmdd ) ) :
    time_step = 0
    while ERA_yyyymmdd [ time_step ] < model_yyyymmdd [ time_n ] : time_step = time_step + 1
    ERA_z500 [ time_n , : , : , : ] = convert_to_daily ( get_ts_ERA ( ERA_z500_file , 'z' , time_step , total_weeks * 7 + 2 , MODEL_DAILY_MEAN_DATA , REANALYSIS_TIME_STEPS_PER_DAY ) , ERA_steps_daily , total_weeks * 7 ) * ( 1 / g0 )
ERA_z500_anomaly = get_all_anomalies ( ERA_z500 , time_dim_name , model_z500time_in )
del ( ERA_z500 )

##### read rmm index
rmm_file = xr.open_dataset ( RMM_DIR )
rmm_time_in = rmm_file [ 'time' ]
#tvalue = netCDF4.num2date ( rmm_time_in , rmm_time_in.units )
tvalue = netCDF4.num2date ( rmm_time_in , rmm_time_in.units.replace ( "after" , "since" ) )
#rmm_yyyymmdd = np.array ( rmm_time_in.dt.year * 10000 + rmm_time_in.dt.month * 100 + rmm_time_in.dt.day )
rmm_yyyymmdd = np.empty ( len ( rmm_time_in ) , dtype='int64' )
for time_n in range ( len ( rmm_time_in ) ) : rmm_yyyymmdd [ time_n ] = tvalue [ time_n ].year * 10000 + tvalue [ time_n ].month * 100 + tvalue [ time_n ].day
rmm_phase_in = np.empty ( len ( rmm_time_in ) , dtype='int64' )
for time_n in range ( len ( rmm_time_in ) ) : rmm_phase_in [ time_n ] = int ( rmm_file [ 'phase' ] [ time_n ] )
rmm_amplitude_in = np.array ( rmm_file [ 'amplitude' ] )
rmm_list = get_rmm_composite_list ( phase_names , model_yyyymmdd , rmm_yyyymmdd , rmm_phase_in , rmm_amplitude_in , compoiste_amplitude_threshold , composite_start_month , composite_end_month )

##### make composites
ERA_eke850_composite = np.empty ( ( len ( phase_names ) , len ( model_lat_in ) , len ( model_lon_in ) ) , dtype=ERA_eke850_anomaly.dtype )
for phase_n in range ( len ( phase_names ) ) : ERA_eke850_composite [ phase_n , : , : ] = np.nanmean ( ERA_eke850_anomaly [ rmm_list [ phase_n ] , ( start_week - 1 ) * 7 : end_week * 7 , : , : ] , axis=( 0 , 1 ) )
ERA_eke850_weeks_avg = np.nanmean ( ERA_eke850_anomaly [ : , ( start_week - 1 ) * 7 : end_week * 7 , : , : ] , axis=1 )
model_eke850_composite = np.empty ( ( len ( phase_names ) , len ( model_lat_in ) , len ( model_lon_in ) ) , dtype=model_eke850_anomaly.dtype )
for phase_n in range ( len ( phase_names ) ) : model_eke850_composite [ phase_n , : , : ] = np.nanmean ( model_eke850_anomaly [ rmm_list [ phase_n ] , ( start_week - 1 ) * 7 : end_week * 7 , : , : ] , axis=( 0 , 1 ) )
model_eke850_weeks_avg = np.nanmean ( model_eke850_anomaly [ : , ( start_week - 1 ) * 7 : end_week * 7 , : , : ] , axis=1 )

ERA_z500_composite = np.empty ( ( len ( phase_names ) , len ( model_lat_in ) , len ( model_lon_in ) ) , dtype=ERA_z500_anomaly.dtype )
for phase_n in range ( len ( phase_names ) ) : ERA_z500_composite [ phase_n , : , : ] = np.nanmean ( ERA_z500_anomaly [ rmm_list [ phase_n ] , ( start_week - 1 ) * 7 : end_week * 7 , : , : ] , axis=( 0 , 1 ) )
ERA_z500_weeks_avg = np.nanmean ( ERA_z500_anomaly [ : , ( start_week - 1 ) * 7 : end_week * 7 , : , : ] , axis=1 )
model_z500_composite = np.empty ( ( len ( phase_names ) , len ( model_lat_in ) , len ( model_lon_in ) ) , dtype=model_z500_anomaly.dtype )
for phase_n in range ( len ( phase_names ) ) : model_z500_composite [ phase_n , : , : ] = np.nanmean ( model_z500_anomaly [ rmm_list [ phase_n ] , ( start_week - 1 ) * 7 : end_week * 7 , : , : ] , axis=( 0 , 1 ) )
model_z500_weeks_avg = np.nanmean ( model_z500_anomaly [ : , ( start_week - 1 ) * 7 : end_week * 7 , : , : ] , axis=1 )

##### test significance
season_list = get_season_list ( model_yyyymmdd , composite_start_month , composite_end_month )
ERA_eke850_significance = np.empty ( ERA_eke850_composite.shape , dtype=ERA_eke850_anomaly.dtype )
for phase_n in range ( len ( phase_names ) ) : ERA_eke850_significance [ phase_n , : , : ] = test_sig_np ( ERA_eke850_weeks_avg , ERA_eke850_composite [ phase_n , : , : ] , bootstrap_size , len ( rmm_list [ phase_n ] ) )
model_eke850_significance = np.empty ( model_eke850_composite.shape , dtype=model_eke850_anomaly.dtype )
for phase_n in range ( len ( phase_names ) ) : model_eke850_significance [ phase_n , : , : ] = test_sig_np ( model_eke850_weeks_avg , model_eke850_composite [ phase_n , : , : ] , bootstrap_size , len ( rmm_list [ phase_n ] ) )

ERA_z500_significance = np.empty ( ERA_z500_composite.shape , dtype=ERA_z500_anomaly.dtype )
for phase_n in range ( len ( phase_names ) ) : ERA_z500_significance [ phase_n , : , : ] = test_sig_np ( ERA_z500_weeks_avg , ERA_z500_composite [ phase_n , : , : ] , bootstrap_size , len ( rmm_list [ phase_n ] ) )
model_z500_significance = np.empty ( model_z500_composite.shape , dtype=model_z500_anomaly.dtype )
for phase_n in range ( len ( phase_names ) ) : model_z500_significance [ phase_n , : , : ] = test_sig_np ( model_z500_weeks_avg , model_z500_composite [ phase_n , : , : ] , bootstrap_size , len ( rmm_list [ phase_n ] ) )

##### pattern correlation
pattern_correlation_eke850 = np.empty ( ( len ( pattern_corr_regions ) , len ( phase_names ) ) , dtype=model_eke850_composite.dtype )
pattern_correlation_z500   = np.empty ( ( len ( pattern_corr_regions ) , len ( phase_names ) ) , dtype=ERA_z500_composite.dtype )
for region_n in range ( len ( pattern_corr_regions ) ) :
    for phase_n in range ( len ( phase_names ) ) :
        pattern_correlation_eke850 [ region_n , phase_n ] = calcPatCorr ( ERA_eke850_composite [ phase_n , : , : ] , model_eke850_composite [ phase_n , : , : ] , np.array ( model_lat_in ) , regions_south_north [ region_n ] [ 0 ] , regions_south_north [ region_n ] [ 1 ] , np.array ( model_lon_in ) , regions_west_east [ region_n ] [ 0 ] , regions_west_east [ region_n ] [ 1 ] )
        pattern_correlation_z500 [ region_n , phase_n ] = calcPatCorr ( ERA_z500_composite [ phase_n , : , : ] , model_z500_composite [ phase_n , : , : ] , np.array ( model_lat_in ) , regions_south_north [ region_n ] [ 0 ] , regions_south_north [ region_n ] [ 1 ] , np.array ( model_lon_in ) , regions_west_east [ region_n ] [ 0 ] , regions_west_east [ region_n ] [ 1 ] )

##### make plots
wks = Ngl.open_wks ( "pdf" , PLOT_DIR )
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
res_polar_color.cnMinLevelValF       = -34.
res_polar_color.cnMaxLevelValF       = 34.
res_polar_color.cnLevelSpacingF      = 4.
res_polar_color.sfXArray             = np.array ( model_lon_in )
res_polar_color.sfYArray             = np.array ( model_lat_in )

res_significance                     = Ngl.Resources ( )
res_significance.nglFrame            = False
res_significance.nglDraw             = False
res_significance.cnFillOn            = False
res_significance.cnLinesOn           = True
res_significance.cnLineLabelsOn      = False
res_significance.cnLevelSelectionMode = "ManualLevels"
res_significance.cnMinLevelValF      = test_confidence_level
res_significance.cnMaxLevelValF      = 1 - test_confidence_level
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
res_polar_color_z500.cnMinLevelValF       = -125
res_polar_color_z500.cnMaxLevelValF       = 125.
res_polar_color_z500.cnLevelSpacingF      = 10.
res_polar_color_z500.sfXArray             = np.array ( model_lon_in )
res_polar_color_z500.sfYArray             = np.array ( model_lat_in )

for phase_n in range ( len ( phase_names ) ) :
    res_polar_color.tiMainString = "reanalysis eke850 phase" + phase_names [ phase_n ]
    plot = Ngl.contour_map ( wks , ERA_eke850_composite [ phase_n , : , : ] , res_polar_color )
    plot1 = Ngl.contour ( wks , ERA_eke850_significance [ phase_n , : , : ] , res_significance )
    Ngl.overlay ( plot , plot1 )
    Ngl.draw ( plot )
    Ngl.frame ( wks )
    res_polar_color.tiMainString = "model eke850 phase" + phase_names [ phase_n ]
    plot = Ngl.contour_map ( wks , model_eke850_composite [ phase_n , : , : ] , res_polar_color )
    plot1 = Ngl.contour ( wks , model_eke850_significance [ phase_n , : , : ] , res_significance )
    Ngl.overlay ( plot , plot1 )
    Ngl.draw ( plot )
    Ngl.frame ( wks )

for phase_n in range ( len ( phase_names ) ) :
    res_polar_color_z500.tiMainString = "reanalysis z500 phase" + phase_names [ phase_n ]
    plot = Ngl.contour_map ( wks , ERA_z500_composite [ phase_n , : , : ] , res_polar_color_z500 )
    plot1 = Ngl.contour ( wks , ERA_z500_significance [ phase_n , : , : ] , res_significance )
    Ngl.overlay ( plot , plot1 )
    Ngl.draw ( plot )
    Ngl.frame ( wks )
    res_polar_color_z500.tiMainString = "model z500 phase" + phase_names [ phase_n ]
    plot = Ngl.contour_map ( wks , model_z500_composite [ phase_n , : , : ] , res_polar_color_z500 )
    plot1 = Ngl.contour ( wks , model_z500_significance [ phase_n , : , : ] , res_significance )
    Ngl.overlay ( plot , plot1 )
    Ngl.draw ( plot )
    Ngl.frame ( wks )

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
#txres.txFont        = "helvetica-bold"
txres.txFontHeightF = 0.02
txres.txJust        = "BottomCenter"

colors  = [ "blue" , "red" , "orange" , "magenta" ]

for region_n in range ( len ( pattern_corr_regions ) ) :
    one_to_one = np.array ( [ pattern_correlation_eke850 [ region_n , 0 ] , pattern_correlation_eke850 [ region_n , 1 ] , res1.trXMinF , res1.trXMaxF ] )
    res1.tiMainString = pattern_corr_regions [ region_n ] + " " + str ( regions_south_north [ region_n ] [ 0 ] ) + "-" + str ( regions_south_north [ region_n ] [ 1 ] ) + "N " + str ( regions_west_east [ region_n ] [ 0 ] ) + "-" + str ( regions_west_east [ region_n ] [ 1 ] )
    res1.tiXAxisString = "z500 pattern correlation"
    res1.tiYAxisString = "eke850 pattern correlation"
    plot = Ngl.xy ( wks , one_to_one , one_to_one , res1 )
    for phase_n in range ( len ( phase_names ) ) :
        gsres.gsMarkerColor = colors [ phase_n ]
        prim6 = Ngl.add_polymarker ( wks , plot , pattern_correlation_z500 [ region_n , phase_n ] , pattern_correlation_eke850 [ region_n , phase_n ] , gsres )
        txres.txFontColor   = colors [ phase_n ]
        text1 = Ngl.add_text ( wks , plot , "phase" + phase_names [ phase_n ] , pattern_correlation_z500 [ region_n , phase_n ] , pattern_correlation_eke850 [ region_n , phase_n ] - .15 , txres )
    Ngl.draw ( plot )
    Ngl.frame ( wks )

Ngl.delete_wks ( wks )
