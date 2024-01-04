import xarray as xr
import numpy as np
import datetime
from datetime import date, timedelta
import yaml
import gc


import sys
sys.path.insert(0, '../Utils')
from pathlib import Path
from obs_utils import *
from fcst_utils import *
from t2m_utils import *


print('Compute T2m diagnostic')


config_file=Path('../driver/config.work.yml').resolve()
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)

if (dictionary['RMM:']==False):
    fil_rmm_erai=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'

ds_rmm=xr.open_dataset(fil_rmm_erai,decode_times=False)

times=ds_rmm['amplitude'].time
init_time=date(1960,1,1)+timedelta(int(times[0]))
time=[]
for i in range(len(times)):
        time.append(init_time+timedelta(i))

import pandas as pd
ds_rmm['time'] = pd.to_datetime(time,format="%Y/%m/%d")


# ERA-Interim data covers 01/01/1979-08/31/2019, 7 years and 8 months, 14853 days

if (dictionary['ERAI:']==True):
    fil_t2m_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/t2m/erai.T2m.day.mean.1979-2019.nc'
    ds_obs_name='ERAI'
if (dictionary['ERAI:']==False):
    ds_obs_name='OBS'
ds_t2m_obs=xr.open_dataset(fil_t2m_obs)


# * Rename lon,lat to match the forecast - useful for plotting
# * Reverse latitude of ERA-I from S->N to N->S

ds_t2m_obs=ds_t2m_obs.rename({'lon': 'longitude','lat': 'latitude'})
ds_t2m_obs=ds_t2m_obs.reindex(latitude=list(reversed(ds_t2m_obs.latitude)))


# Calculate anomalies of observations for the provided Start_Date -- End_Date period


if (dictionary['Daily Anomaly:'] == True):
    var_name='t2m_anom'
    tBegin=dictionary['START_DATE:']
    tEnd=dictionary['END_DATE:']
    t2m_obs_anom=calcAnomObs(ds_t2m_obs['t2m'].sel(time=slice(tBegin,tEnd)),var_name)


# Select all days in November-December-January-February-March

rmm_obs_ndjfm  = ds_rmm['amplitude'].sel(time=ds_rmm['amplitude'].time.dt.month.isin([1, 2, 3, 11, 12]))
pha_obs_ndjfm  = ds_rmm['phase'].sel(time=ds_rmm['phase'].time.dt.month.isin([1, 2, 3, 11, 12]))


# Generate time limits for each initial condition 

nyrs=int(tEnd[0:4])-int(tBegin[0:4])+1
yrStrt=int(tBegin[0:4])
mmStrt=1
initial_days=dictionary['Initial dates:']

dStrt=[]
for dd in initial_days:
    dStrt.append(date(yrStrt,mmStrt,dd))
dLast=[]
for i in range(len(initial_days)):
    dLast.append(dStrt[i]+timedelta(days=nyrs*366))


# Read in forecast data and create the array to hold the final calculation for each initial date

init_dates=dictionary['Number of initial dates:']
fcst_files=dictionary['Path to T2m model data files for date']
ds_fcst_name=dictionary['model name']
ds_names=[ds_obs_name,ds_fcst_name]

master_data_obs_p3=[]
master_data_obs_p7=[]
master_data_fcst_p3=[]
master_data_fcst_p7=[]

