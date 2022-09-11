# interpolate UFS grid to observation grid

import xarray as xr
import numpy as np

# ufs path
ufs_path = '/scratch/hbai/ufs_p6_daily/z500/'

# obeservation path
obs_path = '/scratch/hbai/gpcp/z500_31day_ufsexp/'

months = ['01','02','03','04','05','06','07','08','09','10','11','12']

# create a list of ufs files to open
# this example shows how to open on
ufs_files = [f'{ufs_path}ufs_p6_2012{month}01_z500.nc' for month in months]
ufs_files

# read target lat&lon from observation
ds2 = xr.open_dataset(obs_path+"erai.z500.mean.20120101.nc")
lat = ds2.lat
lon = ds2.lon

# interpolate ufs to grid of observation
z500_ufs_int = z500_ufs.interp(latitude=lat, longitude=lon, method='linear')
z500_ufs_int

# write interpolated ufs data into nctcdf files
for i, month in enumerate(months):
    z500_ufs_int[i].to_netcdf(ufs_path+"ufs_p6_2012"+month+"01_z500_interp.nc")
