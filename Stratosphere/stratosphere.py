import xarray as xr
import numpy as np
import pandas as pd
import math
import yaml
from pathlib import Path
from datetime import datetime 
from datetime import timedelta
from datetime import date
import matplotlib.pyplot as plt
import glob
import os

import sys
sys.path.insert(0, '../Utils')
from stratosphere_utils import *
from obs_utils import*

# %%
import matplotlib.pyplot as plt
from matplotlib import rcParams #For changing text properties
import matplotlib.path as mpath
import matplotlib.colors as mcolors

# Read yaml file
config_file=Path('../driver/config.yml').resolve()
if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        raise

yyyymmdd_Begin=dictionary['START_DATE']
tBegin=yyyymmdd_Begin[0:4]+'-'+yyyymmdd_Begin[4:6]+'-'+yyyymmdd_Begin[6:8]
yyyymmdd_End=dictionary['END_DATE']
tEnd=yyyymmdd_End[0:4]+'-'+yyyymmdd_End[4:6]+'-'+yyyymmdd_End[6:8]

nyrs=date.fromisoformat(tEnd).year-date.fromisoformat(tBegin).year +1
SYY=date.fromisoformat(tBegin).year
SMM=date.fromisoformat(tBegin).month
SDD=date.fromisoformat(tBegin).day
EYY=date.fromisoformat(tEnd).year
EMM=date.fromisoformat(tEnd).month
EDD=date.fromisoformat(tEnd).day
NYRS = EYY-SYY
years = np.arange(SYY,EYY+1)

if dictionary.get('Daily Anomaly', False):
    filv_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/v500/v500.ei.oper.an.pl.regn128uv.1979.2019.nc'
    filt_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/t500/t500.ei.oper.an.pl.regn128sc.1979.2019.nc'
    filz_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/z100/z100.ei.oper.an.pl.regn128sc.1979.2019.nc'
    ds_obs_name='ERAI'
    
else:
    # need to add "Path to heat flux at 500 hPa observation data files" to config.yml
    filv_obs=dictionary['Path to meridional wind at 500 hPa observation data files']
    filt_obs=dictionary['Path to temperature at 500 hPa observation data files']
    filz_obs=dictionary['Path to Z100 observation data files']
    ds_obs_name='OBS'
    
data_v_obs = get_variable_from_dataset(xr.open_mfdataset(filv_obs,combine='by_coords').compute())
data_v_obs = data_v_obs.sel(latitude=slice(80,40))
data_v_obs = np.squeeze(data_v_obs.sel(time=data_v_obs.time.dt.year.isin(years)))

data_t_obs = get_variable_from_dataset(xr.open_mfdataset(filt_obs,combine='by_coords').compute())
data_t_obs = data_t_obs.sel(latitude=slice(80,40))
data_t_obs = np.squeeze(data_t_obs.sel(time=data_t_obs.time.dt.year.isin(years)))

data_z_obs = get_variable_from_dataset(xr.open_mfdataset(filz_obs,combine='by_coords').compute())
data_z_obs = data_z_obs.sel(latitude=slice(90,55))
data_z_obs = np.squeeze(data_z_obs.sel(time=data_z_obs.time.dt.year.isin(years)))

lon = data_z_obs.coords['longitude'].values
lat = data_z_obs.coords['latitude'].values
dlat = np.deg2rad(np.abs(lat[1]-lat[0]))
dlon = np.deg2rad(np.abs(lon[1]-lon[0]))
darea = dlat * dlon * np.cos(np.deg2rad(data_z_obs.latitude))
weights = darea.where(data_z_obs[0])
weights_sum = weights.sum(dim=('longitude', 'latitude'))
data_pcz_obs = (data_z_obs * weights).sum(dim=('longitude', 'latitude')) / weights_sum

# %%


# In[2]:


wavn = 3
vt_obs = heat_flux_amp(data_t_obs, data_v_obs, wavn)

# %%
# compute anomaly
data_r = anom_re(vt_obs)
data_z_r = anom_re(data_pcz_obs)

# %%
if (dictionary['RMM']==True):
    fil_rmm_obs=dictionary['Path to RMM observation data file']
    rmm=xr.open_dataset(fil_rmm_obs)
    
if (dictionary['RMM']==False):
    # read RMM index
    # data is from Cheng Zhang, ERA-interim daily data from 1981.1.1-2019.8.31 
    fil_rmm_erai=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'
    rmm = xr.open_mfdataset(fil_rmm_erai,combine='by_coords').compute()
    
    # assign dates
    date_start = datetime.strftime(datetime(year=1960,month=1,day=1), "%Y.%m.%d")
    time_date = []
    for ii in range(len(rmm.time)):
        time_date.append(datetime.strftime(datetime.strptime(date_start, "%Y.%m.%d") + timedelta(days=int(rmm.time.values[ii])),"%Y.%m.%d"))

    rmm = rmm.assign_coords(time=time_date)
    rmm = rmm.assign_coords(time=pd.DatetimeIndex(rmm.time))
    
rmm = rmm.sel(time = slice(str(SYY),str(EYY)))
rmm = rmm.isel(time=rmm.time.dt.month.isin([11, 12, 1, 2, 3]))

