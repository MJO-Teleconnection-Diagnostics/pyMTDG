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
import sys
sys.path.insert(0, '../Utils')
from STRIPES_utils import *
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.util import add_cyclic_point
import numpy as np
import os

# -------------------------------------------------------
# Read yaml file
try:
    config_file=Path('../driver/config.yml').resolve()
    with open(config_file,'r') as file:
        try:
            dictionary = yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML configuration: {e}")
            raise
except FileNotFoundError:
    print('no config file found, using OSU HPC data paths')
    datadir = '/ceoas/jenneylab/bridges2_transfer/ufs_data'
    dictionary={
            'DIR_IN':datadir,
            'Path to Z500 model data files':datadir+'/Prototype5/gh/',
            'ERAI':True,
            #'ERAI':False,
            'Path to Z500 observation data files':datadir+'/mjo_teleconnections_data/erai/z500/z500.ei.oper.an.pl.regn128sc.1979.2019.nc',
            'RMM':False,
            'START_DATE':'20110401',
            'END_DATE':'20180419',
            'model name':'UFS5',
            }
        
dir_in = dictionary['DIR_IN']

if (dictionary['RMM']==False):
    RMM_FILE = dir_in+'/mjo_teleconnections_data/erai/rmm/rmm_ERA-Interim.nc'
else:
    RMM_FILE = dictionary['Path to RMM observation data file']
    
# where are the z500 data files located?
Z500_DIR = dictionary['Path to Z500 model data files']

if (dictionary['ERAI']==True):
    Z500_DIR_OBS = dir_in+'/mjo_teleconnections_data/erai/z500/'
    obs_name = 'ERAI'
else:
    Z500_DIR_OBS = dictionary['Path to Z500 observation data files']
    obs_name = 'OBS.'
    
# read start and end date
START_DATE = dictionary['START_DATE']
END_DATE = dictionary['END_DATE']

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

# Find the maximum value of stripes for plotting limits
stripesmax = 0.95*(np.nanmax(np.asarray([np.nanmax(stripes_obs), np.nanmax(stripes_fc)])))
stripes_anom_lim = 0.175 * stripesmax

# Nice contour levels
levs_obs = nice_contour_levels(stripesmax, 20)
levs_anom = nice_contour_levels(stripes_anom_lim, 20, anoms=True)

for ilag, lag in enumerate(lags):
    # Create a new figure and axes for each lag
    fig, axs = plt.subplots(nrows=len(lags), figsize=(5, 7), subplot_kw={'projection': ccrs.PlateCarree()})

    # Set up common map elements
    for ax in axs:
        ax.coastlines()
        ax.set_extent([-180, 180, -85, 85], crs=ccrs.PlateCarree())
        ax.projection._central_longitude = 260  # Set the central_longitude

    # Observations
    # stripes_obs_cyclic, lon_cyclic = add_cyclic_point(stripes_obs[ilag], lon)
    # im_obs = axs[0].contourf(lon_cyclic, lat, stripes_obs_cyclic, extend='max', cmap=cmap_obs, levels=levs_obs)
    im_obs = axs[0].contourf(lon, lat, stripes_obs[ilag], extend='max', cmap=cmap_obs, levels=levs_obs)
    cbar_obs = fig.colorbar(im_obs, ax=axs[0], orientation='vertical', label=f'STRIPES ({stripes_obs[0].units})')
    axs[0].set_title(f'{obs_name}, week {lag}')

    # Forecast
    # stripes_fc_cyclic, _ = add_cyclic_point(stripes_fc[ilag], lon)
    # im_fc = axs[1].contourf(lon_cyclic, lat, stripes_fc_cyclic, extend='max', cmap=cmap_obs, levels=levs_obs)
    im_fc = axs[1].contourf(lon, lat, stripes_fc[ilag], extend='max', cmap=cmap_obs, levels=levs_obs)
    cbar_fc = fig.colorbar(im_fc, ax=axs[1], orientation='vertical', label=f'STRIPES ({stripes_obs[0].units})')
    axs[1].set_title(f'{model_name}, week {lag}')

    # Bias
    # bias = stripes_fc_cyclic - stripes_obs_cyclic
    # im_bias = axs[2].contourf(lon_cyclic, lat, bias, extend='both', cmap='RdBu_r', levels=levs_anom)
    bias = stripes_fc[ilag] - stripes_obs[ilag]
    im_bias = axs[2].contourf(lon, lat, bias, extend='both', cmap='RdBu_r', levels=levs_anom)
    cbar_bias = fig.colorbar(im_bias, ax=axs[2], orientation='vertical', label=f'STRIPES ({stripes_obs[0].units})')
    axs[2].set_title(f'{model_name} - {obs_name}, week {lag}') 

    # save
    if not os.path.exists('../output/StripesGeopot/'+model_name): 
        os.mkdir('../output/StripesGeopot/'+model_name)
    figname='stripes_z500_wk' + lag 
    fig.savefig('../output/StripesGeopot/'+model_name+'/'+figname+'.jpg',dpi=300)
