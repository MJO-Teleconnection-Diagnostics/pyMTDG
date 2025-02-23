# Compute the STRIPES index for a gridded variable given
# comp_anom -  an array of composite anomalies. Must be ordered
#                (phases, lags, nlat, nlon)
# pspeed    -  a vector of speeds (how many days does the mjo spend in phase)

import numpy as np
import xarray as xr
import pandas as pd
from datetime import timedelta
import glob
from fcst_utils import *
from obs_utils import *
import gc
# ===============================================================================================
def nice_contour_levels(max_val, num_levels, min_val=0, anoms=False):
    '''
    Computes "nice" contour levels for plotting. 

        Parameters:
            max_val: the maximum value to include in the plotting limits
            num_levels: the desired number of contour levels. Output won't be exact
            min_val: the minimum value to include in the plotting limits (default=0)
            anoms: if True, the contour levels will range from -max_val to max_val 
                   and be centered at 0 (default=False)

        Returns:
            contour_levels: Contour levels that have nice spacings. Note: will not be exactly the 
                            same number of levels as specified num_levels (but will be close)
    '''

    if anoms:
        min_val = -1 * np.abs(max_val)
    
    # Compute the range and the step size
    range_val = max_val - min_val
    step = range_val / num_levels

    # Define possible nice step sizes
    nice_steps = np.array([1, 2, 2.5, 5, 10])
    
    # Find the order of magnitude of the step. This will help define the contour levels
    order_of_magnitude = np.floor(np.log10(step)).astype('int64')
    
    # Scale the nice steps by the order of magnitude
    scaled_nice_steps = nice_steps * 10.0 ** order_of_magnitude
    
    # Find the closest nice step size
    step_nice = scaled_nice_steps[np.searchsorted(scaled_nice_steps, step)]

    # Adjust the minimum and maximum values to the nearest integers
    min_val_nice = np.floor(min_val/step_nice)*step_nice
    max_val_nice = np.ceil(max_val/step_nice)*step_nice

    # Generate the contour levels
    contour_levels = np.arange(min_val_nice, max_val_nice + step_nice, step_nice)
    
    return contour_levels
# ===============================================================================================
def calc_lagged_composite(data, amp, phase, maxlag, minlag=0, nphases=8, obs=False):
    '''
    Computes the lagged composite matrix 
    
        Parameters:
            data: xarray data with named dimensions 'time' (initialization day)
                  and 'forecast_day' (lead time) if forecast data
            amp: boolean xarray vector of length n of MJO amplitudes exceeding threshold
                 !!note: time dimension must be named!!
            phase: vector of length n of MJO phases
            maxlag: maximum lag to composite on 
            minlag: minimum lag to composite on, default=0
            nphases: number of mjo phases, default=8
            obs: boolean indicating whether obs or forecast (default)
            
        Returns:
            lagcomp: lagged composite matrix
    '''
    
    if obs:
        lag = np.arange(minlag, maxlag+1)
    
    lagcomp = []
    for iphase in range(nphases):
        inds = np.squeeze(np.argwhere((amp.values) & (phase==(iphase+1))))
        
        if obs:
            t0=pd.to_datetime(amp.time[inds])+timedelta(days=minlag)
            t1=pd.to_datetime(amp.time[inds])+timedelta(days=maxlag)
            
            comp = []
            for ievent in range(len(t0)):
                subset = data.sel(time=slice(t0[ievent], t1[ievent])).rename(time='lag')
                subset['lag']=lag
                comp.append(subset)
            lagcomp.append(xr.concat(comp, dim='event').mean('event'))
        else:
            lagcomp.append(data.isel(time=inds, 
                                     forecast_day=slice(minlag, 
                                                        maxlag+1)).mean('time'))
    lagcomp=xr.concat(lagcomp,dim='phase')
    lagcomp['phase']=np.arange(1,nphases+1)

    return lagcomp
    
