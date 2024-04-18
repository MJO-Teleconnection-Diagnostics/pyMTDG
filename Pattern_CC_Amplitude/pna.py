import xarray as xr
import numpy as np
import datetime
from datetime import date, timedelta
import netCDF4
import matplotlib.pyplot as plt # matplotlib version 3.2 and custom version 3.3
import proplot as plot
import cartopy
import pandas as pd
import yaml

import sys
sys.path.insert(0, '../Utils')
from pathlib import Path
from obs_utils import *
from fcst_utils import *
from PCC_utils import *


config_file=Path('../driver/config.yml').resolve()
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)


#fil_Z500a_erai='/expanse/nfs/cw3e/cwp137/_From_Comet/UFS/Z500ERAI_79-19_1.5.nc'

if (dictionary['ERAI']==True):
    fil_z500_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/z500/z500.ei.oper.an.pl.regn128sc.1979.2019.nc'
    ds_obs_name='ERAI'
if (dictionary['ERAI']==False):
    fil_z500_obs=dictionary['Path to observational data files']
    ds_obs_name='OBS'
ds_z500_obs=xr.open_dataset(fil_z500_obs)
z500_obs=get_variable_from_dataset(ds_z500_obs)


# Get the forecast period from the provided Start_Date -- End_Date period
yyyymmdd_Begin=dictionary['START_DATE']
tBegin=yyyymmdd_Begin[0:4]+'-'+yyyymmdd_Begin[4:6]+'-'+yyyymmdd_Begin[6:8]
yyyymmdd_End=dictionary['END_DATE']
tEnd=yyyymmdd_End[0:4]+'-'+yyyymmdd_End[4:6]+'-'+yyyymmdd_End[6:8]



#calculate observed anomalies
if (dictionary['Daily Anomaly'] == True):
    var_name='z'
    erai_anomaly=calcAnomObs(z500_obs.sel(time=slice(tBegin,tEnd)),var_name)
if (dictionary['Daily Anomaly'] == False):
    erai_anomaly=z500_obs
    del z500_obs

#var_name='z'
#tBegin="20110401"
#tEnd='20180430'
#erai_anomaly=calcAnomObs(Z500_obs.sel(time=slice(tBegin,tEnd)),var_name)


# Read observed time, latitude, and longitude
erai_time_in = erai_anomaly['time']
erai_yyyymmdd = np.array ( erai_time_in.dt.year * 10000 + erai_time_in.dt.month * 100 + erai_time_in.dt.day )
era_lat_in=ds_z500_obs['latitude']
era_lon_in=ds_z500_obs['longitude']


# ## Read forecast data
#fcst_files= "/expanse/nfs/cw3e/cwp137/UFS/Prototype5/z500_*.nc"
fcst_dir=dictionary['Path to z500 model data files']
ds_fcst_name=dictionary['model name']
ds_names=[ds_obs_name,ds_fcst_name]


#ds_z500_fcst=xr.open_mfdataset(fcst_files,combine='nested',concat_dim='time',parallel=True)

fcst_files=np.sort(glob.glob(str(fcst_dir+'*.nc')))
ds_tz500_fcst=xr.open_mfdataset(fcst_files,combine='nested',concat_dim='time',parallel=True)
z500_fcst=get_variable_from_dataset(ds_z500_fcst)

# Interpolate reforecast data to ERAI grid (regular 0.75 x 0.75)
rgrd_z500_fcst=regrid_scalar_spharm(ds_z500_fcst['z500'],ds_z500_fcst.latitude,ds_z500_fcst.longitude,
                                                        ds_Z500a_erai.latitude,ds_Z500a_erai.longitude)
# Calculate forecast anomalies
z500_fcst_anom=calcAnom(rgrd_z500_fcst,'z500_anom')
# Reshape the forecast data
z500_fcst_anom_reshape=reshape_forecast(z500_fcst_anom,nfc=35)
# Rename the coordinates
z500_fcst_anom_reshape=z500_fcst_anom_reshape.rename({'time': 'initial_date','forecast_day': 'time'})
# Get model time
model_yyyymmdd=z500_fcst_anom_reshape['initial_date']


# ## Read RMM data

if (dictionary['RMM']==False):
    fil_rmm_erai=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'

ds_rmm=xr.open_dataset(fil_rmm_erai,decode_times=False)

times=ds_rmm.time
init_time=date(1960,1,1)+timedelta(int(times[0]))
time=[]
for i in range(len(times)):
        time.append(init_time+timedelta(i))

ds_rmm['time'] = pd.to_datetime(time,format="%Y/%m/%d")

#fil_rmm_erai='/expanse/nfs/cw3e/cwp137/_From_Comet/UFS/rmm_ERA-Interim.nc'
#ds_rmm=xr.open_dataset(fil_rmm_erai,decode_times=False)
#times=ds_rmm['amplitude'].time
#init_time=date(1960,1,1)+timedelta(int(times[0]))
#time=[]
#for i in range(len(times)):
#        time.append(init_time+timedelta(i))

