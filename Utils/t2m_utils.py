import numpy as np
import matplotlib.pyplot as plt # matplotlib version 3.2 and custom version 3.3
import proplot as plot
import os
            

def plotComposites(ds,ds_names,levels,cmap,lon_0,lat_0,sig_map,rcorr,week,phase,fig_name):
    with plot.rc.context(fontsize='20px'):
        fig=plot.figure(refwidth=6.5)
        axes=fig.subplots(nrows=1,ncols=2,proj='npstere',proj_kw={'lon_0': lon_0})
        for p,ax in enumerate(axes):
            h=ax.contourf(ds[p],cmap=cmap,lw=1,ec='none',extend='both',levels=levels)
            ax.contourf(ds[p].longitude,ds[p].latitude,sig_map[p],levels=[0,1],
                    colors='None',hatches=['...',''])
            if (p==0):
                ax.format(title=ds_names[p])
            else:
                ax.format(title=ds_names[p],rtitle='{:.2f}'.format(rcorr))
    
            ax.format(coast='True',boundinglat=lat_0,grid=False,suptitle=week+' after MJO '+phase)
    
        fig.colorbar(h, loc='b', extend='both', label='T2m anomaly',
                      width='2em', extendsize='3em', shrink=0.8,
                    )
    if not os.path.exists('../output/T2m/'+ds_names[1]): 
        os.mkdir('../output/T2m/'+ds_names[1])
    fig.savefig('../output/T2m/'+ds_names[1]+'/'+fig_name+'.jpg',dpi=300)
    return 

def correlate(obs,model,lat_min,lat_max,lon_min,lon_max):
    x=obs.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min,lon_max))
    y=model.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min,lon_max))
    x_stacked=x.stack(grid=('latitude','longitude'))
    y_stacked=y.stack(grid=('latitude','longitude'))
    corr=np.corrcoef(x_stacked,y_stacked)
    
    return corr

def get_variable_from_dataset(ds):
    '''
        Extract the target variable from the dataset. Convert to target units
        
            Parameters
                ds: xarray dataset
            Returns
                da: subsetted dataArray in
    '''
    for name in ['t2m', 'T2m','T','temp']:
        if name in list(ds.keys()):
            break
    da = ds[name]
        
    
    return da
    raise RuntimeError("Couldn't find a 2-meter temperature variable name")
