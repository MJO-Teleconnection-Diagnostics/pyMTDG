# %%
import xarray as xr
import numpy as np
import pandas as pd
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
    fil_obs=dictionary['DIR_IN']+'/ERA-Interim/vt500w12-1979-2018.nc'
    # fil_obs=dictionary['DIR_IN']+'/ERA-Interim/gph100-1979-2018.nc'
    ds_obs_name='ERAI'
    
if (dictionary['ERAI']==False):
    # need to add "Path to heat flux at 500 hPa observation data files" to config.yml
    fil_obs=dictionary['Path to heat flux at 500 hPa observation data files']
    ds_obs_name='OBS'
data_obs = xr.open_mfdataset(fil_obs,combine='by_coords').compute()
data_obs = np.squeeze(data_obs.sel(time=data_obs.time.dt.year.isin(years)))

# %%
# compute anomaly
data_r_clim = data_obs.groupby(data_obs.time.dt.dayofyear).mean(dim='time')
data_r = data_obs.groupby(data_obs.time.dt.dayofyear) - data_r_clim

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

# %%
# model heat flux with MJO events
def compute_heatflux_anom(fileList_v, fileList_t, lats, levs, lons, **kwargs):
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
    date_init_all = []
    
    for ifile in range(len(fileList_v)):
        datafn = fileList_t[ifile]
        data_t = xr.open_mfdataset(datafn,combine='by_coords').compute()
        init_time = data_t.time[0].values
        init_month = pd.to_datetime(init_time).month
        if init_month in [1,2,3,11,12]:
            init_year = pd.to_datetime(init_time).year
            init_day = pd.to_datetime(init_time).day
            date_init = datetime(year=init_year,month=init_month,day=init_day)
            data_t = data_t.sel(latitude=slice(lats[0],lats[1]), lev=levs).t
            
            datafn = fileList_v[ifile]
            data_v = xr.open_mfdataset(datafn,combine='by_coords').compute()
            data_v = data_v.sel(latitude=slice(lats[0],lats[1]), lev=levs).v
            date_init_all.append(date_init)

            wavn = 3 # wave1+2
            # wavn = 2 # wave1
            data = heat_flux_amp(data_t,data_v,wavn)
            nfct = len(data.time)
            if iyear == SYY:
                data_all = data
            else:
                data_all = xr.concat([data_all, data],"time") 
    data_clim = xr.concat([data_all[ii:nfct*7:nfct].mean(dim='time') for ii in range(nfct)],"time")
    times = data_all.time
    days=[]
    for i in range(nyrs):
        days.append(np.arange(nfct))
    days=np.reshape(days,nyrs*nfct)
    data_all['time']=days
    anoms=data_all.groupby(data_all.time)-data_clim
    anoms['time']=times
    return anoms, date_init_all

# %%
# model heat flux with MJO events
def compute_gph_anom(fileList_z, lats, levs, lons, **kwargs):
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
    date_init_all = []
    
    for ifile in range(len(fileList_z)):
        datafn = fileList_z[ifile]
        data = xr.open_mfdataset(datafn,combine='by_coords').compute()
        init_time = data.time[0].values
        init_month = pd.to_datetime(init_time).month
        if init_month in [1,2,3,11,12]:
            init_year = pd.to_datetime(init_time).year
            init_day = pd.to_datetime(init_time).day
            date_init = datetime(year=init_year,month=init_month,day=init_day)

            data_t = data.sel(longitude=slice(lons[0],lons[1]), latitude=slice(lats[0],lats[1]), lev=levs)
            del data
            lon = data_t.coords['longitude'].values
            lat = data_t.coords['latitude'].values
            dlat = np.deg2rad(np.abs(lat[1]-lat[0]))
            dlon = np.deg2rad(np.abs(lon[1]-lon[0]))
            darea = dlat * dlon * np.cos(np.deg2rad(data_t.latitude))
            weights = darea.where(data_t.gh[0])
            weights_sum = weights.sum(dim=('longitude', 'latitude'))
            data = (data_t.gh * weights).sum(dim=('longitude', 'latitude')) / weights_sum
            
            nfct = len(data.time)
            if iyear == SYY:
                data_all = data
            else:
                data_all = xr.concat([data_all, data],"time") 
    data_clim = xr.concat([data_all[ii:nfct*7:nfct].mean(dim='time') for ii in range(nfct)],"time")
    times = data_all.time
    days=[]
    for i in range(nyrs):
        days.append(np.arange(nfct))
    days=np.reshape(days,nyrs*nfct)
    data_all['time']=days
    anoms=data_all.groupby(data_all.time)-data_clim
    anoms['time']=times
    return anoms, date_init_all

# %%
def data_week(data, date_init, nday1, nday2):
    date_start = date_init + timedelta(days=nday1)
    date_end = date_init + timedelta(days=nday2)
    tmp_week = data.sel(time=slice(date_start,date_end))
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
def mjo_anoms_week_mo(data, date_init_all, mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8, **kwargs):
    INITMON = kwargs.get('INITMON', ['01','02','03','11','12'])
    INITDAY = kwargs.get('INITDAY', ['01','15'])
    nt = kwargs.get('nt', 7)

    mjo_pha1_dates = pd.to_datetime(mjo_pha1.time,format="%Y/%m/%d")
    mjo_pha2_dates = pd.to_datetime(mjo_pha2.time,format="%Y/%m/%d")
    mjo_pha3_dates = pd.to_datetime(mjo_pha3.time,format="%Y/%m/%d")
    mjo_pha4_dates = pd.to_datetime(mjo_pha4.time,format="%Y/%m/%d")
    mjo_pha5_dates = pd.to_datetime(mjo_pha5.time,format="%Y/%m/%d")
    mjo_pha6_dates = pd.to_datetime(mjo_pha6.time,format="%Y/%m/%d")
    mjo_pha7_dates = pd.to_datetime(mjo_pha7.time,format="%Y/%m/%d")
    mjo_pha8_dates = pd.to_datetime(mjo_pha8.time,format="%Y/%m/%d")
    for it in range(date_init_all):
        date_init = date_init_all[it]
        if date_init in mjo_pha1_dates:
            data_week1_pha1.append(data_week(data, date_init, 1, nt))
            data_week2_pha1.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha1.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha1.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha1.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 1',date_init)
        if date_init in mjo_pha2_dates:
            data_week1_pha2.append(data_week(data, date_init, 1, nt))
            data_week2_pha2.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha2.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha2.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha2.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 2',date_init)
        if date_init in mjo_pha3_dates:
            data_week1_pha3.append(data_week(data, date_init, 1, nt))
            data_week2_pha3.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha3.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha3.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha3.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 3',date_init)
        if date_init in mjo_pha4_dates:
            data_week1_pha4.append(data_week(data, date_init, 1, nt))
            data_week2_pha4.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha4.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha4.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha4.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 4',date_init)
        if date_init in mjo_pha5_dates:
            data_week1_pha5.append(data_week(data, date_init, 1, nt)) 
            data_week2_pha5.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha5.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha5.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha5.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 5',date_init)
        if date_init in mjo_pha6_dates:
            data_week1_pha6.append(data_week(data, date_init, 1, nt))
            data_week2_pha6.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha6.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha6.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha6.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 6',date_init)
        if date_init in mjo_pha7_dates:
            data_week1_pha7.append(data_week(data, date_init, 1, nt))
            data_week2_pha7.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha7.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha7.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha7.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 7',date_init)
        if date_init in mjo_pha8_dates:
            data_week1_pha8.append(data_week(data, date_init, 1, nt))
            data_week2_pha8.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha8.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha8.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha8.append(data_week(data, date_init, nt*4+1, nt*5))
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

p5_anoms, date_init_all = compute_heatflux_anom(fileList_v, fileList_t, lats, levs, lons)

ds_fcst_name='UFS6' 

fileList_v, fileList_t = extract_files(fcst_dir_v, fcst_dir_t, ds_fcst_name)

p6_anoms, date_init_all = compute_heatflux_anom(fileList_v, fileList_t, lats, levs, lons)

ds_fcst_name='UFS7' 

fileList_v, fileList_t = extract_files(fcst_dir_v, fcst_dir_t, ds_fcst_name)

p7_anoms, date_init_all = compute_heatflux_anom(fileList_v, fileList_t, lats, levs, lons)

ds_fcst_name='UFS8' 

fileList_v, fileList_t = extract_files(fcst_dir_v, fcst_dir_t, ds_fcst_name)

p8_anoms, date_init_all = compute_heatflux_anom(fileList_v, fileList_t, lats, levs, lons)


# %%
# compute gph anomaly
lats = [90,55]; levs = [500,300,100,10]; lons = [300,360]

fcst_dir_z = '/mjo/MJO-Teleconnections-develop/data/z/'
fcst_dir_t = '/mjo/MJO-Teleconnections-develop/data/t/'

ds_fcst_name='UFS5' 

fileList_z, fileList_t = extract_files(fcst_dir_z, fcst_dir_t, ds_fcst_name)

p5_anoms, date_init_all = compute_gph_anom(fileList_z, fileList_t, lats, levs, lons)

ds_fcst_name='UFS6' 

fileList_z, fileList_t = extract_files(fcst_dir_z, fcst_dir_t, ds_fcst_name)

p6_anoms, date_init_all = compute_heatflux_anom(fileList_z, fileList_t, lats, levs, lons)

ds_fcst_name='UFS7' 

fileList_z, fileList_t = extract_files(fcst_dir_z, fcst_dir_t, ds_fcst_name)

p7_anoms, date_init_all = compute_heatflux_anom(fileList_z, fileList_t, lats, levs, lons)

ds_fcst_name='UFS8' 

fileList_z, fileList_t = extract_files(fcst_dir_z, fcst_dir_t, ds_fcst_name)

p8_anoms, date_init_all = compute_heatflux_anom(fileList_z, fileList_t, lats, levs, lons)


# %%
# MJO events models
p5_data_week1, p5_data_week2, p5_data_week3, p5_data_week4, p5_data_week5 = mjo_anoms_week_mo(p5_anoms, date_init_all, 
                                                                                                 mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)

p6_data_week1, p6_data_week2, p6_data_week3, p6_data_week4, p6_data_week5 = mjo_anoms_week_mo(p6_anoms, date_init_all, 
                                                                                                 mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)

p7_data_week1, p7_data_week2, p7_data_week3, p7_data_week4, p7_data_week5 = mjo_anoms_week_mo(p7_anoms, date_init_all,
                                                                                                 mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)

p8_data_week1, p8_data_week2, p8_data_week3, p8_data_week4, p8_data_week5 = mjo_anoms_week_mo(p8_anoms, date_init_all, 
                                                                                                 mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)


# %%
# MJO events reanalysis
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
        data_r_week1_pha1.append(data_week(data_r, date_init, 0, nt))
        data_r_week2_pha1.append(data_week(data_r, date_init, nt, nt*2))
        data_r_week3_pha1.append(data_week(data_r, date_init, nt*2, nt*3))
        data_r_week4_pha1.append(data_week(data_r, date_init, nt*3, nt*4))
        data_r_week5_pha1.append(data_week(data_r, date_init, nt*4, nt*5))
        print('Phase 1',date_init)
    if date_init in mjo_pha2_dates:
        data_r_week1_pha2.append(data_week(data_r, date_init, 0, nt))
        data_r_week2_pha2.append(data_week(data_r, date_init, nt, nt*2))
        data_r_week3_pha2.append(data_week(data_r, date_init, nt*2, nt*3))
        data_r_week4_pha2.append(data_week(data_r, date_init, nt*3, nt*4))
        data_r_week5_pha2.append(data_week(data_r, date_init, nt*4, nt*5))
        print('Phase 2',date_init)
    if date_init in mjo_pha3_dates:
        data_r_week1_pha3.append(data_week(data_r, date_init, 0, nt))
        data_r_week2_pha3.append(data_week(data_r, date_init, nt, nt*2))
        data_r_week3_pha3.append(data_week(data_r, date_init, nt*2, nt*3))
        data_r_week4_pha3.append(data_week(data_r, date_init, nt*3, nt*4))
        data_r_week5_pha3.append(data_week(data_r, date_init, nt*4, nt*5))
        print('Phase 3',date_init)
    if date_init in mjo_pha4_dates:
        data_r_week1_pha4.append(data_week(data_r, date_init, 0, nt))
        data_r_week2_pha4.append(data_week(data_r, date_init, nt, nt*2))
        data_r_week3_pha4.append(data_week(data_r, date_init, nt*2, nt*3))
        data_r_week4_pha4.append(data_week(data_r, date_init, nt*3, nt*4))
        data_r_week5_pha4.append(data_week(data_r, date_init, nt*4, nt*5))
        print('Phase 4',date_init)
    if date_init in mjo_pha5_dates:
        data_r_week1_pha5.append(data_week(data_r, date_init, 0, nt)) 
        data_r_week2_pha5.append(data_week(data_r, date_init, nt, nt*2))
        data_r_week3_pha5.append(data_week(data_r, date_init, nt*2, nt*3))
        data_r_week4_pha5.append(data_week(data_r, date_init, nt*3, nt*4))
        data_r_week5_pha5.append(data_week(data_r, date_init, nt*4, nt*5))
        print('Phase 5',date_init)
    if date_init in mjo_pha6_dates:
        data_r_week1_pha6.append(data_week(data_r, date_init, 0, nt))
        data_r_week2_pha6.append(data_week(data_r, date_init, nt, nt*2))
        data_r_week3_pha6.append(data_week(data_r, date_init, nt*2, nt*3))
        data_r_week4_pha6.append(data_week(data_r, date_init, nt*3, nt*4))
        data_r_week5_pha6.append(data_week(data_r, date_init, nt*4, nt*5))
        print('Phase 6',date_init)
    if date_init in mjo_pha7_dates:
        data_r_week1_pha7.append(data_week(data_r, date_init, 0, nt))
        data_r_week2_pha7.append(data_week(data_r, date_init, nt, nt*2))
        data_r_week3_pha7.append(data_week(data_r, date_init, nt*2, nt*3))
        data_r_week4_pha7.append(data_week(data_r, date_init, nt*3, nt*4))
        data_r_week5_pha7.append(data_week(data_r, date_init, nt*4, nt*5))
        print('Phase 7',date_init)
    if date_init in mjo_pha8_dates:
        data_r_week1_pha8.append(data_week(data_r, date_init, 0, nt))
        data_r_week2_pha8.append(data_week(data_r, date_init, nt, nt*2))
        data_r_week3_pha8.append(data_week(data_r, date_init, nt*2, nt*3))
        data_r_week4_pha8.append(data_week(data_r, date_init, nt*3, nt*4))
        data_r_week5_pha8.append(data_week(data_r, date_init, nt*4, nt*5))
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


# %%
from mpl_toolkits.axes_grid1 import make_axes_locatable
def mjo_phase_lag_plot(data_week1,data_week2,data_week3,data_week4,data_week5,figt,fig_name):
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
    cmin,cmax = -15, 16  #500hPaw1:1,4.4  500hPaw1+2:2,10 u1060:2,26
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
    plt.savefig(fig_name)

# %%
figt = 'vtw1+2 500hPa [Km/s]'
fig_name = 'ERAI_vtw12_500_ndjfm_mjo1-8_resub.png'
mjo_phase_lag_plot(data_r_week1,data_r_week2,data_r_week3,data_r_week4,data_r_week5,sigt_r,figt,fig_name)
fig_name = 'UFSp5_vtw12_500_ndjfm_mjo1-8.png'
mjo_phase_lag_plot(p5_data_week1,p5_data_week2,p5_data_week3,p5_data_week4,p5_data_week5,sigt_p5,figt,fig_name)
fig_name = 'UFSp6_vtw12_500_ndjfm_mjo1-8.png'
mjo_phase_lag_plot(p6_data_week1,p6_data_week2,p6_data_week3,p6_data_week4,p6_data_week5,sigt_p6,figt,fig_name)
fig_name = 'UFSp7_vtw12_500_ndjfm_mjo1-8.png'
mjo_phase_lag_plot(p7_data_week1,p7_data_week2,p7_data_week3,p7_data_week4,p7_data_week5,sigt_p7,figt,fig_name)
fig_name = 'UFSp8_vtw12_500_ndjfm_mjo1-8.png'
mjo_phase_lag_plot(p8_data_week1,p8_data_week2,p8_data_week3,p8_data_week4,p8_data_week5,sigt_p8,figt,fig_name)