phase=np.array(ds_rmm['phase'])
amplitude=np.array(ds_rmm['amplitude'])
phase_int = np.array(list(map(np.int_, phase)))


ds_rmm['time'] = pd.to_datetime(time,format="%Y/%m/%d")
rmm_time_in = ds_rmm['time']
rmm_yyyymmdd = np.array ( rmm_time_in.dt.year * 10000 + rmm_time_in.dt.month * 100 + rmm_time_in.dt.day )
model_time_in = z500_fcst_anom_reshape['initial_date']
model_yyyymmdd = np.array ( model_time_in.dt.year * 10000 + model_time_in.dt.month * 100 + model_time_in.dt.day )


composite_start_month = 11
composite_end_month   = 3
compoiste_amplitude_threshold = 1.
phase_names = [ "8-1" , "2-3" , "4-5" , "6-7" ]
rmm_list = get_rmm_composite_list ( phase_names , model_yyyymmdd , rmm_yyyymmdd , phase_int , amplitude , compoiste_amplitude_threshold , composite_start_month , composite_end_month )


timelag=z500_fcst_anom_reshape['time']
rmm_list_ERA_67 = [ ]
rmm_tem_list_67=rmm_list[3] 
rmm_list_ERA_67 = np.empty (( len (timelag),len (rmm_tem_list_67)) ,dtype=int)
time_n=0
erai_time_in = erai_anomaly['time']
erai_yyyymmdd = np.array ( erai_time_in.dt.year * 10000 + erai_time_in.dt.month * 100 + erai_time_in.dt.day )
for time_step in range ( len ( erai_yyyymmdd ) ) :
    for irmm in range ( len ( rmm_tem_list_67 ) ) : 
        if erai_yyyymmdd [ time_step ] == model_yyyymmdd[rmm_tem_list_67 [irmm]] : 
            time_n=time_n+1
            for itime in range (len (timelag)):
                rmm_list_ERA_67 [itime,time_n-1]=time_step+itime

rmm_list_ERA_23 = [ ]
rmm_tem_list_23=rmm_list[1] 
rmm_list_ERA_23 = np.empty (( len (timelag),len (rmm_tem_list_23)) ,dtype=int)
time_n=0
for time_step in range ( len ( erai_yyyymmdd ) ) :
    for irmm in range ( len ( rmm_tem_list_23 ) ) : 
        if erai_yyyymmdd [ time_step ] == model_yyyymmdd[rmm_tem_list_23 [irmm]] : 
            time_n=time_n+1
            for itime in range (len (timelag)):
                rmm_list_ERA_23 [itime,time_n-1]=time_step+itime


# ## Calculate Pattern CC and amplitude


lat_min=20
lat_max=80
lon_min=120
lon_max=300
rmm_list_model_67=rmm_list [3]
rmm_list_model_23=rmm_list [1]
pcc_ufs_p23 = patterncc(timelag,rmm_list_ERA_23,rmm_list_model_23,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max)
pcc_ufs_p67 = patterncc(timelag,rmm_list_ERA_67,rmm_list_model_67,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max)       
pcc_ufs_p23=np.mean ( pcc_ufs_p23,axis= 1   )
pcc_ufs_p67=np.mean ( pcc_ufs_p67,axis= 1   )



amp_ufs_p23 = amplitude_metric(timelag,rmm_list_ERA_23,rmm_list_model_23,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max)
amp_ufs_p67 = amplitude_metric(timelag,rmm_list_ERA_67,rmm_list_model_67,z500_fcst_anom_reshape,erai_anomaly,lat_min,lat_max,lon_min,lon_max)       
amp_ufs_p23=np.mean ( amp_ufs_p23,axis= 1   )
amp_ufs_p67=np.mean ( amp_ufs_p67,axis= 1   )



import matplotlib.lines as mlines
fig = plt.figure(figsize=(12,6))
plt.rcParams['font.size'] = '14'
def addlegend(ax):
    P23 = mlines.Line2D([],[], color='b', label='Phases 2&3')
    P67 = mlines.Line2D([],[], color='r', label='Phases 6&7')
    ax.legend(handles=[P23, P67], ncol=1, fontsize=12)

ncol = 2
nrow = 1
for i in range(ncol):
    ax = fig.add_subplot(nrow,ncol,i+1)
    if i==0:
        ax.set_title('a. Pattern Correlation',loc='left')
        ax.plot(pcc_ufs_p23,color='b',linewidth=2,label='Phases 2&3')
        ax.plot(pcc_ufs_p67,color='r',linewidth=2,label='Phases 6&7')
    else:
        ax.set_title('b. Relative Amplitude',loc='left')
        ax.plot(amp_ufs_p23,color='b',linewidth=2,label='Phases 2&3')
        ax.plot(amp_ufs_p67,color='r',linewidth=2,label='Phases 6&7')
    if i==0: addlegend(ax)
    ax.grid(True)
