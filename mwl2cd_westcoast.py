from __future__ import division,print_function
import matplotlib as mpl
import scipy as sp
from datatools import *
from gridtools import *
from plottools import *
from projtools import *
from misctools import *
import interptools as ipt
import matplotlib.tri as mplt
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
import os as os
import sys
np.set_printoptions(precision=8,suppress=True,threshold=np.nan)
import time
from matplotlib.collections import LineCollection as LC
from matplotlib.collections import PolyCollection as PC
import matplotlib.path as path
import netCDF4 as n4

# Define names and types of data
name='2012-02-01_2012-03-01_0.01_0.001'
grid='vh_high'
datatype='2d'
outputpath='data/enav/westcoast/'+grid+'_'+name+'_cd.nc'



### load the .nc file #####
data = loadnc('runs/'+grid+'/'+name+'/output/',singlename=grid + '_0001.nc')
print('done load')
data = ncdatasort(data)
print('done sort')


path2cdmwl='data/enav/westcoast/data/cd2mwl/'

cdmwl={}
cdmwl['nv']=np.loadtxt(path2cdmwl+'CANWEST_BG.ele').astype(int)-1
tmp=np.loadtxt(path2cdmwl+'CANWEST_BG_ll.nod')[:,1:]
cdmwl['nodell']=np.fliplr(tmp)
cdmwl['hwarp']=np.loadtxt(path2cdmwl+'PAC_MWL_CD.txt')[:,2:].flatten()

cdmwl['lon']=cdmwl['nodell'][:,0].flatten()
cdmwl['lat']=cdmwl['nodell'][:,1].flatten()
cdmwl['x'],cdmwl['y'],cdmwl['proj']=lcc(cdmwl['lon'],cdmwl['lat'])
cdmwl['trigrid'] = mplt.Triangulation(cdmwl['lon'], cdmwl['lat'],cdmwl['nv'])
cdmwl['trigridxy'] = mplt.Triangulation(cdmwl['x'], cdmwl['y'],cdmwl['nv'])  

region={}
region['region']=np.array([np.min(data['lon']),np.max(data['lon']),np.min(data['lat']),np.max(data['lat'])])


cdmwlr=regioner(cdmwl,region)

#find m2 period closest to m2
#m2range=12.42*np.arange(0,1000000)
#hours=24*(data['time'][-1]-data['time'][0])
#idx=np.argmin(np.fabs(m2range-hours))
#finish this later

#just use whole timeseries for this case
meanel=np.mean(data['zeta'],axis=0)

print('here')
nidx=cdmwlr['nidx_sub']
cdmwlr['trigridxy_sub'] = mplt.Triangulation(cdmwlr['x'][nidx], cdmwlr['y'][nidx],cdmwlr['nv_sub'])
lininterp=mplt.LinearTriInterpolator(cdmwlr['trigridxy_sub'],cdmwlr['hwarp'][nidx])
print('done')

#convert grid longlat to cdmwl xy
x,y=cdmwl['proj'](data['lon'],data['lat'])

cd2mwl=lininterp(x,y)
cdnomask=copy.deepcopy(cd2mwl)
#set points outside the domain to zero
#maybe handle this different?
cdnomask[cd2mwl.mask]=0

os.system('rm ' + outputpath)
os.system('cp ' + 'runs/'+grid+'/'+name+'/output/' +grid + '_0001.nc ' + outputpath)
ncid=n4.Dataset(outputpath,'r+',format='NETCDF3_64BIT')
#remove the dymanic topo.
tmp=data['zeta']-meanel
#add cd2mwl to reference to cd
tmp=tmp+cdnomask
ncid.variables['zeta'][:]=tmp
ncid.close()




#old plots for wrong thing.
#f=plt.figure()
#ax=f.add_axes([.125,.1,.775,.8])
#triax=ax.tripcolor(data['trigrid'],data['h'],vmin=-10,vmax=30)
#cb=plt.colorbar(triax)
#cb.set_label('h (m)')
#f.show()

f=plt.figure()
ax=f.add_axes([.125,.1,.775,.8])
triax=ax.tripcolor(data['trigrid'],meanel)
cb=plt.colorbar(triax)
cb.set_label('meanel (m)')
f.show()

f=plt.figure()
ax=f.add_axes([.125,.1,.775,.8])
triax=ax.tripcolor(data['trigrid'],maxel-minel)
cb=plt.colorbar(triax)
cb.set_label('tidal range (m)')
f.show()

f=plt.figure()
ax=f.add_axes([.125,.1,.775,.8])
triax=ax.tripcolor(data['trigrid'],testel)
cb=plt.colorbar(triax)
cb.set_label('meanel-shallow_bathy (m)')
f.show()

#f=plt.figure()
#ax=f.add_axes([.125,.1,.775,.8])
#triax=ax.tripcolor(data['trigrid'],cdnomask)
#cb=plt.colorbar(triax)
#cb.set_label('cdnomask (m)')
#f.show()

#f=plt.figure()
#ax=f.add_axes([.125,.1,.775,.8])
#triax=ax.tripcolor(data['trigrid'],data['h']-meanel-cdnomask,vmin=-10,vmax=30)
#cb=plt.colorbar(triax)
#cb.set_label('all (m)')
#f.show()




