# Usage: In your main code add <from obs_utils import *>

import numpy as np
import xarray as xr
import pandas as pd
from scipy.stats import bootstrap
from datetime import date, timedelta

import glob

def calcAnomObs(ds,anom_name):
    
    # Compute climatology
    month_day_str = xr.DataArray(ds.indexes['time'].strftime('%m-%d'), coords=ds['time'].coords,
                             name='month_day_str')
    ds_clim=ds.groupby(month_day_str).mean(dim='time').compute()
    
    # Compute anomaly
    anoms=ds.groupby(month_day_str)-ds_clim
    
    return anoms.drop(labels='month_day_str').rename(anom_name)

def select_mjo_event(rmm_index,phase,phase_val):
    
    # Select MJO events with amplitude > 1 and in a given phase
    # rmm_index: time series of the RMM index
    # phase: time series of the phase
    # phase_val: integer 1 ... 8
    
    mjo_events=rmm_index.where((rmm_index>1) & (phase==phase_val),drop=True)
    return mjo_events

def calcComposites(ds,mjo_events,week,name,obs=False):
    
    if week == 'week1':
        sday = 0
    if week == 'week2':
        sday = 7
    if week == 'week3':
        sday = 14
    if week == 'week4':
        sday = 21
    if week == 'week5':
        sday = 28

    tStrt=pd.to_datetime(mjo_events.time,format="%Y/%m/%d")+timedelta(days=sday)
    tLast=pd.to_datetime(mjo_events.time,format="%Y/%m/%d")+timedelta(days=sday+6)

    ds_anoms = []
    for i in range(len(mjo_events)):
        
        if tLast[i].month != 4:
            if obs:
                anoms=ds.where((ds['time'] >= tStrt[i]) & (ds['time'] <= tLast[i])).mean(dim='time')
                ds_anoms.append(anoms.to_dataset(name=name))
            else:
                anoms=ds.sel(time=mjo_events.time[i],forecast_day=slice(sday,sday+7)).mean('forecast_day')
                ds_anoms.append(anoms.to_dataset(name=name))
                
    ds_comp_anoms=xr.combine_nested(ds_anoms,concat_dim='mjo_events')
     
    return ds_comp_anoms

def test_sig(ds,confidence_level,n_resamples):
    # ds shape: (time,longitude,latitude)
    rng = np.random.default_rng()
    res=bootstrap((ds,),np.mean,axis=0,confidence_level=confidence_level, 
                 n_resamples=n_resamples,random_state=rng)
    ci_l,ci_u=res.confidence_interval
    
    ci_l_return=xr.DataArray(ci_l, name='ci_l',
                               dims=['latitude','longitude'],
                               coords=dict(latitude=ds.latitude,longitude=ds.longitude))
    ci_u_return=xr.DataArray(ci_u, name='ci_u',
                               dims=['latitude','longitude'],
                               coords=dict(latitude=ds.latitude,longitude=ds.longitude))
    del ci_l, ci_u
    
    return ci_l_return, ci_u_return

def open_user_obs_fil(obs_dir):
    obs_fil=(glob.glob(obs_dir+'*.nc*'))
    
    if len(obs_fil)==1:
        ds = xr.open_dataset(obs_fil[0],chunks='auto')
    else:
        ds =xr.open_mfdataset(obs_fil)
        
    return len(obs_fil),ds


def reshape_obs(obs,init_day,nfc=35):
    ''' Reshape observation data to match forecast data
    is 2D with dimensions initialization day & forecast day. 
    ---
    Inputs
    ---
    obs: xarray data array of observation data with time dimension named "time"
    init_days: initial days of the forecast
    nfc: number of forecast days, default=35. Must be integer
    
    ---
    Returns
    ---
    obs_reshape: reshaped xarray of observation data with 2D time
    '''
    
    # Check to make sure nfc is an integer
    if not isinstance(nfc, int):
        print('warning: nfc is not an integer. forcing integer type')
        nfc = int(nfc)
    
    # Forecast lead time
    fc_day = np.arange(1,nfc+1)
    
    # Reshape
    obs_reshape=[]
    for iinit in range(len(init_day)):
        # Subset and rename the forecast dimension
        subset = obs.sel(time=slice(init_day.time[iinit],init_day.time[iinit]+pd.Timedelta(days=nfc-1)))
        subset = subset.rename(time='forecast_day')
        subset['forecast_day']=fc_day
        obs_reshape.append(subset)
        
    # Convert to single xarray data array from list of multiple data arrays
    obs_reshape=xr.concat(obs_reshape,dim='time')
    obs_reshape['time']=init_day
    obs_reshape.time.attrs['long_name']='initial time'
    
    return obs_reshape