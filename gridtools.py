from __future__ import division
import numpy as np
import matplotlib as mpl
import scipy as sp
import matplotlib.tri as mplt
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
import os as os
from StringIO import StringIO

from datatools import *
from regions import makeregions
np.set_printoptions(precision=16,suppress=True,threshold=np.nan)
import bisect


"""
Front Matter
=============

Created in 2014

Author: Mitchell O'Flaherty-Sproul

A bunch of functions dealing with finite element grids.

Requirements
===================================
Absolutely Necessary:


Optional, but recommended:


Functions
=========
regions -   given no input regions returns a list of regions, given a valid location it returns long/lat of the region and the passage name in file format and title format.
            
"""



def regions(regionname=None):
    """Returns region locations and full names

    :Parameters:
    	regionname

 
    """

    allregions=makeregions()

    if regionname==None:
        print 'Valid regions are'
        return allregions.keys()        
    else:
        tmpregion=allregions[regionname]
        tmpregion['center']=[(tmpregion['region'][0]+tmpregion['region'][1])/2,(tmpregion['region'][2]+tmpregion['region'][3])/2]
        return tmpregion


def loadnei(neifilename=None):
    """
    Loads a .nei file and returns the data as a dictionary.

 
    """
    
    if neifilename==None:
        print 'loadnei requires a filename to load.'
        return
    try:
        fp=open(neifilename,'r')
    except IOError:
        print 'Can not find ' + neifilename
        return

    nnodes=int(fp.readline())
    maxnei=int(fp.readline())
    llminmax=np.genfromtxt(StringIO(fp.readline()))
    t_data=np.loadtxt(neifilename,skiprows=3,dtype='float64')
    fp.close()

    neifile={}

    neifile['nnodes']=nnodes
    neifile['maxnei']=maxnei
    neifile['llminmax']=llminmax

    neifile['nodenumber']=t_data[:,0]
    neifile['nodell']=t_data[:,1:3]
    neifile['bcode']=t_data[:,3]
    neifile['h']=t_data[:,4]
    neifile['neighbours']=t_data[:,5:]
    neifile['lon']=t_data[:,1]
    neifile['lat']=t_data[:,2]
    
    return neifile


def find_land_nodes(neifile=None):
    """
    Given an neifile dictionary from loadnei. 
    This fuction returns a list of nodes which are constructed from only boundary nodes.

 
    """

    if neifile==None:
        print 'find_land_nodes requires a neifile dictionary.'
        return

    idx=np.where(neifile['bcode']!=0)[0]
    idx2=np.where(neifile['neighbours'][idx]!=0)
    y=np.histogram(idx[idx2[0]],bins=neifile['nnodes'])

    nodes=np.where(y[0]==2)[0]+1

    return nodes


def savenei(neifilename=None,neifile=None):
    """
    Loads a .nei file and returns the data as a dictionary.

 
    """
    
    if neifilename==None:
        print 'savenei requires a filename to save.'
        return
    try:
        fp=open(neifilename,'w')
    except IOError:
        print 'Can''t make ' + neifilename
        return

    if neifile==None:
        print 'No neifile dict given.'
        return



    fp.write('%d\n' % neifile['nnodes'])
    fp.write('%d\n' % neifile['maxnei'])
    fp.write('%f %f %f %f\n' % (neifile['llminmax'][0],neifile['llminmax'][1],neifile['llminmax'][2],neifile['llminmax'][3]))   
   

    for i in range(0,neifile['nnodes']):
        fp.write('%d %f %f %d %f %s\n' % (neifile['nodenumber'][i], neifile['nodell'][i,0], neifile['nodell'][i,1], neifile['bcode'][i] ,neifile['h'][i],np.array_str(neifile['neighbours'][i,].astype(int))[1:-1] ) )

    
    fp.close()

def max_element_side_ll(data=None,elenum=None):
    """
    Given data and an element number returns the length of the longest side in ll.

 
    """
    if data==None:
        print 'Need proper data structure'
        return
    if elenum==None:
        print 'Need to specify an element'
        return
    
    a=data['nodell'][data['nv'][elenum,0],]
    b=data['nodell'][data['nv'][elenum,1],]
    c=data['nodell'][data['nv'][elenum,2],]

    return np.max(sp.spatial.distance.pdist(np.array([a,b,c])))


