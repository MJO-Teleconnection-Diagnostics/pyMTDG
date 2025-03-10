import xarray as xr
import numpy as np
import pandas as pd
import datetime
from datetime import date, timedelta, datetime

import yaml
import glob
import gc

import sys
import copy

sys.path.insert(0, '../Utils')
from pathlib import Path
from obs_utils import*
from fcst_utils import *
from mjo_utils import *

config_file=Path('../driver/config.testing.yml').resolve()
if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        raise  
        
if dictionary.get('Daily Anomaly', False):
    fil_obs_u200=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/u200/u200.2p5.1979.2019.nc'
    fil_obs_u850=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/u850/u850.2p5.1979.2019.nc'
    fil_obs_olr=dictionary['DIR_IN']+'/mjo_teleconnections_data/noaa/olr/olr.day.mean.1979.2019.nc'
    ds_obs_name='ERAI'
    
    ds_obs_u200 = xr.open_dataset(fil_obs_u200,chunks='auto')
    ds_obs_u850 = xr.open_dataset(fil_obs_u850,chunks='auto')
    ds_obs_olr = xr.open_dataset(fil_obs_olr,chunks='auto')
    
else:
    fil_obs_u200=dictionary['Path to U200 observation data files']
    fil_obs_u850=dictionary['Path to U850 observation data files']
    fil_obs_olr=dictionary['Path to OLR observation data files']
    ds_obs_name='OBS'
    
    nf_u200,ds_obs_u200=open_user_obs_fil(fil_obs_u200)
    nf_u850,ds_obs_u850=open_user_obs_fil(fil_obs_u850)
    nf_olr,ds_obs_olr=open_user_obs_fil(fil_obs_olr)
    
    table={'u850':nf_u850, 'u200':nf_u850,'olr':nf_olr}

    if ( (nf_u200!= nf_u850) or (nf_u200 != nf_olr) or (nf_u850 != nf_olr) ):
        print('# of u850 files:{u850:d}; # of u200 files:{u200:d}; # of olr files:{olr:d}'.format(**table))
        raise RuntimeError('Number of files for u850, u200 and olr are not the same:')
    
#selecting data from 120 days before start date to end date given by user
yyyymmdd_Begin=dictionary['START_DATE']
start_date=yyyymmdd_Begin[0:4]+'-'+yyyymmdd_Begin[4:6]+'-'+yyyymmdd_Begin[6:8]
start_date_120 = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=121)).strftime('%Y-%m-%d')
yyyymmdd_End=dictionary['END_DATE']
end_date=yyyymmdd_End[0:4]+'-'+yyyymmdd_End[4:6]+'-'+yyyymmdd_End[6:8]

ds_obs_u200_d = get_variable_from_dataset(ds_obs_u200).sel(time=slice(start_date_120,end_date ))
ds_obs_u850_d = get_variable_from_dataset(ds_obs_u850).sel(time=slice(start_date_120,end_date ))
ds_obs_olr_d = get_variable_from_dataset(ds_obs_olr).sel(time=slice(start_date_120,end_date ))

#Compute anomalies
if dictionary.get('Daily Anomaly', False):
    u200_obs_anom=calcAnomObs(ds_obs_u200_d,'u200_anom') 
    u850_obs_anom=calcAnomObs(ds_obs_u850_d,'u850_anom')
    olr_obs_anom=calcAnomObs(ds_obs_olr_d,'olr_anom')
    
else:
    u200_obs_anom,u850_obs_anom, olr_obs_anom = map(
        copy.deepcopy,
        [ds_obs_u200_d,ds_obs_u850_d,ds_obs_olr_d]
    )
del ds_obs_u200_d, ds_obs_u850_d, ds_obs_olr_d
gc.collect()

# Meridional average of OBS between 15S - 15N
obs_avgd_u200 = slice_avg(u200_obs_anom.load())
obs_avgd_u850 = slice_avg(u850_obs_anom.load())
obs_avgd_olr = slice_avg(olr_obs_anom.load())

