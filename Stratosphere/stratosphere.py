#!/usr/bin/env python
# coding: utf-8

import xarray as xr

import numpy as np

from datetime import datetime

from datetime import timedelta

from datetime import date

import pandas as pd
 
import yaml
import glob
import gc
import proplot as plot


import sys
sys.path.insert(0, '../Utils')
from pathlib import Path
from obs_utils import *
from fcst_utils import *
from stratosphere_utils import *


print(f'Compute stationary waves diagnostic')

config_file=Path('../driver/config.yml').resolve()
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)

 # Get the forecast period from the provided Start_Date -- End_Date period
yyyymmdd_Begin=dictionary['START_DATE']
tBegin=yyyymmdd_Begin[0:4]+'-'+yyyymmdd_Begin[4:6]+'-'+yyyymmdd_Begin[6:8]
yyyymmdd_End=dictionary['END_DATE']
tEnd=yyyymmdd_End[0:4]+'-'+yyyymmdd_End[4:6]+'-'+yyyymmdd_End[6:8]

# ERA-Interim data covers 01/01/1979-08/31/2019, 7 years and 8 months, 14853 days

 
#fil_obs=yml_input['DIR_IN']+'/mjo_teleconnections_data/erai/z500/z500.19790101-20190831.nc'
fil_obs=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/z500/z500.ei.oper.an.pl.regn128sc.1979.2019.nc'
# Cristiana - needs to be updated to link to where files are stored
   
ds_obs_name='ERAI'

ds_obs=xr.open_dataset(fil_obs)
obs=get_variable_from_dataset(ds_obs)


# Generate time limits for each initial condition 

nyrs=date.fromisoformat(tEnd).year-date.fromisoformat(tBegin).year +1
yrStrt=date.fromisoformat(tBegin).year
mmStrt=date.fromisoformat(tBegin).month

# Cristiana: Read in forecast data  (not sure which of the following two lines is correct)
Model_z500_files             = dictionary [ 'Path to Z500 model data files' ]
#Model_z500_files = [ "/data0/czheng/S2S-UFS/data/6hourly/Prototype5/gh_500-isobaricInhPa/gh.500-isobaricInhPa.*.6hourly.nc" ]

fcst_dir=dictionary['Path to Z500 model data files']  #Cristiana - needs to be updated to link to where files are stored
ds_fcst_name=dictionary['model name']
ds_names=[ds_obs_name,ds_fcst_name]


fcst_files=np.sort(glob.glob(str(fcst_dir+'*.nc')))
ds_fcst=xr.open_mfdataset(fcst_files,combine='nested',concat_dim='time',parallel=True)
fcst=get_variable_from_dataset(ds_fcst)

rgrd_fcst=regrid_scalar_spharm(fcst,ds_fcst.latitude,ds_fcst.longitude,
                                        ds_obs.latitude,ds_obs.longitude)
del ds_fcst
gc.collect()
del rgrd_fcst
gc.collect()
        

fcst_anom=fcst  #for this metric we use the raw data, not anomalies, but I'm reusing code written for other packages so I kept this in 
del fcst
 
# Reshape 1D time dimension of UFS anomalies to 2D
fcst_anom = reshape_forecast(fcst_anom, nfc=int(len(fcst_anom.time)/len(fcst_files)))
       
    
# Select initial conditions in the forecast during DJFM


pha_obs_ndjfm  = ds_obs.sel(time=ds_obs.time.dt.month.isin([1, 2, 3, 11, 12]))



fcst_anom=fcst_anom.sel(time=fcst_anom.time.dt.month.isin([1, 2, 3, 11, 12]))

 

 
# Main calculation
weeks=['week2','week3','week4','week5']


 


 


##### make plots [this is borrowed from T2m plots on github 
# https://github.com/cristianastan2/MJO-Teleconnections/blob/develop/T2m_composites/t2m_composites.py
# Plotting parameters
lon_0 = 270
lat_0 = 20

 
cmap='bwr'
clevs=[-250, -225, -200, -175, -150, -125, -100, -75, -50, -25, 0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250]


with plot.rc.context(fontsize='20px'):
        fig=plot.figure(refwidth=6.5)
        axes=fig.subplots(nrows=1,ncols=4,proj='npstere',proj_kw={'lon_0': lon_0})
          
        fig2=plot.figure(refwidth=6.5)
        axes2=fig2.subplots(nrows=1,ncols=4,proj='npstere',proj_kw={'lon_0': lon_0})
          
for whichwk in weeks:       
 
		#I'm pretty sure this is a bug and needs to be fixed
            thisplottablemean = np.nanmean(np.nanmean(np.nanmean(fcst_anom[:, [0, 1, 2, 3, 8, 9], protoind, :, :, whichwk], 1), 2), 6)
            thisplottablemean = thisplottablemean - np.nanmean(thisplottablemean, 1)

# based on https://github.com/cristianastan2/MJO-Teleconnections/blob/develop/Utils/t2m_utils.py
  
            h=axes[whichwk].contourf(thisplottablemean,cmap=cmap,lw=1,ec='none',extend='both',levels= clevs)

            if (p==0):
                axes[whichwk].format(title=weeks[p])
            else:
                axes[whichwk].format(title=weeks[p],rtitle='{:.2f}'.format(rcorr))

            axes[whichwk].format(coast='True',boundinglat=lat_0,grid=False,suptitle=week+whichwk)

            fig.colorbar(h, loc='b', extend='both', label='Z* [stationary waves]',
                          width='2em', extendsize='3em', shrink=0.8,
                        )
            if not os.path.exists('../output/Strat_Path/'): 
                os.mkdir('../output/Strat_Path/')
            fig.savefig('../output/Strat_path/Zstat' + ds_fcst_name + '.jpg',dpi=300)



      


	#I'm pretty sure this is a bug and needs to be fixed
            thisplottablemean = np.nanmean(np.nanmean(np.nanmean(pha_obs_ndjfm[:, [0, 1, 2, 3, 8, 9], protoind, :, :, whichwk], 1), 2), 6)
            thisplottablemean = thisplottablemean - np.nanmean(thisplottablemean, 1)

# based on https://github.com/cristianastan2/MJO-Teleconnections/blob/develop/Utils/t2m_utils.py
  
            h=axes2[whichwk].contourf(thisplottablemean,cmap=cmap,lw=1,ec='none',extend='both',levels= clevs)

            if (p==0):
                axes2[whichwk].format(title=weeks[p])
            else:
                axes2[whichwk].format(title=weeks[p],rtitle='{:.2f}'.format(rcorr))

            axes2[whichwk].format(coast='True',boundinglat=lat_0,grid=False,suptitle=week+whichwk)

            fig.colorbar(h, loc='b', extend='both', label='Z* [stationary waves]',
                          width='2em', extendsize='3em', shrink=0.8,
                        )
            if not os.path.exists('../output/Strat_Path/'): 
                os.mkdir('../output/Strat_Path/')
            fig.savefig('../output/Strat_Path/Zstat' + ds_obs_name + '.jpg',dpi=300)


print(f'Stationary waves diagnostic completed')
                  
