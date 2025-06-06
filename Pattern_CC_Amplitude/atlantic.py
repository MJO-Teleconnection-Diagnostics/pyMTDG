#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import numpy as np
import datetime
from datetime import date, timedelta
import netCDF4
import matplotlib.pyplot as plt # matplotlib version 3.2 and custom version 3.3
import proplot as plot
import cartopy
import pandas as pd
import yaml
import os
import glob
import copy


import sys
sys.path.insert(0, '../Utils')
from pathlib import Path
from obs_utils import *
from fcst_utils import *
from PCC_utils import *


config_file=Path('../driver/config.yml').resolve()
if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        raise

# ## Read in observed files

if (dictionary['ERAI']==True):
    fil_z500_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/z500/daily/z500.ei.oper.an.pl.regn128sc.1979.2019.nc'
    ds_obs_name='ERAI'
    ds_z500_obs = xr.open_dataset(fil_z500_obs,chunks='auto')
    
if (dictionary['ERAI']==False):
    fil_z500_obs=dictionary['Path to Z500 observation data files']
    ds_obs_name='OBS'
    nf,ds_z500_obs0=open_user_obs_fil(fil_z500_obs)
        
z500_obs=get_variable_from_dataset(ds_z500_obs)

# Get the forecast period from the provided Start_Date -- End_Date period
yyyymmdd_Begin=dictionary['START_DATE']
tBegin=yyyymmdd_Begin[0:4]+'-'+yyyymmdd_Begin[4:6]+'-'+yyyymmdd_Begin[6:8]
yyyymmdd_End=dictionary['END_DATE']
tEnd=yyyymmdd_End[0:4]+'-'+yyyymmdd_End[4:6]+'-'+yyyymmdd_End[6:8]


fcst_dir=dictionary['Path to Z500 model data files']
ds_fcst_name=dictionary['model name']
ds_names=[ds_obs_name,ds_fcst_name]

fcst_files=np.sort(glob.glob(str(fcst_dir+'*.nc')))
print(fcst_files)
ds_z500_fcst=xr.open_mfdataset(fcst_files,combine='nested',concat_dim='time',parallel=True)
z500_fcst=get_variable_from_dataset(ds_z500_fcst)

# Interpolate reforecast data to ERAI grid (regular 0.75 x 0.75)
if (dictionary['ERAI']==True):
    rgrd_z500_fcst,rgrd_z500_obs=regrid(z500_fcst,z500_obs,ds_z500_fcst.latitude,ds_z500_fcst.longitude,
                                                       z500_obs.latitude,z500_obs.longitude,scalar=True)
else:
    rgrd_z500_fcst = copy.deepcopy(z500_fcst)
    rgrd_z500_obs = copy.deepcopy(z500_obs)
    
# Calculate forecast anomalies
if (dictionary['Daily Anomaly'] == True):
    z500_fcst_anom=calcAnom(rgrd_z500_fcst,'z500_anom')
# Reshape the forecast data
    z500_fcst_anom_reshape=reshape_forecast(z500_fcst_anom,nfc=dictionary['length of forecasts'])
# Rename the coordinates
    z500_fcst_anom_reshape=z500_fcst_anom_reshape.rename({'time': 'initial_date','forecast_day': 'time'})
# Get model time
    model_yyyymmdd=z500_fcst_anom_reshape['initial_date']
if (dictionary['Daily Anomaly'] == False):
    z500_fcst_anom=rgrd_z500_fcst
    z500_fcst_anom_reshape=z500_fcst_anom_reshape.rename({'time': 'initial_date','forecast_day': 'time'})
    model_yyyymmdd=z500_fcst_anom_reshape['initial_date']
del rgrd_z500_fcst

#calculate observed anomalies
if (dictionary['Daily Anomaly'] == True):
    var_name='z'
    z500_obs_anom=calcAnomObs(rgrd_z500_obs.sel(time=slice(tBegin,tEnd)),var_name)
if (dictionary['Daily Anomaly'] == False):
    z500_obs_anom=z500_obs
    del z500_obs


# Read observed time, latitude, and longitude
obs_time_in = z500_obs_anom['time']
obs_yyyymmdd = np.array ( obs_time_in.dt.year * 10000 + obs_time_in.dt.month * 100 + obs_time_in.dt.day )
obs_lat_in=ds_z500_obs['latitude']
obs_lon_in=ds_z500_obs['longitude']


if (dictionary['RMM']==True):
    fil_rmm_obs=dictionary['Path to RMM observation data file']
    ds_rmm=xr.open_dataset(fil_rmm_obs)
