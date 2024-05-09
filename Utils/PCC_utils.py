import math
import numpy as np
import xarray as xr

def get_rmm_composite_list ( composite_phase_names , model_yyyymmdd , rmm_yyyymmdd , rmm_phase_in , rmm_amplitude_in , amplitude_threshold , start_month , end_month ) :
    rmm_list = [ ]
    for phase_n in range ( len ( composite_phase_names ) ) : rmm_list.append ( [ ] )
    if start_month > end_month :
        for time_step in range ( len ( model_yyyymmdd ) ) :
            month_now = model_yyyymmdd [ time_step ] // 100 % 100
            if month_now >= start_month or month_now <= end_month :
                time_n = 0
                while rmm_yyyymmdd [ time_n ] < model_yyyymmdd [ time_step ] : time_n = time_n + 1
                if rmm_amplitude_in [ time_n ] > amplitude_threshold :
                    rmm_list [ rmm_phase_in [ time_n ] // 2 % 4 ].append ( time_step )
    else :
        for time_step in range ( len ( model_yyyymmdd ) ) :
            month_now = model_yyyymmdd [ time_step ] // 100 % 100
            if month_now >= start_month and month_now <= end_month :
                time_n = 0
                while rmm_yyyymmdd [ time_n ] < model_yyyymmdd [ time_step ] : time_n = time_n + 1
                if rmm_amplitude_in [ time_n ] > amplitude_threshold :
                    rmm_list [ rmm_phase_in [ time_n ] // 2 % 4 ].append ( time_step )
    return rmm_list

def correlate(obs,model,lat_min,lat_max,lon_min,lon_max):
    x=obs.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min,lon_max))
    y=model.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min,lon_max))
    x_stacked=x.stack(grid=('latitude','longitude'))
    y_stacked=y.stack(grid=('latitude','longitude'))
    corr=np.corrcoef(x_stacked,y_stacked)
    return corr

def correlate_atlantic(obs,model,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2):
    x1=obs.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min1,lon_max1))
    y1=model.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min1,lon_max1))
    x2=obs.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min2,lon_max2))
    y2=model.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min2,lon_max2))
    x=xr.concat((x1, x2),dim="longitude")
    y=xr.concat((y1, y2),dim="longitude")
    x_stacked=x.stack(grid=('latitude','longitude'))
    y_stacked=y.stack(grid=('latitude','longitude'))
    corr=np.corrcoef(x_stacked,y_stacked)
    return corr

def patterncc(timelag,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min,lon_max):
    nn=len(rmm_list_ERA[0,:])
    pcc=np.empty( ( len (timelag),nn) ,dtype=float)
    for inumber in range (len(rmm_list_ERA[0,:])):
        for itime in range (len (timelag)):
            model_z500_temp=modeldata [ rmm_list_model[inumber], itime, : , : ]
            erai_anomaly_temp=eraidata [ rmm_list_ERA[itime,inumber], : , : ]
            res_temp=correlate(erai_anomaly_temp,
                model_z500_temp,lat_min,lat_max,lon_min,lon_max)
            pcc[itime,inumber]=res_temp[0,1]
    return pcc

def patterncc_bootstrap(timelag,random_number,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min,lon_max):
    nn=len(rmm_list_ERA[0,:])
    pcc=np.empty( ( len (timelag),nn) ,dtype=float)
    for inumber in range (len(rmm_list_ERA[0,:])):
        for itime in range (len (timelag)):
            model_z500_temp=modeldata [ rmm_list_model[random_number[inumber]], itime, : , : ]
            erai_anomaly_temp=eraidata [ rmm_list_ERA[itime,random_number[inumber]], : , : ]
            res_temp=correlate(erai_anomaly_temp,
                model_z500_temp,lat_min,lat_max,lon_min,lon_max)
            pcc[itime,inumber]=res_temp[0,1]
    return pcc

def patterncc_atlantic(timelag,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2):
    nn=len(rmm_list_ERA[0,:])
    pcc=np.empty( ( len (timelag),nn) ,dtype=float)
    for inumber in range (len(rmm_list_ERA[0,:])):
        for itime in range (len (timelag)):
            model_z500_temp=modeldata [ rmm_list_model[inumber], itime, : , : ]
            erai_anomaly_temp=eraidata [ rmm_list_ERA[itime,inumber], : , : ]
            res_temp=correlate_atlantic(erai_anomaly_temp,
                model_z500_temp,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2)
            pcc[itime,inumber]=res_temp[0,1]
    return pcc

def patterncc_atlantic_bootstrap(timelag,random_number,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2):
    nn=len(rmm_list_ERA[0,:])
    pcc=np.empty( ( len (timelag),nn) ,dtype=float)
    for inumber in range (len(rmm_list_ERA[0,:])):
        for itime in range (len (timelag)):
            model_z500_temp=modeldata [ rmm_list_model[random_number[inumber]], itime, : , : ]
            erai_anomaly_temp=eraidata [ rmm_list_ERA[itime,random_number[inumber]], : , : ]
            res_temp=correlate_atlantic(erai_anomaly_temp,
                model_z500_temp,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2)
            pcc[itime,inumber]=res_temp[0,1]
    return pcc
    
