import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime 
from datetime import timedelta
from datetime import date
import matplotlib.pyplot as plt
import glob
import os

def data_week(data, date_init, nday1, nday2):
    date_start = date_init + timedelta(days=nday1)
    date_end = date_init + timedelta(days=nday2)
    tmp_week = data.sel(time=slice(date_start,date_end))
    if date_end.month >= 11 or date_end.month <= 3:
        data_week = tmp_week.mean(dim='time',skipna=True).values
    else:
        data_week = tmp_week.mean(dim='time',skipna=True).values+np.nan
    return data_week

def get_variable_from_dataset(ds):
    '''
        Extract the target variable from the dataset. Convert to target units
        
            Parameters
                ds: xarray dataset
            Returns
                da: subsetted dataArray in
    '''
    for name in ['U', 'u', 'uwnd','U10','u10','uwnd10']:
        if name in list(ds.keys()):
            break
    da = ds[name]


    return da
    raise RuntimeError("Couldn't find a zonal wind variable name")

def read_data_mo(datafn,lats,**kwargs):
    lons = kwargs.get('lons', [0,360])
    
    #files = np.sort(glob.glob(datafn+'*.nc*'))
    data_tmp = xr.open_mfdataset(datafn,combine='by_coords').compute()
    init_time = data_tmp.time[0].values
    init_year = pd.to_datetime(init_time).year
    init_month = pd.to_datetime(init_time).month
    init_day = pd.to_datetime(init_time).day
    if init_month in [1,2,3,11,12]:
        fcst = get_variable_from_dataset(data_tmp)
        data = fcst.sel(latitude=lats,method='nearest').mean(dim=('longitude'),skipna=True)
    else: 
        data = 0     
    return data, init_year, init_month, init_day

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

# MJO events
def mjo_week_mo(fileList, SYY, EYY, lats, lons, mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8, **kwargs):
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
    mjo_pha1_dates = pd.to_datetime(mjo_pha1.time,format="%Y/%m/%d")
    mjo_pha2_dates = pd.to_datetime(mjo_pha2.time,format="%Y/%m/%d")
    mjo_pha3_dates = pd.to_datetime(mjo_pha3.time,format="%Y/%m/%d")
    mjo_pha4_dates = pd.to_datetime(mjo_pha4.time,format="%Y/%m/%d")
    mjo_pha5_dates = pd.to_datetime(mjo_pha5.time,format="%Y/%m/%d")
    mjo_pha6_dates = pd.to_datetime(mjo_pha6.time,format="%Y/%m/%d")
    mjo_pha7_dates = pd.to_datetime(mjo_pha7.time,format="%Y/%m/%d")
    mjo_pha8_dates = pd.to_datetime(mjo_pha8.time,format="%Y/%m/%d")
    for ifile in range(len(fileList)):
        datafn = fileList[ifile]
        data, init_year, init_month, init_day = read_data_mo(datafn,lats,lons=lons)
        date_init = datetime(year=init_year,month=init_month,day=init_day)
        if date_init in mjo_pha1_dates:
            data_week1_pha1.append(data_week(data, date_init, 1, nt))
            data_week2_pha1.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha1.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha1.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha1.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 1',date_init)
            date_init_all.append(date_init)
        if date_init in mjo_pha2_dates:
            data_week1_pha2.append(data_week(data, date_init, 1, nt))
            data_week2_pha2.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha2.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha2.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha2.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 2',date_init)
            date_init_all.append(date_init)
        if date_init in mjo_pha3_dates:
            data_week1_pha3.append(data_week(data, date_init, 1, nt))
            data_week2_pha3.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha3.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha3.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha3.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 3',date_init)
            date_init_all.append(date_init)
        if date_init in mjo_pha4_dates:
            data_week1_pha4.append(data_week(data, date_init, 1, nt))
            data_week2_pha4.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha4.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha4.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha4.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 4',date_init)
            date_init_all.append(date_init)
        if date_init in mjo_pha5_dates:
            data_week1_pha5.append(data_week(data, date_init, 1, nt)) 
            data_week2_pha5.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha5.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha5.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha5.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 5',date_init)
            date_init_all.append(date_init)
        if date_init in mjo_pha6_dates:
            data_week1_pha6.append(data_week(data, date_init, 1, nt))
            data_week2_pha6.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha6.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha6.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha6.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 6',date_init)
            date_init_all.append(date_init)
        if date_init in mjo_pha7_dates:
            data_week1_pha7.append(data_week(data, date_init, 1, nt))
            data_week2_pha7.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha7.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha7.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha7.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 7',date_init)
            date_init_all.append(date_init)
        if date_init in mjo_pha8_dates:
            data_week1_pha8.append(data_week(data, date_init, 1, nt))
            data_week2_pha8.append(data_week(data, date_init, nt+1, nt*2))
            data_week3_pha8.append(data_week(data, date_init, nt*2+1, nt*3))
            data_week4_pha8.append(data_week(data, date_init, nt*3+1, nt*4))
            data_week5_pha8.append(data_week(data, date_init, nt*4+1, nt*5))
            print('Phase 8',date_init)
            date_init_all.append(date_init)
    
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
    return data_week1, data_week2, data_week3, data_week4, data_week5, date_init_all