##EOF analysis
ds_eof=xr.open_dataset('../MJO/ceof.nc')
modes=2
eof_olr=ds_eof['olr'][:modes,:]
eof_u850=ds_eof['u850'][:modes,:]
eof_u200=ds_eof['u200'][:modes,:]


# Subtract the 120-day rolling mean and normalize
observation_u200_120_nor = remove_120days_seasonalvar_obs(obs_avgd_u200,ds_eof.norm_u200)
observation_u850_120_nor = remove_120days_seasonalvar_obs(obs_avgd_u850,ds_eof.norm_u850)
observation_olr_120_nor = remove_120days_seasonalvar_obs(obs_avgd_olr,ds_eof.norm_u200)

olr_obs = observation_olr_120_nor.dropna('time') #longitude, time
u200_obs = observation_u200_120_nor.dropna('time')
u850_obs = observation_u850_120_nor.dropna('time')

olrt_dot1_obs= xr.dot(olr_obs[:,:],eof_olr[0,:],dims='longitude')
olrt_dot2_obs = xr.dot(olr_obs[:,:],eof_olr[1,:],dims='longitude')

u200t_dot1_obs = xr.dot(u200_obs[:,:],eof_u200[0,:],dims='longitude')
u200t_dot2_obs = xr.dot(u200_obs[:,:],eof_u200[1,:],dims='longitude')

u850t_dot1_obs = xr.dot(u850_obs[:,:],eof_u850[0,:],dims='longitude')
u850t_dot2_obs = xr.dot(u850_obs[:,:],eof_u850[1,:],dims='longitude')
        
innerdot1 = (olrt_dot1_obs + u200t_dot1_obs + u850t_dot1_obs) 
innerdot2  = (olrt_dot2_obs + u200t_dot2_obs + u850t_dot2_obs) 
pc1_obs = innerdot1 / 12.0  #obs std
pc2_obs = innerdot2 / 12.0  #obs std
pc1_obs=pc1_obs.dropna('time')
pc2_obs=pc2_obs.dropna('time') 

print('started model MJO calculation')
    
ds_fcst_name=dictionary['model name']
ds_names=[ds_obs_name,ds_fcst_name]
nfcst_days=dictionary['length of forecasts']

fcst_dir = [
     dictionary['Path to zonal wind at 200 hPa model data files'],
     dictionary['Path to zonal wind at 850 hPa model data files'],
     dictionary['Path to OLR model data files']
     ]

file_dict = get_netcdf_files(fcst_dir)
verify_file_counts(file_dict)

#Read forecast data 
fcst_u200, fcst_u850, fcst_olr = process_data(file_dict)

# Regriding to verification grid
rgrd_fcst_u200,rgrd_obs_u200=regrid(fcst_u200,u200_obs_anom,fcst_u200.latitude,fcst_u200.longitude,
                                        ds_obs_u200.latitude,ds_obs_u200.longitude,scalar=True)
print('u200 regridding done')
rgrd_fcst_u850,rgrd_obs_u850=regrid(fcst_u850,u850_obs_anom,fcst_u850.latitude,fcst_u850.longitude,
                                         ds_obs_u850.latitude,ds_obs_u850.longitude,scalar=True)
print('850 regridding done')
rgrd_fcst_olr,rgrd_obs_olr=regrid(fcst_olr,olr_obs_anom,fcst_olr.latitude,fcst_olr.longitude,
                                         ds_obs_olr.latitude,ds_obs_olr.longitude,scalar=True)
print('olr regridding done')

# If required calculate forecast anomalies
if dictionary.get('Daily Anomaly', False):
    var_name = 'u200_anom'
    u200_fcst_anom = calcAnom(rgrd_fcst_u200, var_name)
    var_name = 'u850_anom'
    u850_fcst_anom = calcAnom(rgrd_fcst_u850, var_name)
    var_name = 'olr_anom'
    olr_fcst_anom = calcAnom(rgrd_fcst_olr, var_name)
    