def amplitude_metric(timelag,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min,lon_max):
    nn=len(rmm_list_ERA[0,:])
    amp=np.empty( ( len (timelag),nn) ,dtype=float)
    for inumber in range (len(rmm_list_ERA[0,:])):
        for itime in range (len (timelag)):
            model_z500_temp=modeldata [ rmm_list_model[inumber], itime, : , : ]
            erai_anomaly_temp=eraidata [ rmm_list_ERA[itime,inumber], : , : ]
            x=erai_anomaly_temp.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min,lon_max))
            y=model_z500_temp.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min,lon_max))
            x_stacked=x.stack(grid=('latitude','longitude'))
            y_stacked=y.stack(grid=('latitude','longitude'))
            model_z500_variance_temp=np.var(y_stacked)
            erai_anomaly_variance_temp=np.var(x_stacked)
            amp[itime,inumber]=math.sqrt(model_z500_variance_temp/erai_anomaly_variance_temp)
    return amp  

def amplitude_metric_bootstrap(timelag,random_number,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min,lon_max):
    nn=len(rmm_list_ERA[0,:])
    amp=np.empty( ( len (timelag),nn) ,dtype=float)
    for inumber in range (len(rmm_list_ERA[0,:])):
        for itime in range (len (timelag)):
            model_z500_temp=modeldata [ rmm_list_model[random_number[inumber]], itime, : , : ]
            erai_anomaly_temp=eraidata [ rmm_list_ERA[itime,random_number[inumber]], : , : ]
            x=erai_anomaly_temp.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min,lon_max))
            y=model_z500_temp.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min,lon_max))
            x_stacked=x.stack(grid=('latitude','longitude'))
            y_stacked=y.stack(grid=('latitude','longitude'))
            model_z500_variance_temp=np.var(y_stacked)
            erai_anomaly_variance_temp=np.var(x_stacked)
            amp[itime,inumber]=math.sqrt(model_z500_variance_temp/erai_anomaly_variance_temp)
    return amp

def amplitude_metric_atlantic(timelag,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2):
    nn=len(rmm_list_ERA[0,:])
    amp=np.empty( ( len (timelag),nn) ,dtype=float)
    for inumber in range (len(rmm_list_ERA[0,:])):
        for itime in range (len (timelag)):
            model_z500_temp=modeldata [ rmm_list_model[inumber], itime, : , : ]
            erai_anomaly_temp=eraidata [ rmm_list_ERA[itime,inumber], : , : ]
            x1=erai_anomaly_temp.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min1,lon_max1))
            x2=erai_anomaly_temp.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min2,lon_max2))
            y1=model_z500_temp.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min1,lon_max1))
            y2=model_z500_temp.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min2,lon_max2))
            x=xr.concat((x1, x2),dim="longitude")
            y=xr.concat((y1, y2),dim="longitude")
            x_stacked=x.stack(grid=('latitude','longitude'))
            y_stacked=y.stack(grid=('latitude','longitude'))
            model_z500_variance_temp=np.var(y_stacked)
            erai_anomaly_variance_temp=np.var(x_stacked)
            amp[itime,inumber]=math.sqrt(model_z500_variance_temp/erai_anomaly_variance_temp)
    return amp

def amplitude_metric_atlantic_bootstrap(timelag,random_number,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2):
    nn=len(rmm_list_ERA[0,:])
    amp=np.empty( ( len (timelag),nn) ,dtype=float)
    for inumber in range (len(rmm_list_ERA[0,:])):
        for itime in range (len (timelag)):
            model_z500_temp=modeldata [ rmm_list_model[random_number[inumber]], itime, : , : ]
            erai_anomaly_temp=eraidata [ rmm_list_ERA[itime,random_number[inumber]], : , : ]
            x1=erai_anomaly_temp.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min1,lon_max1))
            x2=erai_anomaly_temp.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min2,lon_max2))
            y1=model_z500_temp.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min1,lon_max1))
            y2=model_z500_temp.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min2,lon_max2))
            x=xr.concat((x1, x2),dim="longitude")
            y=xr.concat((y1, y2),dim="longitude")
            x_stacked=x.stack(grid=('latitude','longitude'))
            y_stacked=y.stack(grid=('latitude','longitude'))
            model_z500_variance_temp=np.var(y_stacked)
            erai_anomaly_variance_temp=np.var(x_stacked)
            amp[itime,inumber]=math.sqrt(model_z500_variance_temp/erai_anomaly_variance_temp)
    return amp