def fvcom_savecage(filename=None,nodes=None,drag=None,depth=None):
    """
    Saves a fvcom cage file.

 
    """
    #Check for filename and open, catch expection if it can't create file.
    if filename==None:
        print 'fvcom_savecage requires a filename to save.'
        return
    try:
        fp=open(filename,'w')
    except IOError:
        print 'Can''t make ' + filename
        return

    #Make sure all arrays were given
    if ((nodes==None) or (drag==None) or (depth==None)):
        print 'Need to gives arrays of nodes,drag, and depth.'
        fp.close()
        return
    #Make sure they are all the same size
    if ((nodes.size!=drag.size) or (nodes.size!=depth.size)):
        print 'Arrays are not the same size.'
        fp.close()
        return 
    #Make sure that the arrays are single columns or rank 1. If not then transpose them.
    #Check if the transposed arrays are the same as size, if not then they have more then one column/row so exit
    if (nodes.shape[0]<nodes.size):
        nodes=nodes.T
        drag=drag.T
        depth=depth.T
        if (nodes.shape[0]<nodes.size):  
            fp.close()
            return
     
  
    fp.write('%s %d\n' % ('CAGE Node Number = ',np.max(nodes.shape) ) )

    for i in range(0,len(nodes)):
        fp.write('%d %f %f\n' % (nodes[i],drag[i],depth[i]) )

    
    fp.close()


def equal_vectors(data,region,spacing):
    """
    Take an FVCOM data dictionary, a region dictionary and a spacing in meters.
    Returns: The element idx that best approximates the given spacing in the region.

 
    """

    centerele=np.argsort((data['uvnodell'][:,1]-(region['region'][3]+region['region'][2])/2)**2+(data['uvnodell'][:,0]-(region['region'][1]+region['region'][0])/2)**2)
    xhalf=0.75*np.fabs(region['region'][1]-region['region'][0])*112200
    yhalf=0.75*np.fabs(region['region'][3]-region['region'][2])*112200

    #xmultiplier=np.floor(np.fabs(xhalf*2)/spacing)
    #ymultiplier=np.floor(np.fabs(yhalf*2)/spacing)    

    XI=np.arange((data['uvnode'][centerele[1],0]-xhalf),(data['uvnode'][centerele[1],0]+xhalf),spacing)
    YI=np.arange((data['uvnode'][centerele[1],1]-yhalf),(data['uvnode'][centerele[1],1]+yhalf),spacing)

    xv,yv=np.meshgrid(XI,YI)
    xytrigrid = mplt.Triangulation(data['x'], data['y'],data['nv'])
    host=xytrigrid.get_trifinder().__call__(xv.reshape(-1,1),yv.reshape(-1,1))

    idx=get_elements(data,region)

    common=np.in1d(host,idx)

    return np.unique(host[common].flatten())



def regionll2xy(data,region):
    """
    Take an FVCOM data dictionary, a region dictionary and return a region dictionary with regionxy added which best approximates the ll region in xy.
 
    """

    left=np.argmin(np.sqrt((data['uvnodell'][:,0]-region['region'][0])**2+(data['uvnodell'][:,1]-(region['region'][2]+region['region'][3])*.5)**2))
    right=np.argmin(np.sqrt((data['uvnodell'][:,0]-region['region'][1])**2+(data['uvnodell'][:,1]-(region['region'][2]+region['region'][3])*.5)**2))
    
    top=np.argmin(np.sqrt((data['uvnodell'][:,1]-region['region'][3])**2+(data['uvnodell'][:,0]-(region['region'][0]+region['region'][1])*.5)**2))
    bottom=np.argmin(np.sqrt((data['uvnodell'][:,1]-region['region'][2])**2+(data['uvnodell'][:,0]-(region['region'][0]+region['region'][1])*.5)**2))

    region['regionxy']=[data['uvnode'][left,0],data['uvnode'][right,0],data['uvnode'][bottom,1],data['uvnode'][top,1]]


    return region