if (dictionary['RMM']==False):
    fil_rmm_erai=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'
    ds_rmm=xr.open_dataset(fil_rmm_erai,decode_times=False)

times=ds_rmm.time
init_time=date(1960,1,1)+timedelta(int(times[0]))
time=[]
for i in range(len(times)):
        time.append(init_time+timedelta(i))

ds_rmm['time'] = pd.to_datetime(time,format="%Y/%m/%d")

phase=np.array(ds_rmm['phase'])
amplitude=np.array(ds_rmm['amplitude'])
phase_int = np.array(list(map(np.int_, phase)))


rmm_time_in = ds_rmm['time']
rmm_yyyymmdd = np.array ( rmm_time_in.dt.year * 10000 + rmm_time_in.dt.month * 100 + rmm_time_in.dt.day )
model_time_in = z500_fcst_anom_reshape['initial_date']
model_yyyymmdd = np.array ( model_time_in.dt.year * 10000 + model_time_in.dt.month * 100 + model_time_in.dt.day )


composite_start_month = 11
composite_end_month   = 3
compoiste_amplitude_threshold = 1.
phase_names = [ "8-1" , "2-3" , "4-5" , "6-7" ]
rmm_list = get_rmm_composite_list ( phase_names , model_yyyymmdd , rmm_yyyymmdd , phase_int , amplitude , compoiste_amplitude_threshold , composite_start_month , composite_end_month )


timelag=z500_fcst_anom_reshape['time']
rmm_list_obs_67 = [ ]
rmm_tem_list_67=rmm_list[3] 
rmm_list_obs_67 = np.empty (( len (timelag),len (rmm_tem_list_67)) ,dtype=int)
time_n=0
obs_time_in = z500_obs_anom['time']
obs_yyyymmdd = np.array ( obs_time_in.dt.year * 10000 + obs_time_in.dt.month * 100 + obs_time_in.dt.day )
for time_step in range ( len ( obs_yyyymmdd ) ) :
    for irmm in range ( len ( rmm_tem_list_67 ) ) : 
        if obs_yyyymmdd [ time_step ] == model_yyyymmdd[rmm_tem_list_67 [irmm]] : 
            time_n=time_n+1
            for itime in range (len (timelag)):
                rmm_list_obs_67 [itime,time_n-1]=time_step+itime

rmm_list_obs_23 = [ ]
rmm_tem_list_23=rmm_list[1] 
rmm_list_obs_23 = np.empty (( len (timelag),len (rmm_tem_list_23)) ,dtype=int)
time_n=0
for time_step in range ( len ( obs_yyyymmdd ) ) :
    for irmm in range ( len ( rmm_tem_list_23 ) ) : 
        if obs_yyyymmdd [ time_step ] == model_yyyymmdd[rmm_tem_list_23 [irmm]] : 
            time_n=time_n+1
            for itime in range (len (timelag)):
                rmm_list_obs_23 [itime,time_n-1]=time_step+itime


#########Euro-Atlantic region Pattern CC & Relative amplitude line plots#############
z500_obs_anom.load()
lat_min=20
lat_max=80
lon_min1=300
lon_max1=360
lon_min2=0
lon_max2=90
rmm_list_model_67=rmm_list [3]
rmm_list_model_23=rmm_list [1]
pcc_ufs_p23 = patterncc_atlantic(timelag,rmm_list_obs_23,rmm_list_model_23,
                                 z500_fcst_anom_reshape,z500_obs_anom,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2)
pcc_ufs_p67 = patterncc_atlantic(timelag,rmm_list_obs_67,rmm_list_model_67,
                                 z500_fcst_anom_reshape,z500_obs_anom,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2)             
pcc_ufs_p23=np.mean ( pcc_ufs_p23,axis= 1   )
pcc_ufs_p67=np.mean ( pcc_ufs_p67,axis= 1   )


amp_ufs_p23 = amplitude_metric_atlantic(timelag,rmm_list_obs_23,rmm_list_model_23,
                                        z500_fcst_anom_reshape,z500_obs_anom,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2)
amp_ufs_p67 = amplitude_metric_atlantic(timelag,rmm_list_obs_67,rmm_list_model_67,
                                        z500_fcst_anom_reshape,z500_obs_anom,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2)       
amp_ufs_p23=np.mean ( amp_ufs_p23,axis= 1   )
amp_ufs_p67=np.mean ( amp_ufs_p67,axis= 1   )

