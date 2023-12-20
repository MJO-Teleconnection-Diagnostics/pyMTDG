Instruction for input files:
The input files (from the interface) should be in the xxx*yyy format (e.g. /data/UFS5/UFS_u_*.nc). The "*" part can only contain the reforecast initialization time (either in yyyymmddhh format or yyyymmdd format, e.g. /data/UFS5/UFS_u_2011040100.nc or /data/UFS5/UFS_u_20110401.nc)
Both yyyymmddhh format and yyymmdd format are supported. 
The variable name of u850, v850, and z500 in the netcdf file needs to be "u" , "v" , "z" respectively.

For UFS:
In the interface:
Number of ensembles = 1
Number of initial dates = 1
Use ERA_I for validation = True (default)
Are the model data daily-mean values?, Forecast time step interval = select according to your data files
Does the model data include the initial conditions = Yes (default)
Compute RMM index = No (default)

Other options in the interface do not matter for the code.

Please note to make the code running, 6-hourly ERA-I files are required (u850, v850 and z500). No daily-mean ERA-I data needed. If model input is daily mean, the code will automatically calculate the daily means from 6-hourly ERA-I for the analysis.