# ===============================================================================================
def compSTRIPES1D(comp_anom,pspeed):
    '''
    Compute the STRIPES index for a variable with inputs:
        comp_anom -  an array of composite anomalies. Must be ordered
                     (phases, lags). Must be a numpy matrix
        pspeed    -  a vector of speeds (how many days does the mjo spend in phase)    
    '''

    # Make sure pspeed is an array
    try: len(pspeed)
    except: pspeed=[pspeed]
    
    nphases,nlags = comp_anom.shape

    # calculate the maximum number of samples we can get in 
    # diagonal means. New in this computation of STRIPES 
    # (not in Jenney et al. (2019))
    nsample = int(nlags/nphases)

    # instead of reordering as in Jenney et al. (2019), stack the lagged
    # composite matrix on the phase axis nphases number of times. This
    # gives a 30x speedup
    comp_anom_stack=np.tile(comp_anom,(nphases,1))
    nphases = comp_anom_stack.shape[0] # for creating the shifted array

    shiftsum_var = []
    # Loop through each speed and compute the diagonal mean
    for ispeed, speed in enumerate(pspeed):
        n_diag=nlags + (nphases-1)*speed
        shiftsum=[]
        for idiag in range(n_diag):
            # First diagonals are the first SPEED lags of the first phase
            if idiag < n_diag-nlags:
                iphases = np.arange(np.floor(idiag/speed),-1,-1,dtype='uint8')
                ilags = np.arange(idiag%speed,nlags,speed,dtype='uint8')
            # Last diagonals are the entire row in the last phase
            else:
                iphases = np.arange(7,-1,-1,dtype='uint8')
                ilags = np.arange(idiag-((nphases-1)*speed),nlags,speed,
                                  dtype='uint8')

            n_items = min(len(iphases), len(ilags))
            shiftsum.append(np.mean(comp_anom_stack[iphases[:n_items], 
                                                    ilags[:n_items]]))

        # Compute the variance
        shiftsum_var.append(np.var(np.asarray(shiftsum)))

    stripes = np.sqrt(2*np.nanmean(np.asarray(shiftsum_var)))
    return(stripes)
    
# ===============================================================================================
def compSTRIPES2D(comp_anom,pspeed):
    '''
    Compute the STRIPES index for a 2D variable
       comp_anom -  an array of composite anomalies. Must be ordered
                    (phases, lags, lat/lon, lon/lat)
       pspeed    -  a vector of speeds (how many days does the mjo spend in phase)    
    '''

    # Make sure pspeed is a vector
    try: len(pspeed)
    except: pspeed=[pspeed]

    nphases,nlags = comp_anom.shape[:2]
    
    # instead of reordering as in Jenney et al. (2019), stack the lagged
    # composite matrix on the phase axis nphases number of times. This
    # gives a 30x speedup
    comp_anom_stack=np.tile(comp_anom,(nphases,1,1,1))
    nphases = comp_anom_stack.shape[0] # for creating the shifted array
    
    diagonal_mean_var = []
    # Loop through each speed and compute the diagonal mean
    for speed in pspeed:
        n_diag=nlags + (nphases-1)*speed
        diagonal_mean=[]
        n_in_diagonal=[]
        
        # Loop through each diagonal
        for idiag in range(n_diag):
            # Find the indices of the diagonal
            # First diagonals are the first SPEED lags of the first phase
            if idiag < n_diag-nlags:
                iphases = np.arange(np.floor(idiag/speed),-1,-1,dtype='uint8')
                ilags = np.arange(idiag%speed,nlags,speed,dtype='uint8')
            # Last diagonals are the entire row in the last phase
            else:
                iphases = np.arange(7,-1,-1,dtype='uint8')
                ilags = np.arange(idiag-((nphases-1)*speed),nlags,speed,
                                  dtype='uint8')
                
            n_items = min(len(iphases), len(ilags))
            diagonal_mean.append(np.mean(comp_anom_stack[iphases[:n_items], 
                                        ilags[:n_items],:,:],
                        axis=0))
            
        # After calculating all of the diagonal means, compute the 
        # variance of the resulting vector for the current speed
        diagonal_mean_var.append(np.var(np.asarray(diagonal_mean),axis=0))
        
    # After computing the variance for each speed, compute the mean 
    # variance, and then convert the variance to the STRIPES amplitude
    stripes = np.sqrt(2*np.nanmean(np.asarray(diagonal_mean_var),axis=0))

    return(stripes)
# ===============================================================================================
def compSTRIPES(comp_anom,pspeed):
    '''
    Computes the STRIPES index
    
        Parameters:
            comp_anom: matrix of lagged composite with first 2 dims (phases, lags)
                       input can be 2D or 4D
            pspeed: vector or scalar of speeds (# of days does the mjo spends in a phase)
            
        Returns:
            stripes: stripes index
    '''

    if len(np.shape(comp_anom)) == 2:
        stripes = compSTRIPES1D(comp_anom,pspeed)
    elif len(np.shape(comp_anom)) == 4:
        stripes = compSTRIPES2D(comp_anom,pspeed)
                                                 
    return(stripes)
