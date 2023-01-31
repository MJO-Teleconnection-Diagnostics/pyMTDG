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
  
def regrid_scalar_spharm ( data_in , grid_input , grid_output ) : # This function is from the original code provided by Cheng
    input_reorder  = np.transpose ( data_in , ( 1 , 2 , 0 ) )
    regrid_data = spharm.regrid ( grid_input , grid_output , input_reorder )
    regrid_reorder = np.transpose ( regrid_data , ( 2 , 0 , 1 ) )
    return regrid_reorder

def regrid_vector_spharm ( u_input , v_input , grid_input , grid_output ) :   # This function is from the original code provided by Cheng
    nlat = grid_input.nlat
    nlon = grid_input.nlon
    nlat_out = grid_output.nlat
    nlon_out = grid_output.nlon
    if nlat%2:                              # nlat is odd
        n2 = (nlat + 1)/2
    else:
        n2 = nlat/2
    nt = u_input.shape[2]
    ntrunc = grid_output.nlat - 1
    w = u_input
    v = - v_input
    lwork = (2*nt+1)*nlat*nlon
    lwork_out = (2*nt+1)*nlat_out*nlon_out
    br,bi,cr,ci,ierror = _spherepack.vhaes(v,w,grid_input.wvhaes,lwork)
    bc = _spherepack.twodtooned(br,bi,ntrunc)
    cc = _spherepack.twodtooned(cr,ci,ntrunc)
    br_out, bi_out = _spherepack.onedtotwod(bc,nlat_out)
    cr_out, ci_out = _spherepack.onedtotwod(cc,nlat_out)
    v_out, w_out, ierror = _spherepack.vhses(nlon_out,br_out,bi_out,cr_out,ci_out,grid_output.wvhses,lwork_out)
    return w_out,-v_out

def interpolate_scalar(ds_in,nlon_out,nlat_out,grid_type,var_name):
    
    #grid_type: "regular", "gaussian"
    
    # Coordinates of field to be regrided
    nlon_in = len(ds_in.longitude)
    nlat_in = len(ds_in.latitude)
    
    # Define the input and output grids
    ingrid = spharm.Spharmt ( nlon_in  , nlat_in  , gridtype=grid_type )
    outgrid = spharm.Spharmt ( nlon_out , nlat_out , gridtype=grid_type )
    
    delat = 180. / ( nlat_out - 1 )
    lat_out = 90 - np.arange ( nlat_out ) * delat
    delon = 360. / nlon_out
    lon_out = np.arange ( nlon_out ) * delon
    
    data_in_pre_regrid=np.empty([1, nlat_in, nlon_in])
    data_regrid=np.empty([len (ds_in.time),nlat_out,nlon_out])
    for i in range(len (ds_in.time)):
        data_in_pre_regrid[0,:,:]=ds_in[i,:,:]
        data_regrid[i,:,:]=regrid_scalar_spharm(data_in_pre_regrid,ingrid,outgrid)
    output_regrid=xr.DataArray(data_regrid, name=var_name,
                               dims=[ 'time','latitude','longitude'],
                               coords=dict(time=ds_in.time,latitude=lat_out,longitude=lon_out),
                               attrs=ds_in.attrs)
    output_regird['time']=ds_in.time
    return output_regrid 

# Interpolation function for vector fields to be added
