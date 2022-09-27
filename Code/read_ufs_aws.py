import fsspec
import s3fs
import xarray as xr
import numpy as np
import datetime
from datetime import timedelta

# Each experiment consists of 141 forecast leads. f000 corresponds to analysis.

steps = ['000','006','012','018','024','030','036','042',
         '048','054','060','066','072','078','084','090',
         '096','102','108','114','120','126','132','138',
         '144','150','156','162','168','174','180','186',
         '192','198','204','210','216','222','228','234',
         '240','246','252','258','264','270','276','282',
         '288','294','300','306','312','318','324','330',
         '336','342','348','354','360','366','372','378',
         '384','390','396','402','408','414','420','426',
         '432','438','444','450','456','462','468','474',
         '480','486','492','498','504','510','516','522',
         '528','534','540','546','552','558','564','570',
         '576','582','588','594','600','606','612','618',
         '624','630','636','642','648','654','660','666',
         '672','678','684','690','696','702','708','714',
         '720','726','732','738','744','750','756','762',
         '768','774','780','786','792','798','804','810',
         '816','822','828','834','840']

# Time stamp of the forecast. yyyymm01 coresponds to 1st of the month IC,
# yyyymm15 corresponds to 15th of the month IC.

yyyymmdd = '20140601'

# Get coordinates info

of = fsspec.open_local("filecache::https://noaa-ufs-prototypes-pds.s3.amazonaws.com/Prototype7/"+yyyymmdd+"/pgrb2/gfs."+yyyymmdd+"/00/atmos/gfs.t00z.pgrb2.0p25.f006",
                           s3={'anon': True}, filecache={'cache_storage':'/scratch/stan/ufs/'})     

ds_sf0 = xr.open_dataset(of, engine='cfgrib',
                         backend_kwargs={'filter_by_keys':{'cfVarName': 'gh','typeOfLevel':'isobaricInhPa'}})

latitude = ds_sf0.latitude
longitude = ds_sf0.longitude
strt_time=datetime.datetime(int(yyyymmdd[0:4]),int(yyyymmdd[4:6]),int(yyyymmdd[6:8]),0,0,0)
time=[strt_time+datetime.timedelta(hours=int(steps[i])) for i in range(len(steps)-1)]

# Define xarray to store all forecast leads. This case is for 500hPa geopotential height (gh)

gh500 = xr.DataArray(
    np.ndarray([len(steps)-1,len(latitude),len(longitude)]),
    coords={'latitude':latitude,'longitude':longitude,'time':time},
    dims=['time','latitude','longitude']
)
gh500.attrs['units'] = 'gpm'
gh500.attrs['name'] = '500hPa geopotential height'

# Read all forecast leads and store them into the xarray defined at previous step. Forecast lead f000 will be neglected.
# Note: Precipitation is defiined as 6h accoumulation, thus f000 is undefined.

i = 0
for istep in steps[1:]:
    
    of = fsspec.open_local("filecache::https://noaa-ufs-prototypes-pds.s3.amazonaws.com/Prototype7/"+yyyymmdd+"/pgrb2/gfs."+yyyymmdd+"/00/atmos/gfs.t00z.pgrb2.0p25.f"+istep,
                           s3={'anon': True}, filecache={'cache_storage':'/scratch/stan/ufs/'})     
    ds_iso = xr.open_dataset(of, engine='cfgrib',
                     backend_kwargs={'filter_by_keys':{'typeOfLevel':'isobaricInhPa','name':'Geopotential Height','level':500}})
    gh500[i,:,:] = ds_iso.gh
    
    i = i+1

# Compute daily means

z500 = gh500.resample(time='D').mean(dim='time')
z500.attrs['units'] = 'gpm'
z500.attrs['name'] = '500hPa geopotential height'
time_daily_mean = z500['time']

# Write out in netcdf format using single precision. If multiple varaibles are to be writen out,
# repeat this step for the other variables and then concatenate then over
# time as shown in the comment line, and modify the encoding line accordingly.

ds_out = xr.DataArray(
    z500.rename('z500'),
    coords={'latitude':latitude,'longitude':longitude,'time':time_daily_mean},
    dims=['time','latitude','longitude']
)

#ds_out = xr.concat([ds1_out['var1'], ds2_out['var2']], dim="time")

encoding = {'latitude': {'dtype':'float32','_FillValue': None},
            'longitude': {'dtype':'float32','_FillValue': None},
            'time': {'dtype':'int32'},
            'z500':{'dtype':'float32'}
            }

ds_out.to_netcdf("/scratch/stan/ufs/z500_"+yyyymmdd+".nc", encoding=encoding)

# Note: The code creates some files in the directory specified in "filecache".
# Delete these files after you process the "yyyymmdd" forecast case. 
