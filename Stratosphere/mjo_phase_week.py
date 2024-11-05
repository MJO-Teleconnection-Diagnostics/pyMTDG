# %%
import xarray as xr
import numpy as np
import pandas as pd
import math
import yaml
from pathlib import Path
from datetime import datetime 
from datetime import timedelta
from datetime import date
import numpy.fft as npft
import matplotlib.pyplot as plt
import glob
import os

import sys
sys.path.insert(0, '../Utils')
from u10_utils import *

# %%
import matplotlib.pyplot as plt
from matplotlib import rcParams #For changing text properties
import matplotlib.path as mpath
import matplotlib.colors as mcolors

# %%
# Read yaml file
config_file=Path('../driver/config.yml').resolve()
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)

# %%
tBegin=dictionary['START_DATE']
tEnd=dictionary['END_DATE']
nyrs=date.fromisoformat(tEnd).year-date.fromisoformat(tBegin).year +1
SYY=date.fromisoformat(tBegin).year
SMM=date.fromisoformat(tBegin).month
SDD=date.fromisoformat(tBegin).day
EYY=date.fromisoformat(tEnd).year
EMM=date.fromisoformat(tEnd).month
EDD=date.fromisoformat(tEnd).day
NYRS = EYY-SYY
years = np.arange(SYY,EYY+1)

# %%
# Suppose the users have heat flux or geopotential height data computed already for the reanalysis
if (dictionary['ERAI']==True):
    filv_obs=dictionary['DIR_IN']+'/ERA-Interim/v500-1979-2018.nc'
    filt_obs=dictionary['DIR_IN']+'/ERA-Interim/t500-1979-2018.nc'
    filz_obs=dictionary['DIR_IN']+'/ERA-Interim/z100-1979-2018.nc'
    ds_obs_name='ERAI'
    
if (dictionary['ERAI']==False):
    # need to add "Path to heat flux at 500 hPa observation data files" to config.yml
    filv_obs=dictionary['Path to meridional wind at 500 hPa observation data files']
    filt_obs=dictionary['Path to temperature at 500 hPa observation data files']
    filz_obs=dictionary['Path to z100 observation files']
    ds_obs_name='OBS'
data_v_obs = xr.open_mfdataset(filv_obs,combine='by_coords').compute()
data_v_obs = data_v_obs.sel(latitude=slice(80,40))
data_v_obs = np.squeeze(data_v_obs.sel(time=data_v_obs.time.dt.year.isin(years)).v)

data_t_obs = xr.open_mfdataset(filt_obs,combine='by_coords').compute()
data_t_obs = data_t_obs.sel(latitude=slice(80,40))
data_t_obs = np.squeeze(data_t_obs.sel(time=data_t_obs.time.dt.year.isin(years)).t)

data_z_obs = xr.open_mfdataset(filz_obs,combine='by_coords').compute()
data_z_obs = data_z_obs.sel(latitude=slice(90,55))
data_z_obs = np.squeeze(data_z_obs.sel(time=data_z_obs.time.dt.year.isin(years)).z)

lon = data_z_obs.coords['longitude'].values
lat = data_z_obs.coords['latitude'].values
dlat = np.deg2rad(np.abs(lat[1]-lat[0]))
dlon = np.deg2rad(np.abs(lon[1]-lon[0]))
darea = dlat * dlon * np.cos(np.deg2rad(data_z_obs.latitude))
weights = darea.where(data_z_obs[0])
weights_sum = weights.sum(dim=('longitude', 'latitude'))
data_pcz_obs = (data_z_obs * weights).sum(dim=('longitude', 'latitude')) / weights_sum

# %%
def heat_flux_amp(data_t, data_v, wavn):
    nlon = len(data_t.longitude.values)
    data_t_fft = npft.fft(data_t,axis=2)
    data_v_fft = npft.fft(data_v,axis=2)
    data_t_fft_conj = np.conj(data_t_fft)
    data_vt = np.multiply(data_v_fft[:,:,1:wavn],data_t_fft_conj[:,:,1:wavn])
    vt_amp = np.sum(data_vt.real,axis=2)*2/nlon/nlon

    time_dim = data_t.coords['time']
    lat_dim = data_t.coords['latitude']
    data_vt_amp = xr.DataArray(vt_amp, coords={'time': time_dim, 'latitude': lat_dim}, dims=["time","latitude"])

    weights = np.cos(np.deg2rad(data_vt_amp.latitude))
    weights.name = "weights"
    data_vt_amp_weighted = data_vt_amp.weighted(weights)
    data_amp = data_vt_amp_weighted.mean(dim=("latitude"))
    return data_amp

wavn = 3
vt_obs = heat_flux_amp(data_t_obs, data_v_obs, wavn)

# %%
# compute anomaly
def anom_re(data_obs):
    data_r_clim = data_obs.groupby(data_obs.time.dt.dayofyear).mean(dim='time')
    data_r = data_obs.groupby(data_obs.time.dt.dayofyear) - data_r_clim
    return data_r

