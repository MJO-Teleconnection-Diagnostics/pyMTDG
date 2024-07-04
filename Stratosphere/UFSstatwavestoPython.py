#!/usr/bin/env python
# coding: utf-8

import xarray as xr

import numpy.fft as npft

from datetime import datetime

from datetime import timedelta

from datetime import date

import pandas as pd
 
import yaml
import glob
import gc


import sys
sys.path.insert(0, '../Utils')
from pathlib import Path
from obs_utils import *
from fcst_utils import *
from t2m_utils import *


print(f'Compute stationary waves diagnostic')

config_file=Path('../driver/config.yml').resolve()
with open(config_file,'r') as file:
    try:
        dictionary = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)

 # Get the forecast period from the provided Start_Date -- End_Date period
yyyymmdd_Begin=dictionary['START_DATE']
tBegin=yyyymmdd_Begin[0:4]+'-'+yyyymmdd_Begin[4:6]+'-'+yyyymmdd_Begin[6:8]
yyyymmdd_End=dictionary['END_DATE']
tEnd=yyyymmdd_End[0:4]+'-'+yyyymmdd_End[4:6]+'-'+yyyymmdd_End[6:8]

# ERA-Interim data covers 01/01/1979-08/31/2019, 7 years and 8 months, 14853 days

 
fil_obs=yml_input['DIR_IN']+'/mjo_teleconnections_data/erai/z500/z500.19790101-20190831.nc'
# Cristiana - needs to be updated to link to where files are stored
   
ds_obs_name='ERAI'

ds_obs=xr.open_dataset(fil_obs)
obs=get_variable_from_dataset(ds_obs)


# Generate time limits for each initial condition 

nyrs=date.fromisoformat(tEnd).year-date.fromisoformat(tBegin).year +1
yrStrt=date.fromisoformat(tBegin).year
mmStrt=date.fromisoformat(tBegin).month

# Cristiana: Read in forecast data  (not sure which of the following two lines is correct)
Model_z500_files             = yml_input [ 'Path to Z500 model data files' ]
Model_z500_files = [ "/data0/czheng/S2S-UFS/data/6hourly/Prototype5/gh_500-isobaricInhPa/gh.500-isobaricInhPa.*.6hourly.nc" ]

fcst_dir=dictionary['Path to zg model data files for date']  #Cristiana - needs to be updated to link to where files are stored
ds_fcst_name=dictionary['model name']
ds_names=[ds_obs_name,ds_fcst_name]


fcst_files=np.sort(glob.glob(str(fcst_dir+'*.nc')))
ds_fcst=xr.open_mfdataset(fcst_files,combine='nested',concat_dim='time',parallel=True)
fcst=get_variable_from_dataset(ds_fcst)

rgrd_fcst=regrid_scalar_spharm(fcst,ds_fcst.latitude,ds_fcst.longitude,
                                        ds_obs.latitude,ds_obs.longitude)
del ds_fcst
gc.collect()
del rgrd_fcst
gc.collect()
        

fcst_anom=fcst  #for this metric we use the raw data, not anomalies, but I'm reusing code written for other packages so I kept this in 
del fcst
 
# Reshape 1D time dimension of UFS anomalies to 2D
fcst_anom = reshape_forecast(fcst_anom, nfc=int(len(fcst_anom.time)/len(fcst_files)))
       
    
# Select initial conditions in the forecast during DJFM


pha_obs_ndjfm  = ds_obs.sel(time=ds_obs.time.dt.month.isin([1, 2, 3, 11, 12]))



fcst_anom=fcst_anom.sel(time=fcst_anom.time.dt.month.isin([1, 2, 3, 11, 12]))

 

 
# Main calculation
weeks=['week2','week3','week4','week5']


 


 


##### make plots [this is borrowed from Cheng's directory, as he also makes stereographic plots
# https://github.com/cristianastan2/MJO-Teleconnections/blob/develop/eke/eke_plot.py
mpres                       = Ngl.Resources()
mpres.nglDraw               = False
mpres.nglFrame              = False
mpres.nglMaximize           = False
mpres.vpXF                  = 0.05
mpres.vpYF                  = 0.88
mpres.vpWidthF              = 0.45
mpres.vpHeightF             = 0.45
mpres.mpProjection          = 'Stereographic'
mpres.mpEllipticalBoundary  = True
mpres.mpDataSetName         = 'Earth..4'
mpres.mpDataBaseVersion     = 'MediumRes'
mpres.mpLimitMode           = 'LatLon'
mpres.mpMaxLatF             = 90.
mpres.mpMinLatF             = 20.
mpres.mpCenterLatF          = 90.
mpres.mpGridAndLimbOn       = False
mpres.pmTickMarkDisplayMode = 'Never'