for ndate,idate in enumerate(initial_days):

    ds_t2m_fcst=xr.open_mfdataset(fcst_files[ndate],combine='nested',concat_dim='time',parallel=True,engine='h5netcdf')
    
    # Interpolate reforecast data to ERAI grid (regular 0.75 x 0.75)
    rgrd_t2m_fcst=regrid_scalar_spharm(ds_t2m_fcst['t2m'],ds_t2m_fcst.latitude,ds_t2m_fcst.longitude,
                                                        ds_t2m_obs.latitude,ds_t2m_obs.longitude)
    #del ds_t2m_fcst
    
    # Calculate forecast anomalies
    t2m_fcst_anom=calcAnom(rgrd_t2m_fcst,'t2m_anom')
    
    #del rgrd_t2m_fcst
    gc.collect()
    
    # Select the time period of the forecast (dStrt-dEnd) for MJO amplitude and phase in OBS
    
    rmm_obs=rmm_obs_ndjfm.sel(time=slice(dStrt[ndate],dLast[ndate]))
    pha_obs=pha_obs_ndjfm.sel(time=slice(dStrt[ndate],dLast[ndate]))
    
    
    # Select initial conditions in the forecast
    rmm_fcst = rmm_obs.sel(time=rmm_obs.time.dt.day.isin(idate)) 
    pha_fcst = pha_obs.sel(time=pha_obs.time.dt.day.isin(idate))
    
    #Select MJO events for MJO phase 3 and 7
    
    phases=[3,7]
    mjo_event_phases=[]
    for phase in phases:
        ds=select_mjo_event(rmm_fcst,pha_fcst,phase)
        mjo_event_phases.append(ds)
        #print('ndate=',ndate,'idate=',idate,'phase=',phase,'mjo_event_pahses=',ds)
    rmm_events=xr.concat(mjo_event_phases, dim='phase')
    #print('ndate=',ndate,'idate=',idate,'phase=',phase,'rmm_events=',rmm_events)

    # Calculate phase composites of observations and forecast for a given week for each phase
    weeks=['week3','week4']
    obs_comp_anom_weeks_p3=[]
    obs_comp_anom_weeks_p7=[]
    fcst_comp_anom_weeks_p3=[]
    fcst_comp_anom_weeks_p7=[]

    for week in weeks:
        obs_comp_anom_week=[]
        fcst_comp_anom_week=[]
        for p,phase in enumerate(phases):
            #print('idate=', idate,'phase=',phase,'week=',
            #week,rmm_events[p,:],'rmm_events_time=',rmm_events[p,:].time)
            print('idate=',idate,'phase=',phase, 'week=',week)
            ds_obs_phase=calcComposites(t2m_obs_anom,
                                        rmm_events[p,:].dropna(dim='time',how='any'),
                                        week,var_name)                       
            ds_fcst_phase=calcComposites(t2m_fcst_anom,
                                         rmm_events[p,:].dropna(dim='time',how='any'),
                                         week,var_name)
            obs_comp_anom_week.append(ds_obs_phase)
            fcst_comp_anom_week.append(ds_fcst_phase)
            
        ds_obs_week_p3=obs_comp_anom_week[0]
        ds_obs_week_p7=obs_comp_anom_week[1]
        ds_fcst_week_p3=fcst_comp_anom_week[0]
        ds_fcst_week_p7=fcst_comp_anom_week[1]  
        
        obs_comp_anom_weeks_p3.append(ds_obs_week_p3)
        obs_comp_anom_weeks_p7.append(ds_obs_week_p7)
        fcst_comp_anom_weeks_p3.append(ds_fcst_week_p3)
        fcst_comp_anom_weeks_p7.append(ds_fcst_week_p7)
        
    ds_obs_comp_anom_p3=xr.concat(obs_comp_anom_weeks_p3,dim='week')
    ds_obs_comp_anom_p7=xr.concat(obs_comp_anom_weeks_p7,dim='week')
    ds_fcst_comp_anom_p3=xr.concat(fcst_comp_anom_weeks_p3,dim='week')
    ds_fcst_comp_anom_p7=xr.concat(fcst_comp_anom_weeks_p7,dim='week')

    master_data_obs_p3.append(ds_obs_comp_anom_p3)
    master_data_obs_p7.append(ds_obs_comp_anom_p7)
    master_data_fcst_p3.append(ds_fcst_comp_anom_p3)
    master_data_fcst_p7.append(ds_fcst_comp_anom_p7)
    
obs_comp_anom_p3=xr.concat([master_data_obs_p3[p] for p in range(len(phases))],dim='mjo_events')
obs_comp_anom_p7=xr.concat([master_data_obs_p7[p] for p in range(len(phases))],dim='mjo_events')
fcst_comp_anom_p3=xr.concat([master_data_fcst_p3[p] for p in range(len(phases))],dim='mjo_events')
fcst_comp_anom_p7=xr.concat([master_data_fcst_p7[p] for p in range(len(phases))],dim='mjo_events')

