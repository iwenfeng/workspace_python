from __future__ import division,print_function
import numpy as np
import matplotlib as mpl
import scipy as sp
import matplotlib.tri as mplt
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
import os as os
import gridtools as gt
import datatools as dt
import plottools as pt
np.set_printoptions(precision=16,suppress=True,threshold=np.nan)
import pandas as pd


def runstats(datain=None):
    """Takes an array and returns basic stats on it. Max,Min,Mean,Std

    :Parameters:
    

 
    """

   

    if datain==None:
        print('Need to pass in data array')
    else:
        maxval=np.nanmax(datain)
        minval=np.nanmin(datain)
        meanval=np.nanmean(datain)
        stdval=np.nanstd(datain)
        np.sum(np.isnan(datain))

        return maxval,minval,meanval,stdval,np.sum(np.isnan(datain))/np.size(datain)


def ne_fv(casename,h=False,is31=False):    
    depdata=gt.load_nodfile(casename+'.nod',h)
    grddata=gt.load_elefile(casename+'.ele')
    gt.save_grdfile(grddata,depdata,casename+'_grd.dat',is31)
    gt.save_depfile(depdata,casename+'_dep.dat',is31)


def dic_shape(indic):
    df=pd.DataFrame([str(np.shape(indic[key])) for key in indic.keys()],indic.keys())
    print(df)


def speeder(ua,va):
    return np.sqrt(ua**2+va**2)

def myprint(d):
  """
    Print nested dictionaries in a readable manner.
    Code from Stack overflow - Scharron
    
  """  
    
  for k, v in d.iteritems():
    if isinstance(v, dict):
      myprint(v)
    else:
      print("{0} : {1}".format(k, v))

def tg2csv(npyfile,outname):
    data=np.load(npyfile)
    data=data[()]

    mykeys=['00065','00060','00055','00053','00046','00129']
    cons=['M2  ','N2  ','S2  ','K1  ','O1  ','M4  ']
    consout=['M2 A','M2 P','N2 A','N2 P','S2 A','S2 P','K1 A','K1 P','O1 A','O1 P','M4 A','M4 P']
    
    tidecon=np.empty((6,12))
    for i in range(6):
        for j in range(6):
            tidecon[i,2*j]=data[mykeys[i]]['df'].lookup([cons[j]],['Amp diff'])
            tidecon[i,(2*j)+1]=data[mykeys[i]]['df'].lookup([cons[j]],['Phase diff'])    

    df=pd.DataFrame(tidecon,columns=consout,index=mykeys)
    df.to_csv(outname)