data_r = anom_re(vt_obs)
data_z_r = anom_re(data_pcz_obs)

# %%
if (dictionary['RMM']==False):
    # read RMM index
    # data is from Cheng Zhang, ERA-interim daily data from 1981.1.1-2019.8.31 
    fil_rmm_erai=dictionary['DIR_IN']+'/ERA-Interim/rmm_ERA-Interim.nc'
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


def get_variable_from_dataset(ds):
    '''
        Extract the target variable from the dataset. Convert to target units
        
            Parameters
                ds: xarray dataset
            Returns
                da: subsetted dataArray in
    '''
    for name in ['V', 'v', 'vwnd','T','t','temp','Z','z','gh']:
        if name in list(ds.keys()):
            break
    da = ds[name]
    return da
    raise RuntimeError("Couldn't find a zonal wind variable name")


def data_fct_anom(data,kk,ninit_per_year,ninit,nyrs,nfct):
    for jj in range(kk,ninit,ninit_per_year):
        if jj == kk:
            data_all = data[nfct*jj:nfct*(jj+1)]
        else:
            data_all =  xr.concat([data_all,data[nfct*jj:nfct*(jj+1)]],"time")
        data_clim = xr.concat([data_all[ii:nfct*7:nfct].mean(dim='time') for ii in range(nfct)],"time")
    times = data_all.time
    days=[]
    for i in range(nyrs):
        days.append(np.arange(nfct))
    days=np.reshape(days,nyrs*nfct)
    print(data_all.shape)
    data_all['time']=days
    anoms=data_all.groupby(data_all.time)-data_clim
    anoms['time']=times
    return anoms

def data_fct_concat(data,ninit_per_year,ninit,nyrs,nfct):
    for kk in range(ninit_per_year):
        anoms = data_fct_anom(data,kk,ninit_per_year,ninit,nyrs,nfct)
        if kk == 0:
            anoms_all = anoms
        else:
            anoms_all = xr.concat([anoms_all,anoms],"time")
    return anoms_all


# %%
# model heat flux with MJO events
def compute_heatflux_anom(fileList_v, fileList_t, lats, levs, lons, nyrs, **kwargs):
    INITMON = kwargs.get('INITMON', ['01','02','03','11','12'])
    INITDAY = kwargs.get('INITDAY', ['01','15'])
    nt = kwargs.get('nt', 7)
    months = kwargs.get('months', [1,2,3,11,12])

    date_init_all = []

    kk1 = 0; kk2 = 0; kk3 = 0; kk4 = 0; kk5 = 0
    for ifile in range(len(fileList_v)):
        datafn = fileList_t[ifile]
        data_tmp = xr.open_mfdataset(datafn,combine='by_coords')
        init_month = data_tmp['time.month'][0]
        if init_month in months:
            data_tmp = data_tmp.compute()
            init_month = data_tmp['time.month'][0]
            init_year = data_tmp['time.year'][0] 
            init_day = data_tmp['time.day'][0]
            date_init = datetime(year=init_year.values,month=init_month.values,day=init_day.values)
            data_tmp = data_tmp.sel(latitude=slice(lats[0],lats[1]), lev=levs)
            data_t = get_variable_from_dataset(data_tmp)
            
            datafn = fileList_v[ifile]
            data_tmp1 = xr.open_mfdataset(datafn,combine='by_coords').compute()
            data_tmp1 = data_tmp1.sel(latitude=slice(lats[0],lats[1]), lev=levs)
            data_v = get_variable_from_dataset(data_tmp1)
            date_init_all.append(date_init)

            wavn = 3 # wave1+2
            # wavn = 2 # wave1
            data = heat_flux_amp(data_t,data_v,wavn)
            nfct = len(data.time)
            if kk1 == 0:
                if init_month == months[0]: data_all1 = data; kk1 = kk1+1
            else:
                if init_month == months[0]: data_all1 = xr.concat([data_all1, data],"time")
            if kk2 == 0:
                if init_month == months[1]: data_all2 = data; kk2 = kk2+1
            else:
                if init_month == months[1]: data_all2 = xr.concat([data_all2, data],"time")
            if kk3 == 0:
                if init_month == months[2]: data_all3 = data; kk3 = kk3+1
            else:
                if init_month == months[2]: data_all3 = xr.concat([data_all3, data],"time")
            if kk4 == 0:
                if init_month == months[3]: data_all4 = data; kk4 = kk4+1
            else:
                if init_month == months[3]: data_all4 = xr.concat([data_all4, data],"time")
            if kk5 == 0:
                if init_month == months[4]: data_all5 = data; kk5 = kk5+1
            else:
                if init_month == months[4]: data_all5 = xr.concat([data_all5, data],"time")

    ninit_per_year = int(len(data_all1)/nfct/nyrs)
    ninit = int(len(data_all1)/nfct)
    anoms1 = data_fct_concat(data_all1,ninit_per_year,ninit,nyrs,nfct)
    anoms2 = data_fct_concat(data_all2,ninit_per_year,ninit,nyrs,nfct)
    anoms3 = data_fct_concat(data_all3,ninit_per_year,ninit,nyrs,nfct)
    anoms4 = data_fct_concat(data_all4,ninit_per_year,ninit,nyrs,nfct)
    anoms5 = data_fct_concat(data_all5,ninit_per_year,ninit,nyrs,nfct)
    anoms = xr.concat([anoms1,anoms2,anoms3,anoms4,anoms5],"time")
    return anoms, date_init_all, nfct

