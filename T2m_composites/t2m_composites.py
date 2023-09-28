#!/usr/bin/env python
# coding: utf-8

# In[1]:


import xarray as xr
import numpy as np
import datetime
from datetime import date, timedelta
from scipy.stats import bootstrap
import yaml


# In[2]:


import sys
sys.path.insert(0, '../Utils')
from pathlib import Path
from obs_utils import *
from fcst_utils import *
from t2m_utils import *


# In[ ]:


print(xr.__version__)


# In[5]:


config_file=Path('../driver/config.yml').resolve()
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)


# In[6]:


dictionary


# In[ ]:


if (dictionary['RMM:']==False):
    fil_rmm_erai=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'


# In[ ]:


fil_rmm_erai


# In[ ]:


ds_rmm=xr.open_dataset(fil_rmm_erai,decode_times=False)


# In[ ]:


times=ds_rmm['amplitude'].time
init_time=date(1960,1,1)+timedelta(int(times[0]))
time=[]
for i in range(len(times)):
        time.append(init_time+timedelta(i))


# In[ ]:


import pandas as pd
ds_rmm['time'] = pd.to_datetime(time,format="%Y/%m/%d")


# ERA-Interim data covers 01/01/1979-08/31/2019, 7 years and 8 months, 14853 days

# In[ ]:


if (dictonary['ERAI:']==True):
    fil_t2m_erai=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/t2m/erai.T2m.day.mean.1979-2019.nc'
ds_t2m_erai=xr.open_dataset(fil_t2m_erai)


# * Rename lon,lat to match the forecast - useful for plotting
# * Reverse latitude of ERA-I from S->N to N->S

# In[ ]:


ds_t2m_erai=ds_t2m_erai.rename({'lon': 'longitude','lat': 'latitude'})
ds_t2m_erai=ds_t2m_erai.reindex(latitude=list(reversed(ds_t2m_erai.latitude)))


# Calculate anomalies of observations for the provided Start_Date -- End_Date period

# In[ ]:


if (dictionary['Daily Anomaly:'] == True):
    tBegin=dictionary['START_DATE:']
    tEnd=dictonary['END_DATE:']
    t2m_obs_anom=calcAnomObs(ds_t2m_erai['t2m'].sel(time=slice(tBegin,tEnd)),'t2m_anom')


# Read in forecast data

# In[ ]:


fil_t2m_fcst_1='/projects/cstan/ufs6/daily/mean/t2m/t2m_*01.nc'
fil_t2m_fcst_15='/projects/cstan/ufs6/daily/mean/t2m/t2m_*15.nc'


# In[ ]:


ds_t2m_fcst_1=xr.open_mfdataset(fil_t2m_fcst_1,combine='nested',concat_dim='time',parallel=True)
ds_t2m_fcst_15=xr.open_mfdataset(fil_t2m_fcst_15,combine='nested',concat_dim='time',parallel=True)


# Interpolate reforecast data to ERAI grid (regular 0.75 x 0.75)

# In[ ]:


rgrd_t2m_fcst_1=regrid_scalar_spharm(ds_t2m_fcst_1['t2m'],ds_t2m_fcst_1.latitude,ds_t2m_fcst_1.longitude,
                                                        ds_t2m_erai.latitude,ds_t2m_erai.longitude)
rgrd_t2m_fcst_15=regrid_scalar_spharm(ds_t2m_fcst_15['t2m'],ds_t2m_fcst_1.latitude,ds_t2m_fcst_1.longitude,
                                                        ds_t2m_erai.latitude,ds_t2m_erai.longitude)

del ds_t2m_fcst_1, ds_t2m_fcst_15


# In[ ]:


# Calculate forecast anomalies
t2m_anom_fcst_1=calcAnom(rgrd_t2m_fcst_1,'t2m_anom')
t2m_anom_fcst_15=calcAnom(rgrd_t2m_fcst_15,'t2m_anom')

del rgrd_t2m_fcst_1, rgrd_t2m_fcst_15


# Select all days in November-December-January-February-March

# In[ ]:


rmm_obs_ndjfm = ds_rmm['amplitude'].sel(time=is_ndjfm(ds_rmm['time.month']))
pha_obs_ndjfm = ds_rmm['phase'].sel(time=is_ndjfm(ds_rmm['time.month']))


# In[ ]:


tBegin


# Generate time limits for each initial condition 

# In[ ]:


nyrs=int(tEnd[0:4])-int(tBegin[0:4])+1
yrStrt=int(tBegin[0:4])
mmStrt=1
initial_days=[1, 15]

dStrt=[]
for dd in initial_days:
    dStrt.append(date(yrStrt,mmStrt,dd))
dLast=[]
for i in range(len(initial_days)):
    dLast.append(dStrt[i]+timedelta(days=nyrs*366))


# Select the time period of the forecast 01/01/2011-12/31/2018

# In[ ]:


rmm_obs_1=rmm_obs_ndjfm.sel(time=slice(dStrt[0],dLast[0]))
rmm_obs_15=rmm_obs_ndjfm.sel(time=slice(dStrt[1],dLast[1]))

pha_obs_1=pha_obs_ndjfm.sel(time=slice(dStrt[0],dLast[0]))
pha_obs_15=pha_obs_ndjfm.sel(time=slice(dStrt[1],dLast[1]))


# Select initial conditions in the forecast

# In[ ]:


rmm_fcst_1 = rmm_obs_1.sel(time=is_day1(rmm_obs_1['time.day']))
rmm_fcst_15 = rmm_obs_15.sel(time=is_day15(rmm_obs_15['time.day']))

pha_fcst_1 = pha_obs_1.sel(time=is_day1(pha_obs_1['time.day']))
pha_fcst_15 = pha_obs_15.sel(time=is_day15(pha_obs_15['time.day']))


