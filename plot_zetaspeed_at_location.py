from __future__ import division
import matplotlib as mpl
import scipy as sp
from datatools import *
from gridtools import *
from misctools import *
from plottools import *
from projtools import *
import matplotlib.tri as mplt
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
import os as os
import sys
np.set_printoptions(precision=8,suppress=True,threshold=np.nan)
import scipy.io as sio
import scipy.fftpack as fftp


# Define names and types of data
name_orig='kit4_kelp_nodrag'
name_change='kit4_kelp_20m_drag_0.018'
grid='kit4_kelp'
datatype='2d'
starttime=384
endtime=432
endtime=456
locx=[-129.4875,-129.475]
locy=[52.65,52.65]
ABC=[.02,.87]
ABC_text=['A','B']

single=False

### load the .nc file #####
data = loadnc('runs/'+grid+'/'+name_orig+'/output/',singlename=grid + '_0001.nc')
data2 = loadnc('runs/'+grid+'/'+name_change+'/output/',singlename=grid + '_0001.nc')
print 'done load'
data = ncdatasort(data)
print 'done sort'
data['time']=data['time']-678576


cages=loadcage('runs/'+grid+'/' +name_change+ '/input/' +grid+ '_cage.dat')
if np.shape(cages)!=():
    tmparray=[list(zip(data['nodell'][data['nv'][i,[0,1,2]],0],data['nodell'][data['nv'][i,[0,1,2]],1])) for i in cages ]
    color='g'

savepath='figures/png/' + grid + '_' + datatype + '/zetaspeed_at_location/'
if not os.path.exists(savepath): os.makedirs(savepath)



for i in range(len(locx)):

    f,ax=plt.subplots(nrows=2,ncols=1,sharex=True)


    element=closest_element(data,[locx[i],locy[i]])

    uvzeta1=(data['zeta'][starttime:endtime,data['nv'][element,0]] + data['zeta'][starttime:endtime,data['nv'][element,1]] + data['zeta'][starttime:endtime,data['nv'][element,2]]) / 3.0
    uvzeta2=(data2['zeta'][starttime:endtime,data['nv'][element,0]] + data2['zeta'][starttime:endtime,data['nv'][element,1]] + data2['zeta'][starttime:endtime,data['nv'][element,2]]) / 3.0

    ax[0].plot(data['time'][starttime:endtime],uvzeta1,'k',lw=1,label='No Kelp')
    ax[0].plot(data2['time'][starttime:endtime],uvzeta2,'g',lw=1,label='Kelp')

    ax[1].plot(data['time'][starttime:endtime],speeder(data['ua'][starttime:endtime,element],data['va'][starttime:endtime,element]),'k',lw=1,label='No Kelp')
    ax[1].plot(data2['time'][starttime:endtime],speeder(data2['ua'][starttime:endtime,element],data2['va'][starttime:endtime,element]),'g',lw=1,label='Kelp')

    ax[0].set_ylabel(r'Elevation (m s$^{-1}$)',fontsize=8)
    ax[1].set_ylabel(r'Speed (m s$^{-1}$)',fontsize=8)


#    for label in legend.get_lines():
#        label.set_linewidth(1.5)
#    for label in ax[i].get_yticklabels()[::2]:
#        label.set_visible(False)
#    for label in ax[i].get_yticklabels():
#        label.set_fontsize(8)
    for j in range(len(ax)):
        handles, labels = ax[j].get_legend_handles_labels()
        legend=ax[j].legend(handles, labels,prop={'size':6})
        ax[j].text(ABC[0],ABC[1],ABC_text[j],transform=ax[j].transAxes,bbox={'facecolor':'white','edgecolor':'None', 'alpha':1, 'pad':3},zorder=31)
        for label in ax[j].get_xticklabels()+ax[j].get_yticklabels():
            label.set_fontsize(8)


    ax[1].set_xlabel(r'Time (day)',fontsize=8)





    if single==True:
        ax[1].set_ylim([-.4,.1])
        ax[2].set_ylim([-.2,.4])

    f.subplots_adjust(hspace=.075)

    f.savefig(savepath + grid + '_'+name_orig+'_'+name_change+'_zetaspeed_at_location_'+("%f"%locx[i])+'_'+("%f"%locy[i])+'.png',dpi=300)
    plt.close(f)




