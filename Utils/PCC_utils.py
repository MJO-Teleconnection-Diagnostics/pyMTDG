import math
import numpy as np

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