def test_significance (N_samples,timelag,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min,lon_max,PCC=False,amp=False):
    rng = np.random.default_rng()
    data = np.full ( ( N_samples, len (timelag) ) , np.nan , dtype=float )
    for n in range (N_samples) :
       random_numbers = rng.choice ( len(rmm_list_ERA[0,:]), len(rmm_list_ERA[0,:]))
       if (PCC==True):
          pcc_temp=patterncc_bootstrap(timelag,random_numbers,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min,lon_max)
          data[n,:]=np.mean ( pcc_temp,axis= 1   )
       if (amp==True):
          amp_temp=amplitude_metric_bootstrap(timelag,random_numbers,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min,lon_max)
          data[n,:]=np.mean ( amp_temp,axis= 1   )
    percentile_low = np.full ( ( len (timelag) ) , np.nan , dtype=float )
    percentile_high = np.full ( ( len (timelag) ) , np.nan , dtype=float )
    for i in range (len(timelag)):
       percentile_low[i]=np.percentile(data[:,i], 2.5)
       percentile_high[i]=np.percentile(data[:,i], 97.5)
    return percentile_low,percentile_high

def test_significance_atlantic (N_samples,timelag,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2,PCC=False,amp=False):
    rng = np.random.default_rng()
    data = np.full ( ( N_samples, len (timelag) ) , np.nan , dtype=float )
    for n in range (N_samples) :
       random_numbers = rng.choice ( len(rmm_list_ERA[0,:]), len(rmm_list_ERA[0,:]))
       if (PCC==True):
          pcc_temp=patterncc_atlantic_bootstrap(timelag,random_numbers,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2)
          data[n,:]=np.mean ( pcc_temp,axis= 1   )
       if (amp==True):
          amp_temp=amplitude_metric_atlantic_bootstrap(timelag,random_numbers,rmm_list_ERA,rmm_list_model,modeldata,eraidata,lat_min,lat_max,lon_min1,lon_max1,lon_min2,lon_max2)
          data[n,:]=np.mean ( amp_temp,axis= 1   )
    percentile_low = np.full ( ( len (timelag) ) , np.nan , dtype=float )
    percentile_high = np.full ( ( len (timelag) ) , np.nan , dtype=float )
    for i in range (len(timelag)):
       percentile_low[i]=np.percentile(data[:,i], 2.5)
       percentile_high[i]=np.percentile(data[:,i], 97.5)
    return percentile_low,percentile_high

def composites_model(rmm_list_model,modeldata,data_lat_in,data_lon_in):
    model_z500_composite=np.empty(  ( 4, len ( data_lat_in ) , len ( data_lon_in ) ) ,dtype=float)
    model_z500_composite[0,:,:]=np.nanmean(modeldata [ rmm_list_model, 0:6, : , : ],axis=(0,1))
    model_z500_composite[1,:,:]=np.nanmean(modeldata [ rmm_list_model, 7:13, : , : ],axis=(0,1))
    model_z500_composite[2,:,:]=np.nanmean(modeldata [ rmm_list_model, 14:20, : , : ],axis=(0,1))
    model_z500_composite[3,:,:]=np.nanmean(modeldata [ rmm_list_model, 21:27, : , : ],axis=(0,1))
    return model_z500_composite

def composites_era(rmm_list_ERA,eraidata,data_lat_in,data_lon_in):
    ERA5_z500_composite=np.empty(  ( 4, len ( data_lat_in ) , len ( data_lon_in ) ) ,dtype=float)
    rmm_list_ERA_new = rmm_list_ERA.flatten()
    week1_start=0
    week1_end=len((rmm_list_ERA[0,:]))*7-1
    ERA5_z500_composite[0,:,:]=np.nanmean(eraidata[ rmm_list_ERA_new[week1_start:week1_end], : , : ],axis=0)
    week2_start=len((rmm_list_ERA[0,:]))*7
    week2_end=len((rmm_list_ERA[0,:]))*14-1
    ERA5_z500_composite[1,:,:]=np.nanmean(eraidata[ rmm_list_ERA_new[week2_start:week2_end], : , : ],axis=0)
    week3_start=len((rmm_list_ERA[0,:]))*14
    week3_end=len((rmm_list_ERA[0,:]))*21-1
    ERA5_z500_composite[2,:,:]=np.nanmean(eraidata[ rmm_list_ERA_new[week3_start:week3_end], : , : ],axis=0)
    week4_start=len((rmm_list_ERA[0,:]))*21
    week4_end=len((rmm_list_ERA[0,:]))*28-1
    ERA5_z500_composite[3,:,:]=np.nanmean(eraidata[ rmm_list_ERA_new[week4_start:week4_end], : , : ],axis=0)
    return ERA5_z500_composite

def get_variable_from_dataset(ds):
    '''
        Extract the target variable from the dataset. Convert to target units
        
            Parameters
                ds: xarray dataset
                vartype: options are 'gh','prate'. look for Z names or precip. names
                
            Returns
                da: subsetted dataArray in
    '''
    
    
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
        
