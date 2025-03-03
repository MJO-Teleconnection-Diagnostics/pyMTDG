import numpy as np
import xarray as xr
from pathlib import Path
from typing import Dict, List, Tuple

from datetime import date, timedelta
import matplotlib.pyplot as plt
import proplot as plot
import os
import glob

from multiprocessing import Pool
from functools import partial
from fcst_utils import *

def get_netcdf_files(directories: List[str]) -> Dict[str, List[str]]:
    """Get sorted lists of NetCDF files from specified directories.
    
    Args:
        directories: List of directory paths
        
    Returns:
        Dictionary mapping variable names to file lists
    """
    variables = ['u200', 'u850', 'olr']
    return {
        var: sorted(glob.glob(str(directories[i] + '*.nc')))
        for i, var in enumerate(variables)
    }

def verify_file_counts(file_dict: Dict[str, List[str]]) -> None:
    """Verify that all variables have the same number of files.
    
    Args:
        file_dict: Dictionary mapping variable names to file lists
        
    Raises:
        RuntimeError: If file counts don't match
    """
    counts = {var: len(files) for var, files in file_dict.items()}
    if len(set(counts.values())) != 1:
        error_msg = '; '.join(f"# of {var} files: {count}" 
                            for var, count in counts.items())
        raise RuntimeError(f"Inconsistent file counts: {error_msg}")

def load_datasets(file_dict: Dict[str, List[str]]) -> Dict[str, xr.Dataset]:
    """Load datasets for all variables using xarray.
    
    Args:
        file_dict: Dictionary mapping variable names to file lists
        
    Returns:
        Dictionary mapping variable names to xarray datasets
    """
    return {
        var: xr.open_mfdataset(
            files,
            combine='nested',
            concat_dim='time',
            parallel=True,
            engine='h5netcdf'
        )
        for var, files in file_dict.items()
    }

def process_data(file_dict: Dict[str, List[str]]) -> Tuple[xr.DataArray, xr.DataArray, xr.DataArray]:
    """Main data processing function.
    
     Args:
         config_file: Path to configuration file
        
     Returns:
         Tuple of processed DataArrays (u200, u850, olr)
     """     
    
    # Load datasets
    datasets = load_datasets(file_dict)
    
    # Process variables
    return tuple(
         get_variable_from_dataset(datasets[var])
         for var in ['u200', 'u850', 'olr']
     )


def mean_120(model):
    return model.rolling(time=120, center=False).mean().dropna("time")
    #return model.rolling(forecast_day=120, center=False).mean().dropna("forecast_day")

def is_month_in_ndjfm(date):
    month = date.month
    if month in [11, 12, 1, 2, 3]:
        return True
    else:
        return False
    
def remove_120days_seasonalvar_obs(obs,std):
    avg = obs.rolling(time=120, center=False).mean()
    #print(sum(obs.values[:,:120])/120)
    obs=obs - avg
    return obs/std
    