def regioner(data,region,subset=False):
    
    nidx=get_nodes(data,region)

    idx0=np.in1d(data['nv'][:,0],nidx)
    idx1=np.in1d(data['nv'][:,1],nidx)
    idx2=np.in1d(data['nv'][:,2],nidx)
    eidx=idx0+idx1+idx2

    nv2 = data['nv'][eidx].flatten(order='F')
    nidx_uni=np.unique(nv2)
    nv_tmp2=np.empty(shape=nv2.shape)
    nv2_sortedind = nv2.argsort()
    nv2_sortd = nv2[nv2_sortedind]
         
    for i in xrange(len(nidx_uni)):
        i1 = bisect.bisect_left(nv2_sortd, nidx_uni[i])
        i2 = bisect.bisect_right(nv2_sortd,nidx_uni[i])
        inds = nv2_sortedind[i1:i2]
        nv_tmp2[inds] = i

    nv_new = np.reshape(nv_tmp2, (-1, 3), 'F')

    data['trigrid_sub'] = mplt.Triangulation(data['lon'][nidx_uni], data['lat'][nidx_uni],nv_new)
    data['nidx_sub']=nidx_uni
    data['eidx_sub']=eidx


    if subset==True:  
        data['zeta']=data['zeta'][:,nidx_uni]
        data['ua']=data['ua'][:,eidx]
        data['va']=data['va'][:,eidx]
        data['u']=data['u'][:,:,eidx]
        data['v']=data['v'][:,:,eidx]
        data['ww']=data['ww'][:,:,eidx]
        
    return data




