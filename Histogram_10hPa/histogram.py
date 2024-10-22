#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import numpy as np
import pandas as pd
import yaml
from pathlib import Path
from datetime import datetime 
from datetime import timedelta
from datetime import date
import os

import sys
sys.path.insert(0, '../Utils')
from u10_utils import *
from obs_utils import *

# Read yaml file
config_file=Path('../driver/config.yml').resolve()
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)

import matplotlib.pyplot as plt
from matplotlib import rcParams #For changing text properties
import matplotlib.path as mpath
import matplotlib.colors as mcolors


#tBegin=dictionary['START_DATE']
#tEnd=dictionary['END_DATE']

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

fcst_dir=dictionary['Path to zonal wind at 10 hPa model data files']
ds_fcst_name=dictionary['model name']
#model_fcst_dir = fcst_dir+str(ds_fcst_name)+'/'
#tmp = os.listdir(fcst_dir+str(ds_fcst_name))

model_fcst_dir = fcst_dir
tmp = os.listdir(fcst_dir)

dummy = sorted(tmp)
fileList = [model_fcst_dir+f for f in dummy]


if (dictionary['ERAI']==True):
    fil_u_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/u10/u10.ei.oper.an.pl.regn128sc.1979.2019.nc'
    ds_obs_name='ERAI'
    
if (dictionary['ERAI']==False):
    fil_u_obs=dictionary['Path to zonal wind at 10 hPa observation data files']
    ds_obs_name='OBS'
    
data_r = xr.open_mfdataset(fil_u_obs,combine='by_coords').compute()
data_r = np.squeeze(data_r.mean(dim=('longitude')).sel(time=data_r.time.dt.year.isin(years)).u10)


if (dictionary['RMM']==True):
    fil_rmm_obs=dictionary['Path to RMM observation data file']
    rmm=xr.open_mfdataset(fil_rmm_obs,combine='by_coords').compute()

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


# MJO events
mjo_pha1 = select_mjo_event(rmm.amplitude,rmm.phase,1)
mjo_pha2 = select_mjo_event(rmm.amplitude,rmm.phase,2)
mjo_pha3 = select_mjo_event(rmm.amplitude,rmm.phase,3)
mjo_pha4 = select_mjo_event(rmm.amplitude,rmm.phase,4)
mjo_pha5 = select_mjo_event(rmm.amplitude,rmm.phase,5)
mjo_pha6 = select_mjo_event(rmm.amplitude,rmm.phase,6)
mjo_pha7 = select_mjo_event(rmm.amplitude,rmm.phase,7)
mjo_pha8 = select_mjo_event(rmm.amplitude,rmm.phase,8)


fcst_dir=dictionary['Path to zonal wind at 10 hPa model data files']
ds_fcst_name=dictionary['model name']
#DIR = fcst_dir+ds_fcst_name
DIR = fcst_dir

VAR = 'u'
lats = 60; levs = 10; lons = [0,360]
#p5_data_week1, p5_data_week2, p5_data_week3, p5_data_week4, p5_data_week5 = mjo_week_mo(fileList, SYY, EYY, lats, levs, lons, 
#                                                                                       mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)
p5_data_week1, p5_data_week2, p5_data_week3, p5_data_week4, p5_data_week5, date_init_all = mjo_week_mo(fileList, SYY, EYY, lats, lons, 
                                                                                       mjo_pha1, mjo_pha2, mjo_pha3, mjo_pha4, mjo_pha5, mjo_pha6, mjo_pha7, mjo_pha8)


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


data_r_week1_pha12, data_r_week2_pha12, data_r_week3_pha12, data_r_week4_pha12, data_r_week5_pha12 = data_week_pha_comb(data_r_week1, data_r_week2, data_r_week3, data_r_week4, data_r_week5, 2, [0,1])
p5_data_week1_pha12, p5_data_week2_pha12, p5_data_week3_pha12, p5_data_week4_pha12, p5_data_week5_pha12 = data_week_pha_comb(p5_data_week1, p5_data_week2, p5_data_week3, p5_data_week4, p5_data_week5, 2, [0,1])


data_r_week1_pha56, data_r_week2_pha56, data_r_week3_pha56, data_r_week4_pha56, data_r_week5_pha56 = data_week_pha_comb(data_r_week1, data_r_week2, data_r_week3, data_r_week4, data_r_week5, 2, [4,5])
p5_data_week1_pha56, p5_data_week2_pha56, p5_data_week3_pha56, p5_data_week4_pha56, p5_data_week5_pha56 = data_week_pha_comb(p5_data_week1, p5_data_week2, p5_data_week3, p5_data_week4, p5_data_week5, 2, [4,5])


xlabel = 'u1060 [m/s]'
fig_name = 'u1060_hist'

histogram_mjo(ds_fcst_name,ds_obs_name,xlabel,fig_name,p5_data_week1_pha12,p5_data_week2_pha12,p5_data_week3_pha12,p5_data_week4_pha12,p5_data_week5_pha12,
              p5_data_week1_pha56,p5_data_week2_pha56,p5_data_week3_pha56,p5_data_week4_pha56,p5_data_week5_pha56,
              data_r_week1_pha12,data_r_week2_pha12,data_r_week3_pha12,data_r_week4_pha12,data_r_week5_pha12,
              data_r_week1_pha56,data_r_week2_pha56,data_r_week3_pha56,data_r_week4_pha56,data_r_week5_pha56)

