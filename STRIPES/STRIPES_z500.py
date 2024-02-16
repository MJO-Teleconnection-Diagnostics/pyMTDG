'''
Wrapper around the calculation of the stripes index for z500.
This code:
    - loads the data
    - passes the calculation of the STRIPES index to functions in STRIPES_utils
    - plots the STRIPES index and anomalies from observed
'''

import xarray as xr
import numpy as np
import yaml
from pathlib import Path
from STRIPES_utils import *
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.util import add_cyclic_point
import numpy as np
import os

# -------------------------------------------------------
# Read yaml file
config_file=Path('../driver/config.yml').resolve()
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)
        
# Load RMM data. 
# !!! Note: This code does not handle the case where RMM data is computed

dir_in = dictionary['DIR_IN']

if (dictionary['RMM:']==False):
    # !!! Note: this will need to be updated with a correct final path for the RMM data
    #     This is a pretty small data file (< 1 MB) maybe we shoud just include it in the package
    # fil_rmm_erai=dictionary['DIR_IN']+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'
    #RMM_FILE = dir_in+'/erai/rmm_ERA-Interim.nc'
    RMM_FILE = dir_in+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'

    
# where are the z500 data files located?
# !!! Note: This code ignores situations where the files for different initialization dates 
#           are in different directories.
# !!! Suggestion: gui should check directories for a trailing / and ensure consistency?
#Z500_DIR = dictionary['Path to z500 date files'][0] + '*.nc*'
Z500_DIR = dictionary['Path to z500 date files'][0]

#Z500_DIR_OBS = dictionary['Path to z500 observational files'] + '*.nc*'

if (dictionary['ERAI:']==True):
    Z500_DIR_OBS = dictionary['Path to z500 observational files']+'/mjo_teleconnections_data/erai/z500/z500.ei.oper.an.pl.regn128sc.1979.2019.nc'

# read start and end date
START_DATE = dictionary['START_DATE:']
END_DATE = dictionary['END_DATE:']

# Read model name
model_name = dictionary['model name']
# -------------------------------------------------------
# Calculate 
stripes_obs, stripes_fc = calcSTRIPES_forecast_obs(Z500_DIR, 
                                                   Z500_DIR_OBS, 
                                                   RMM_FILE, 
                                                   'gh', 
                                                   START_DATE, 
                                                   END_DATE)
# -------------------------------------------------------
# Plot
lags = ['1-2', '2-3', '3-4']  # in weeks
lon = stripes_obs[0].longitude
lat = stripes_obs[0].latitude
cmap_obs = 'YlGnBu'
levs_obs = np.arange(0, 110, 10)
levs_anom = np.arange(-25, 30, 5)

for ilag, lag in enumerate(lags):
    # Create a new figure and axes for each lag
    fig, axs = plt.subplots(nrows=len(lags), figsize=(5, 7), subplot_kw={'projection': ccrs.PlateCarree()})

    # Set up common map elements
    for ax in axs:
        ax.coastlines()
        ax.set_extent([-180, 180, -85, 85], crs=ccrs.PlateCarree())
        ax.projection._central_longitude = 260  # Set the central_longitude

    # Observations
    stripes_obs_cyclic, lon_cyclic = add_cyclic_point(stripes_obs[ilag], lon)
    im_obs = axs[0].contourf(lon_cyclic, lat, stripes_obs_cyclic, extend='max', cmap=cmap_obs, levels=levs_obs)
    cbar_obs = fig.colorbar(im_obs, ax=axs[0], orientation='vertical', label=f'STRIPES ({stripes_obs[0].units})')
    axs[0].set_title(f'Obs., week {lag}')

    # Forecast
    stripes_fc_cyclic, _ = add_cyclic_point(stripes_fc[ilag], lon)
    im_fc = axs[1].contourf(lon_cyclic, lat, stripes_fc_cyclic, extend='max', cmap=cmap_obs, levels=levs_obs)
    cbar_fc = fig.colorbar(im_fc, ax=axs[1], orientation='vertical', label=f'STRIPES ({stripes_obs[0].units})')
    axs[1].set_title(f'Forecast., week {lag}')

    # Bias
    bias = stripes_fc_cyclic - stripes_obs_cyclic
    im_bias = axs[2].contourf(lon_cyclic, lat, bias, extend='both', cmap='RdBu_r', levels=levs_anom)
    cbar_bias = fig.colorbar(im_bias, ax=axs[2], orientation='vertical', label=f'STRIPES ({stripes_obs[0].units})')
    axs[2].set_title(f'Forecast - Obs., week {lag}')
    
    # save
    if not os.path.exists('../output/STRIPES/'+model_name): 
        os.mkdir('../output/STRIPES/'+model_name)
    figname='stripes_z500_wk' + lag 
    fig.savefig('../output/STRIPES/'+model_name+'/'+figname+'.jpg',dpi=300)