def data_week_pha_comb(data_week1,data_week2,data_week3,data_week4,data_week5,npha,phase):
    data_week1_pha, data_week2_pha, data_week3_pha, data_week4_pha, data_week5_pha = [],[],[],[],[]
    for ii in range(npha):
        data_week1_pha.append(data_week1[phase[ii]])
        data_week2_pha.append(data_week2[phase[ii]])
        data_week3_pha.append(data_week3[phase[ii]])
        data_week4_pha.append(data_week4[phase[ii]])
        data_week5_pha.append(data_week5[phase[ii]])
    return data_week1_pha, data_week2_pha, data_week3_pha, data_week4_pha, data_week5_pha

# plotting histogram
def histogram_mjo(EXP,OBS,xlabel,fig_name,data_week1_pha12,data_week2_pha12,data_week3_pha12,data_week4_pha12,data_week5_pha12,
                  data_week1_pha56,data_week2_pha56,data_week3_pha56,data_week4_pha56,data_week5_pha56,
                 data_r_week1_pha12,data_r_week2_pha12,data_r_week3_pha12,data_r_week4_pha12,data_r_week5_pha12,
                 data_r_week1_pha56,data_r_week2_pha56,data_r_week3_pha56,data_r_week4_pha56,data_r_week5_pha56):
    #fig = plt.figure(figsize=(20,2))
    fig = plt.figure(figsize=(8,6))
    #fig_title = [EXP+' Week1-2', EXP+' Week3-5', 'ERA-Interim Week1-2', 'ERA-Interim Week3-5']
    fig_title = [OBS+' Week1-2', EXP+' Week1-2', OBS+' Week3-5', EXP+' Week3-5']
    count = 1
    for ii in range(4):
        if ii == 0: 
            #tmp = np.hstack(data_week1_pha12+data_week2_pha12)
            #tmp1 = np.hstack(data_week1_pha56+data_week2_pha56)
            tmp = np.hstack(data_r_week1_pha12+data_r_week2_pha12)
            tmp1 = np.hstack(data_r_week1_pha56+data_r_week2_pha56)
        if ii == 1:
            #tmp = np.hstack(data_week3_pha12+data_week4_pha12+data_week5_pha12)
            #tmp1 = np.hstack(data_week3_pha56+data_week4_pha56+data_week5_pha56)
            tmp = np.hstack(data_week1_pha12+data_week2_pha12)
            tmp1 = np.hstack(data_week1_pha56+data_week2_pha56)
        if ii == 2: 
            #tmp = np.hstack(data_r_week1_pha12+data_r_week2_pha12)
            #tmp1 = np.hstack(data_r_week1_pha56+data_r_week2_pha56)
            tmp = np.hstack(data_r_week3_pha12+data_r_week4_pha12+data_r_week5_pha12)
            tmp1 = np.hstack(data_r_week3_pha56+data_r_week4_pha56+data_r_week5_pha56)
        if ii == 3: 
            #tmp = np.hstack(data_r_week3_pha12+data_r_week4_pha12+data_r_week5_pha12)
            #tmp1 = np.hstack(data_r_week3_pha56+data_r_week4_pha56+data_r_week5_pha56)
            tmp = np.hstack(data_week3_pha12+data_week4_pha12+data_week5_pha12)
            tmp1 = np.hstack(data_week3_pha56+data_week4_pha56+data_week5_pha56)
        weights = np.ones_like(tmp) / float(len(tmp))
        weights_1 = np.ones_like(tmp1) / float(len(tmp1))
        #ax = fig.add_subplot(1,5,count) #-30,80,5   -10,300,10   -10,36,2   -5,30,1.5
        ax = fig.add_subplot(2,2,count) #-30,80,5 -10,300,10 -10,36,2 -5,30,1.5
        cmin, cmax, cinterv = -30,80,5 
        plt.hist(tmp,bins=np.arange(cmin, cmax, cinterv), weights=weights, edgecolor="black", color="blue", alpha = 0.7)
        plt.hist(tmp1,bins=np.arange(cmin, cmax, cinterv), weights=weights_1, edgecolor="black", color="yellow", alpha = 0.5)
        plt.subplots_adjust(left=0.1,
                     bottom=0.1, 
                     right=0.9, 
                     top=0.9, 
                     wspace=0.2, 
                     hspace=0.4)
        ax.legend(labels=['MJO12', 'MJO56'])
        plt.vlines(np.nanmean(tmp), 0, 0.52, colors='b')
        plt.vlines(np.nanpercentile(tmp, 5), 0, 0.52, colors='b', linestyle='dashed')
        plt.vlines(np.nanpercentile(tmp, 95), 0, 0.52, colors='b', linestyle='dashed')
        plt.vlines(np.nanmean(tmp1), 0, 0.52, colors='y')
        plt.vlines(np.nanpercentile(tmp1, 5), 0, 0.52, colors='y', linestyle='dashed')
        plt.vlines(np.nanpercentile(tmp1, 95), 0, 0.52, colors='y', linestyle='dashed')
        plt.ylim([0, 0.4])
        plt.title(fig_title[ii])
        ax.set_xlabel(xlabel)
        if count == 1 or count == 3:
            ax.set_ylabel('Frequency')
        ax.grid(axis='y')
        count += 1
    if not os.path.exists('../output/Zonal_Wind_Hist/'+EXP): 
        os.mkdir('../output/Zonal_Wind_Hist/'+EXP)
    plt.savefig('../output/Zonal_Wind_Hist/'+EXP+'/'+fig_name+'.png',bbox_inches = 'tight')
    return