else:
    u200_fcst_anom,u850_fcst_anom,olr_fcst_anom = map(
        copy.deepcopy,
        [rgrd_fcst_u200, rgrd_fcst_u850,rgrd_fcst_olr]
    )
del rgrd_fcst_u200, rgrd_fcst_u850, rgrd_fcst_olr
gc.collect()

# Meridional average of forecast between 15S - 15N
fcst_avgd_u200 = slice_avg(u200_fcst_anom.load())
fcst_avgd_u850 = slice_avg(u850_fcst_anom.load())
fcst_avgd_olr = slice_avg(olr_fcst_anom.load())

# Extract the initial dates of the forecast
nfc = int(len(fcst_avgd_u200.time)/len(file_dict['u200']))
init_days = fcst_avgd_u200.time[::nfc]
exp_start_dates = pd.to_datetime(init_days)

# Subtract the 120-day rolling mean and normalize by std of observations
fcst_u200_120_nor_lis = remove_120days_seasonalvar(exp_start_dates, fcst_avgd_u200, obs_avgd_u200, 
                                                   ds_eof.norm_u200,nfc)
fcst_u850_120_nor_lis = remove_120days_seasonalvar(exp_start_dates, fcst_avgd_u850, obs_avgd_u850, 
                                                   ds_eof.norm_u850,nfc)
fcst_olr_120_nor_lis = remove_120days_seasonalvar(exp_start_dates, fcst_avgd_olr, obs_avgd_olr, 
                                                  ds_eof.norm_olr,nfc)

# Project observed observed EOF1 and EOF2 on forecast anomaly to compute PC1 & PC2 of forecast
pc1s_fcst_lis = []
pc2s_fcst_lis = []

for i in range(len(fcst_u200_120_nor_lis)):
    u200_fcst = fcst_u200_120_nor_lis[i]
    olr_fcst = fcst_olr_120_nor_lis[i]
    u850_fcst = fcst_u850_120_nor_lis[i]
    
    olrt_dot1_fcst = xr.dot(olr_fcst[:,:], eof_olr[0,:], dims='longitude')
    olrt_dot2_fcst = xr.dot(olr_fcst[:,:], eof_olr[1,:], dims='longitude')
    

    u200t_dot1_fcst = xr.dot(u200_fcst[:,:], eof_u200[0,:], dims='longitude')
    u200t_dot2_fcst = xr.dot(u200_fcst[:,:], eof_u200[1,:], dims='longitude')
    
    u850t_dot1_fcst = xr.dot(u850_fcst[:,:], eof_u850[0,:], dims='longitude')
    u850t_dot2_fcst = xr.dot(u850_fcst[:,:], eof_u850[1,:], dims='longitude')

    innerdot1_fcst = (olrt_dot1_fcst + u200t_dot1_fcst + u850t_dot1_fcst) 
    innerdot2_fcst  = (olrt_dot2_fcst + u200t_dot2_fcst + u850t_dot2_fcst)
    
    pc1_fcst = innerdot1_fcst / 12.0  # obs std
    pc2_fcst = innerdot2_fcst / 12.0  # obs std
        
    pc1_fcst = pc1_fcst.dropna('time')
    pc2_fcst = pc2_fcst.dropna('time')
    
    pc1s_fcst_lis.append(pc1_fcst)
    pc2s_fcst_lis.append(pc2_fcst)
    
# Compute PC1 & PC2 of observations for the same dates as the forecast
pc1s_obs_lis = []
pc2s_obs_lis = []

for i in range(len(pc1s_fcst_lis)):
    sd = np.datetime_as_string(pc1s_fcst_lis[i].time.values[0], unit='D')
    ed = np.datetime_as_string(pc1s_fcst_lis[i].time.values[-1], unit='D')
    pc1s = pc1_obs.sel(time=slice(sd, ed))
    pc2s = pc2_obs.sel(time=slice(sd, ed))
    pc1s_obs_lis.append(pc1s)
    pc2s_obs_lis.append(pc2s)
    