# %%
# model gph with MJO events
def compute_gph_anom(fileList_z, lats, levs, lons, nyrs, **kwargs):
    INITMON = kwargs.get('INITMON', ['01','02','03','11','12'])
    INITDAY = kwargs.get('INITDAY', ['01','15'])
    nt = kwargs.get('nt', 7)

    date_init_all = []

    kk = 0
    for ifile in range(len(fileList_z)):
        datafn = fileList_z[ifile]
        data = xr.open_mfdataset(datafn,combine='by_coords').compute()
        init_time = data.time[0].values
        init_month = pd.to_datetime(init_time).month
        if init_month in [1,2,3,11,12]:
            init_year = pd.to_datetime(init_time).year
            init_day = pd.to_datetime(init_time).day
            date_init = datetime(year=init_year,month=init_month,day=init_day)

            data_tmp = data.sel(longitude=slice(lons[0],lons[1]), latitude=slice(lats[0],lats[1]), lev=levs)
            data_t = get_variable_from_dataset(data_tmp)
            del data
            lon = data_t.coords['longitude'].values
            lat = data_t.coords['latitude'].values
            dlat = np.deg2rad(np.abs(lat[1]-lat[0]))
            dlon = np.deg2rad(np.abs(lon[1]-lon[0]))
            darea = dlat * dlon * np.cos(np.deg2rad(data_t.latitude))
            weights = darea.where(data_t[0])
            weights_sum = weights.sum(dim=('longitude', 'latitude'))
            data = (data_t * weights).sum(dim=('longitude', 'latitude')) / weights_sum
            
            nfct = len(data.time)
            if kk1 == 0:
                if init_month == months[0]: data_all1 = data; kk1 = kk1+1
            else:
                if init_month == months[0]: data_all1 = xr.concat([data_all1, data],"time")
            if kk2 == 0:
                if init_month == months[1]: data_all2 = data; kk2 = kk2+1
            else:
                if init_month == months[1]: data_all2 = xr.concat([data_all2, data],"time")
            if kk3 == 0:
                if init_month == months[2]: data_all3 = data; kk3 = kk3+1
            else:
                if init_month == months[2]: data_all3 = xr.concat([data_all3, data],"time")
            if kk4 == 0:
                if init_month == months[3]: data_all4 = data; kk4 = kk4+1
            else:
                if init_month == months[3]: data_all4 = xr.concat([data_all4, data],"time")
            if kk5 == 0:
                if init_month == months[4]: data_all5 = data; kk5 = kk5+1
            else:
                if init_month == months[4]: data_all5 = xr.concat([data_all5, data],"time")

    ninit_per_year = int(len(data_all1)/nfct/nyrs)
    ninit = int(len(data_all1)/nfct)
    anoms1 = data_fct_concat(data_all1,ninit_per_year,ninit,nyrs,nfct)
    anoms2 = data_fct_concat(data_all2,ninit_per_year,ninit,nyrs,nfct)
    anoms3 = data_fct_concat(data_all3,ninit_per_year,ninit,nyrs,nfct)
    anoms4 = data_fct_concat(data_all4,ninit_per_year,ninit,nyrs,nfct)
    anoms5 = data_fct_concat(data_all5,ninit_per_year,ninit,nyrs,nfct)
    anoms = xr.concat([anoms1,anoms2,anoms3,anoms4,anoms5],"time")
    return anoms, date_init_all, nfct

# %%
def data_week(data, date_init, nday1, nday2, model_name):
    if model_name == 'model':
        date_start = nday1
        date_end = nday2
    else:
        date_start = date_init + timedelta(days=nday1)
        date_end = date_init + timedelta(days=nday2)
    tmp_week = data.sel(time=slice(date_start,date_end))
    date_start = date_init + timedelta(days=nday1)
    date_end = date_init + timedelta(days=nday2)
    if date_end.month >= 11 or date_end.month <= 3:
        data_week = tmp_week.mean(dim='time',skipna=True).values
    else:
        data_week = tmp_week.mean(dim='time',skipna=True).values+np.nan
    return data_week

# %%
def comb_list(data_pha1, data_pha2, data_pha3, data_pha4, data_pha5, data_pha6, data_pha7, data_pha8):
    data_out = []
    data_out.append(data_pha1)
    data_out.append(data_pha2)
    data_out.append(data_pha3)
    data_out.append(data_pha4)
    data_out.append(data_pha5)
    data_out.append(data_pha6)
    data_out.append(data_pha7)
    data_out.append(data_pha8)
    return data_out