res_polar_color                      = Ngl.Resources ( )
res_polar_color.nglFrame             = False
res_polar_color.nglDraw              = False
res_polar_color.cnFillOn             = True
res_polar_color.cnLinesOn            = False
res_polar_color.cnLineLabelsOn       = False
res_polar_color.cnFillPalette        = "NCV_blue_red"
res_polar_color.cnLevelSelectionMode = "ManualLevels"
res_polar_color.lbOrientation        = "horizontal"
res_polar_color.sfYArray             = np.array ( data_lat_in )

 
res_polar_color_z500                      = Ngl.Resources ( )
res_polar_color_z500.nglFrame             = False
res_polar_color_z500.nglDraw              = False
res_polar_color_z500.cnFillOn             = True
res_polar_color_z500.cnLinesOn            = False
res_polar_color_z500.cnLineLabelsOn       = False
res_polar_color_z500.cnFillPalette        = "NCV_blue_red"
res_polar_color_z500.cnLevelSelectionMode = "ManualLevels"
res_polar_color_z500.lbOrientation        = "horizontal"
res_polar_color_z500.sfYArray             = np.array ( data_lat_in )

lnres                   = Ngl.Resources()
lnres.gsLineColor       = "black"
lnres.gsLineThicknessF  = 1.0
lnres.gsLineDashPattern = 0

plot_levels = 8
 

 
for whichwk in weeks:

      
           
            factor = [1, 1, 1.5, 2, 3]
                
#Chaim - I did my best to merge Cheng's EKE plotting code with mine
                 factorx = 0.4
               
		  res_polar_color_z500.cnLevelSpacingF =  list(range(-250, 251, 25))  
		  res_polar_color_z500.cnMaxLevelValF  = max(res_polar_color_z500.cnLevelSpacingF)
		  res_polar_color_z500.cnMinLevelValF  = - res_polar_color_z500.cnMaxLevelValF
	
		#I'm pretty sure this is a bug and needs to be fixed
                    thisplottablemean = np.nanmean(np.nanmean(np.nanmean(fcst_anom[:, [0, 1, 2, 3, 8, 9], protoind, :, :, whichwk], 1), 2), 6)
                    thisplottablemean = thisplottablemean - np.nanmean(thisplottablemean, 1)

 		 wks_model = Ngl.open_wks ( "png" , plot_dir + "z500_week" + weeks [ whichwk ] )
		 mpres.vpXF = 0.025             #-- viewport x-position
	 	 map1 = Ngl.map ( wks_model , mpres )                        #-- create base map
		 Ngl.draw ( map1 )                                   #-- draw map
		 lines = []
		  lines.append ( Ngl.add_polyline ( wks_model , map1 , [ - 180 , 0 , 180 ] , [ mpres.mpMinLatF , mpres.mpMinLatF , mpres.mpMinLatF ] ,lnres ) )
	        plot_cyclic , lon_cyclie       = Ngl.add_cyclic ( thisplottablemean , data_lon_in )
		     res_polar_color_z500.sfXArray  = lon_cyclie
  
   		 res_polar_color_z500.tiMainString = Model_name + " z500 week" + weeks [ whichwk ]
   			plot = Ngl.contour ( wks_model , plot_cyclic , res_polar_color_z500 )
    		  Ngl.overlay ( map1 , plot )
   
    		Ngl.draw ( map1 )
   		 mpres.vpXF = 0.525             #-- viewport x-position
   		 map2 = Ngl.map ( wks_model , mpres )                        #-- create base map
   		 Ngl.draw ( map2 )                                   #-- draw map
   		 lines = []


	#I'm pretty sure this is a bug and needs to be fixed
                    thisplottablemean = np.nanmean(np.nanmean(np.nanmean(pha_obs_ndjfm[:, [0, 1, 2, 3, 8, 9], protoind, :, :, whichwk], 1), 2), 6)
                    thisplottablemean = thisplottablemean - np.nanmean(thisplottablemean, 1)


   		 lines.append ( Ngl.add_polyline ( wks_model , map2 , [ - 180 , 0 , 180 ] , [ mpres.mpMinLatF , mpres.mpMinLatF , mpres.mpMinLatF ] ,lnres ) )
   		 plot_cyclic , lon_cyclie       = Ngl.add_cyclic ( thisplottablemean, data_lon_in )
   		     res_polar_color_z500.sfXArray  = lon_cyclie
   		   res_polar_color_z500.tiMainString = Reanalysis_name + " z500 week" + weeks [ whichwk ]
  		  plot = Ngl.contour ( wks_model , plot_cyclic , res_polar_color_z500 )
  		    Ngl.overlay ( map2 , plot )
  		   Ngl.draw ( map2 )
  		  Ngl.frame ( wks_model )
  		  Ngl.delete_wks ( wks_model )

                  