def interp_vel(data,loc,layer=None,ll=True):
    loc=np.array(loc)
    host=data['trigrid_finder'].__call__(loc[0],loc[1])
    if host==-1:
        print 'Point at: (' + ('%f'%loc[0]) + ', ' +('%f'%loc[1]) + ') is external to the grid.'
        out=np.empty(shape=data['va'][:,0].shape)
        out[:]=np.nan
        return out,out

    #code for ll adapted from mod_utils.F
    if ll==True:
        TPI=111194.92664455874
        y0c = TPI * (loc[1] - data['uvnodell'][host,1])
        dx_sph = loc[0] - data['uvnodell'][host,0]
        if (dx_sph > 180.0):
            dx_sph=dx_sph-360.0
        elif (dx_sph < -180.0):
            dx_sph =dx_sph+360.0
        x0c = TPI * np.cos(np.deg2rad(loc[1] + data['uvnodell'][host,1])*0.5) * dx_sph
    else:       
        x0c=loc[0]-data['uvnode'][host,0]
        y0c=loc[1]-data['uvnode'][host,1] 

    e0=data['nbe'][host,0]
    e1=data['nbe'][host,1]
    e2=data['nbe'][host,2]


    if (layer==None and loc.size==2):
        u_e=data['ua'][:,host]
        v_e=data['va'][:,host]

        if e0==-1:
            u_0=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            v_0=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
        else:
            u_0=data['ua'][:,e0]
            v_0=data['va'][:,e0]

        if e1==-1:
            u_1=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            v_1=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
        else:
            u_1=data['ua'][:,e1]
            v_1=data['va'][:,e1]

        if e2==-1:
            u_2=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            v_2=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
        else:
            u_2=data['ua'][:,e2]
            v_2=data['va'][:,e2]

        dudx= data['a1u'][0,host]*u_e+data['a1u'][1,host]*u_0+data['a1u'][2,host]*u_1+data['a1u'][3,host]*u_2;
        dudy= data['a2u'][0,host]*u_e+data['a2u'][1,host]*u_0+data['a2u'][2,host]*u_1+data['a2u'][3,host]*u_2;
        dvdx= data['a1u'][0,host]*v_e+data['a1u'][1,host]*v_0+data['a1u'][2,host]*v_1+data['a1u'][3,host]*v_2;
        dvdy= data['a2u'][0,host]*v_e+data['a2u'][1,host]*v_0+data['a2u'][2,host]*v_1+data['a2u'][3,host]*v_2;

        ua= u_e + dudx*x0c + dudy*y0c;
        va= v_e + dvdx*x0c + dvdy*y0c;

        return ua,va

    if (layer!=None and loc.size==2):        
        u_e=data['u'][:,layer,host]
        v_e=data['v'][:,layer,host]
        w_e=data['ww'][:,layer,host]

        if e0==-1:
            u_0=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            v_0=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            w_0=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
        else:
            u_0=data['u'][:,layer,e0]
            v_0=data['v'][:,layer,e0]
            w_0=data['ww'][:,layer,e0]

        if e1==-1:
            u_1=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            v_1=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            w_1=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
        else:
            u_1=data['u'][:,layer,e1]
            v_1=data['v'][:,layer,e1]
            w_1=data['ww'][:,layer,e1]

        if e2==-1:
            u_2=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            v_2=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            w_2=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
        else:
            u_2=data['u'][:,layer,e2]
            v_2=data['v'][:,layer,e2]
            w_2=data['ww'][:,layer,e2]

        dudx= data['a1u'][0,host]*u_e+data['a1u'][1,host]*u_0+data['a1u'][2,host]*u_1+data['a1u'][3,host]*u_2;
        dudy= data['a2u'][0,host]*u_e+data['a2u'][1,host]*u_0+data['a2u'][2,host]*u_1+data['a2u'][3,host]*u_2;
        dvdx= data['a1u'][0,host]*v_e+data['a1u'][1,host]*v_0+data['a1u'][2,host]*v_1+data['a1u'][3,host]*v_2;
        dvdy= data['a2u'][0,host]*v_e+data['a2u'][1,host]*v_0+data['a2u'][2,host]*v_1+data['a2u'][3,host]*v_2;
        dwdx= data['a1u'][0,host]*w_e+data['a1u'][1,host]*w_0+data['a1u'][2,host]*w_1+data['a1u'][3,host]*w_2;
        dwdy= data['a2u'][0,host]*w_e+data['a2u'][1,host]*w_0+data['a2u'][2,host]*w_1+data['a2u'][3,host]*w_2;

        u= u_e + dudx*x0c + dudy*y0c;
        v= v_e + dvdx*x0c + dvdy*y0c;
        w= w_e + dwdx*x0c + dwdy*y0c;

        
        return u,v,w


    if (layer==None and loc.size==3): 
        print "This code isn't finished"
        return None

        if (loc[2]>100000):
            print "z-coordinate must be less than 100,000"
            out=np.empty(shape=data['va'][:,0].shape)
            out[:]=np.nan
            return out,out,out

        uvzeta=(data['zeta'][:,data['nv'][host,0]] + data['zeta'][:,data['nv'][host,1]] + data['zeta'][:,data['nv'][host,2]]) / 3.0
        leveltime=np.vstack([-1*data['siglay'][:,0].reshape(-1,1)*(uvzeta+data['uvh'][host]).reshape(1,-1),100000+np.zeros((len(uvzeta),1)).T])
    
        deepidx=(leveltime>loc[2]).argmax(axis=0)
        deepidx[deepidx==len(data['siglay'][:,0])]=len(data['siglay'][:,0])-1

        test=np.zeros((1081,20),dtype=bool)
        test[0:1081,deepidx]=1

        u_e=data['u'][:,deepidx,host]
        v_e=data['v'][:,deepidx,host]
        w_e=data['ww'][:,deepidx,host]

        if e0==-1:
            u_0=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            v_0=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            w_0=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
        else:
            u_0=data['u'][:,deepidx,e0]
            v_0=data['v'][:,deepidx,e0]
            w_0=data['ww'][:,deepidx,e0]

        if e1==-1:
            u_1=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            v_1=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            w_1=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
        else:
            u_1=data['u'][:,deepidx,e1]
            v_1=data['v'][:,deepidx,e1]
            w_1=data['ww'][:,deepidx,e1]

        if e2==-1:
            u_2=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            v_2=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
            w_2=np.zeros(shape=u_e.shape,dtype=u_e.dtype)
        else:
            u_2=data['u'][:,deepidx,e2]
            v_2=data['v'][:,deepidx,e2]
            w_2=data['ww'][:,deepidx,e2]

        dudx= data['a1u'][0,host]*u_e+data['a1u'][1,host]*u_0+data['a1u'][2,host]*u_1+data['a1u'][3,host]*u_2;
        dudy= data['a2u'][0,host]*u_e+data['a2u'][1,host]*u_0+data['a2u'][2,host]*u_1+data['a2u'][3,host]*u_2;
        dvdx= data['a1u'][0,host]*v_e+data['a1u'][1,host]*v_0+data['a1u'][2,host]*v_1+data['a1u'][3,host]*v_2;
        dvdy= data['a2u'][0,host]*v_e+data['a2u'][1,host]*v_0+data['a2u'][2,host]*v_1+data['a2u'][3,host]*v_2;
        dwdx= data['a1u'][0,host]*w_e+data['a1u'][1,host]*w_0+data['a1u'][2,host]*w_1+data['a1u'][3,host]*w_2;
        dwdy= data['a2u'][0,host]*w_e+data['a2u'][1,host]*w_0+data['a2u'][2,host]*w_1+data['a2u'][3,host]*w_2;

        u= u_e + dudx*x0c + dudy*y0c;
        v= v_e + dvdx*x0c + dvdy*y0c;
        w= w_e + dwdx*x0c + dwdy*y0c;

        
        return u,v,w        

    