del ds_t2m_obs
gc.collect()


lon_0 = 270
lat_0 = 20
cmap='bwr'
clevs=[-5.0, -4.0, -3.0, -2.0, -1.0, -0.5, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0]
n_samples=1000
sig_level=0.95

lat_min=obs_comp_anom_p3.latitude.sel(latitude=lat_0,method='nearest')
lat_max=obs_comp_anom_p3.latitude[0]
lon_min=obs_comp_anom_p3.longitude[0]
lon_max=obs_comp_anom_p3.longitude[-1]


for week in range(len(weeks)):

        # Calculate statistical significance of composites (forecast) over the MJO events
        obs_low_p3,obs_high_p3=test_sig(obs_comp_anom_p3['t2m_anom'][week,:,:,:],
                                        sig_level,n_samples)
        obs_low_p7,obs_high_p7=test_sig(obs_comp_anom_p7['t2m_anom'][week,:,:,:],
                                        sig_level,n_samples)
        fcst_low_p3,fcst_high_p3=test_sig(fcst_comp_anom_p3['t2m_anom'][week,:,:,:],
                                          sig_level,n_samples)
        fcst_low_p7,fcst_high_p7=test_sig(fcst_comp_anom_p7['t2m_anom'][week,:,:,:],
                                          sig_level,n_samples)
        
        obs_sig_p3=xr.where((obs_low_p3<0) & (obs_high_p3>0),np.nan,1)
        obs_sig_p7=xr.where((obs_low_p7<0) & (obs_high_p7>0),np.nan,1)
        fcst_sig_p3=xr.where((fcst_low_p3<0) & (fcst_high_p3>0),np.nan,1)
        fcst_sig_p7=xr.where((fcst_low_p7<0) & (fcst_high_p7>0),np.nan,1)
        
        sig_p3 = [obs_sig_p3,fcst_sig_p3]
        del obs_sig_p3, fcst_sig_p3
        gc.collect()
        
        sig_p7 = [obs_sig_p7,fcst_sig_p7]
        del obs_sig_p7, fcst_sig_p7
        gc.collect()
        
        #Calculate pattern correlation between ERA-I composites and forecast composites
    
        r_p3= correlate(obs_comp_anom_p3['t2m_anom'][week,:,:,:].mean(dim='mjo_events'),
                fcst_comp_anom_p3['t2m_anom'][week,:,:,:].mean(dim='mjo_events'),
                        lat_min,lat_max,lon_min,lon_max)
        r_p7= correlate(obs_comp_anom_p7['t2m_anom'][week,:,:,:].mean(dim='mjo_events'),
                fcst_comp_anom_p7['t2m_anom'][week,:,:,:].mean(dim='mjo_events'),
                        lat_min,lat_max,lon_min,lon_max)

        print('week=', week)
        print('r_p3=',r_p3[0,1])
        print('r_p7=',r_p7[0,1])
        
        comp_anom_p3=[obs_comp_anom_p3['t2m_anom'][week,:,:,:].mean(dim='mjo_events'),
                        fcst_comp_anom_p3['t2m_anom'][week,:,:,:].mean(dim='mjo_events')]
        
        #del obs_comp_anom_p3, fcst_comp_anom_p3
        #gc.collect()
        
        comp_anom_p7=[obs_comp_anom_p7['t2m_anom'][week,:,:,:].mean(dim='mjo_events'),
                        fcst_comp_anom_p7['t2m_anom'][week,:,:,:].mean(dim='mjo_events')]
        
        #del obs_comp_anom_p7, fcst_comp_anom_p7
        #gc.collect()

        plotComposites(comp_anom_p3, ds_names,
                        clevs, cmap, lon_0, lat_0,
                        sig_p3,r_p3[0,1],
                        weeks[week].capitalize(),' P3','t2m_'+weeks[week]+'_p3')
        
        plotComposites(comp_anom_p7, ds_names,
                        clevs, cmap, lon_0, lat_0,
                        sig_p7,r_p7[0,1],
                        weeks[week].capitalize(),' P7','t2m_'+weeks[week]+'_p7')


print('Finished T2m diagnostic')



