from __future__ import division
import matplotlib as mpl
import scipy as sp
from datatools import *
from gridtools import *
from plottools import *
import matplotlib.tri as mplt
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
import os as os
import sys
np.set_printoptions(precision=8,suppress=True,threshold=np.nan)


# Define names and types of data
name1='kit4_45days_3'
name2='kit4_kelp_0.05'
grid='kit4'
regionname='gilisland'
datatype='2d'
starttime=384
endtime=450
cmin=-.01
cmax=.01




### load the .nc file #####
data1 = loadnc('/media/moe46/My Passport/kit4_runs/'+name1+'/output/',singlename=grid + '_0001.nc')
data2 = loadnc('/media/moe46/My Passport/kit4_runs/'+name2+'/output/',singlename=grid + '_0001.nc')
print 'done load'
data1 = ncdatasort(data1)
print 'done sort'


region=regions(regionname)

savepath='figures/timeseries/' + grid + '_' + datatype + '/curl_diff/' + name1+ '_'+ name2 + '_' + regionname + '_' +("%f" %cmin) + '_' + ("%f" %cmax) + '/'
if not os.path.exists(savepath): os.makedirs(savepath)
plt.close()




# Plot mesh
for i in range(starttime,endtime):
    print i
    ua=np.hstack([data1['ua'][i,:],0])
    va=np.hstack([data1['va'][i,:],0])
    dudy1= data1['a2u'][0,:]*ua[0:-1]+data1['a2u'][1,:]*ua[data1['nbe'][:,0]]+data1['a2u'][2,:]*ua[data1['nbe'][:,1]]+data1['a2u'][3,:]*ua[data1['nbe'][:,2]];
    dvdx1= data1['a1u'][0,:]*va[0:-1]+data1['a1u'][1,:]*va[data1['nbe'][:,0]]+data1['a1u'][2,:]*va[data1['nbe'][:,1]]+data1['a1u'][3,:]*va[data1['nbe'][:,2]];
    ua=np.hstack([data2['ua'][i,:],0])
    va=np.hstack([data2['va'][i,:],0])
    dudy2= data1['a2u'][0,:]*ua[0:-1]+data1['a2u'][1,:]*ua[data1['nbe'][:,0]]+data1['a2u'][2,:]*ua[data1['nbe'][:,1]]+data1['a2u'][3,:]*ua[data1['nbe'][:,2]];
    dvdx2= data1['a1u'][0,:]*va[0:-1]+data1['a1u'][1,:]*va[data1['nbe'][:,0]]+data1['a1u'][2,:]*va[data1['nbe'][:,1]]+data1['a1u'][3,:]*va[data1['nbe'][:,2]];
    
    #print np.mean(dvdx-dudy)
    #print np.min(dvdx-dudy)
    #print np.max(dvdx-dudy)
    #print np.std(dvdx-dudy)
    f=plt.figure()
    ax=plt.axes([.1,.1,.7,.85])
    triax=ax.tripcolor(data1['trigrid'],(dvdx1-dudy1)-(dvdx2-dudy2),vmin=cmin,vmax=cmax)
    prettyplot_ll(ax,setregion=region,cblabel='Curl',cb=triax)
    f.savefig(savepath + grid + '_' + regionname +'_curl_diff_' + ("%04d" %(i)) + '.png',dpi=600)
    plt.close(f)






