# %%
def mjo_anoms_week_mo(data_all, date_init_all, mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8, **kwargs):
    INITMON = kwargs.get('INITMON', ['01','02','03','11','12'])
    INITDAY = kwargs.get('INITDAY', ['01','15'])
    nt = kwargs.get('nt', 7)

    data_week1_pha1,data_week2_pha1,data_week3_pha1,data_week4_pha1,data_week5_pha1 = [],[],[],[],[]
    data_week1_pha2,data_week2_pha2,data_week3_pha2,data_week4_pha2,data_week5_pha2 = [],[],[],[],[]
    data_week1_pha3,data_week2_pha3,data_week3_pha3,data_week4_pha3,data_week5_pha3 = [],[],[],[],[]
    data_week1_pha4,data_week2_pha4,data_week3_pha4,data_week4_pha4,data_week5_pha4 = [],[],[],[],[]
    data_week1_pha5,data_week2_pha5,data_week3_pha5,data_week4_pha5,data_week5_pha5 = [],[],[],[],[]
    data_week1_pha6,data_week2_pha6,data_week3_pha6,data_week4_pha6,data_week5_pha6 = [],[],[],[],[]
    data_week1_pha7,data_week2_pha7,data_week3_pha7,data_week4_pha7,data_week5_pha7 = [],[],[],[],[]
    data_week1_pha8,data_week2_pha8,data_week3_pha8,data_week4_pha8,data_week5_pha8 = [],[],[],[],[]
    
    mjo_pha1_dates = pd.to_datetime(mjo_pha1.time,format="%Y/%m/%d")
    mjo_pha2_dates = pd.to_datetime(mjo_pha2.time,format="%Y/%m/%d")
    mjo_pha3_dates = pd.to_datetime(mjo_pha3.time,format="%Y/%m/%d")
    mjo_pha4_dates = pd.to_datetime(mjo_pha4.time,format="%Y/%m/%d")
    mjo_pha5_dates = pd.to_datetime(mjo_pha5.time,format="%Y/%m/%d")
    mjo_pha6_dates = pd.to_datetime(mjo_pha6.time,format="%Y/%m/%d")
    mjo_pha7_dates = pd.to_datetime(mjo_pha7.time,format="%Y/%m/%d")
    mjo_pha8_dates = pd.to_datetime(mjo_pha8.time,format="%Y/%m/%d")
    for it in range(len(date_init_all)):
        date_init = date_init_all[it]
        if date_init in mjo_pha1_dates:
            data = data_all.sel(date_init=date_init)
            data_week1_pha1.append(data_week(data, date_init, 1, nt, 'model'))
            data_week2_pha1.append(data_week(data, date_init, nt+1, nt*2, 'model'))
            data_week3_pha1.append(data_week(data, date_init, nt*2+1, nt*3, 'model'))
            data_week4_pha1.append(data_week(data, date_init, nt*3+1, nt*4, 'model'))
            data_week5_pha1.append(data_week(data, date_init, nt*4+1, nt*5, 'model'))
            print('Phase 1',date_init)
        if date_init in mjo_pha2_dates:
            data = data_all.sel(date_init=date_init)
            data_week1_pha2.append(data_week(data, date_init, 1, nt, 'model'))
            data_week2_pha2.append(data_week(data, date_init, nt+1, nt*2, 'model'))
            data_week3_pha2.append(data_week(data, date_init, nt*2+1, nt*3, 'model'))
            data_week4_pha2.append(data_week(data, date_init, nt*3+1, nt*4, 'model'))
            data_week5_pha2.append(data_week(data, date_init, nt*4+1, nt*5, 'model'))
            print('Phase 2',date_init)
        if date_init in mjo_pha3_dates:
            data = data_all.sel(date_init=date_init)
            data_week1_pha3.append(data_week(data, date_init, 1, nt, 'model'))
            data_week2_pha3.append(data_week(data, date_init, nt+1, nt*2, 'model'))
            data_week3_pha3.append(data_week(data, date_init, nt*2+1, nt*3, 'model'))
            data_week4_pha3.append(data_week(data, date_init, nt*3+1, nt*4, 'model'))
            data_week5_pha3.append(data_week(data, date_init, nt*4+1, nt*5, 'model'))
            print('Phase 3',date_init)
        if date_init in mjo_pha4_dates:
            data = data_all.sel(date_init=date_init)
            data_week1_pha4.append(data_week(data, date_init, 1, nt, 'model'))
            data_week2_pha4.append(data_week(data, date_init, nt+1, nt*2, 'model'))
            data_week3_pha4.append(data_week(data, date_init, nt*2+1, nt*3, 'model'))
            data_week4_pha4.append(data_week(data, date_init, nt*3+1, nt*4, 'model'))
            data_week5_pha4.append(data_week(data, date_init, nt*4+1, nt*5, 'model'))
            print('Phase 4',date_init)
        if date_init in mjo_pha5_dates:
            data = data_all.sel(date_init=date_init)
            data_week1_pha5.append(data_week(data, date_init, 1, nt, 'model')) 
            data_week2_pha5.append(data_week(data, date_init, nt+1, nt*2, 'model'))
            data_week3_pha5.append(data_week(data, date_init, nt*2+1, nt*3, 'model'))
            data_week4_pha5.append(data_week(data, date_init, nt*3+1, nt*4, 'model'))
            data_week5_pha5.append(data_week(data, date_init, nt*4+1, nt*5, 'model'))
            print('Phase 5',date_init)
        if date_init in mjo_pha6_dates:
            data = data_all.sel(date_init=date_init)
            data_week1_pha6.append(data_week(data, date_init, 1, nt, 'model'))
            data_week2_pha6.append(data_week(data, date_init, nt+1, nt*2, 'model'))
            data_week3_pha6.append(data_week(data, date_init, nt*2+1, nt*3, 'model'))
            data_week4_pha6.append(data_week(data, date_init, nt*3+1, nt*4, 'model'))
            data_week5_pha6.append(data_week(data, date_init, nt*4+1, nt*5, 'model'))
            print('Phase 6',date_init)
        if date_init in mjo_pha7_dates:
            data = data_all.sel(date_init=date_init)
            data_week1_pha7.append(data_week(data, date_init, 1, nt, 'model'))
            data_week2_pha7.append(data_week(data, date_init, nt+1, nt*2, 'model'))
            data_week3_pha7.append(data_week(data, date_init, nt*2+1, nt*3, 'model'))
            data_week4_pha7.append(data_week(data, date_init, nt*3+1, nt*4, 'model'))
            data_week5_pha7.append(data_week(data, date_init, nt*4+1, nt*5, 'model'))
            print('Phase 7',date_init)
        if date_init in mjo_pha8_dates:
            data = data_all.sel(date_init=date_init)
            data_week1_pha8.append(data_week(data, date_init, 1, nt, 'model'))
            data_week2_pha8.append(data_week(data, date_init, nt+1, nt*2, 'model'))
            data_week3_pha8.append(data_week(data, date_init, nt*2+1, nt*3, 'model'))
            data_week4_pha8.append(data_week(data, date_init, nt*3+1, nt*4, 'model'))
            data_week5_pha8.append(data_week(data, date_init, nt*4+1, nt*5, 'model'))
            print('Phase 8',date_init)
            
    data_week1 = comb_list(data_week1_pha1, data_week1_pha2, data_week1_pha3, data_week1_pha4, 
                            data_week1_pha5, data_week1_pha6, data_week1_pha7, data_week1_pha8)
    data_week2 = comb_list(data_week2_pha1, data_week2_pha2, data_week2_pha3, data_week2_pha4, 
                            data_week2_pha5, data_week2_pha6, data_week2_pha7, data_week2_pha8)
    data_week3 = comb_list(data_week3_pha1, data_week3_pha2, data_week3_pha3, data_week3_pha4, 
                            data_week3_pha5, data_week3_pha6, data_week3_pha7, data_week3_pha8)
    data_week4 = comb_list(data_week4_pha1, data_week4_pha2, data_week4_pha3, data_week4_pha4, 
                            data_week4_pha5, data_week4_pha6, data_week4_pha7, data_week4_pha8)
    data_week5 = comb_list(data_week5_pha1, data_week5_pha2, data_week5_pha3, data_week5_pha4, 
                            data_week5_pha5, data_week5_pha6, data_week5_pha7, data_week5_pha8)      
    return data_week1, data_week2, data_week3, data_week4, data_week5

# %%
def extract_files(fcst_dir_1, fcst_dir_2, ds_fcst_name):
    model_fcst_dir = fcst_dir_1+str(ds_fcst_name)+'/'
    tmp = os.listdir(fcst_dir_1+str(ds_fcst_name))
    dummy = sorted(tmp)
    fileList_1 = [model_fcst_dir+f for f in dummy]
    
    model_fcst_dir = fcst_dir_2+str(ds_fcst_name)+'/'
    tmp = os.listdir(fcst_dir_2+str(ds_fcst_name))
    dummy = sorted(tmp)
    fileList_2 = [model_fcst_dir+f for f in dummy]
    return fileList_1, fileList_2

# %%
# compute heat flux anomaly 
lats = [80,40]; levs = 500; lons = [0,360]

# fcst_dir_v=dictionary['Path to meridional wind at 500 hPa model data files']
# fcst_dir_t=dictionary['Path to temperature at 500 hPa model data files']
# if the data is only at a specific pressure level, should delete levs in the code
# if the data contains all pressure levels, select the wanted levs
fcst_dir_v = '/mjo/MJO-Teleconnections-develop/data/v/'
fcst_dir_t = '/mjo/MJO-Teleconnections-develop/data/t/'

ds_fcst_name='UFS5' 

fileList_v, fileList_t = extract_files(fcst_dir_v, fcst_dir_t, ds_fcst_name)

p5_anoms, date_init_all, nfct = compute_heatflux_anom(fileList_v, fileList_t, lats, levs, lons, NYRS)

date_init = []
for ii in range(int(len(p5_anoms)/nfct)):
    date_init.append(p5_anoms.time[ii*nfct].values)
dummy = p5_anoms.values
dummy = dummy.reshape(int(len(p5_anoms)/nfct),nfct)
dates_mo = np.arange(nfct)
coords= {
    'date_init':date_init,
    'time':dates_mo
}
p5_anoms_new = xr.DataArray(dummy, coords=coords)

# %%
# compute gph anomaly
lats = [90,55]; levs = [100]; lons = [300,360]

fcst_dir_z = '/mjo/MJO-Teleconnections-develop/data/z/'
fcst_dir_t = '/mjo/MJO-Teleconnections-develop/data/t/'

ds_fcst_name='UFS5' 

fileList_z, fileList_t = extract_files(fcst_dir_z, fcst_dir_t, ds_fcst_name)

p5_z_anoms, date_init_all, nfct = compute_gph_anom(fileList_z, fileList_t, lats, levs, lons, NYRS)

date_init = []
for ii in range(int(len(p5_z_anoms)/nfct)):
    date_init.append(p5_z_anoms.time[ii*nfct].values)
dummy = p5_z_anoms.values
dummy = dummy.reshape(int(len(p5_z_anoms)/nfct),nfct)
dates_mo = np.arange(nfct)
coords= {
    'date_init':date_init,
    'time':dates_mo
}
p5_z_anoms_new = xr.DataArray(dummy, coords=coords)


# %%
# MJO events models
p5_data_week1, p5_data_week2, p5_data_week3, p5_data_week4, p5_data_week5 = mjo_anoms_week_mo(p5_anoms_new, date_init_all, 
                                                                                                 mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)

p5_z_data_week1, p5_z_data_week2, p5_z_data_week3, p5_z_data_week4, p5_z_data_week5 = mjo_anoms_week_mo(p5_z_anoms, date_init_all, 
                                                                                                 mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)

# %%
# MJO events reanalysis
def mjo_anoms_week_re(data_r, date_init_all, mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8):
    nt = 7
    data_r_week1_pha1,data_r_week2_pha1,data_r_week3_pha1,data_r_week4_pha1,data_r_week5_pha1 = [],[],[],[],[]
    data_r_week1_pha2,data_r_week2_pha2,data_r_week3_pha2,data_r_week4_pha2,data_r_week5_pha2 = [],[],[],[],[]
    data_r_week1_pha3,data_r_week2_pha3,data_r_week3_pha3,data_r_week4_pha3,data_r_week5_pha3 = [],[],[],[],[]
    data_r_week1_pha4,data_r_week2_pha4,data_r_week3_pha4,data_r_week4_pha4,data_r_week5_pha4 = [],[],[],[],[]
    data_r_week1_pha5,data_r_week2_pha5,data_r_week3_pha5,data_r_week4_pha5,data_r_week5_pha5 = [],[],[],[],[]
    data_r_week1_pha6,data_r_week2_pha6,data_r_week3_pha6,data_r_week4_pha6,data_r_week5_pha6 = [],[],[],[],[]
    data_r_week1_pha7,data_r_week2_pha7,data_r_week3_pha7,data_r_week4_pha7,data_r_week5_pha7 = [],[],[],[],[]
    data_r_week1_pha8,data_r_week2_pha8,data_r_week3_pha8,data_r_week4_pha8,data_r_week5_pha8 = [],[],[],[],[]
    mjo_pha1_dates = pd.to_datetime(mjo_pha1.time,format="%Y/%m/%d")
    mjo_pha2_dates = pd.to_datetime(mjo_pha2.time,format="%Y/%m/%d")
    mjo_pha3_dates = pd.to_datetime(mjo_pha3.time,format="%Y/%m/%d")
    mjo_pha4_dates = pd.to_datetime(mjo_pha4.time,format="%Y/%m/%d")
    mjo_pha5_dates = pd.to_datetime(mjo_pha5.time,format="%Y/%m/%d")
    mjo_pha6_dates = pd.to_datetime(mjo_pha6.time,format="%Y/%m/%d")
    mjo_pha7_dates = pd.to_datetime(mjo_pha7.time,format="%Y/%m/%d")
    mjo_pha8_dates = pd.to_datetime(mjo_pha8.time,format="%Y/%m/%d")
    for it in range(len(date_init_all)): 
        date_init = date_init_all[it]        
        if date_init in mjo_pha1_dates:
            data_r_week1_pha1.append(data_week(data_r, date_init, 0, nt, 'reanalysis'))
            data_r_week2_pha1.append(data_week(data_r, date_init, nt, nt*2, 'reanalysis'))
            data_r_week3_pha1.append(data_week(data_r, date_init, nt*2, nt*3, 'reanalysis'))
            data_r_week4_pha1.append(data_week(data_r, date_init, nt*3, nt*4, 'reanalysis'))
            data_r_week5_pha1.append(data_week(data_r, date_init, nt*4, nt*5, 'reanalysis'))
            print('Phase 1',date_init)
        if date_init in mjo_pha2_dates:
            data_r_week1_pha2.append(data_week(data_r, date_init, 0, nt, 'reanalysis'))
            data_r_week2_pha2.append(data_week(data_r, date_init, nt, nt*2, 'reanalysis'))
            data_r_week3_pha2.append(data_week(data_r, date_init, nt*2, nt*3, 'reanalysis'))
            data_r_week4_pha2.append(data_week(data_r, date_init, nt*3, nt*4, 'reanalysis'))
            data_r_week5_pha2.append(data_week(data_r, date_init, nt*4, nt*5, 'reanalysis'))
            print('Phase 2',date_init)
        if date_init in mjo_pha3_dates:
            data_r_week1_pha3.append(data_week(data_r, date_init, 0, nt, 'reanalysis'))
            data_r_week2_pha3.append(data_week(data_r, date_init, nt, nt*2, 'reanalysis'))
            data_r_week3_pha3.append(data_week(data_r, date_init, nt*2, nt*3, 'reanalysis'))
            data_r_week4_pha3.append(data_week(data_r, date_init, nt*3, nt*4, 'reanalysis'))
            data_r_week5_pha3.append(data_week(data_r, date_init, nt*4, nt*5, 'reanalysis'))
            print('Phase 3',date_init)
        if date_init in mjo_pha4_dates:
            data_r_week1_pha4.append(data_week(data_r, date_init, 0, nt, 'reanalysis'))
            data_r_week2_pha4.append(data_week(data_r, date_init, nt, nt*2, 'reanalysis'))
            data_r_week3_pha4.append(data_week(data_r, date_init, nt*2, nt*3, 'reanalysis'))
            data_r_week4_pha4.append(data_week(data_r, date_init, nt*3, nt*4, 'reanalysis'))
            data_r_week5_pha4.append(data_week(data_r, date_init, nt*4, nt*5, 'reanalysis'))
            print('Phase 4',date_init)
        if date_init in mjo_pha5_dates:
            data_r_week1_pha5.append(data_week(data_r, date_init, 0, nt, 'reanalysis')) 
            data_r_week2_pha5.append(data_week(data_r, date_init, nt, nt*2, 'reanalysis'))
            data_r_week3_pha5.append(data_week(data_r, date_init, nt*2, nt*3, 'reanalysis'))
            data_r_week4_pha5.append(data_week(data_r, date_init, nt*3, nt*4, 'reanalysis'))
            data_r_week5_pha5.append(data_week(data_r, date_init, nt*4, nt*5, 'reanalysis'))
            print('Phase 5',date_init)
        if date_init in mjo_pha6_dates:
            data_r_week1_pha6.append(data_week(data_r, date_init, 0, nt, 'reanalysis'))
            data_r_week2_pha6.append(data_week(data_r, date_init, nt, nt*2, 'reanalysis'))
            data_r_week3_pha6.append(data_week(data_r, date_init, nt*2, nt*3, 'reanalysis'))
            data_r_week4_pha6.append(data_week(data_r, date_init, nt*3, nt*4, 'reanalysis'))
            data_r_week5_pha6.append(data_week(data_r, date_init, nt*4, nt*5, 'reanalysis'))
            print('Phase 6',date_init)
        if date_init in mjo_pha7_dates:
            data_r_week1_pha7.append(data_week(data_r, date_init, 0, nt, 'reanalysis'))
            data_r_week2_pha7.append(data_week(data_r, date_init, nt, nt*2, 'reanalysis'))
            data_r_week3_pha7.append(data_week(data_r, date_init, nt*2, nt*3, 'reanalysis'))
            data_r_week4_pha7.append(data_week(data_r, date_init, nt*3, nt*4, 'reanalysis'))
            data_r_week5_pha7.append(data_week(data_r, date_init, nt*4, nt*5, 'reanalysis'))
            print('Phase 7',date_init)
        if date_init in mjo_pha8_dates:
            data_r_week1_pha8.append(data_week(data_r, date_init, 0, nt, 'reanalysis'))
            data_r_week2_pha8.append(data_week(data_r, date_init, nt, nt*2, 'reanalysis'))
            data_r_week3_pha8.append(data_week(data_r, date_init, nt*2, nt*3, 'reanalysis'))
            data_r_week4_pha8.append(data_week(data_r, date_init, nt*3, nt*4, 'reanalysis'))
            data_r_week5_pha8.append(data_week(data_r, date_init, nt*4, nt*5, 'reanalysis'))
            print('Phase 8',date_init)
        
    data_r_week1 = comb_list(data_r_week1_pha1, data_r_week1_pha2, data_r_week1_pha3, data_r_week1_pha4, 
                            data_r_week1_pha5, data_r_week1_pha6, data_r_week1_pha7, data_r_week1_pha8)
    data_r_week2 = comb_list(data_r_week2_pha1, data_r_week2_pha2, data_r_week2_pha3, data_r_week2_pha4, 
                            data_r_week2_pha5, data_r_week2_pha6, data_r_week2_pha7, data_r_week2_pha8)
    data_r_week3 = comb_list(data_r_week3_pha1, data_r_week3_pha2, data_r_week3_pha3, data_r_week3_pha4, 
                            data_r_week3_pha5, data_r_week3_pha6, data_r_week3_pha7, data_r_week3_pha8)
    data_r_week4 = comb_list(data_r_week4_pha1, data_r_week4_pha2, data_r_week4_pha3, data_r_week4_pha4, 
                            data_r_week4_pha5, data_r_week4_pha6, data_r_week4_pha7, data_r_week4_pha8)
    data_r_week5 = comb_list(data_r_week5_pha1, data_r_week5_pha2, data_r_week5_pha3, data_r_week5_pha4, 
                            data_r_week5_pha5, data_r_week5_pha6, data_r_week5_pha7, data_r_week5_pha8)

    print(np.shape(data_r_week1_pha1),np.shape(data_r_week1_pha2),np.shape(data_r_week1_pha3),np.shape(data_r_week1_pha4),np.shape(data_r_week1_pha5),np.shape(data_r_week1_pha6),np.shape(data_r_week1_pha7),np.shape(data_r_week1_pha8))
    return data_r_week1, data_r_week2, data_r_week3, data_r_week4, data_r_week5