bootstrap_size = 1000
P23_atlantic_low,P23_atlantic_high=test_significance_atlantic(bootstrap_size,timelag,rmm_list_obs_23,rmm_list_model_23,z500_fcst_anom_reshape,z500_obs_anom,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2,PCC=True)
P67_atlantic_low,P67_atlantic_high=test_significance_atlantic(bootstrap_size,timelag,rmm_list_obs_67,rmm_list_model_67,z500_fcst_anom_reshape,z500_obs_anom,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2,PCC=True)
P23_atlantic_low_amp,P23_atlantic_high_amp=test_significance_atlantic(bootstrap_size,timelag,rmm_list_obs_23,rmm_list_model_23,z500_fcst_anom_reshape,z500_obs_anom,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2,amp=True)
P67_atlantic_low_amp,P67_atlantic_high_amp=test_significance_atlantic(bootstrap_size,timelag,rmm_list_obs_67,rmm_list_model_67,z500_fcst_anom_reshape,z500_obs_anom,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2,amp=True)


import matplotlib.lines as mlines
fig = plt.figure(figsize=(12,6))
#x = np.linspace(0, 34, 35)
x = np.linspace(0, dictionary['length of forecasts'] - 1, dictionary['length of forecasts'])
if(dictionary['length of forecasts']>=35):
    xend=35
if(dictionary['length of forecasts']<35):
    xend=dictionary['length of forecasts']
plt.rcParams['font.size'] = '14'
def addlegend(ax):
    P23 = mlines.Line2D([],[], color='b', label='Phases 2&3')
    P67 = mlines.Line2D([],[], color='r', label='Phases 6&7')
    ax.legend(handles=[P23, P67], ncol=1, fontsize=12)

ncol = 2
nrow = 1
for i in range(ncol):
    ax = fig.add_subplot(nrow,ncol,i+1)
    if i==0:
        ax.set_title('a. Pattern Correlation_Euro-Atlantic',loc='left')
        ax.plot(pcc_ufs_p23[0:xend],color='b',linewidth=2,label='Phases 2&3')
        ax.fill_between(x[0:xend], P23_atlantic_low[0:xend], P23_atlantic_high[0:xend], color='C0',alpha=0.2)
        ax.plot(pcc_ufs_p67[0:xend],color='r',linewidth=2,label='Phases 6&7')
        ax.fill_between(x[0:xend], P67_atlantic_low[0:xend], P67_atlantic_high[0:xend], color='C3',alpha=0.2)
    else:
        ax.set_title('b. Relative Amplitude_Euro-Atlantic',loc='left')
        ax.plot(amp_ufs_p23[0:xend],color='b',linewidth=2,label='Phases 2&3')
        ax.fill_between(x[0:xend], P23_atlantic_low_amp[0:xend], P23_atlantic_high_amp[0:xend], color='C0',alpha=0.2)
        ax.plot(amp_ufs_p67[0:xend],color='r',linewidth=2,label='Phases 6&7')
        ax.fill_between(x[0:xend], P67_atlantic_low_amp[0:xend], P67_atlantic_high_amp[0:xend], color='C3',alpha=0.2)
    if i==0: addlegend(ax)
    ax.grid(True)
    
# save
if not os.path.exists('../output/PatternCC_Atlantic/'+ds_fcst_name): 
    os.mkdir('../output/PatternCC_Atlantic/'+ds_fcst_name)
figname='z500_PatternCC&Amplitude_Atlantic' 
fig.savefig('../output/PatternCC_Atlantic/'+ds_fcst_name+'/'+figname+'.jpg',dpi=300)

write_output_text('../output/PatternCC_Atlantic/'+ds_fcst_name+'/'+figname,
        ['PatternCC P23','PatternCC_low P23','PatternCC_high P23',
         'PatternCC P67','PatternCC_low P67','PatternCC _high P67',
         'RelAmp P23','RelAmp_low P23','RelAmp_high P23',
         'RelAmp P67','RelAmp_low P67','RelAmp_high P67'],
        [pcc_ufs_p23,P23_atlantic_low, P23_atlantic_high,
         pcc_ufs_p67,P67_atlantic_low, P67_atlantic_high,
         amp_ufs_p23,P23_atlantic_low_amp, P23_atlantic_high_amp,
         amp_ufs_p67,P67_atlantic_low_amp, P67_atlantic_high_amp])