# ===============================================================================================
def bootstrapSTRIPES(anoms, nboot, rmm, minlag, maxlag):
    '''
    Block bootstrap (using random shuffles of the years) computation
    of the STRIPES index
    
        Parameters:
            anoms: data array of forecast anomalies, must have dimension named
                   "time"
            nboot: number of bootstrap samples, each one takes about 10 seconds
            rmm: data array of rmm phases and amplitudes 
            minlag: minimum lag used for composites
            maxlag: maximum lag used for composites
            
        Returns:
            stripes_boot: nboot * nlat * nlon array of STRIPES indices
    '''
    print('computing bootstrap STRIPES significance...\n estimated time to complete = ' 
          + str(10*nboot/60) + ' min.')
    
    # Reorder forecast data by year
    groups = anoms.groupby('time.year')
    data_by_year = [group[1] for group in groups]
    nyr = len(data_by_year)
    ntime = len(anoms.time)
    
    stripes_boot = []
    for iboot in range(nboot):
        inds_shuffle = np.random.choice(nyr,nyr,replace=True)
        anoms_shuffle_year = xr.concat([data_by_year[idx] for idx in inds_shuffle], dim='time')
        
        # make sure the time dimension is the correct size, if it isn't ei ther shorten it
        # or try again
        ntime_boot = len(anoms_shuffle_year.time)
        while ntime_boot != ntime:
            if ntime_boot > ntime:
                anoms_shuffle_year = anoms_shuffle_year.isel(time=slice(0,ntime))
            else:
                inds_shuffle = np.random.choice(nyr,nyr,replace=True)
                anoms_shuffle_year = xr.concat([data_by_year[idx] 
                                                for idx in inds_shuffle], dim='time')
            ntime_boot = len(anoms_shuffle_year.time)
            
        # Calculate lagged composite with the bootstrap sample
        lagcomp = calc_lagged_composite(anoms_shuffle_year,
                                        rmm.amplitude>1.0,
                                        rmm.phase.values,
                                        maxlag,
                                        minlag)
        # Calculate STRIPES index
        stripes_boot.append(compSTRIPES(lagcomp.values, [5,6,7,8]))
        
    # Concatenate bootstrap samples
    stripes_boot = np.stack(stripes_boot)
    
    return stripes_boot
# ===============================================================================================
def get_variable_from_dataset(ds,vartype):
    '''
        Extract the target variable from the dataset. Convert to target units
        
            Parameters
                ds: xarray dataset
                vartype: options are 'gh','prate'. look for Z names or precip. names
                
            Returns
                da: subsetted dataArray in
    '''
    
    if vartype == 'gh':
        for name in ['z', 'Z','gh','z500']:
            if name in list(ds.keys()):
                break
        da = ds[name]
        
        # convert geopotential to geopotential height if needed
        for units in ['m**2 s**-2', 'm^2/s^2', 'm2/s2','m2s-2', 'm2 s-2']:
            if units == da.units:
                print('converting geopotential to geopotential height')
                da = da/9.81
                da.attrs['units']='m'
                break
        return da
        raise RuntimeError("Couldn't find a geopotential variable name")
        
    if vartype == 'prate':
        for name in ['prate', 'precipitationCal','pr','precip','precipitation']:
            if name in list(ds.keys()):
                break
        da = ds[name]

        # convert kg/m2/s to mm/day if needed
        for units in ['kg m**-2 s**-1','kg/m2/s','kg m-2 s-1','mm/s','mm s**-1', 'mm s-1']:
            if units == da.units:
                print('converting kg/m2/s to mm/day')
                da = da * 86400
                da.attrs['units']='mm/day'
                break

        return da
        raise RuntimeError("Couldn't find a precipitation variable name")
