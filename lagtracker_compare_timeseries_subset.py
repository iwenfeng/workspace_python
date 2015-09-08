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
from projtools import *
from regions import makeregions
np.set_printoptions(precision=8,suppress=True,threshold=np.nan)
import h5py as h5
from matplotlib.collections import PolyCollection as PC
import time



# Define names and types of data
name='kit4_kelp_nodrag'
name2='kit4_kelp_20m_drag_0.018'
grid='kit4_kelp'
regionname='kit4_kelp_tight5'
datatype='2d'



### load the .nc file #####
data = loadnc('runs/'+grid+'/' + name +'/output/',singlename=grid + '_0001.nc')
print('done load')
data = ncdatasort(data)
print('done sort')



cages=loadcage('runs/'+grid+'/' +name2+ '/input/' +grid+ '_cage.dat')
if np.shape(cages)!=():
    tmparray=[list(zip(data['nodexy'][data['nv'][i,[0,1,2]],0],data['nodexy'][data['nv'][i,[0,1,2]],1])) for i in cages ]
    color='g'
    lw=.1
    ls='solid'



region=regions(regionname)
region=expand_region(region,[0,0],[-4500,0])
region=regionll2xy(data,region)









for i in range(5,6,1):
    lname='kit4_kelp_tight5_1elements_250x150_1000pp_s' + ("%d"%i)


    savepath='figures/timeseries/' + grid + '_' + datatype + '/lagtracker/subset/' + name + '_'+name2+'/'+regionname+'/' +lname +'/'
    if not os.path.exists(savepath): os.makedirs(savepath)


    print "Loading savelag1"
    fileload=h5.File('savedir/'+name+'/'+lname+'.mat')
    savelag1={}
    for i in fileload['savelag'].keys():
        if (i=='x' or i=='y' or i=='time'):
            savelag1[i]=fileload['savelag'][i].value.T

    print "Loading savelag2"
    fileload=h5.File('savedir/'+name2+'/'+lname+'.mat')
    savelag2={}
    for i in fileload['savelag'].keys():
        if (i=='x' or i=='y'):
            savelag2[i]=fileload['savelag'][i].value.T





    subset=1000

    for sub in range(int(savelag1['x'].shape[0]/subset)):


        #for i in range(0,len(savelag1['time']),4):
        for i in range(0,3700,2):
            print ("%d"%i)+"              "+("%f"%(i/len(savelag1['time'])*100)) 
            f = plt.figure()
            ax=f.add_axes([.125,.1,.775,.8])


            #plotcoast(ax,filename='pacific.nc',color='k')
            #ax.triplot(data['trigridxy'],lw=.25,zorder=1)
            ax.axis(region['regionxy'])
            lseg1=PC(tmparray,facecolor = 'g',edgecolor='None')
            ax.add_collection(lseg1)
            ax.scatter(savelag1['x'][(subset*sub):(subset*(sub+1)),i],savelag1['y'][(subset*sub):(subset*(sub+1)),i],color='b',label='No drag',s=.25,zorder=10)
            ax.scatter(savelag2['x'][(subset*sub):(subset*(sub+1)),i],savelag2['y'][(subset*sub):(subset*(sub+1)),i],color='r',label='Drag',s=.25,zorder=15)

            handles, labels = ax.get_legend_handles_labels()
            handles[0:2]=[handles[0],handles[-1]]
            labels[0:2]=[labels[0],labels[-1]]
            legend=ax.legend(handles[0:2], labels[0:2],prop={'size':10},loc=4,numpoints=1)
            legend.set_zorder(25)

            tstr=time.strftime("%d-%H:%M", time.gmtime(savelag1['time'][i]-savelag1['time'][0]))
            ax.annotate(("Time: %s"%tstr),xy=(.025,.95),xycoords='axes fraction',bbox={'facecolor':'white','edgecolor':'None', 'alpha':1, 'pad':3})

            f.savefig(savepath +''+name+'_'+name2+'_'+regionname+'_'+lname+'_timestep_'+("%05d"%i)+'.png',dpi=150)
            plt.close(f)



















