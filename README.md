# MJO-Teleconnections Diagnostics Package

This repository contains the user interface and code to run the diagnostics for evaluating the MJO teleconnections forecasted by a subseasonal to seasonal system. For the background information on diagnostics see: 

Stan, C., C. Zheng, E. K.-M. Chang, D. I. V. Domeisen, C. Garfienkel, A. M. Jenney, H. Kim, Y.-K. Lim, H. Lin, A. Robertson, C. Schwartz, F. Vitart, J. Wang, P. Yadav, 2022: Advances in the prediction of MJO-Teleconnections in the S2S forecast systems. Bulletin of the American Meteorological Society, 103, E11427-E1447. https://doi.org/10.1175/BAMS-D-21-0130.1

Contents:
1. [Software requirements](#introduction)
2. [Obtaining the code](#code)
3. [Data format](#data)
4. [Variables](#vars)

## 1. Software and computational requirements <a name="introduction"></a>
The package has been developed using `Python 3.9`.

SLURM (`salloc`) is enabled but is not required.

Required packages:

`+` proplot

`+` pyqt5

`+` pyspharm

`+` scipy

`+` xarray

## 2. Obtaining the code <a name="code"></a>
To checkout and run the code, no git knowledge is required. To obtain the code you need to do the following:

a. Clone the repository.

  a.1 Clone the repository: master and all other branches
  
~~~
git clone https://github.com/cristianastan2/MJO-Teleconnections.git MJO-Teleconnections
~~~

  a.2 Clone the repository and fetch only a single branch
~~~
git clone --branch develop --single-branch  https://github.com/cristianastan2/MJO-Teleconnections.git MJO-Teleconnections
~~~

This will create a directory `MJO-Teleconnections/` in your current working directory.

b. Go into the newly created MJO-Teleconnections repository to create the environment required to run the package from the `mjo_telecon.yml` file included in the pckage.
~~~
cd MJO-Teleconnections
conda env create -n mjo_telecon --file mjo_telecon.yml
~~~

c. Go to the `driver` directory to run the code.
~~~
cd driver
python mjo_gui.py
~~~

## 3. Data format <a name="data"></a>
The package can only read data in the netcdf format. Most diagnostics work with daily mean and ensemble mean forecast data. Each forecast experiment must be aggregated into one file with the forecast leads (days) as the record dimension. In the example below, the forecast initial condition is 2018-03-15. 
~~~
netcdf z500_20180315 {
dimensions:
	latitude = 721 ;
	longitude = 1440 ;
	time = 35 ;
variables:
	float latitude(latitude) ;
		latitude:units = "degrees_north" ;
		latitude:standard_name = "latitude" ;
		latitude:long_name = "latitude" ;
		latitude:stored_direction = "decreasing" ;
	float longitude(longitude) ;
		longitude:units = "degrees_east" ;
		longitude:standard_name = "longitude" ;
		longitude:long_name = "longitude" ;
	int time(time) ;
		time:units = "days since 2018-03-15 00:00:00" ;
		time:calendar = "proleptic_gregorian" ;
	float z500(time, latitude, longitude) ;
		z500:_FillValue = NaNf ;
		z500:units = "gpm" ;
		z500:name = "Geopotential Height" ;

time = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 
    20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34 ;
~~~
The Extra-tropical Cyclone Activity diagnostic requires 6-hourly forecast data for each ensemble member. The forecast files can include the initial condition (analysis) but is not a requirement. Each forecast experiment must be aggregated into one file with the `forecast_hour` as the record dimension. In the example below the forecast initial condition is 2018-03-15. The initial condition (forecast_hour=0) is included. 
~~~
netcdf gh.500-isobaricInhPa.2018031500_e00 {
dimensions:
        forecast_hour = 140 ;
        latitude = 121 ;
        longitude = 240 ;
variables:
        float z(forecast_hour, latitude, longitude) ;
                z:time = 0. ;
                z:_FillValue = NaNf ;
                z:missing_value = NaNf ;
                z:GRIB_centre = "kwbc" ;
                z:GRIB_centreDescription = "US National Weather Service - NCEP" ;
         double forecast_hour(forecast_hour) ;
                forecast_hour:units = "hour" ;
                forecast_hour:axis = "Z" ;
        double latitude(latitude) ;
                latitude:standard_name = "latitude" ;
                latitude:long_name = "latitude" ;
                latitude:units = "degrees_north" ;
                latitude:axis = "Y" ;
        double longitude(longitude) ;
                longitude:standard_name = "longitude" ;
                longitude:long_name = "longitude" ;
                longitude:units = "degrees_east" ;
                longitude:axis = "X" ;

	forecast_hour = 0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 
    	90, 96, 102, 108, 114, 120, 126, 132, 138, 144, 150, 156, 162, 168, 174, 
    	180, 186, 192, 198, 204, 210, 216, 222, 228, 234, 240, 246, 252, 258, 
    	264, 270, 276, 282, 288, 294, 300, 306, 312, 318, 324, 330, 336, 342, 
    	348, 354, 360, 366, 372, 378, 384, 390, 396, 402, 408, 414, 420, 426, 
    	432, 438, 444, 450, 456, 462, 468, 474, 480, 486, 492, 498, 504, 510, 
    	516, 522, 528, 534, 540, 546, 552, 558, 564, 570, 576, 582, 588, 594, 
    	600, 606, 612, 618, 624, 630, 636, 642, 648, 654, 660, 666, 672, 678, 
    	684, 690, 696, 702, 708, 714, 720, 726, 732, 738, 744, 750, 756, 762, 
    	768, 774, 780, 786, 792, 798, 804, 810, 816, 822, 828, 834 ;
~~~

The package includes ERA-Interim fields for validation. The ERA-Interim data can be downloaded from here. The data is provided on the native grid (`latitudes=256, longitudes=512`), and the package will interpolate the forecast data to the ERA-Interim grid. For precipitation, [Integrated Multi-satellitE Retrivers for GPM](https://gpm.nasa.gov/data/imerg), IMERG, is the default validation dataset. IMERG covers 2000-2023 and is interpolated to (`latitudes=241`,`longitudes=480`). The package will interpolate the forecast data to the the IMERG grid.

## 4. Variables <a name="vars"></a>
The list of diagnostics and required meteorological fields:
~~~
STRIPES Index for Geopotential:
	* Geopotential at 500 hPa
 	*** Variable can be named any of: 'z', 'Z', 'gh', 'z500'
	*** Unit can be any of:'m**2 s**-2', 'm^2/s^2', 'm2/s2','m2s-2', 'm2 s-2'	
~~~
~~~
STRIPES Index for precipitation:
	* Precipitation rate:
	*** Variable can be named any of: 'prate', 'precipitationCal','precipitation','precip'
	*** Unit: mm/day
~~~
~~~
Pattern Correlation and Relative Amplitude of the MJO teleconnections over the PNA region:
	* Geopotential at 500 hPa
 	*** Variable can be named any of: 'z', 'Z', 'gh', 'z500'
	*** Unit can be any of:'m**2 s**-2', 'm^2/s^2', 'm2/s2','m2s-2', 'm2 s-2'
~~~
~~~
Pattern Correlation and Relative Amplitude of the MJO teleconnections over the Atlantic region:
	* Geopotential at 500 hPa
 	*** Variable can be named any of: 'z', 'Z', 'gh', 'z500'
	*** Unit can be any of:'m**2 s**-2', 'm^2/s^2', 'm2/s2','m2s-2', 'm2 s-2'
~~~
~~~
Extra-tropical Cyclone Activity:
	* Geopotential at 500 hPa
 	*** Variable can be named any of: 'z', 'Z', 'gh', 'z500'
	*** Unit can be any of:'m**2 s**-2', 'm^2/s^2', 'm2/s2','m2s-2', 'm2 s-2'
	* Zonal and meridional winds at 850mb
	*** Zonal wind can be named any of: 'U','u', 'uwnd', U850', 'u850', 'uwnd850'
	*** Meridional wind can be named any of: 'V', 'v', 'vwnd', 'V850', 'v850', 'vwnd850'
	*** Unit: m/s
~~~
~~~
Histogram of zonal wind at 10mb:
	* Zonal wind at 10mb
	*** Variable can be named any of: 'U', 'u', 'uwnd', 'U10', 'u10', 'uwnd10' 
	*** Unit: m/s
~~~
~~~
Stratosphere:
	*
	*** Variable can be named any of:
	*** Unit:
~~~
~~~
Madden-Julian Oscillation (MJO)
	* Zonal winds at 850mb:
	*** Variable can be any of: 'U', 'u','uwnd','U850', 'u850',uwnd850'
	* Zonal winds at 200mb:
	*** Variable can be any of: 'U', 'u','uwnd','U200', 'u200',uwnd200'
	*** Unit: m/s
	* Outgoing Longwave Radiation (OLR):
	*** Variable can be named any of: 'olr', 'ulwf'
	*** Unit can be any of 'w/m^2','w/m**2'
~~~
~~~
Composites of 2-meter temperature over the Northern Hemisphere midlatitudes:
	* 2-meter Temperature:
	*** Variable can be named any of: 't2m', 'T2m', 'temp'
	*** Unit: K
~~~