# ===============================================================================================
def calcSTRIPES_forecast_obs(fc_dir, obs_dir, frmm, vartype, t0, t1, testing=False): 
    '''
        Compute the STRIPES index for observations and forecast data

            Parameters
                fc_dir: directory where forecasts are located
                obs_dir: directory where observations are located
                frmm: rmm file containing phase and amplitude information
                vartype: type of variable (options are 'gh', and 'prate')
                t0: START_DATE (string)
                t1: END_DATE (string)
        		testing: default=False. Use during testing. Returns empty dataArrays
            
            Returns
                stripes_obs: list of length 3 of xarray dataArrays of observed stripes index
                stripes_fc: list of length 3 of xarray dataArrays of forecast stripes index

    '''
    
    lags = [[0,13],  # week 1-2
            [7,20],  # week 2-3
            [14,27]] # week 3-4

    # -------- Open data --------
    rmm = xr.open_dataset(frmm,decode_times=False)
    time=np.datetime64(rmm.time.units.split()[2]
                )+[np.timedelta64(int(days), 'D') for days in rmm.time.values]
    rmm['time']=time

    # read forecast data
    files = np.sort(glob.glob(fc_dir+'*.nc*'))
    
    ds = xr.open_mfdataset(files, combine='nested',
                           concat_dim='time',parallel='true',engine='h5netcdf')
    fc = get_variable_from_dataset(ds, vartype)

    # read obs
    obs_files = np.sort(glob.glob(obs_dir + '*.nc*'))
    if len(obs_files)==1:
    	ds = xr.open_dataset(obs_files[0],chunks='auto')
    else:
    	ds =xr.open_mfdataset(obs_files)
    obs = get_variable_from_dataset(ds, vartype)

    # if testing, stop here
    if testing:
        print('testing')
        nlon = len(obs.longitude)
        nlat = len(obs.latitude)
        stripes=xr.DataArray(np.nan*np.ones((nlat,nlon)),attrs={'long_name': 'STRIPES','units':
	'm'},dims=['latitude','longitude'],coords={"latitude":obs.latitude,"longitude":obs.longitude})

        stripes_obs = []
        stripes_obs.append(stripes)
        stripes_obs.append(stripes)
        stripes_obs.append(stripes)

        return stripes_obs, stripes_obs


    # subset time
    obs = obs.sel(time=slice(t0,t1))
    # make sure obs is organized time x lat x lon
    obs = obs.transpose('time','latitude','longitude')

    # -------- Calculate anomalies --------
    obs_anom=calcAnomObs(obs, vartype)
    obs_anom.attrs['units']=obs.units
    del obs
    gc.collect()

    fc_anom = calcAnom(fc,vartype)
    # Reshape 1D time dimension of UFS anomalies to 2D
    fc_anom = reshape_forecast(fc_anom, nfc=int(len(fc_anom.time)/len(files)))
    del fc
    gc.collect()

    # -------- Subset RMM and forecast data to winter --------
    rmm = rmm.sel(time=is_ndjfm(rmm['time.month']) & rmm.time.isin(fc_anom.time))
    fc_anom=fc_anom.sel(time=is_ndjfm(fc_anom['time.month']))

    # -------- Calculate STRIPES index --------
    stripes_obs = []
    stripes_fc = []
    for minlag, maxlag in lags:

        # ----- Obs -----
        lagcomp = calc_lagged_composite(obs_anom,
                                        rmm.amplitude > 1.0,
                                        rmm.phase.values, 
                                        maxlag = maxlag,
                                        minlag = minlag, 
                                        obs = True)
        stripes=compSTRIPES(lagcomp.values, [5,6,7,8])

        stripes_obs_TEMP=xr.DataArray(stripes,
                                   attrs={'long_name': 'STRIPES',
                                          'units': obs_anom.units},
                                   dims=['latitude','longitude'],
                                   coords={"latitude": obs_anom.latitude,
                                           "longitude": obs_anom.longitude})    
        del lagcomp
        del stripes
        gc.collect()

        # ----- Forecast -----
        lagcomp = calc_lagged_composite(fc_anom,
                                        rmm.amplitude > 1.0,
                                        rmm.phase.values, 
                                        maxlag = maxlag,
                                        minlag = minlag, 
                                        obs = False)
        stripes=compSTRIPES(lagcomp.values, [5,6,7,8])
        stripes_fc_TEMP=xr.DataArray(stripes, 
                             attrs={'long_name': 'STRIPES', 
                                    'units': obs_anom.units},
                             dims=['latitude','longitude'],
                             coords={"latitude": fc_anom.latitude,
                                     "longitude": fc_anom.longitude})

        del lagcomp
        del stripes
        gc.collect()

        # ----- Regrid if needed -----
        stripes_fc_TEMP, stripes_obs_TEMP = regrid(stripes_fc_TEMP,
                                                   stripes_obs_TEMP,
                                                   fc_anom.latitude,
                                                   fc_anom.longitude,
                                                   obs_anom.latitude,
                                                   obs_anom.longitude,
                                                   scalar=True)
        

        stripes_obs.append(stripes_obs_TEMP)
        stripes_fc.append(stripes_fc_TEMP)
        del stripes_fc_TEMP
        del stripes_obs_TEMP
        gc.collect()
        
    return stripes_obs, stripes_fc