def _load_grdfile(casename=None):
    """
    Loads an FVCOM grd input file and returns the data as a dictionary.

 
    """
    
    data={}    

    if casename==None:
        print '_load_grdfile requires a filename to load.'
        return
    try:
        fp=open(casename+'_grd.dat','r')
    except IOError:
        print  '_load_grdfiles: invalid case name.'
        return data

    nodes_str=fp.readline().split('=')
    elements_str=fp.readline().split('=')
    nnodes=int(nodes_str[1])
    nele=int(elements_str[1])
    #llminmax=np.genfromtxt(StringIO(fp.readline()))
    t_data1=np.genfromtxt(casename+'_grd.dat',skip_header=2, skip_footer=nnodes,dtype='int64')
    t_data2=np.genfromtxt(casename+'_grd.dat',skip_header=2+nele,dtype='float64')
    fp.close()

    data['nnodes']=nnodes
    data['nele']=nele
    data['nodexy']=t_data2[:,1:3]
    data['x']=t_data2[:,1]
    data['y']=t_data2[:,2]
    data['nv']=t_data1[:,1:4].astype(int)-1
    data['trigridxy'] = mplt.Triangulation(data['x'], data['y'],data['nv'])
    
    return data

def _load_depfile(casename=None):
    """
    Loads an FVCOM dep input file and returns the data as a dictionary.

 
    """

    data={}
    
    if casename==None:
        print '_load_depfile requires a filename to load.'
        return
    try:
        fp=open(casename+'_dep.dat','r')
    except IOError:
        print  '_load_depfile: invalid case name.'
        return data

    dep_str=fp.readline().split('=')
    dep_num=int(dep_str[1])
    t_data1=np.genfromtxt(casename+'_dep.dat',skip_header=1)
    fp.close()

    data['dep_num']=dep_num
    data['x']=t_data1[:,0]
    data['y']=t_data1[:,1]
    data['h']=t_data1[:,2]
    data['nodexy']=t_data1[:,0:2]
    
    return data

def _load_spgfile(casename=None):
    """
    Loads an FVCOM spg input file and returns the data as a dictionary.

 
    """

    data={}
    
    if casename==None:
        print '_load_spgfile requires a filename to load.'
        return
    try:
        fp=open(casename+'_spg.dat','r')
    except IOError:
        print  '_load_spgfile: invalid case name.'
        return data

    spg_str=fp.readline().split('=')
    spg_num=int(spg_str[1])
    t_data1=np.genfromtxt(casename+'_spg.dat',skip_header=1)
    fp.close()

    data['spgf_num']=spg_num
    data['spgf_nodes']=t_data1[:,0]
    data['spgf_distance']=t_data1[:,1]
    data['spgf_value']=t_data1[:,2]

    
    return data


