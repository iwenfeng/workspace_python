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

# Define names and types of data
name='kit4_kelp_nodrag'
name2='kit4_kelp_20m_drag_0.018'
#name='kit4_45days_3'
grid='kit4_kelp'
datatype='2d'
regionname='kit4_kelp_tight5'

starttime=384


### load the .nc file #####
data = loadnc('runs/'+grid+'/'+name+'/output/',singlename=grid + '_0001.nc')
print('done load')
data = ncdatasort(data)
print('done sort')

cages=loadcage('runs/'+grid+'/' +name2+ '/input/' +grid+ '_cage.dat')
if np.shape(cages)!=():
    tmparray=[list(zip(data['nodexy'][data['nv'][i,[0,1,2]],0],data['nodexy'][data['nv'][i,[0,1,2]],1])) for i in cages ]
    color='g'
    lw=.1
    ls='solid'






savepath='figures/png/' + grid + '_' + datatype + '/lagtracker/movement_compare_subset_withvectors/'
if not os.path.exists(savepath): os.makedirs(savepath)


for i in range(0,22,1):
    lname='kit4_kelp_tight5_1elements_250x150_1000pp_s' + ("%d"%i)




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





    cols=3
    rows=3

    nos=rows*cols
    timestep=(savelag1['time'][1]-savelag1['time'][0]).astype(int)
    num_hours=2
    subtimes=np.linspace(0,num_hours*timestep*(nos),nos+1)

    x=savelag1['x'][:,:subtimes[-1]]
    y=savelag1['x'][:,:subtimes[-1]]


    region=regions(regionname)
    region=expand_region(region,[-2000,-2000],[-4500,0])
    region=regionll2xy(data,region)


    eidx=equal_vectors(data,region,500)
    scale1=.001
    subset=1000





    for sub in range(int(savelag1['x'].shape[0]/subset)):
        print "Subset " +("%d"%sub)
        print
        f, ax = plt.subplots(nrows=rows,ncols=cols, sharex=True, sharey=True)
        ax=ax.flatten()

        for i in range(0,len(ax)):
            print i
            #ax[i].triplot(data['trigridxy'],lw=.05)
            tidx=np.argwhere((np.arange(len(data['time']))>=(num_hours*(i)+starttime)) &(np.arange(len(data['time']))<(num_hours*(i+1)+starttime)))
            Q1=ax[i].quiver(data['uvnode'][eidx,0],data['uvnode'][eidx,1],data['ua'][tidx,eidx].mean(axis=0),data['va'][tidx,eidx].mean(axis=0),angles='xy',scale_units='xy',scale=scale1,zorder=10)
            lseg1=PC(tmparray,facecolor = 'g',edgecolor='None')
            ax[i].add_collection(lseg1)
            ax[i].scatter(savelag1['x'][(subset*sub):(subset*(sub+1)),subtimes[i].astype(int)],savelag1['y'][(subset*sub):(subset*(sub+1)),subtimes[i].astype(int)],color='b',label='No drag',s=.25,zorder=10)
            ax[i].scatter(savelag2['x'][(subset*sub):(subset*(sub+1)),subtimes[i].astype(int)],savelag2['y'][(subset*sub):(subset*(sub+1)),subtimes[i].astype(int)],color='r',label='Drag',s=.25,zorder=15)
            ax[i].axis(region['regionxy'])
            ax[i].set_title('Hour '+ ("%.0f"% ( ( ((savelag1['time'][1]-savelag1['time'][0])*subtimes[i].astype(int) )/3600)  ) ))
            scaler=1000
            ticks = mpl.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/scaler))
            ax[i].xaxis.set_major_formatter(ticks)
            ax[i].yaxis.set_major_formatter(ticks)
            if (i>=((rows-1)*cols)):
                ax[i].set_xlabel(r'x (km)')
            if (np.mod(i,cols)==0):
                ax[i].set_ylabel(r'y (km)')
            #ax[i]=prettyplot_ll(ax[i],setregion=region,grid=True,title='Day '+ ("%d"% (48*daysi*i/48)))

            for label in (ax[i].get_xticklabels() + ax[i].get_yticklabels()):
                #label.set_fontname('Arial')
                label.set_fontsize(8)
            for label in (ax[i].get_xticklabels()):
                label.set_rotation('vertical')

          
        f.tight_layout(pad=1)
        #f.show()  
        days=( ( ( ((savelag1['time'][1]-savelag1['time'][0])*subtimes[1].astype(int) )/3600)/24  ) )-(( ( ((savelag1['time'][1]-savelag1['time'][0])*subtimes[0].astype(int) )/3600)/24  ) )
        f.savefig(savepath +name+'_'+ name2+'_'+regionname+'_'+ lname+'_every_'+("%f"%days)+'days_rows_'+("%d"%rows)+'_cols_'+("%d"%cols)+'_'+("%05d"%(subset*sub))+'_'+("%05d"%(subset*(sub+1)))+'_withvectors.png',dpi=600)
        plt.close(f)


    








