##Usage: In the main code add from fcst_utils import *

import numpy as np
import xarray as xr
import spharm

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

def regrid_scalar_spharm_original ( data_in , grid_input , grid_output ) :
    input_reorder  = np.transpose ( data_in , ( 1 , 2 , 0 ) )
    regrid_data = spharm.regrid ( grid_input , grid_output , input_reorder )
    regrid_reorder = np.transpose ( regrid_data , ( 2 , 0 , 1 ) )
    return regrid_reorder

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
    output_regrid['time']=ds_in.time
    return output_regrid 
  
def regrid_scalar_spharm(data, lat_in, lon_in, lat_out, lon_out):
    '''
    Regrid global scalar data using spherical harmonics.
    
        Parameters:
            data:    xarray data array of gridded data to be regridded. 
                     coordinate dimensions must be named 'latitude', 
                     and 'longitude'. Dimensions can be 2D, 3D, or 4D.
            lat_in:  latitudes corresponding to input data 
            lon_in:  longitudes corresponding to input data
            lat_out: latitudes corresponding to regridded data (xarray data array)
            lon_out: longitudes corresponding to regridded data (xarray data array)
            
        Returns:
            data_regrid: regridded data. note order of dimensions will be 
                         re-arranged so that latitude & longitude are leading
    '''
    # dimension names
    dims = data.dims
    dims_not_lat_lon = list(set(['latitude','longitude']) ^ set(dims))
    
    ingrid = spharm.Spharmt(len(lon_in), len(lat_in), gridtype='regular')
    outgrid = spharm.Spharmt(len(lon_out), len(lat_out), gridtype='regular')
    
    # From spharm documentation: input data dimensionality needs to be 
    # (lat, lon, ...), and max. 3D
    data = data.transpose('latitude','longitude',...)
    
    if data.ndim>2:
        # Works for 3D or 4D data
        data_regrid=[]
        for ii in range(len(data[dims_not_lat_lon[0]])):
            data_regrid.append(spharm.regrid(ingrid,outgrid,
                                        data.isel(**{dims_not_lat_lon[0]: ii}).values))
            
        data_regrid = np.asarray(data_regrid) # list of arrays to one array
        
        # Construct data array from numpy array
        data_regrid = xr.DataArray(data=data_regrid,dims=dims)
            
        # Assign the remaining coordinates
        data_regrid['latitude'] = lat_out
        data_regrid['longitude'] = lon_out
        
        for dim in dims_not_lat_lon:
            data_regrid[dim]=data[dim]
            data_regrid['time']=data.time
            
    else:
        data_regrid=spharm.regrid(ingrid,outgrid,data.values)
        
        # Construct data array from numpy array
        data_regrid = xr.DataArray(data=data_regrid,
                                   coords={'latitude':lat_out,
                                           'longitude':lon_out})
        
    return data_regrid

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


def reshape_forecast(fc,nfc=35):
    ''' Reshape forecast data so the time dimension
    is 2D with dimensions initialization day & forecast day. 
    ---
    Inputs
    ---
    fc: xarray data array of forecast data with merged time dimension named "time"
    nfc: number of forecast days, default=35. Must be integer
    
    ---
    Returns
    ---
    fc_reshape: reshaped xarray of forecast data with 2D time
    '''
    
    # Check to make sure nfc is an integer
    if not isinstance(nfc, int):
        print('warning: nfc is not an integer. forcing integer type')
        nfc = int(nfc)
    
    # Initialization days
    init_day = fc.time[::nfc]
    
    # Forecast lead time
    fc_day = np.arange(1,nfc+1)
    
    # Reshape
    fc_reshape=[]
    for iinit in range(len(init_day)):
        # Subset and rename the forecast dimension
        subset = fc.isel(time=np.arange(iinit*nfc,iinit*nfc+nfc))
        subset = subset.rename(time='forecast_day')
        subset['forecast_day']=fc_day
        fc_reshape.append(subset)
        
    # Convert to single xarray data array from list of multiple data arrays
    fc_reshape=xr.concat(fc_reshape,dim='time')
    fc_reshape['time']=init_day
    fc_reshape.time.attrs['long_name']='initial time'
    
    return fc_reshape

def is_ndjfm(month):
    ''' Returns true if winter month
    '''
    return (month >= 11) | (month <= 3)
