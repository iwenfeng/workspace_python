from __future__ import division
import matplotlib as mpl
import scipy as sp
from datatools import *
from gridtools import *
import matplotlib.tri as mplt
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
import os as os
import sys
from numba import jit
np.set_printoptions(precision=8,suppress=True,threshold=np.nan)


# Define names and types of data
name='kit4_45days_3'
grid='kit4'
datatype='2d'
starttime=384
interpheight=1

### load the .nc file #####
data = loadnc('/media/moflaher/My Book/kit4_runs/' + name + '/output/',singlename=grid + '_0001.nc')
print 'done load'
data = ncdatasort(data)
print 'done sort'


def interzeta(rlhzero,interpheight,i):
        tidx=(np.where(rlhzero[i,:]<interpheight)[0]).min()
        weightdiff=rlhzero[i,tidx-1]-rlhzero[i,tidx]
        uweight=1-((rlhzero[i,tidx-1]-interpheight)/weightdiff)
        lweight=1-((interpheight-rlhzero[i,tidx])/weightdiff)    
        if (tidx==20):  
            tu=(data['u'][starttime:,tidx-1,i]*uweight)
            tv=(data['v'][starttime:,tidx-1,i]*uweight)
        else:
            tu=((data['u'][starttime:,tidx-1,i]*uweight)+(data['u'][starttime:,tidx,i]*lweight))
            tv=((data['v'][starttime:,tidx-1,i]*uweight)+(data['v'][starttime:,tidx,i]*lweight))
        
        
        return tu,tv






levelheight=data['uvh']*data['siglay'][:,0]
levelheight=-1*levelheight
rlh=data['uvh']-levelheight
rlhzero=np.hstack((rlh,np.zeros((data['nele'],1))))



base_dir = os.path.dirname(__file__)
filename='_' + grid + '_' +name+ '_' + ("%d" %interpheight) + 'm.npy'
if (os.path.exists(os.path.join(base_dir,'data', 'u' + filename)) & os.path.exists(os.path.join(base_dir,'data', 'v' + filename))):
    print 'Loading old interpolated data'
    newu=np.load(os.path.join(base_dir,'data', 'u' + filename))
    newv=np.load(os.path.join(base_dir,'data', 'v' + filename))
else:
    print 'Creating new interpolated data'
    newu=np.zeros((len(data['time'][starttime:]),data['nele']))
    newv=np.zeros((len(data['time'][starttime:]),data['nele']))
    for i in range(0,data['nele']):
        print i
        newu[:,i],newv[:,i]=interzeta(rlhzero,interpheight,i)
    np.save(os.path.join(base_dir,'data', 'u' + filename))
    np.save(os.path.join(base_dir,'data', 'v' + filename))