# %%
# MJO events
mjo_pha1 = select_mjo_event(rmm.amplitude,rmm.phase,1)
mjo_pha2 = select_mjo_event(rmm.amplitude,rmm.phase,2)
mjo_pha3 = select_mjo_event(rmm.amplitude,rmm.phase,3)
mjo_pha4 = select_mjo_event(rmm.amplitude,rmm.phase,4)
mjo_pha5 = select_mjo_event(rmm.amplitude,rmm.phase,5)
mjo_pha6 = select_mjo_event(rmm.amplitude,rmm.phase,6)
mjo_pha7 = select_mjo_event(rmm.amplitude,rmm.phase,7)
mjo_pha8 = select_mjo_event(rmm.amplitude,rmm.phase,8)


# %%
# compute heat flux anomaly 
lats = [80,40]; levs = 500; lons = [0,360]

fcst_dir_v = dictionary['Path to meridional wind at 500 hPa model data files']
fcst_dir_t = dictionary['Path to temperature at 500 hPa model data files']
fcst_dir_z = dictionary['Path to Z100 model data files']


ds_fcst_name=dictionary['model name'] 

fileList_v, fileList_t = extract_files(fcst_dir_v, fcst_dir_t, ds_fcst_name)
fcst_anoms, date_init_all, nfct = compute_heatflux_anom(fileList_v, fileList_t, lats, lons, NYRS)

date_init = []
for ii in range(int(len(fcst_anoms)/nfct)):
    date_init.append(fcst_anoms.time[ii*nfct].values)
dummy = fcst_anoms.values
dummy = dummy.reshape(int(len(fcst_anoms)/nfct),nfct)
dates_mo = np.arange(nfct)
coords= {
    'date_init':date_init,
    'time':dates_mo
}
fcst_anoms_new = xr.DataArray(dummy, coords=coords)
del fcst_anoms


# %%
# compute gph anomaly
lats = [90,55]; levs = [100]; lons = [300,360]

fileList_z, fileList_t = extract_files(fcst_dir_z, fcst_dir_t, ds_fcst_name)
fcst_z_anoms, date_init_all, nfct = compute_gph_anom(fileList_z, lats, lons, NYRS)

date_init = []
for ii in range(int(len(fcst_z_anoms)/nfct)):
    date_init.append(fcst_z_anoms.time[ii*nfct].values)
dummy = fcst_z_anoms.values
dummy = dummy.reshape(int(len(fcst_z_anoms)/nfct),nfct)
dates_mo = np.arange(nfct)
coords= {
    'date_init':date_init,
    'time':dates_mo
}
fcst_z_anoms_new = xr.DataArray(dummy, coords=coords)
del fcst_z_anoms


# %%
# MJO events models
fcst_data_week1, fcst_data_week2, fcst_data_week3, fcst_data_week4, fcst_data_week5 = mjo_anoms_week_mo(fcst_anoms_new, date_init_all, 
                                                mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)

fcst_z_data_week1, fcst_z_data_week2, fcst_z_data_week3, fcst_z_data_week4, fcst_z_data_week5 = mjo_anoms_week_mo(fcst_z_anoms_new, date_init_all, 
                                                mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)

# %%
# MJO events reanalysis

data_r_week1, data_r_week2, data_r_week3, data_r_week4, data_r_week5 = mjo_anoms_week_re(data_r, date_init_all, 
                                                mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)

data_z_r_week1, data_z_r_week2, data_z_r_week3, data_z_r_week4, data_z_r_week5 = mjo_anoms_week_re(data_z_r, date_init_all, 
                                                mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)

# %%
figt = ds_obs_name+' vtw1+2 500hPa [Km/s]'
fig_name = '1_'+ds_obs_name+'_vtw1+2_500hPa'
cmin,cmax,cint = -5, 5.5, 0.5
mjo_phase_lag_plot(data_r_week1,data_r_week2,data_r_week3,data_r_week4,data_r_week5,
                   ds_fcst_name,cmin,cmax,cint,figt,fig_name)
figt = ds_fcst_name+' vtw1+2 500hPa [Km/s]'
fig_name = '2_'+ds_fcst_name+'_vtw1+2_500hPa'
mjo_phase_lag_plot(fcst_data_week1,fcst_data_week2,fcst_data_week3,fcst_data_week4,fcst_data_week5,
                   ds_fcst_name,cmin,cmax,cint,figt,fig_name)

figt = ds_obs_name+' polar cap 100hPa Z mean'
fig_name = '3_'+ds_obs_name+'_polar_cap_Z100'
cmin,cmax,cint = -190, 200, 10
mjo_phase_lag_plot(data_z_r_week1,data_z_r_week2,data_z_r_week3,data_z_r_week4,data_z_r_week5,
                   ds_fcst_name,cmin,cmax,cint,figt,fig_name)
figt = ds_fcst_name+' polar cap 100hPa Z mean'
fig_name = '4_'+ds_fcst_name+'_polar_cap_Z100'
mjo_phase_lag_plot(fcst_z_data_week1,fcst_z_data_week2,fcst_z_data_week3,fcst_z_data_week4,fcst_z_data_week5,
                   ds_fcst_name,cmin,cmax,cint,figt,fig_name)


# In[ ]:




