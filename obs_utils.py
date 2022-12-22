# Usage: In your main code add <from obs_utils import *>

import numpy as np
import xarray as xr
import pandas as pd
from scipy.stats import bootstrap

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

def calcComposites(ds,mjo_events,week,name):
    
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
            anoms=ds.sel(time=slice(tStrt[i],tLast[i])).mean(dim='time')
            ds_anoms.append(anoms.to_dataset(name=name))
    ds_comp_anoms=xr.combine_nested(ds_anoms,concat_dim='mjo_events')
    
    return ds_comp_anoms

def test_sig(ds,confidence_level,n_resamples):
    # ds shape (mjo_events,longitude,latitude)
    rng = np.random.default_rng()
    res=bootstrap((ds.to_array(),),np.mean,axis=1,confidence_level=confidence_level, 
                 n_resamples=n_resamples,random_state=rng)
    ci_l,ci_u=res.confidence_interval
    
    return ci_l, ci_u
