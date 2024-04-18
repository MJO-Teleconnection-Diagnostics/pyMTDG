#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import numpy as np
import pandas as pd
import datetime
from datetime import date, timedelta
import yaml
import glob
import gc


import sys
sys.path.insert(0, '../Utils')
from pathlib import Path
from obs_utils import *
from fcst_utils import *
from t2m_utils import *

print(f'Compute T2m diagnostic')

config_file=Path('../driver/config.yml').resolve()
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)


if (dictionary['RMM']==False):
    fil_rmm_erai=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'

ds_rmm=xr.open_dataset(fil_rmm_erai,decode_times=False)

times=ds_rmm.time
init_time=date(1960,1,1)+timedelta(int(times[0]))
time=[]
for i in range(len(times)):
        time.append(init_time+timedelta(i))

ds_rmm['time'] = pd.to_datetime(time,format="%Y/%m/%d")

# Get the forecast period from the provided Start_Date -- End_Date period
yyyymmdd_Begin=dictionary['START_DATE']
tBegin=yyyymmdd_Begin[0:4]+'-'+yyyymmdd_Begin[4:6]+'-'+yyyymmdd_Begin[6:8]
yyyymmdd_End=dictionary['END_DATE']
tEnd=yyyymmdd_End[0:4]+'-'+yyyymmdd_End[4:6]+'-'+yyyymmdd_End[6:8]

# ERA-Interim data covers 01/01/1979-08/31/2019, 7 years and 8 months, 14853 days

if (dictionary['ERAI']==True):
    fil_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/t2m/t2m.ei.oper.an.sfc.regn128sc.1979.2019.nc'
    ds_obs_name='ERAI'
if (dictionary['ERAI']==False):
    fil_obs=dictionary['Path to observational data files']
    ds_obs_name='OBS'
ds_obs=xr.open_dataset(fil_obs)
obs=get_variable_from_dataset(ds_obs)


# If requested, calculate anomalies of observations for the provided Start_Date -- End_Date period; otherwise read the anomalies from the provided file


if (dictionary['Daily Anomaly'] == True):
    var_name='t2m_anom'
    obs_anom=calcAnomObs(obs.sel(time=slice(tBegin,tEnd)),var_name)
if (dictionary['Daily Anomaly'] == False):
    obs_anom=obs
    del obs

# Select all days in November-December-January-February-March

rmm_obs_ndjfm  = ds_rmm.sel(time=ds_rmm.time.dt.month.isin([1, 2, 3, 11, 12]))
pha_obs_ndjfm  = ds_rmm.sel(time=ds_rmm.time.dt.month.isin([1, 2, 3, 11, 12]))


# Generate time limits for each initial condition 

nyrs=date.fromisoformat(tEnd).year-date.fromisoformat(tBegin).year +1
yrStrt=date.fromisoformat(tBegin).year
mmStrt=date.fromisoformat(tBegin).month

# Read in forecast data

fcst_dir=dictionary['Path to T2m model data files for date']
ds_fcst_name=dictionary['model name']
ds_names=[ds_obs_name,ds_fcst_name]


fcst_files=np.sort(glob.glob(str(fcst_dir+'*.nc')))
ds_fcst=xr.open_mfdataset(fcst_files,combine='nested',concat_dim='time',parallel=True)
fcst=get_variable_from_dataset(ds_fcst)
    
if (dictionary['Daily Anomaly'] == True):
    # Interpolate reforecast data to ERAI grid (regular 0.75 x 0.75)
    rgrd_fcst=regrid_scalar_spharm(fcst,ds_fcst.latitude,ds_fcst.longitude,
                                        ds_obs.latitude,ds_obs.longitude)
del ds_fcst
gc.collect()
    
# Calculate forecast anomalies
fcst_anom=calcAnom(rgrd_fcst,'t2m_anom')
    
del rgrd_fcst
gc.collect()
        
if (dictionary['Daily Anomaly'] == False):
    fcst_anom=fcst
del fcst

# Reshape 1D time dimension of UFS anomalies to 2D
fcst_anom = reshape_forecast(fcst_anom, nfc=int(len(fcst_anom.time)/len(fcst_files)))
       
    
# Select initial conditions in the forecast during DJFM

rmm=ds_rmm.sel(time=ds_rmm.time.dt.month.isin([1, 2, 3, 11, 12])& ds_rmm.time.isin(fcst_anom.time))
fcst_anom=fcst_anom.sel(time=fcst_anom.time.dt.month.isin([1, 2, 3, 11, 12]))

# Select MJO events for MJO phases 3 and 7

phases=[3,7]

mjo_event_phases=[]
for phase in phases:
    ds=select_mjo_event(rmm.amplitude,rmm.phase,phase)
    mjo_event_phases.append(ds)
rmm_events=xr.concat(mjo_event_phases, dim='phase')

# Parameters for bootstrap significance
n_samples=1000
sig_level=0.95

# Plotting parameters
lon_0 = 270
lat_0 = 20

lat_min=obs.latitude.sel(latitude=lat_0,method='nearest')
lat_max=obs.latitude[0]
lon_min=obs.longitude[0]
lon_max=obs.longitude[-1]

cmap='bwr'
clevs=[-5.0, -4.0, -3.0, -2.0, -1.0, -0.5, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0]

# Main calculation
weeks=['week2','week3','week4','week5']

for week in weeks:
        
    for p,phase in enumerate(phases):
        # Composites    
        ds_obs_comp=calcComposites(obs_anom,
                                    rmm_events[p,:].dropna(dim='time',how='any'),
                                    week,var_name,obs=True)                       
        ds_fcst_comp=calcComposites(fcst_anom,
                                    rmm_events[p,:].dropna(dim='time',how='any'),
                                        week,var_name,obs=False)
        #Significance
        obs_low,obs_high=test_sig(ds_obs_comp['t2m_anom'].dropna(dim='mjo_events',how='any'),
                                        sig_level,n_samples)
        fcst_low,fcst_high=test_sig(ds_fcst_comp['t2m_anom'].dropna(dim='mjo_events',how='any'),
                                        sig_level,n_samples)
        
        obs_sig=xr.where((obs_low<0) & (obs_high>0),np.nan,1)
        fcst_sig=xr.where((fcst_low<0) & (fcst_high>0),np.nan,1)
           
        
        #Calculate pattern correlation between ERA-I composites and forecast composites
    
        r_p= correlate(ds_obs_comp['t2m_anom'].mean(dim='mjo_events'),
                        ds_fcst_comp['t2m_anom'].mean(dim='mjo_events'),
                        lat_min,lat_max,lon_min,lon_max)
        #Plotting 
        plotComposites([ds_obs_comp['t2m_anom'].mean(dim='mjo_events'),
                        ds_fcst_comp['t2m_anom'].mean(dim='mjo_events')], ds_names,
                        clevs, cmap, lon_0, lat_0,
                        [obs_sig,fcst_sig],r_p[0,1],
                        week.capitalize(),' P'+str(phase),'t2m_'+week+'_'+'p'+str(phase))     