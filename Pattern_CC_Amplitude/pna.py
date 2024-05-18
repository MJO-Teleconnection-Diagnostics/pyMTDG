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


import sys
sys.path.insert(0, '../Utils')
from pathlib import Path
from obs_utils import *
from fcst_utils import *
from PCC_utils import *


config_file=Path('../driver/config.yml').resolve()
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)


# ## Read in observed files

if (dictionary['ERAI']==True):
    fil_z500_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/z500/z500.ei.oper.an.pl.regn128sc.1979.2019.nc'
    ds_obs_name='ERAI'
if (dictionary['ERAI']==False):
    fil_z500_obs=dictionary['Path to observational data files']
    ds_obs_name='OBS'
ds_z500_obs=xr.open_dataset(fil_z500_obs)
z500_obs=get_variable_from_dataset(ds_z500_obs)


# Get the forecast period from the provided Start_Date -- End_Date period
yyyymmdd_Begin=dictionary['START_DATE']
tBegin=yyyymmdd_Begin[0:4]+'-'+yyyymmdd_Begin[4:6]+'-'+yyyymmdd_Begin[6:8]
yyyymmdd_End=dictionary['END_DATE']
tEnd=yyyymmdd_End[0:4]+'-'+yyyymmdd_End[4:6]+'-'+yyyymmdd_End[6:8]

#calculate observed anomalies
if (dictionary['Daily Anomaly'] == True):
    var_name='z'
    erai_anomaly=calcAnomObs(z500_obs.sel(time=slice(tBegin,tEnd)),var_name)
if (dictionary['Daily Anomaly'] == False):
    erai_anomaly=z500_obs
    del z500_obs


# Read observed time, latitude, and longitude
erai_time_in = erai_anomaly['time']
erai_yyyymmdd = np.array ( erai_time_in.dt.year * 10000 + erai_time_in.dt.month * 100 + erai_time_in.dt.day )
era_lat_in=ds_z500_obs['latitude']
era_lon_in=ds_z500_obs['longitude']


fcst_dir=dictionary['Path to Z500 model data files']
ds_fcst_name=dictionary['model name']
ds_names=[ds_obs_name,ds_fcst_name]


fcst_files=fcst_dir+'*.nc'
print(fcst_files)
ds_z500_fcst=xr.open_mfdataset(fcst_files,combine='nested',concat_dim='time',parallel=True)
z500_fcst=get_variable_from_dataset(ds_z500_fcst)

# Interpolate reforecast data to ERAI grid (regular 0.75 x 0.75)
rgrd_z500_fcst=regrid_scalar_spharm(ds_z500_fcst['z500'],ds_z500_fcst.latitude,ds_z500_fcst.longitude,
                                                        ds_z500_obs.latitude,ds_z500_obs.longitude)
# Calculate forecast anomalies
z500_fcst_anom=calcAnom(rgrd_z500_fcst,'z500_anom')
# Reshape the forecast data
z500_fcst_anom_reshape=reshape_forecast(z500_fcst_anom,nfc=dictionary['length of forecasts'])
# Rename the coordinates
z500_fcst_anom_reshape=z500_fcst_anom_reshape.rename({'time': 'initial_date','forecast_day': 'time'})
# Get model time
model_yyyymmdd=z500_fcst_anom_reshape['initial_date']

if (dictionary['RMM']==False):
    fil_rmm_erai=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'

ds_rmm=xr.open_dataset(fil_rmm_erai,decode_times=False)

times=ds_rmm.time
init_time=date(1960,1,1)+timedelta(int(times[0]))
time=[]
for i in range(len(times)):
        time.append(init_time+timedelta(i))

ds_rmm['time'] = pd.to_datetime(time,format="%Y/%m/%d")

#fil_rmm_erai='/expanse/nfs/cw3e/cwp137/_From_Comet/UFS/rmm_ERA-Interim.nc'
#ds_rmm=xr.open_dataset(fil_rmm_erai,decode_times=False)
#times=ds_rmm['amplitude'].time
#init_time=date(1960,1,1)+timedelta(int(times[0]))
#time=[]
#for i in range(len(times)):
#        time.append(init_time+timedelta(i))

phase=np.array(ds_rmm['phase'])
amplitude=np.array(ds_rmm['amplitude'])
phase_int = np.array(list(map(np.int_, phase)))


ds_rmm['time'] = pd.to_datetime(time,format="%Y/%m/%d")
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
rmm_list_ERA_67 = [ ]
rmm_tem_list_67=rmm_list[3] 
rmm_list_ERA_67 = np.empty (( len (timelag),len (rmm_tem_list_67)) ,dtype=int)
time_n=0
erai_time_in = erai_anomaly['time']
erai_yyyymmdd = np.array ( erai_time_in.dt.year * 10000 + erai_time_in.dt.month * 100 + erai_time_in.dt.day )
for time_step in range ( len ( erai_yyyymmdd ) ) :
    for irmm in range ( len ( rmm_tem_list_67 ) ) : 
        if erai_yyyymmdd [ time_step ] == model_yyyymmdd[rmm_tem_list_67 [irmm]] : 
            time_n=time_n+1
            for itime in range (len (timelag)):
                rmm_list_ERA_67 [itime,time_n-1]=time_step+itime


rmm_list_ERA_23 = [ ]
rmm_tem_list_23=rmm_list[1] 
rmm_list_ERA_23 = np.empty (( len (timelag),len (rmm_tem_list_23)) ,dtype=int)
time_n=0
for time_step in range ( len ( erai_yyyymmdd ) ) :
    for irmm in range ( len ( rmm_tem_list_23 ) ) : 
        if erai_yyyymmdd [ time_step ] == model_yyyymmdd[rmm_tem_list_23 [irmm]] : 
            time_n=time_n+1
            for itime in range (len (timelag)):
                rmm_list_ERA_23 [itime,time_n-1]=time_step+itime


#########PNA region Pattern CC & Relative amplitude line plots#############
lat_min=20
lat_max=80
lon_min=120
lon_max=300
rmm_list_model_67=rmm_list [3]
rmm_list_model_23=rmm_list [1]
pcc_ufs_p23 = patterncc(timelag,rmm_list_ERA_23,rmm_list_model_23,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max)
pcc_ufs_p67 = patterncc(timelag,rmm_list_ERA_67,rmm_list_model_67,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max)       
pcc_ufs_p23=np.mean ( pcc_ufs_p23,axis= 1   )
pcc_ufs_p67=np.mean ( pcc_ufs_p67,axis= 1   )


amp_ufs_p23 = amplitude_metric(timelag,rmm_list_ERA_23,rmm_list_model_23,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max)
amp_ufs_p67 = amplitude_metric(timelag,rmm_list_ERA_67,rmm_list_model_67,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max)       
amp_ufs_p23=np.mean ( amp_ufs_p23,axis= 1   )
amp_ufs_p67=np.mean ( amp_ufs_p67,axis= 1   )

bootstrap_size = 1000
P23_PNA_low=test_significance(bootstrap_size,timelag,rmm_list_ERA_23,rmm_list_model_23,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max,PCC=True)[0]
P23_PNA_high=test_significance(bootstrap_size,timelag,rmm_list_ERA_23,rmm_list_model_23,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max,PCC=True)[1]
P67_PNA_low=test_significance(bootstrap_size,timelag,rmm_list_ERA_67,rmm_list_model_67,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max,PCC=True)[0]
P67_PNA_high=test_significance(bootstrap_size,timelag,rmm_list_ERA_67,rmm_list_model_67,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max,PCC=True)[1]
P23_PNA_low_amp=test_significance(bootstrap_size,timelag,rmm_list_ERA_23,rmm_list_model_23,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max,amp=True)[0]
P23_PNA_high_amp=test_significance(bootstrap_size,timelag,rmm_list_ERA_23,rmm_list_model_23,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max,amp=True)[1]
P67_PNA_low_amp=test_significance(bootstrap_size,timelag,rmm_list_ERA_67,rmm_list_model_67,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max,amp=True)[0]
P67_PNA_high_amp=test_significance(bootstrap_size,timelag,rmm_list_ERA_67,rmm_list_model_67,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max,amp=True)[1]


