##Usage: In the main code add from fcst_utils import *

import numpy as np
import xarray as xr

def calcAnom(ds,anom_name):
    # Save the original dates 
    time=ds.time
    
    # Get the time dimensions; ntimes=# of samples; nyrs=# of calendar years; nlead=# of foreecast leads
    ntimes=len(time)
    index=ds.time['time.year']
    yStrt=index[0]
    yLast=index[-1]
    nyrs=int(yLast-yStrt)
    nlead=int(len(index)/nyrs)
    
    # Compute climatology for each forecast lead 
    climo=[]
    for i in range(nlead):
        #AMJ 12/22/22 fixed indexing bug
        #da=ds[i:ntimes-1:nlead,:,:].mean(dim='time')
        da=ds[i:ntimes:nlead,:,:].mean(dim='time')
        climo.append(da.to_dataset(name='clim'))
    ds_clim=xr.combine_nested(climo,concat_dim='time')
    
    # Change time coordinate from calendar dates to integers [0:ntimes]
    days=[]
    for i in range(nyrs):
        days.append(np.arange(nlead))
    days=np.reshape(days,nyrs*nlead)
    
    ds['time']=days
    
    # Compute anomalies 
    anoms=ds.groupby(ds.time)-ds_clim
    
    # Rename anomaly 
    anom=anoms['clim'].rename(anom_name)
    
    # Remap time coordinate to original calendar dates
    anom['time']=time
    
    return anom
  
  #Plan to add regridding code shared by Cheng
