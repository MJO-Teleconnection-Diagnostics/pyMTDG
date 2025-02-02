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
import copy


import sys
sys.path.insert(0, '../Utils')
from pathlib import Path
from obs_utils import *
from fcst_utils import *
from t2m_utils import *

print(f'Compute T2m diagnostic')

config_file=Path('../driver/config.yml').resolve()
if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        raise

if (dictionary['RMM']==True):
    fil_rmm_obs=dictionary['Path to RMM observation data file']
    ds_rmm=xr.open_dataset(fil_rmm_obs)

if (dictionary['RMM']==False):
    fil_rmm_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'
    ds_rmm=xr.open_dataset(fil_rmm_obs,decode_times=False)
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


# Select all days in November-December-January-February-March

rmm_obs_ndjfm  = ds_rmm.sel(time=ds_rmm.time.dt.month.isin([1, 2, 3, 11, 12]))
pha_obs_ndjfm  = ds_rmm.sel(time=ds_rmm.time.dt.month.isin([1, 2, 3, 11, 12]))


# Generate time limits for each initial condition 

nyrs=date.fromisoformat(tEnd).year-date.fromisoformat(tBegin).year +1
yrStrt=date.fromisoformat(tBegin).year
mmStrt=date.fromisoformat(tBegin).month

# Read in observations
# ERA-Interim data covers 01/01/1979-08/31/2019, 7 years and 8 months, 14853 days

if dictionary.get('ERAI', False):
    fil_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/t2m/t2m.ei.oper.an.sfc.regn128sc.1979.2019.nc'
    ds_obs_name='ERAI'
    ds_obs = xr.open_dataset(fil_obs,chunks='auto')
    
else:
    fil_obs=dictionary['Path to T2m observation data files']
    ds_obs_name='OBS'
    nf,ds_obs=open_user_obs_fil(fil_obs)

obs=get_variable_from_dataset(ds_obs)

#subset time
obs=obs.sel(time=slice(tBegin,tEnd))
# make sure obs is organized time x lat x lon
obs = obs.transpose('time','latitude','longitude')

# Read in forecast data

fcst_dir=dictionary['Path to T2m model data files']
ds_fcst_name=dictionary['model name']
ds_names=[ds_obs_name,ds_fcst_name]


fcst_files=np.sort(glob.glob(str(fcst_dir+'*.nc')))
ds_fcst=xr.open_mfdataset(fcst_files,combine='nested',concat_dim='time',parallel=True,engine='h5netcdf')
fcst=get_variable_from_dataset(ds_fcst)
    

# Regriding 
if (dictionary['ERAI']==True):
    rgrd_fcst,rgrd_obs=regrid(fcst,obs,ds_fcst.latitude,ds_fcst.longitude,
                                        ds_obs.latitude,ds_obs.longitude,scalar=True)
    print('Done regriding')
    del ds_fcst, ds_obs
    
else:
    rgrd_fcst = copy.deepcopy(fcst)
    rgrd_obs = copy.deepcopy(obs)

del fcst, obs
gc.collect()

# If requested, calculate anomalies of observations for the provided Start_Date -- End_Date period; otherwise read the anomalies from the provided file

if (dictionary['Daily Anomaly'] == True):
    var_name='t2m_anom'
    obs_anom=calcAnomObs(rgrd_obs.sel(time=slice(tBegin,tEnd)),var_name)
if (dictionary['Daily Anomaly'] == False):
    obs_anom=copy.deepcopy(rgrd_obs)
    
del rgrd_obs
gc.collect()
    
# If required calculate forecast anomalies
if (dictionary['Daily Anomaly'] == True):
    var_name='t2m_anom'
    fcst_anom=calcAnom(rgrd_fcst,var_name)
        
if (dictionary['Daily Anomaly'] == False):
    fcst_anom=copy.deepcopy(rgrd_fcst)
del rgrd_fcst
gc.collect()


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

lat_min=obs_anom.latitude.sel(latitude=lat_0,method='nearest')
lat_max=obs_anom.latitude[0]
lon_min=obs_anom.longitude[0]
lon_max=obs_anom.longitude[-1]

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