def remove_120days_seasonalvar(exp_start_dates,model_data,obs,std,nfc):
    
    model_data_120remlis=[]
    for n,i in enumerate(exp_start_dates):

        days_start=n*nfc
        if is_month_in_ndjfm(i):
            
            #Start date of the most recent 120 days of experiment i
            start_date_119_obs = i - timedelta(days=119)
            end_date_119 = i - timedelta(days=1)
            
            #cases when start or end date fall on leap dates
            if end_date_119.month == 2 and end_date_119.day == 29:
                end_date_119=end_date_119 - timedelta(days=1)
                start_date_119_obs = start_date_119_obs - timedelta(days=1)

            elif start_date_119_obs.month == 2 and start_date_119_obs.day == 29:
                start_date_119_obs = start_date_119_obs - timedelta(days=1)

            start_date_119_obs = (start_date_119_obs).strftime('%Y-%m-%d')
            end_date_119 = (end_date_119).strftime('%Y-%m-%d')

            #selecting obs data from start_date_120_obs to end_date_i
            obs_data = obs.sel(time=slice(start_date_119_obs,end_date_119))

            #if there is a day less, it means the date range includes a leap date
            if len(obs_data.time) == 118:
                start_date_119_obs = (datetime.strptime(start_date_119_obs, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
                obs_data = obs.sel(time=slice(start_date_119_obs,end_date_119))
            
            ##model data selection
             #n = number of experiments 
             #days_start is the index of the experiment
             #using integer-based indexing because of non-unique labels in days dimension
            model = model_data.isel(time=slice(days_start,days_start+nfc))

            ##Concatenation of model and obs using time dimension
            concatenated_data =xr.concat([obs_data, model], dim='time')
            avg=mean_120(concatenated_data)
            avg=avg.isel(time = slice(-nfc,None))
            avg = avg.transpose('time','longitude')
            
            ##resetting time dimension back to 1-35 days

            model_120daysrem = xr.DataArray((model[:]-avg[:]).data, dims=('time',  'longitude'), coords={'time': model.time[:nfc], 'longitude': model.longitude})
            #model_data[n*35:n*35+35,:]= model_120daysrem[:] 
            
            ##program 2 normalization by observed std
            model_data_120rem = model_120daysrem[:]/std
            model_data_120remlis.append(model_data_120rem)
        
    return model_data_120remlis


def slice_avg(ds):
    ds_selected = ds.sel(latitude=slice(15., -15.))
    ds_avg_latitude = ds_selected.mean(dim='latitude')
    model_data = ds_avg_latitude
    return model_data

def slice_long(ds):
    ds_selected = ds.sel(longitude=slice(45., 240.))
    return ds_selected

def generate_start_dates(initial_date,start_date,end_date):
    date_range= pd.date_range(start=start_date, end=end_date, freq='MS')
    dates=[date for date in date_range if date.day == initial_date and date >= pd.to_datetime(start_date)]
    return dates

def rmm_amplitude(pc1_lis,pc2_lis):
    amplitude = np.sqrt(np.asarray(pc1_lis)**2+np.asarray(pc2_lis)**2)
    
    return amplitude.tolist()


def mjo_phase(pc1_lis, pc2_lis):
    pc1 = np.asarray(pc1_lis)
    pc2 = np.asarray(pc2_lis)
    
    if pc1.shape != pc2.shape:
        raise RuntimeError('The two PCs must have the same size')
    
    # Check for zero values in pc1
    if np.any(pc1 == 0):
        raise Warning('PC1 contains zero values')
    
    # Compute the angles
    tmp = np.arctan2(pc2, pc1)
    tmp[tmp < 0] += 2 * np.pi  # Ensure angles are in [0, 2π]
    
    # Assign phases based on angle ranges
    pha = np.zeros_like(tmp, dtype=int)
    pha[(tmp > np.pi) & (tmp <= np.pi + np.pi/4.)] = 1
    pha[(tmp > np.pi + np.pi/4.) & (tmp <= np.pi + 2*np.pi/4.)] = 2
    pha[(tmp > np.pi + 2*np.pi/4.) & (tmp <= np.pi + 3*np.pi/4.)] = 3
    pha[(tmp > np.pi + 3*np.pi/4.) & (tmp <= 2*np.pi)] = 4
    pha[(tmp > 0) & (tmp <= np.pi/4.)] = 5
    pha[(tmp > np.pi/4.) & (tmp <= 2*np.pi/4.)] = 6
    pha[(tmp > 2*np.pi/4.) & (tmp <= 3*np.pi/4.)] = 7
    pha[(tmp > 3*np.pi/4.) & (tmp <= np.pi)] = 8
    pha[(pha == 0)] = -1  # Default phase for values not matching any range
    
    return pha.tolist()


def get_variable_from_dataset(ds):
    '''
        Extract the target variable from the dataset. Convert to target units
        
            Parameters
                ds: xarray dataset
            Returns
                da: subsetted dataArray in
    '''
    for name in ['var', 'u200','U200','u850','U850','olr','OLR']:
        if name in list(ds.keys()):
            break
    da = ds[name]
        
    
    return da
    raise RuntimeError("Couldn't find a u200/u850/OLR variable name")


# Function to select MJO events based on two phases
def select_mjo_event_phases(amplitude, phase, selected_phases, amplitude_threshold):
    condition = (amplitude > amplitude_threshold) & (phase.isin(selected_phases))
    return condition

# Plots
def plot_acc_rmse(ds_corr,ds_rmse,ds_names,nfcst_days,fig_name):
    
    c1, c2 = plot.scale_luminance('cerulean', 0.5), plot.scale_luminance('red', 0.5)
    
    fcst_days=np.arange(nfcst_days)+1
    
    fig,ax1=plot.subplots(figsize=(8,4))
    ax2=ax1.twinx()

    ax1.plot(fcst_days,ds_corr,color=c1)
    ax1.axhline(y=0.5, color='k', linestyle='-',linewidth=0.5)
    ax1.format(ylim=(0,1),ylabel='ACC',ycolor=c1)
    ax1.grid(False)

    ax2.plot(fcst_days,ds_rmse,color=c2)
    ax2.format(ylim=(0,np.ceil(max(ds_rmse))+0.5),ylabel='RMSE',ycolor=c2)
    ax2.grid(False)
    
    ax2.set_title('MJO prediction skill: ACC and RMSE')


    ax1.set(xlabel='Forecast lead day')
    ax1.set(xlim=(0,len(fcst_days)))

    if not os.path.exists('../output/MJO/'+ds_names[1]): 
        os.mkdir('../output/MJO/'+ds_names[1])
    fig.savefig('../output/MJO/'+ds_names[1]+'/'+fig_name+'.jpg',dpi=300)
            
    return
            
def plot_amp_phase_err(ds_amp_err,ds_phase_err,ds_names,nfcst_days,fig_name):
    c1, c2 = plot.scale_luminance('cerulean', 0.5), plot.scale_luminance('red', 0.5)
    
    fcst_days=np.arange(nfcst_days)+1
    
    ya_min = np.round(-max(ds_amp_err),3) if min(ds_amp_err) > 0 else np.round(min(ds_amp_err),3)
    ya_max = np.round(-min(ds_amp_err),3) if max(ds_amp_err) < 0 else np.round(max(ds_amp_err),3)
    
    yp_min = np.round(-max(ds_phase_err)) if min(ds_phase_err) > 0 else np.round(min(ds_phase_err))
    yp_max = np.round(-min(ds_phase_err)) if max(ds_phase_err) < 0 else np.round(max(ds_phase_err))
            
    fig,ax1=plot.subplots(figsize=(8,4))
    ax2=ax1.twinx()

    ax1.plot(fcst_days,ds_phase_err,color=c1)
    ax1.axhline(y=0., color='k', linestyle='-',linewidth=0.5)
    ax1.format(ylim=(yp_min,yp_max),ylabel='Phase error, deg',ycolor=c1)
    ax1.grid(False)

    ax2.plot(fcst_days,ds_amp_err,color=c2)
    ax2.format(ylim=(ya_min,ya_max),ylabel='Amplitude error',ycolor=c2)
    ax2.grid(False)
    
    ax2.set_title('MJO prediction skill: Phase and Amplitude')

    ax1.set(xlabel='Forecast lead day')
    ax1.set(xlim=(0,len(fcst_days)))

    if not os.path.exists('../output/MJO/'+ds_names[1]): 
        os.mkdir('../output/MJO/'+ds_names[1])
    fig.savefig('../output/MJO/'+ds_names[1]+'/'+fig_name+'.jpg',dpi=300)
    return

def plot_hovmoler(ds_olr,ds_u850,ds_names,fig_name):
    colors=['#1A2C62','#2E4F96','#578AC3','#8ABEE5','#E3F2F9','#FFFFFF','#FBF1BC','#ED9546','#DB5F3A','#B8312E','#872320']

    with plot.rc.context(fontsize='18px'):
        fig,axes=plot.subplots(nrows=2,ncols=1,axwidth=6.5,axheight=4.0,share=0)
        for p,ax in enumerate(axes):
            # Adjusting the color map for increased saturation and sharper transitions
            contourf_olr = ax.contourf(
            slice_long(ds_olr[p].longitude),ds_olr[p].forecast_day,
            slice_long(ds_olr[p]),
            colors=colors,
            levels=[-9, -7, -5, -3, -1, 1, 3, 5, 7, 9],
            extend='both'
            )

            # Plotting the U850 data using contour with less prominent lines
            contour_u850 = ax.contour(
            slice_long(ds_u850[p].longitude),ds_u850[p].forecast_day,
            slice_long(ds_u850[p]),
            colors='grey',
            levels=np.arange(-1.8, 1.8, 0.3),  # Adjust the contour intervals to match the colors
            linewidths=0.75  # Slightly thicker lines for more prominence
            )

            # Adding a vertical line at 120° longitude
            ax.axvline(x=120, color='purple', linestyle='-', linewidth=1.5)

            # Setting the y-axis limits to range from 5 to 25
            ax.format(xlocator=plot.arange(60, 241, 60),xticklabels=['60°E', '120°E', '180°', '120°W'],
                      ylim=(1, 28),ylocator=plot.arange(5, 30, 5),ylabel='Forecast Day',
                      title='   '+ds_names[p],titleloc='l')
    
            # Adding colorbar with the exact range as in the provided color bar
        cbar_olr = fig.colorbar(contourf_olr, loc='b',extend='both', 
                                label='OLR Anomalies (W/m²)')

    if not os.path.exists('../output/MJO/'+ds_names[1]): 
        os.mkdir('../output/MJO/'+ds_names[1])
    fig.savefig('../output/MJO/'+ds_names[1]+'/'+fig_name+'.jpg',dpi=300)
    return
