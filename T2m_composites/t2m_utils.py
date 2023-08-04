import numpy as np
import matplotlib.pyplot as plt # matplotlib version 3.2 and custom version 3.3
import proplot as plot

def is_ndjfm(month):
    return (month >= 11) | (month <= 3)
import matplotlib.pyplot as plt # matplotlib version 3.2 and custom version 3.3
import proplot as plot

def is_day1(day):
    return (day == 1)
def is_day6(day):
    return (day == 6)
def is_day11(day):
    return (day == 11)
def is_day15(day):
    return (day == 15)
def is_day16(day):
    return (day == 16)
def is_day21(day):
    return (day == 21)
def is_day26(day):
    return (day == 26)

def plotComposites(ds,levels,cmap,lon_0,lat_0,sig_map,fig_name):
    fig=plot.figure(refwidth=4.5)
    ax=fig.subplot(proj='npstere',proj_kw={'lon_0': lon_0})
    ax.contourf(ds,cmap=cmap,colorbar='b', lw=1,ec='none',extend='both',levels=levels)
    ax.contourf(ds.longitude,ds.latitude,sig_map,levels=[0,1],
                colors='None',hatches=['...',''])
    ax.format(coast='True',boundinglat=lat_0,grid=False)
    fig.savefig(fig_name+'.jpg',dpi=300)
    return 

def correlate(obs,model,lat_min,lat_max,lon_min,lon_max):
    x=obs.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min,lon_max))
    y=model.sel(latitude=slice(lat_max,lat_min),longitude=slice(lon_min,lon_max))
    x_stacked=x.stack(grid=('latitude','longitude'))
    y_stacked=y.stack(grid=('latitude','longitude'))
    corr=np.corrcoef(x_stacked,y_stacked)
    
    return corr
