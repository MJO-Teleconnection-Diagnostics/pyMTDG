import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime 
from datetime import timedelta
from datetime import date
import matplotlib.pyplot as plt
import os


def get_variable_from_dataset(ds):
    '''
        Extract the target variable from the dataset. Convert to target units
        
            Parameters
                ds: xarray dataset
            Returns
                da: subsetted dataArray in
    '''
    for name in ['V', 'v', 'v500','vwnd','T','t','temp','t500','Z','z','gh','z100']:
        if name in list(ds.keys()):
            break
    da = ds[name]
    
    # convert geopotential to geopotential height if needed
    for units in ['m**2 s**-2', 'm^2/s^2', 'm2/s2','m2s-2', 'm2 s-2']:
            if units == da.units:
                print('converting geopotential to geopotential height')
                da = da/9.81
                da.attrs['units']='m'
                break
    return da
    raise RuntimeError("Couldn't find a wind, geopotential, or temperature variable name")

#%%
def heat_flux_amp(data_t, data_v, wavn):
    nlon = len(data_t.longitude.values)
    data_t_fft = np.fft.fft(data_t,axis=2)
    data_v_fft = np.fft.fft(data_v,axis=2)
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
    return data_r_week1, data_r_week2, data_r_week3, data_r_week4, data_r_week5

# %%
def anom_re(data_obs):
    data_r_clim = data_obs.groupby(data_obs.time.dt.dayofyear).mean(dim='time')
    data_r = data_obs.groupby(data_obs.time.dt.dayofyear) - data_r_clim
    return data_r

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
def extract_files(fcst_dir_1, fcst_dir_2,ds_fcst_name):
    model_fcst_dir = fcst_dir_1+'/'
    tmp = os.listdir(fcst_dir_1)
    dummy = sorted(tmp)
    fileList_1 = [model_fcst_dir+f for f in dummy]
    
    model_fcst_dir = fcst_dir_2+'/'
    tmp = os.listdir(fcst_dir_2)
    dummy = sorted(tmp)
    fileList_2 = [model_fcst_dir+f for f in dummy]
    return fileList_1, fileList_2

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