import matplotlib.lines as mlines
fig = plt.figure(figsize=(12,6))
x = np.linspace(0, 34, 35)
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
        ax.set_title('a. Pattern Correlation_PNA',loc='left')
        ax.plot(pcc_ufs_p23,color='b',linewidth=2,label='Phases 2&3')
        ax.fill_between(x, P23_PNA_low, P23_PNA_high, color='C0',alpha=0.2)
        ax.plot(pcc_ufs_p67,color='r',linewidth=2,label='Phases 6&7')
        ax.fill_between(x, P67_PNA_low, P67_PNA_high, color='C3',alpha=0.2)
    else:
        ax.set_title('b. Relative Amplitude_PNA',loc='left')
        ax.plot(amp_ufs_p23,color='b',linewidth=2,label='Phases 2&3')
        ax.fill_between(x, P23_PNA_low_amp, P23_PNA_high_amp, color='C0',alpha=0.2)
        ax.plot(amp_ufs_p67,color='r',linewidth=2,label='Phases 6&7')
        ax.fill_between(x, P67_PNA_low_amp, P67_PNA_high_amp, color='C3',alpha=0.2)
    if i==0: addlegend(ax)
    ax.grid(True)

# save figures
if not os.path.exists('../output/PatternCC_PNA/'+dictionary['model name']): 
    os.mkdir('../output/PatternCC_PNA/'+dictionary['model name'])
figname='z500_PatternCC&Amplitude_PNA' 
fig.savefig('../output/PatternCC_PNA/'+dictionary['model name']+'/'+figname+'.jpg',dpi=300)

#save data

if not os.path.exists('../output/PatternCC_PNA/'+dictionary['model name']):
    os.mkdir('../output/PatternCC_PNA/'+dictionary['model name'])

write_output_text('../output/PatternCC_PNA/'+dictionary['model name']+'/'+figname,
        ['PatternCC P23','PatternCC_low P23','PatternCC_high P23',
         'PatternCC P67','PatternCC_low P67','PatternCC _high P67',
         'RelAmp P23','RelAmp_low P23','RelAmp_high P23',
         'RelAmp P67','RelAmp_low P67','RelAmp_high P67'],
        [pcc_ufs_p23,P23_PNA_low, P23_PNA_high,
         pcc_ufs_p67,P67_PNA_low, P67_PNA_high,
         amp_ufs_p23,P23_PNA_low_amp, P23_PNA_high_amp,
         amp_ufs_p67,P67_PNA_low_amp, P67_PNA_high_amp])

if (dictionary['Compute composites']==True):

   model_z500_composite_p23=composites_model(rmm_list_model_23,z500_fcst_anom_reshape,era_lat_in,era_lon_in)
   model_z500_composite_p67=composites_model(rmm_list_model_67,z500_fcst_anom_reshape,era_lat_in,era_lon_in)



   ERA5_z500_composite_p23=composites_era(rmm_list_ERA_23,erai_anomaly,era_lat_in,era_lon_in)
   ERA5_z500_composite_p67=composites_era(rmm_list_ERA_67,erai_anomaly,era_lat_in,era_lon_in)



   coords= {
       'phase':[1,2,3,4],
       'latitude':era_lat_in,
       'longitude':era_lon_in
   }



   xr_ERA5_z500_composite_p23= xr.DataArray(ERA5_z500_composite_p23,coords)
   xr_ERA5_z500_composite_p67= xr.DataArray(ERA5_z500_composite_p67,coords)
   xr_model_z500_composite_p23= xr.DataArray(model_z500_composite_p23,coords)
   xr_model_z500_composite_p67= xr.DataArray(model_z500_composite_p67,coords)


