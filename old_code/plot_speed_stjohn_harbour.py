from __future__ import division,print_function
import matplotlib as mpl
mpl.use('Agg')
import scipy as sp
from folderpath import *
from datatools import *
from gridtools import *
from plottools import *
from projtools import *
import matplotlib.tri as mplt
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
import os as os
import sys
np.set_printoptions(precision=8,suppress=True,threshold=np.nan)
from matplotlib.collections import LineCollection as LC
from matplotlib.collections import PolyCollection as PC
import multiprocessing
import pymp
import seawater as sw


global name
global grid
global regionname
global region
global tmparray
global savepath
global data
global cmin
global cmax
global vectorflag
global uniformvectorflag
global coastflag
global vidx
global vector_scale



# Define names and types of data
name='sjh_lr_v1_year_wd_gotm-my25_bathy20171109_dt30_calib1_jcool0_15mins'
grid='sjh_lr_v1'
#name='sjh_hr_v3_year_wet_15mins'
#grid='sjh_hr_v3'
datatype='2d'
regionname='stjohn_harbour'
starttime=0
endtime=-1
layer=0
cmin=0
cmax=2

region=regions(regionname)
#region={}
#region['region']=np.array([-66.3,-65.8,45.1,45.28])
#region['regionname']='nemofvcom_inner'

### load the .nc file #####
data = loadnc('/mnt/drive_1/runs/{}/{}/output/'.format(grid,name),singlename=grid + '_0001.nc')
print('done load')

if endtime==-1:
    endtime=len(data['time'])
    print('Plotting {} timesteps'.format(endtime-starttime))

vectorflag=True
coastflag=True
uniformvectorflag=False
vector_spacing=200
vector_scale=250


#region=regions(regionname)
vidx=equal_vectors(data,region,vector_spacing)


savepath='{}timeseries/{}_{}/speed_nemofvcom/{}_{}_{}_{:.3f}_{:.3f}/'.format(figpath,grid,datatype,name,region['regionname'],layer,cmin,cmax)
if not os.path.exists(savepath): os.makedirs(savepath)


def plot_fun(i):
    print(i)
    f=plt.figure(figsize=(25/2.539,15/2.536))
    ax=plt.axes([.13,.11,.8825,.8125])    
    if coastflag:
        plotcoast(ax,filename='mid_nwatl6c_sjh_lr.nc', filepath=coastpath, color='k', fill=True)
    
    speed=np.sqrt(data['u'][i,layer,:]**2+data['v'][i,layer,:]**2)
    triax=ax.tripcolor(data['trigrid'],speed,vmin=cmin,vmax=cmax)

    if vectorflag:
        Q1=ax.quiver(data['uvnodell'][vidx,0],data['uvnodell'][vidx,1],data['u'][i,layer,vidx],data['v'][i,layer,vidx],angles='xy',scale_units='xy',scale=vector_scale,zorder=100,width=.001)    
    if uniformvectorflag:
        norm=np.sqrt(data['u'][i,layer,vidx]**2+data['v'][i,layer,vidx]**2)
        Q1=ax.quiver(data['uvnodell'][vidx,0],data['uvnodell'][vidx,1],np.divide(data['u'][i,layer,vidx],norm),np.divide(data['v'][i,layer,vidx],norm),angles='xy',scale_units='xy',scale=vector_scale,zorder=100,width=.002,color='k')  
    qaxk=ax.quiverkey(Q1,.775,.9,2, r'2 ms$^{-1}$')
    cb=plt.colorbar(triax)
    cb.set_label(r'Speed (ms$^{-1}$)',fontsize=10)    
    ax.set_xlabel(r'Longitude ($^{\circ}$)')
    ax.set_ylabel(r'Latitude ($^{\circ}$)')
    ax.axis(region['region'])
    ax.annotate('{} {}'.format(data['Time'][i][:10],data['Time'][i][11:19]),xy=(.425,.93),xycoords='axes fraction')
    for label in ax.get_xticklabels()[::2]:
        label.set_visible(False)
    f.savefig(savepath + grid + '_' + region['regionname'] +'_speed_nemofvcom_' + ("%04d" %(i)) + '.png',dpi=300)
    plt.close(f)



#pool = multiprocessing.Pool()
#pool.map(speed_plot,range(starttime,endtime))

with pymp.Parallel(24) as p:
    for i in p.range(starttime,endtime):
        plot_fun(i)




