# Compute amplitude for forecast and observations
amp_fcst_lis = rmm_amplitude(pc1s_fcst_lis, pc2s_fcst_lis)
amp_obs_lis = rmm_amplitude(pc1s_obs_lis, pc2s_obs_lis)

# Compute phase for forecast and observations
pha_fcst_lis = mjo_phase(pc1s_fcst_lis, pc2s_fcst_lis)
pha_obs_lis = mjo_phase(pc1s_obs_lis, pc2s_obs_lis)

# Compute bivariate correlation, root mean square error, amplitude error and phase error
acors = []
rmses = []
perrs = []
aerrs= []

for t in range(nfc):  # Ensure we run for the 35-day window
    num = 0
    denom_1 = 0
    denom_2 = 0
    rmse1 = 0
    rmse2 = 0
    num_err = 0
    denom_err = 0
    taninv = 0
 
    nmjos = 0
    for i in range(len(pc1s_obs_lis)):
        a1 = pc1s_obs_lis[i][t]
        a2 = pc2s_obs_lis[i][t]
        b1 = pc1s_fcst_lis[i][t]
        b2 = pc2s_fcst_lis[i][t]   
        
        if (amp_obs_lis[i][t] > 1):    #select MJO events with amplitude > 1 for obs
            num += (a1*b1 + a2*b2)
            denom_1 += a1**2 + a2**2
            denom_2 += b1**2 + b2**2

            rmse1 += (a1-b1)**2
            rmse2 += (a2-b2)**2

            num_err = a1*b2 - a2*b1
            denom_err = a1*b1 + a2*b2
            taninv += np.arctan2(num_err,denom_err)  # Using arctan2 to handle all quadrants correctly
                                                     # the angle is defined between [-π, π]
            nmjos += 1

    acor = num / (np.sqrt(denom_1) * np.sqrt(denom_2))
    rmse = np.sqrt((rmse1 + rmse2) / nmjos)
    aerr = (np.sqrt(denom_2)-np.sqrt(denom_1)) / nmjos
    perr = 180.*taninv / (np.pi*nmjos)
    
    acors.append(acor.values)
    rmses.append(rmse.values)
    aerrs.append(aerr.values)
    perrs.append(perr.values)
    print('For forecast day ',t,' the number of observed MJO events (amplitude > 1) is: ',nmjos)
    
# Plot acc, rmse, amplitude and phase errors 
nfcst_days=dictionary['length of forecasts']

plot_acc_rmse(acors,rmses,ds_names,nfcst_days,'acc_rmse')
plot_amp_phase_err(aerrs,perrs,ds_names,nfcst_days,'amp_pha_err')

# Write out ACC, RMSE, amplitude and phase errors
write_output_text('../output/MJO/'+dictionary['model name']+'/acc_rmse',
                  ['forecast day','acc','rmse'],[np.arange(1,nfcst_days+1),acors,rmses])

write_output_text('../output/MJO/'+dictionary['model name']+'/amp_pha_err',
                  ['forecast day','amp_err','phse_err'],[np.arange(1,nfcst_days+1),aerrs,perrs])

# Construct Hovmoller of OLR and U850 for phases 2 & 3

if (dictionary['RMM']==True):
    fil_rmm_obs=dictionary['Path to RMM observation data file']
    ds_rmm=xr.open_dataset(fil_rmm_obs)

if (dictionary['RMM']==False):
    fil_rmm_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'
    ds_rmm=xr.open_dataset(fil_rmm_obs,decode_times=False)
    times=ds_rmm.time
    init_time=date(1960,1,1)+timedelta(int(times[0]))
    
    time=[]
    for i in range(len(times)):
        time.append(init_time+timedelta(i))
    ds_rmm['time'] = pd.to_datetime(time,format="%Y/%m/%d")