def _load_obcfile(casename=None):
    """
    Loads an FVCOM obc input file and returns the data as a dictionary.

 
    """    

    data={}

    if casename==None:
        print '_load_obcfile requires a filename to load.'
        return
    try:
        fp=open(casename+'_obc.dat','r')
    except IOError:
        print  '_load_obcfile: invalid case name.'
        return data

    obc_str=fp.readline().split('=')
    obc_num=int(obc_str[1])
    t_data1=np.genfromtxt(casename+'_obc.dat',skip_header=1)
    fp.close()

    data['obcf_num']=obc_num
    data['obcf_numbers']=t_data1[:,0]
    data['obcf_nodes']=t_data1[:,1]
    data['obcf_value']=t_data1[:,2]

    
    return data


def _load_llfiles(casename=None):
    """
    Loads an long/lat files and returns the data as a dictionary.
 
    """

    data={}
    
    if casename==None:
        print '_load_llfiles requires a filename to load.'
        return
    try:
        fp=open(casename+'_long.dat','r')
    except IOError:
        print  '_load_llfiles: long file is invalid.'
        return data

    lon=np.genfromtxt(casename+'_long.dat')
    fp.close()

    try:
        fp=open(casename+'_lat.dat','r')
    except IOError:
        print  '_load_llfiles: lat file is invalid.'
        return data

    lat=np.genfromtxt(casename+'_lat.dat')
    fp.close()

    data['nodell']=np.vstack([lon,lat]).T
    data['lat']=lat
    data['lon']=lon
    
    return data


def _load_nc(filename=None):
    """
        Loads an .nc  data file      
    """

    ncid = netcdf.netcdf_file(filename, 'r',mmap=True)
    
    data={}

    for i in ncid.variables.keys():
        data[i]=ncid.variables[i].data

    return data


def load_fvcom_files(filepath=None,casename=None,ncname=None,neifile=None):
    """
        Loads FVCOM input files and returns the data as a dictionary.
 
    """

    currdir=os.getcwd()
    os.chdir(filepath)

    data=_load_grdfile(casename)

    data.update(_load_depfile(casename))
    
    data.update(_load_spgfile(casename))

    data.update(_load_obcfile(casename))

    data.update(_load_llfiles(casename))

    if ncname!=None:
        data.update(_load_nc(ncname))

    if neifile!=None:
        data.update(loadnei(neifile))

    os.chdir(currdir)

    return data


def save_spgfile(datain,filepath,casename=None):
    """
    Save an FVCOM spg input file.
 
    """

    data={}
    
    if casename==None:
        print 'save_spgfile requires a filename to save.'
        return
    try:
        fp=open(filepath + casename+'_spg.dat','w')
    except IOError:
        print  'save_spgfile: invalid case name.'
        return data

    fp.write('Sponge Node Number = %d\n' % datain['spgf_num'] )
    for i in range(0,datain['spgf_num']):
        fp.write('%d %f %f\n'% (datain['spgf_nodes'][i],datain['spgf_distance'][i],datain['spgf_value'][i]))
    fp.close()



def save_obcfile(datain,filepath,casename=None):
    """
    Save an FVCOM obc input file.
 
    """

    data={}
    
    if casename==None:
        print 'save_obcfile requires a filename to save.'
        return
    try:
        fp=open(filepath + casename+'_obc.dat','w')
    except IOError:
        print  'save_obcfile: invalid case name.'
        return data

    fp.write('OBC Node Number = %d\n' % datain['spgf_num'] )
    for i in range(0,datain['obcf_num']):
        fp.write('%d %d %d\n'% (datain['obcf_numbers'][i],datain['obcf_nodes'][i],datain['obcf_value'][i]))
    fp.close()


def loadcage(filepath):

    cages=None
    try:
        with open(filepath) as f_in:
            cages=np.genfromtxt(f_in,skiprows=1)
            if len(cages)>0:
                cages=(cages[:,0]-1).astype(int)
            else:
                cages=None
    except:
        cages=None

    return cages