data_r_week1, data_r_week2, data_r_week3, data_r_week4, data_r_week5 = mjo_anoms_week_re(data_r, date_init_all, 
                                                                                                 mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)

data_z_r_week1, data_z_r_week2, data_z_r_week3, data_z_r_week4, data_z_r_week5 = mjo_anoms_week_mo(data_z_r, date_init_all, 
                                                                                                 mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)

# %%
from mpl_toolkits.axes_grid1 import make_axes_locatable
def mjo_phase_lag_plot(data_week1,data_week2,data_week3,data_week4,data_week5,cmin,cmax,figt):
    fig = plt.figure(figsize=(9,3))
    dat1 = np.ndarray((5,8)) # (week, mjo phase)
    dat2 = np.ndarray((5,8))
    dat3 = np.ndarray((5,8))
    for ii in range(5):
        if ii == 0:
            dummy = data_week1
        if ii == 1:
            dummy = data_week2
        if ii == 2:
            dummy = data_week3
        if ii == 3:
            dummy = data_week4
        if ii == 4:
            dummy = data_week5
        for jj in range(8):
            dat1[ii,jj] = np.nanmean(dummy[jj])
            
    datx = np.arange(8)+1
    daty = np.arange(5)+1
    count = 1
    dat = dat1
    fig_title = figt
    clevs = np.arange(cmin,cmax,1) # np.linspace(cmin,cmax,11)
    ax = fig.add_subplot(1,3,count)
    h = ax.contourf(datx, daty, dat, clevs, cmap='RdBu_r', extend='both')
    ax.set_xticks(ticks=datx)
    ax.set_yticks(ticks=daty)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.title(fig_title, fontsize=22)
    ax.set_xlabel('phase', fontsize=18)
    ax.set_ylabel('week', fontsize=18)

# %%
figt = 'Reanalysis vtw1+2 500hPa [Km/s]'
cmin = math.floor(np.amin(data_r_week1.values))
cmax = math.ceil(np.amax(data_r_week1.values))
mjo_phase_lag_plot(data_r_week1,data_r_week2,data_r_week3,data_r_week4,data_r_week5,sigt_r,cmin,cmax,figt)
figt = 'Model vtw1+2 500hPa [Km/s]'
mjo_phase_lag_plot(p5_data_week1,p5_data_week2,p5_data_week3,p5_data_week4,p5_data_week5,sigt_p5,cmin,cmax,figt)

figt = 'Reanalysis polar cap 100hPa Z mean'
cmin = math.floor(np.amin(data_z_r_week1.values))
cmax = math.ceil(np.amax(data_z_r_week1.values))
mjo_phase_lag_plot(data_z_r_week1,data_z_r_week2,data_z_r_week3,data_z_r_week4,data_z_r_week5,sigt_r,cmin,cmax,figt)
figt = 'Model polar cap 100hPa Z mean'
mjo_phase_lag_plot(p5_z_data_week1,p5_z_data_week2,p5_z_data_week3,p5_z_data_week4,p5_z_data_week5,sigt_p5,cmin,cmax,figt)