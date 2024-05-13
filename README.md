# MJO-Teleconnections Diagnostics Package

This repository contains the user interface and code to run the diagnostics for evaluating the MJO teleconnections forecasted by a subseasonal to seasonal system. For the background information on diagnostics see: 

Stan, C., C. Zheng, E. K.-M. Chang, D. I. V. Domeisen, C. Garfienkel, A. M. Jenney, H. Kim, Y.-K. Lim, H. Lin, A. Robertson, C. Schwartz, F. Vitart, J. Wang, P. Yadav, 2022: Advances in the prediction of MJO-Teleconnections in the S2S forecast systems. Bulletin of the American Meteorological Society, 103, E11427-E1447. https://doi.org/10.1175/BAMS-D-21-0130.1

Contents:
1. [Software requirements](#introduction)
2. [Obtaining the code](#code)
3. [Data format](#data)

## 1. Software and computational requirements <a name="introduction"></a>
The packages has been developed using Python 3.9.
SLURM (salloc) is enaabled but is not required.

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
The packaage can only data in netcdf format. Most diagnostics work with daily mean of ensemble mean forecast data. Each forecast experiment must be aggregated into one file with the forecast leads as the time dimension. In the exaample below, the forecast initiaal condition is 2018-03-15. 
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
~~~
