# MJO-Teleconnection Diagnostics Package

This repository contains the user interface and code to run the diagnostics for evaluating the MJO teleconnections forecasted by a subseasonal to seasonal system. For the background information on diagnostics see: 

Stan, C., C. Zheng, E. K.-M. Chang, D. I. V. Domeisen, C. Garfienkel, A. M. Jenney, H. Kim, Y.-K. Lim, H. Lin, A. Robertson, C. Schwartz, F. Vitart, J. Wang, P. Yadav, 2022: Advances in the prediction of MJO-Teleconnections in the S2S forecast systems. Bulletin of the American Meteorological Society, 103, E11427-E1447. [https://doi.org/10.1175/BAMS-D-21-0130.1](https://doi.org/10.1175/BAMS-D-21-0130.1)

Zheng, C., D. I. V. Domeisen, C. I. Garfinkel, A. M. Jenney, H. Kim, J. Wang, Z. Wu, C. Stan, 2024: The impact of vertical model levels on the prediction of MJO teleconnections: Part I—The tropospheric pathways in the UFS global coupled model. Climate Dynamics, 62, 9031-9056. [https://doi.org/10.1007/s00382-024-07377-x](https://doi.org/10.1007/s00382-024-07377-x)

Garfinkel, C. I., Z. Wu, P. Yadav, Z. Lawrence, D. I. V. Domeisen, C. Zheng, J. Wang, A. M. Jenney, H. Kim, C. Schwartz, C. Stan, 2025: The impact of vertical model levels on the prediction of MJO teleconnections. Part II: The stratospheric pathway in the UFS global coupled model, Climate Dynamics, 63. [https://doi.org/10.1007/s00382-024-07512-8](https://doi.org/10.1007/s00382-024-07512-8)

Wang, J. D. I. V. Domeisen, C. I. Garfinkel, A. M. Jenney, H. Kim, Z. Wu, C. Zheng, C. Stan, 2025: Prediction of MJO teleconnections in the UFS global fully coupled model. [https://doi.org/10.21203/rs.3.rs-4903941/v1](https://doi.org/10.21203/rs.3.rs-4903941/v1)

Stan, C., S. Kollapaneni, C. I. Garfinkel, A. M. Jenney, H. Kim, J. Wang, Z. Wu, C. Zheng, and A. Singh, 2025: A Python diagnostics package for evaluation of MJO-Teleconnections in S2S forecast systems. Geophysical Model Development. (submitted)


Contents:
1. [Software requirements](#introduction)
2. [Obtaining the code](#code)
3. [Data format](#data)
4. [Variables](#vars)
5. [Examples](#output)

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

  a.1 Clone the repository (main and all other branches):
  
~~~
git clone https://github.com/MJO-Teleconnection-Diagnostics/pyMTDG.git MJO-Teleconnections
~~~

Check what you just cloned (by default you will have only the _main_ branch):

~~~
cd MJO-Teleconnections
git branch
* main
~~~

To see all branches:

~~~
git branch -a
~~~

a.2 Clone the repository and fetch only a single branch


~~~
git clone --branch branc_name --single-branch  https://github.com/MJO-Teleconnection-Diagnostics/pyMTDG.git MJO-Teleconnections
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
~~~
Example: Display help text for the driver, which shows the necessary flags/options
~~~
python mjo_telecon_main.py -h
~~~
Example: Run WITH the graphical interface
~~~
python mjo_telecon_main.py -g yes
~~~
Example: Run WITHOUT the graphical interface. The user will be prompted to select specific diagnostics to run using comma-separated integers. Text will appear indicating which number corresponds to which diagnostic. The input configuration file needed to run the package without the graphical interfact specifies various user options as well as the paths to the forecast and verification data for each diagnostic. It should be formatted the same as the one that is generated automatically and saved to the driver folder when using the graphical interface. An example file has been included in the driver folder. 
~~~
python mjo_telecon_main.py -g no -c config.yml
~~~

## 3. Data format <a name="data"></a>
The package can only read data in the netcdf format using the [CF Metadata Conventions](https://cfconventions.org/cf-conventions/cf-conventions.html#time-axis-ex).

### 3.1 Forecast <a name="data"></a>
Most diagnostics work with daily mean and ensemble mean forecast data. Each forecast experiment must be aggregated into one file with the forecast leads (days) as the record dimension. In the example below, the forecast initial condition is 2018-03-15. 
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

### 3.2 Observations <a name="data"></a>
The package includes ERA-Interim fields for validation. The ERA-Interim data can be downloaded from [here](https://drive.google.com/drive/folders/1wT51DRQhbXPAzVwvCWIkcojvWnCp7tgm?usp=share_link). The data is provided on the native grid (`latitudes=256, longitudes=512`), and the package will interpolate the forecast data to the ERA-Interim grid. For precipitation, [Integrated Multi-satellitE Retrivers for GPM](https://gpm.nasa.gov/data/imerg), IMERG, is the default validation dataset. IMERG covers 2000-2023 and is interpolated to (`latitudes=241`,`longitudes=480`). The package will interpolate the forecast data to the IMERG grid.

The package also works with user specified validation data. These data must be on the same grid as the forecast data.

The RMM Index can also be specified. The file must contain the time series of:
- [x] **RMM Index amplitude** [var_name(dimension): amplitude(time)]
- [x] **MJO phase** [var_name(dimension): phase(time)]	

For the MJO diagnostic, the first two EOF patterns of OLR, zonal wind at 850 and 200 hPa along with their normalization factors must be specified in a file called 'ceof.nc' placed in the directory MJO-Teleconnections/MJO/. The structure of the 'ceof.nc' must be the same as the file included in the package and shown below. The number of EOF modes (mode) can be limited to the first two only. 
~~~
netcdf ceof {
dimensions:
        mode = 25 ;
        longitude = 144 ;
variables:
        int mode(mode) ;
                mode:long_name = "number of EOFs" ;
        float longitude(longitude) ;
                longitude:units = "degrees_east" ;
        float olr(mode, longitude) ;
        float u850(mode, longitude) ;
        float u200(mode, longitude) ;
        double norm_olr ;
                norm_olr:_FillValue = NaN ;
                norm_olr:long_name = "normalization factor for OLR" ;
        double norm_u850 ;
                norm_u850:_FillValue = NaN ;
                norm_u850:long_name = "normalization factor for U850" ;
        double norm_u200 ;
                norm_u200:_FillValue = NaN ;
                norm_u200:long_name = "normalization factor for U200" ;
data:

 mode = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 
    20, 21, 22, 23, 24 ;

 longitude = 0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30, 
    32.5, 35, 37.5, 40, 42.5, 45, 47.5, 50, 52.5, 55, 57.5, 60, 62.5, 65, 
    67.5, 70, 72.5, 75, 77.5, 80, 82.5, 85, 87.5, 90, 92.5, 95, 97.5, 100, 
    102.5, 105, 107.5, 110, 112.5, 115, 117.5, 120, 122.5, 125, 127.5, 130, 
    132.5, 135, 137.5, 140, 142.5, 145, 147.5, 150, 152.5, 155, 157.5, 160, 
    162.5, 165, 167.5, 170, 172.5, 175, 177.5, 180, 182.5, 185, 187.5, 190, 
    192.5, 195, 197.5, 200, 202.5, 205, 207.5, 210, 212.5, 215, 217.5, 220, 
    222.5, 225, 227.5, 230, 232.5, 235, 237.5, 240, 242.5, 245, 247.5, 250, 
    252.5, 255, 257.5, 260, 262.5, 265, 267.5, 270, 272.5, 275, 277.5, 280, 
    282.5, 285, 287.5, 290, 292.5, 295, 297.5, 300, 302.5, 305, 307.5, 310, 
    312.5, 315, 317.5, 320, 322.5, 325, 327.5, 330, 332.5, 335, 337.5, 340, 
    342.5, 345, 347.5, 350, 352.5, 355, 357.5 ;
}
~~~

The OLR data is the [NOAA Interpolated Outgoing Longwave Radiation](https://psl.noaa.gov/data/gridded/data.olrcdr.interp.html). The zonal wind at 850 and 200 hPa are from ERAI and interpolated to (`latitudes=72`,`longitudes=144`). The package will interpolate forecast data to this grid.

Note: Regridding is done using spherical harmonic decomposition, a computational intensive method. Diagnostics involving interpolation of multiple fields take longer time than diagnostics applied to one field. Providing the data on the same grid as verification data can reduce the computation time.  

## 4. Variables <a name="vars"></a>
The list of diagnostics and required meteorological fields:
~~~
STRIPES Index for Geopotential:
	* Geopotential height at 500 hPa
 	*** Variable can be named any of: 'z', 'Z', 'gh', 'z500'
	*** Unit: meters OR conversion to geopotential height will occur for any of the following:'m**2 s**-2', 'm^2/s^2', 'm2/s2','m2s-2', 'm2 s-2'	
~~~
~~~
STRIPES Index for precipitation:
	* Precipitation rate:
	*** Variable can be named any of: 'prate', 'precipitationCal','precipitation','precip'
	*** Unit: mm/day OR conversion to mm/day will occur for any of the following: 'kg m**-2 s**-1','kg/m2/s','kg m-2 s-1','mm/s','mm s**-1', 'mm s-1'
~~~
~~~
Pattern Correlation and Relative Amplitude of the MJO teleconnections over the PNA region:
	* Geopotential height at 500 hPa
 	*** Variable can be named any of: 'z', 'Z', 'gh', 'z500'
	*** Unit: meters OR conversion to geopotential height will occur for any of the following:'m**2 s**-2', 'm^2/s^2', 'm2/s2','m2s-2', 'm2 s-2'
~~~
~~~
Pattern Correlation and Relative Amplitude of the MJO teleconnections over the Atlantic region:
	* Geopotential at 500 hPa
 	*** Variable can be named any of: 'z', 'Z', 'gh', 'z500'
	*** Unit: Unit: meters OR conversion to geopotential height will occur for any of the following:'m**2 s**-2', 'm^2/s^2', 'm2/s2','m2s-2', 'm2 s-2'
~~~
~~~
Extra-tropical Cyclone Activity:
	* Geopotential at 500 hPa
 	*** Variable can be named any of: 'z', 'Z', 'gh', 'z500'
	*** Unit can be any of:'m**2 s**-2', 'm^2/s^2', 'm2/s2','m2s-2', 'm2 s-2'
	* Zonal and meridional winds at 850 hPa
	*** Zonal wind can be named any of: 'U','u', 'uwnd', U850', 'u850', 'uwnd850'
	*** Meridional wind can be named any of: 'V', 'v', 'vwnd', 'V850', 'v850', 'vwnd850'
	*** Unit: m/s
~~~
~~~
Histogram of zonal wind at 10 hPa:
	* Zonal wind at 10 hPa
	*** Variable can be named any of: 'U', 'u', 'uwnd', 'U10', 'u10', 'uwnd10' 
	*** Unit: m/s
~~~
~~~
Stratosphere:
	* Meridional wind at 500 hPa
	*** Variable can be named any of: 'V', 'v', 'v500','vwnd'
	*** Unit: m/s
	* Air temperature at 500 hPa
	*** Variable can be named any of: 'T','t','temp','t500'
	*** Unit: K
	* Geopotential height at 100 hPa
	*** Variable can be named any of: 'z', 'Z', 'gh', 'z500'
        * Unit: meters OR conversion to geopotential height will occur for any of the following:'m**2 s**-2', 'm^2/s^2', 'm2/s2','m2s-2', 'm2 s-2'
~~~
~~~
Madden-Julian Oscillation (MJO)
	* Zonal wind at 850mb:
	*** Variable can be any of: 'U', 'u','uwnd','U850', 'u850',uwnd850'
	* Zonal wind at 200mb:
	*** Variable can be any of: 'U', 'u','uwnd','U200', 'u200',uwnd200'
	*** Unit: m/s
	* Outgoing Longwave Radiation (OLR):
	*** Variable can be named any of: 'olr', 'ulwf'
	*** Unit can be any of 'w/m^2','w/m**2'
~~~
~~~
Composites of 2-meter temperature over the Northern Hemisphere midlatitudes:
	* 2-meter temperature:
	*** Variable can be named any of: 't2m', 'T2m', 'temp'
	*** Unit: K
~~~
## 4. Examples <a name="output"></a>
The package provides a set of figures and data files in the directory `output/`. They can be visualized from the graphical interface by selecting `View results from previous calculation` and `UFS5` when prompted for the model name. 