# Reshaping 1D time dimension of UFS anomalies to 2D
u850_fcst_anom_reshaped = reshape_forecast(fcst_avgd_u850, nfc=nfc)
olr_fcst_anom_reshaped = reshape_forecast(fcst_avgd_olr, nfc=nfc)

u850_obs_anom_reshaped = reshape_obs(obs_avgd_u850, init_days, nfc=nfcst_days)
olr_obs_anom_reshaped = reshape_obs(obs_avgd_olr, init_days, nfc=nfcst_days)

# Selecting initial conditions during DJFM
u850_fcst_anom_djfm = u850_fcst_anom_reshaped.sel(time=u850_fcst_anom_reshaped.time.dt.month.isin([1, 2, 3, 11, 12]))
olr_fcst_anom_djfm = olr_fcst_anom_reshaped.sel(time=olr_fcst_anom_reshaped.time.dt.month.isin([1, 2, 3, 11, 12]))

u850_obs_anom_djfm = u850_obs_anom_reshaped.sel(time=u850_obs_anom_reshaped.time.dt.month.isin([1, 2, 3, 11, 12]))
olr_obs_anom_djfm = olr_obs_anom_reshaped.sel(time=olr_obs_anom_reshaped.time.dt.month.isin([1, 2, 3, 11, 12]))

# Filter MJO events (RMM > 1) in phases 2 & 3 during the same dates as the forecaast
rmm = ds_rmm.sel(time=ds_rmm.time.dt.month.isin([1, 2, 3, 11, 12]) & ds_rmm.time.isin(olr_fcst_anom_djfm.time))
phases=[2,3]
amplitude_threshold = 1.0

mjo_event_conditions = select_mjo_event_phases(rmm.amplitude, rmm.phase, phases, amplitude_threshold)
mjo_events = rmm.sel(time=mjo_event_conditions)

# Filter the forecast anomalies based on the selected RMM events

u850_fcst_anom_mjo = u850_fcst_anom_djfm.sel(time=mjo_events.time)
olr_fcst_anom_mjo = olr_fcst_anom_djfm.sel(time=mjo_events.time)

# Filter the observed anomalies based on the selected RMM events

u850_obs_anom_mjo = u850_obs_anom_djfm.sel(time=mjo_events.time)
olr_obs_anom_mjo = olr_obs_anom_djfm.sel(time=mjo_events.time)

# Calculate the averages
u850_avg_fcst = u850_fcst_anom_mjo.mean(dim='time')
olr_avg_fcst = olr_fcst_anom_mjo.mean(dim='time')

u850_avg_obs = u850_obs_anom_mjo.mean(dim='time')
olr_avg_obs = olr_obs_anom_mjo.mean(dim='time')

# Apply rolling mean with window size of 5 forecast days
u850_avg_fcst_rolling = u850_avg_fcst.rolling(forecast_day=5, center=False).mean()
u850_avg_fcst_rolling[0:5,:] = copy.deepcopy(u850_avg_fcst[0:5,:])
olr_avg_fcst_rolling = olr_avg_fcst.rolling(forecast_day=5, center=False).mean()
olr_avg_fcst_rolling[0:5,:] = copy.deepcopy(olr_avg_fcst[0:5,:])

u850_avg_obs_rolling = u850_avg_obs.rolling(forecast_day=5, center=False).mean()
u850_avg_obs_rolling[0:5,:] = copy.deepcopy(u850_avg_obs[0:5,:])
olr_avg_obs_rolling = olr_avg_obs.rolling(forecast_day=5, center=False).mean()
olr_avg_obs_rolling[0:5,:] = copy.deepcopy(olr_avg_obs[0:5,:])

# Plot Hovoller diagrams

plot_hovmoler([olr_avg_obs_rolling,olr_avg_fcst_rolling],[u850_avg_obs_rolling,u850_avg_fcst_rolling],
              ds_names,'hov_diag')