#########PNA region#############
   lat_min=20
   lat_max=80
   lon_min=120
   lon_max=300
   PCC_PNA_composite_p23_round=np.empty( ( 4) ,dtype=float)
   PCC_PNA_composite_p67_round=np.empty( ( 4) ,dtype=float)
   PCC_PNA_composite_p23=np.empty( ( 4) ,dtype=float)
   PCC_PNA_composite_p67=np.empty( ( 4) ,dtype=float)
   for i in range ( 4 ) :
     res_temp_p23=correlate(xr_ERA5_z500_composite_p23[i,:,:], xr_model_z500_composite_p23[i,:,:],lat_min,lat_max,lon_min,lon_max)
     res_temp_p67=correlate(xr_ERA5_z500_composite_p67[i,:,:], xr_model_z500_composite_p67[i,:,:],lat_min,lat_max,lon_min,lon_max)
     PCC_PNA_composite_p23[i]=res_temp_p23[0,1]
     PCC_PNA_composite_p67[i]=res_temp_p67[0,1]
     PCC_PNA_composite_p23_round[i] = round(PCC_PNA_composite_p23[i], 2)
     PCC_PNA_composite_p67_round[i] = round(PCC_PNA_composite_p67[i], 2)


# Plot PNA region Z500 composites

   lags = ['1','2','3','4'] # in weeks
   lon = era_lon_in
   lat = era_lat_in
   levs_anom = np.arange(-60,60,10)
   fig=plot.figure(refwidth=5)
   axes=fig.subplots(nrows=4,ncols=4,proj='cyl',proj_kw={'lon_0': 180})
   axes.format(coast=True, latlines=20, lonlines=40,
                  lonlim=(120,300),latlim=(20,80),
                  lonlabels=(True,False),
                  latlabels=(True,False),abc=True)

   for ilag, lag in enumerate(lags):


       # Observations
       h1=axes[ilag,0].contourf(lon,lat,xr_ERA5_z500_composite_p23[ilag],extend='both',
                       cmap='RdBu_r', levels=levs_anom)
       axes[ilag,0].format(title='Obs. Phases 2&3_Week ' + lag)
    
       # Forecast
       h2=axes[ilag,1].contourf(lon,lat,xr_model_z500_composite_p23[ilag],extend='both',
                       cmap='RdBu_r', levels=levs_anom)
       axes[ilag,1].format(title=dictionary['model name']+' Phases 2&3_Week ' + lag)
       axes[ilag,1].set_title(PCC_PNA_composite_p23_round[ilag], loc = "right")
    
       h3=axes[ilag,2].contourf(lon,lat,xr_ERA5_z500_composite_p67[ilag],extend='both',
                       cmap='RdBu_r', levels=levs_anom)
       axes[ilag,2].format(title='Obs. Phases 6&7_Week ' + lag)
    
       h4=axes[ilag,3].contourf(lon,lat,xr_model_z500_composite_p67[ilag],extend='both',
                       cmap='RdBu_r', levels=levs_anom)
       axes[ilag,3].format(title=dictionary['model name']+' Phases 6&7_Week ' + lag)
       axes[ilag,3].set_title(PCC_PNA_composite_p67_round[ilag], loc = "right")

   fig.colorbar(h1, loc='b', extend='both', label='Z500 anomaly',
                     width='1.5em', extendsize='2em', shrink=0.3,)

   # save
   if not os.path.exists('../output/PatternCC_PNA/'+dictionary['model name']): 
       os.mkdir('../output/PatternCC_PNA/'+dictionary['model name'])
   figname='z500_composites_PNA' 
   fig.savefig('../output/PatternCC_PNA/'+dictionary['model name']+'/'+figname+'.jpg',dpi=300)
