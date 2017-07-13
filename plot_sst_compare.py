from __future__ import division,print_function
import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 200000
import scipy as sp
from folderpath import *
from datatools import *
from gridtools import *
from plottools import *
from projtools import *
import interptools as ipt
import matplotlib.tri as mplt
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
import os as os
import sys
np.set_printoptions(precision=8,suppress=True,threshold=np.nan)
import pandas as pd

# Define names and types of data
name='sjh_hr_v2_noriver'
grid='sjh_hr_v2'
regionname='sfmwhole'
datatype='2d'
starttime=960
endtime=-1


### load the .nc file #####
#data = loadnc(runpath+grid+'/'+name+'/output/',singlename=grid + '_0001.nc')
data = loadnc('/home/mif001/scratch/susan/sjh_hr_v2/runs/sjh_hr_v2_noriver/output/',singlename=grid + '_0001.nc')
data['lon']=data['lon']-360
data['x'],data['y'],data['proj']=lcc(data['lon'],data['lat'])
print('done load')
del data['trigrid']
data = ncdatasort(data)
print('done sort')

region=regions(regionname)
sst=loadnc('data/','A20153352015365.L3m_MO_SST_sst_4km.nc',fvcom=False)


savepath='{}/png/{}_{}/sst_compare/'.format(figpath,grid,datatype)
if not os.path.exists(savepath): os.makedirs(savepath)


XX,YY=np.meshgrid(sst['lon'],sst['lat'])
xx=np.ravel(XX)
yy=np.ravel(YY)

mtemp=data['temp'][960:-1,0,:].mean(axis=0)

pidx=np.argwhere((xx>=region['region'][0])&(xx<=region['region'][1])&(yy>=region['region'][2])&(yy<=region['region'][3]))

print(pidx.shape)
val=sp.interpolate.griddata(np.vstack([data['lon'],data['lat']]).T,mtemp,np.hstack([xx[pidx],yy[pidx]]))


mask=copy.deepcopy(sst['sst'][:].mask)
sstvals=copy.deepcopy(sst['sst'][:])
a=np.ravel(sstvals)
a[pidx[~np.isnan(val)]]=val[~np.isnan(val)]
sstvals=a.reshape(4320,8640)
print('test')
sstvals.mask=mask

f,ax=plt.subplots(1,2,sharex=True,sharey=True,figsize=(8,4))
ax[0].pcolormesh(sst['lon'],sst['lat'],sst['sst'],vmin=7,vmax=12)
plotcoast(ax[0],filename='mid_nwatl6c_sjh_lr.nc',filepath=coastpath, color='k', fcolor='0.75', fill=True)
ax[0].axis(region['region'])
colorax=ax[1].pcolormesh(sst['lon'],sst['lat'],sstvals,vmin=7,vmax=12)
plotcoast(ax[1],filename='mid_nwatl6c_sjh_lr.nc',filepath=coastpath, color='k', fcolor='0.75', fill=True)
ax[1].axis(region['region'])
plt.colorbar(colorax)
f.savefig('{}{}_{}_temp_compare_month_mean.png'.format(savepath,name,regionname),dpi=600)

regionname='bof_nemo'
region=regions(regionname)
ax[0].axis(region['region'])
ax[1].axis(region['region'])
f.savefig('{}{}_{}_temp_compare_month_mean.png'.format(savepath,name,regionname),dpi=600)


regionname='sfmwhole'
region=regions(regionname)
f=plt.figure()
ax=f.add_axes([.1,.125,.775,.8])
colorax=ax.pcolormesh(sst['lon'],sst['lat'],sst['sst']-sstvals,vmin=-3,vmax=3,cmap=mpl.cm.seismic)
plotcoast(ax,filename='mid_nwatl6c_sjh_lr.nc',filepath=coastpath, color='k', fcolor='0.75', fill=True)
ax.axis(region['region'])
plt.colorbar(colorax)
f.savefig('{}{}_{}_temp_compare_month_mean_difference.png'.format(savepath,name,regionname),dpi=600)

regionname='bof_nemo'
region=regions(regionname)
ax.axis(region['region'])
f.savefig('{}{}_{}_temp_compare_month_mean_difference.png'.format(savepath,name,regionname),dpi=600)





