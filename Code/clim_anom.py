# calculate ufs climatology & anomaly

import xarray as xr
import numpy as np

# ufs path
ufs_path = '/scratch/hbai/ufs_p6_daily/z500/'

year = 2012
months = ['01','02','03','04','05','06','07','08','09','10','11','12']

# create a list of ufs files to open
# open one year's files (reforeccasts initiated on 1st or 15th)
ufs_files = [f'{ufs_path}ufs_p6_{year}{month}01_z500.nc' for month in months]
ufs_files

# read one year's ufs files at once
ds = xr.open_mfdataset(ufs_files, combine='nested', concat_dim='month')
z500_ufs = ds.z500
z500_ufs

# Calculate climatology

clim = []

# Jan
clim = z500_ufs[0,0:31,:,:]
# Feb
if year == 2012 or 2016: # leap year
    clim = xr.concat((clim, z500_ufs[1,0:29,:,:]), "ncl0")
else:
    clim = xr.concat((clim, z500_ufs[1,0:28,:,:]), "ncl0")
# Mar
clim = xr.concat((clim, z500_ufs[2,0:31,:,:]), "ncl0")
# Apr
clim = xr.concat((clim, z500_ufs[3,0:30,:,:]), "ncl0")
# May
clim = xr.concat((clim, z500_ufs[4,0:31,:,:]), "ncl0")
# Jun
clim = xr.concat((clim, z500_ufs[5,0:30,:,:]), "ncl0")
# Jul
clim = xr.concat((clim, z500_ufs[6,0:31,:,:]), "ncl0")
# Aug
clim = xr.concat((clim, z500_ufs[7,0:31,:,:]), "ncl0")
# Sep
clim = xr.concat((clim, z500_ufs[8,0:30,:,:]), "ncl0")
# Oct
clim = xr.concat((clim, z500_ufs[9,0:31,:,:]), "ncl0")
# Nov
clim = xr.concat((clim, z500_ufs[10,0:30,:,:]), "ncl0")
# Dec
clim = xr.concat((clim, z500_ufs[11,0:31,:,:]), "ncl0")

clim

# write climatology to nctcdf file
clim.to_netcdf(ufs_path+"ufs_p6_"+str(year)+"z500_climatology.nc")

## calculate anomaly

# climatological mean
clim_mean = clim.mean(dim='ncl0')
clim_mean

# anomaly
z500_ufs_anom = z500_ufs - clim_mean
z500_ufs_anom

# write anomaly to nctcdf files
for i, month in enumerate(months):
    z500_ufs_anom[i].to_netcdf(ufs_path+"ufs_p6_"+str(year)+month+"01_z500_anomaly.nc")



