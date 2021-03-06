from __future__ import division,print_function
import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.tri as mplt
import matplotlib.pyplot as plt
import scipy.io as sio
#from mpl_toolkits.basemap import Basemap
import os as os
import sys
from StringIO import StringIO
from gridtools import *
from datatools import *
from misctools import *
from plottools import *
from regions import makeregions
np.set_printoptions(precision=8,suppress=True,threshold=np.nan)
import h5py as h5
from matplotlib.collections import PolyCollection as PC



# Define names and types of data
name='kit4_kelp_nodrag'
name2='kit4_kelp_20m_drag_0.018'
grid='kit4_kelp'
regionname='kit4_kelp_tight5'
datatype='2d'
lname='kit4_kelp_tight5_6elements_200x200_1000pp_s0'
#averaging length (breaks code if zero). N=1 for original data
#plotend is the number of days?
N=1
plotend=1

### load the .nc file #####
data = loadnc('runs/'+grid+'/' + name +'/output/',singlename=grid + '_0001.nc')
print('done load')
data = ncdatasort(data,trifinder=True)
print('done sort')

savepath='figures/png/' + grid + '_' + datatype + '/lagtracker/particles_inkelp/' + name + '_'+name2+'/'
if not os.path.exists(savepath): os.makedirs(savepath)

data['trigridxy'] = mplt.Triangulation(data['x'], data['y'],data['nv'])
region=regions(regionname)
region=regionll2xy(data,region)
eidx=get_elements(data,region)


if 'savelag1' not in globals():
    print "Loading savelag1"
    fileload=h5.File('savedir/'+name+'/'+lname+'.mat')
    savelag1={}
    for i in fileload['savelag'].keys():
        if (i=='u' or i=='v' or i=='w' or i=='sig' or i=='z'):
            continue
        savelag1[i]=fileload['savelag'][i].value.T

if 'savelag2' not in globals():
    print "Loading savelag2"
    fileload=h5.File('savedir/'+name2+'/'+lname+'.mat')
    savelag2={}
    for i in fileload['savelag'].keys():
        if (i=='u' or i=='v' or i=='w' or i=='sig' or i=='z'):
            continue
        savelag2[i]=fileload['savelag'][i].value.T


cages=loadcage('runs/'+grid+'/' +name2+ '/input/' +grid+ '_cage.dat')


#comment out this line for any kelp not just kelp in the start box
cages=eidx[np.in1d(eidx,cages)]

tmparray=[list(zip(data['nodexy'][data['nv'][i,[0,1,2]],0],data['nodexy'][data['nv'][i,[0,1,2]],1])) for i in cages ]
sidx=np.where((savelag1['x'][:,0]>region['regionxy'][0])&(savelag1['x'][:,0]<region['regionxy'][1])&(savelag1['y'][:,0]>region['regionxy'][2])&(savelag1['y'][:,0]<region['regionxy'][3]))[0]


host=data['trigridxy_finder'].__call__(savelag1['x'][sidx,0],savelag1['y'][sidx,0])

cidx=np.in1d(host,cages)

npts=savelag1['x'].shape[0]
timediff=savelag1['time'][2]-savelag1['time'][1]


expand=0
region['regionxy']=[region['regionxy'][0]-expand,region['regionxy'][1]+expand,region['regionxy'][2]-expand,region['regionxy'][3]+expand]

#computed values for each timestep, changed to check all places and reshape much faster
#numberin1=np.empty((len(savelag1['time']),1))
#numberin2=np.empty((len(savelag1['time']),1))
#for i in range(0,len(savelag1['time'])):
#    print ("%d"%i)+"              "+("%f"%(i/len(savelag1['time'])*100)) 
#    numberin1[i]=np.sum(np.in1d(data['trigridxy'].get_trifinder().__call__(savelag1['x'][sidx,i],savelag1['y'][sidx,i]),cages))
#    numberin2[i]=np.sum(np.in1d(data['trigridxy'].get_trifinder().__call__(savelag2['x'][sidx,i],savelag2['y'][sidx,i]),cages))



#find particles in kelp from region start
numberin1=np.sum(np.in1d(data['trigridxy_finder'].__call__(savelag1['x'][sidx,:],savelag1['y'][sidx,:]),cages).reshape(savelag1['x'][sidx,:].shape),axis=0)/npts
numberin2=np.sum(np.in1d(data['trigridxy_finder'].__call__(savelag2['x'][sidx,:],savelag2['y'][sidx,:]),cages).reshape(savelag2['x'][sidx,:].shape),axis=0)/npts

f, (ax1,ax2) = plt.subplots(2, sharex=True, sharey=True)

ax1.plot((savelag1['time']-savelag1['time'].min())/3600,numberin1,'k',label='No drag')
ax1.plot((savelag2['time']-savelag2['time'].min())/3600,numberin2,'r',label='Drag')
ax1.set_xlim([plotend*24*-.1,plotend*24])

handles, labels = ax1.get_legend_handles_labels()
legend=ax1.legend(handles, labels)

ax1.set_ylabel(r'Proportion of particles in kelp',fontsize=8)


for label in (ax1.get_xticklabels() + ax1.get_yticklabels()):
    label.set_fontsize(8)


numberin1=np.convolve(numberin1,np.ones((N,))/N,mode='same')
numberin2=np.convolve(numberin2,np.ones((N,))/N,mode='same')

numberin1[0:np.ceil(N/2)]=np.nan
numberin2[0:np.ceil(N/2)]=np.nan

ax2.plot((savelag1['time']-savelag1['time'].min())/3600,numberin1,'k',label='No drag')
ax2.plot((savelag2['time']-savelag2['time'].min())/3600,numberin2,'r',label='Drag')
#ax2.set_xlim([-10,ax2.get_xlim()[1]])

handles, labels = ax2.get_legend_handles_labels()
legend=ax2.legend(handles, labels)

ax2.set_ylabel(r'Proportion of particles in kelp',fontsize=8)
ax2.set_xlabel(r'Time (hour)',fontsize=8)

for label in (ax2.get_xticklabels() + ax2.get_yticklabels()):
    label.set_fontsize(8)




f.savefig(savepath +''+name+'_'+name2+'_'+regionname+'_'+lname+'_compare_particles_inkelp_regionstart.png',dpi=150)
plt.close(f)