if (dictionary['Compute composites']==True):
    model_z500_composite_p23=composites_model(rmm_list_model_23,z500_fcst_anom_reshape,obs_lat_in,obs_lon_in)
    model_z500_composite_p67=composites_model(rmm_list_model_67,z500_fcst_anom_reshape,obs_lat_in,obs_lon_in)


    obs_z500_composite_p23=composites_obs(rmm_list_obs_23,z500_obs_anom,obs_lat_in,obs_lon_in)
    obs_z500_composite_p67=composites_obs(rmm_list_obs_67,z500_obs_anom,obs_lat_in,obs_lon_in)


    coords= {
       'phase':[1,2,3,4],
       'latitude':obs_lat_in,
       'longitude':obs_lon_in
   }


    xr_obs_z500_composite_p23= xr.DataArray(obs_z500_composite_p23,coords)
    xr_obs_z500_composite_p67= xr.DataArray(obs_z500_composite_p67,coords)
    xr_model_z500_composite_p23= xr.DataArray(model_z500_composite_p23,coords)
    xr_model_z500_composite_p67= xr.DataArray(model_z500_composite_p67,coords)


#########Euro-Atlantic region#############
    lat_min=20
    lat_max=80
    lon_min1=300
    lon_max1=360
    lon_min2=0
    lon_max2=90
    PCC_Atlantic_composite_p23_round=np.empty( ( 4) ,dtype=float)
    PCC_Atlantic_composite_p67_round=np.empty( ( 4) ,dtype=float)
    PCC_Atlantic_composite_p23=np.empty( ( 4) ,dtype=float)
    PCC_Atlantic_composite_p67=np.empty( ( 4) ,dtype=float)
    for i in range ( 4 ) :
        res_temp_p23=correlate_atlantic(xr_obs_z500_composite_p23[i,:,:],
                                        xr_model_z500_composite_p23[i,:,:],lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2)
        res_temp_p67=correlate_atlantic(xr_obs_z500_composite_p67[i,:,:],
                                        xr_model_z500_composite_p67[i,:,:],lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2)
        PCC_Atlantic_composite_p23[i]=res_temp_p23[0,1]
        PCC_Atlantic_composite_p67[i]=res_temp_p67[0,1]
        PCC_Atlantic_composite_p23_round[i] = round(PCC_Atlantic_composite_p23[i], 2)
        PCC_Atlantic_composite_p67_round[i] = round(PCC_Atlantic_composite_p67[i], 2)


# Plot Euro-Atlantic region Z500 composites

    lags = ['1','2','3','4'] # in weeks
    lon = obs_lon_in
    lat = obs_lat_in
    levs_anom = np.arange(-60,60,10)
    fig=plot.figure(refwidth=5)
    axes=fig.subplots(nrows=4,ncols=4,proj='cyl',proj_kw={'lon_0': 0})

    axes.format(coast=True, latlines=20, lonlines=40,
                  lonlim=(-60,90),latlim=(20,80),
                  lonlabels=(True,False),
                  latlabels=(True,False),abc=True)

    for ilag, lag in enumerate(lags):


       # Observations
        h1=axes[ilag,0].contourf(lon,lat,xr_obs_z500_composite_p23[ilag],extend='both',
                       cmap='RdBu_r', levels=levs_anom)
        axes[ilag,0].format(title=ds_obs_name + ' Phases 2&3_Week ' + lag)
    
       # Forecast
        h2=axes[ilag,1].contourf(lon,lat,xr_model_z500_composite_p23[ilag],extend='both',
                       cmap='RdBu_r', levels=levs_anom)
        axes[ilag,1].format(title=ds_fcst_name + ' Phases 2&3_Week ' + lag)
        axes[ilag,1].set_title(PCC_Atlantic_composite_p23_round[ilag], loc = "right")
    
        h3=axes[ilag,2].contourf(lon,lat,xr_obs_z500_composite_p67[ilag],extend='both',
                       cmap='RdBu_r', levels=levs_anom)
        axes[ilag,2].format(title=ds_obs_name + ' Phases 6&7_Week ' + lag)
    
        h4=axes[ilag,3].contourf(lon,lat,xr_model_z500_composite_p67[ilag],extend='both',
                       cmap='RdBu_r', levels=levs_anom)
        axes[ilag,3].format(title=ds_fcst_name + ' Phases 6&7_Week ' + lag)
        axes[ilag,3].set_title(PCC_Atlantic_composite_p67_round[ilag], loc = "right")

    fig.colorbar(h1, loc='b', extend='both', label='Z500 anomaly',
                     width='1.5em', extendsize='2em', shrink=0.3,)


    # save
    if not os.path.exists('../output/PatternCC_Atlantic/'+ds_fcst_name): 
        os.mkdir('../output/PatternCC_Atlantic/'+ds_fcst_name)
    figname='z500_composites_Atlantic' 
    fig.savefig('../output/PatternCC_Atlantic/'+ds_fcst_name+'/'+figname+'.jpg',dpi=300)