# Select MJO events for MJO phase 3 and 7

# In[ ]:


phase3 = 3
mjo_events_1_p3 = select_mjo_event(rmm_fcst_1,pha_fcst_1,phase3)
mjo_events_15_p3 = select_mjo_event(rmm_fcst_15,pha_fcst_15,phase3)

phase7 = 7
mjo_events_1_p7 = select_mjo_event(rmm_fcst_1,pha_fcst_1,phase7)
mjo_events_15_p7 = select_mjo_event(rmm_fcst_15,pha_fcst_15,phase7)


# In[ ]:


lon_0 = 270
lat_0 = 20
cmap='bwr'
clevs=[-5.0, -4.0, -3.0, -2.0, -1.0, -0.5, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0]


# In[ ]:


weeks=['week3','week4']

# Calculate phase composites of observations for a given week
for week in weeks:
    var_name='t2m_anom_p3'
    obs_comp_anom_1_p3=calcComposites(t2m_obs_anom,mjo_events_1_p3,week,var_name)
    obs_comp_anom_15_p3=calcComposites(t2m_obs_anom,mjo_events_15_p3,week,var_name)

    var_name='t2m_anom_p7'
    obs_comp_anom_1_p7=calcComposites(t2m_obs_anom,mjo_events_1_p7,week,var_name)
    obs_comp_anom_15_p7=calcComposites(t2m_obs_anom,mjo_events_15_p7,week,var_name)
    
    obs_comp_anom_p3=xr.concat([obs_comp_anom_1_p3,obs_comp_anom_15_p3],dim='mjo_events')
    obs_comp_anom_p7=xr.concat([obs_comp_anom_1_p7,obs_comp_anom_15_p7],dim='mjo_events')
    
# Calculate statistical significance of composites (**observations**) over the MJO events
    n_samples=1000
    sig_level=0.95
    obs_low_p3,obs_high_p3=test_sig(obs_comp_anom_p3,sig_level,n_samples)
    obs_low_p7,obs_high_p7=test_sig(obs_comp_anom_p7,sig_level,n_samples)
    
    obs_sig_p3=xr.where((obs_low_p3<0) & (obs_high_p3>0),np.nan,1)
    obs_sig_p7=xr.where((obs_low_p7<0) & (obs_high_p7>0),np.nan,1)

# Calculate phase composites of forecasts for the given week
    var_name='t2m_anom_p3'
    fcst_comp_anom_1_p3=calcComposites(t2m_anom_fcst_1,mjo_events_1_p3,week,var_name)
    fcst_comp_anom_15_p3=calcComposites(t2m_anom_fcst_15,mjo_events_15_p3,week,var_name)

    var_name='t2m_anom_p7'
    fcst_comp_anom_1_p7=calcComposites(t2m_anom_fcst_1,mjo_events_1_p7,week,var_name)
    fcst_comp_anom_15_p7=calcComposites(t2m_anom_fcst_15,mjo_events_15_p7,week,var_name)
    
# Combine all MJO events in forecast
    fcst_comp_anom_p3=xr.concat([fcst_comp_anom_1_p3,fcst_comp_anom_15_p3],dim='mjo_events')
    fcst_comp_anom_p7=xr.concat([fcst_comp_anom_1_p7,fcst_comp_anom_15_p7],dim='mjo_events')
    
# Calculate statistical significance of composites (forecast) over the MJO events
    n_samples=1000
    sig_level=0.95
    fcst_low_p3,fcst_high_p3=test_sig(fcst_comp_anom_p3,sig_level,n_samples)
    fcst_low_p7,fcst_high_p7=test_sig(fcst_comp_anom_p7,sig_level,n_samples)

    fcst_sig_p3=xr.where((fcst_low_p3<0) & (fcst_high_p3>0),np.nan,1)
    fcst_sig_p7=xr.where((fcst_low_p7<0) & (fcst_high_p7>0),np.nan,1)
    
#Calculate pattern correlation between ERA-I composites and forecast composites
    lat_min=obs_comp_anom_p3.latitude.sel(latitude=20,method='nearest')
    lat_max=obs_comp_anom_p3.latitude[0]
    lon_min=obs_comp_anom_p3.longitude[0]
    lon_max=obs_comp_anom_p3.longitude[-1]
    r_p3= correlate(obs_comp_anom_p3['t2m_anom_p3'].mean(dim='mjo_events'),
                fcst_comp_anom_p3['t2m_anom_p3'].mean(dim='mjo_events'),lat_min,lat_max,lon_min,lon_max)
    r_p7=correlate(obs_comp_anom_p7['t2m_anom_p7'].mean(dim='mjo_events'),
                 fcst_comp_anom_p7['t2m_anom_p7'].mean(dim='mjo_events'),lat_min,lat_max,lon_min,lon_max) 

#Plot composites 
    plotComposites(obs_comp_anom_p3['t2m_anom_p3'].mean(dim='mjo_events'),
               clevs,cmap,lon_0,lat_0,obs_sig_p3,'t2m_obs_'+week+'_p3')
    plotComposites(obs_comp_anom_p7['t2m_anom_p7'].mean(dim='mjo_events'),
               clevs,cmap,lon_0,lat_0,obs_sig_p7,'t2m_obs_'+week+'_p7')
    plotComposites(fcst_comp_anom_p3['t2m_anom_p3'].mean(dim='mjo_events'),
               clevs,cmap,lon_0,lat_0,fcst_sig_p3,'t2m_fcst_'+week+'_p3')
    plotComposites(fcst_comp_anom_p7['t2m_anom_p7'].mean(dim='mjo_events'),
               clevs,cmap,lon_0,lat_0,fcst_sig_p7,'t2m_fcst_'+week+'_p7')


# In[ ]:




