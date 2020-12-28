import pandas as pd
import sys
sys.path.append('/home/ZhiLi/CRESTHH')
# sys.path.append('/home/ZhiLi/CRESTHH/data/Example-cali')
import cresthh
import cresthh.anuga as anuga
from osgeo import gdal
from glob import glob
from affine import Affine
import geopandas as gpd
import pypar
from cresthh.anuga import SWW_plotter
from cresthh.utils import flowAreaCalc as flow_area
from cresthh.utils import processSWW
%matplotlib inline
sys.path.append('/home/ZhiLi/PlotGallary')
from matplotlibconfig import basic

basic()

# Allow inline jshtml animations
from matplotlib import rc
rc('animation', html='jshtml')
#  Mesh partition routines

import matplotlib
cmap= matplotlib.cm.get_cmap('ocean_r')

reanalysis_20040819= SWW_plotter('20040819_reanalysis.sww')
future_20040819= SWW_plotter('20040819_future.sww')
reanalysis_20061015= SWW_plotter('20061015_reanalysis.sww')
future_20061015= SWW_plotter('20061015_future.sww')
reanalysis_20080913= SWW_plotter('20080913_reanalysis.sww')
future_20080913= SWW_plotter('20080913_future.sww')
reanalysis_20100907= SWW_plotter('20100907_reanalysis.sww')
future_20100907= SWW_plotter('20100907_future.sww')
reanalysis_20130920= SWW_plotter('20130920_reanalysis.sww')
future_20130920= SWW_plotter('20130920_future.sww')

SWWs= [reanalysis_20040819, future_20040819, reanalysis_20061015, future_20061015,
       reanalysis_20080913,future_20080913,reanalysis_20100907,future_20100907, reanalysis_20130920, future_20130920]

events= ['20040819','20061015','20080913','20100907','20130920']

# ===============================DYNAMIC PLOT=========================
'''
Below save every graph in the folder and then use ffmpeg to add time feature
'''
j=0
for t in range(240):
    if t%3==0:
        i=1
        fig= plt.figure(figsize=(12,20))
        for date in ['20040819','20061015','20080913','20100907','20130920']:
            for scenario in ['reanalysis','future']:
                ax=fig.add_subplot(5,2,i)
                splotter=SWWs[i-1]
                dr= pd.date_range(start=date, freq='H', periods=len(splotter.depth))
                _depth= splotter.depth.copy()
                _depth[_depth<0.1]= np.nan
                ax.tripcolor(splotter.triang, _depth[t,:], vmin=0, vmax=4, cmap=cmap)
                ax.set_title(dr[t].strftime('%Y-%m-%d %H'), fontsize=12)
                ax.axis('off')
                i+=1
        plt.close();
        plt.tight_layout();
        fig.savefig('figures/%03d.png'%j, dpi=300)
        j+=1

# ==================================HAZARD PLOT=======================
from matplotlib.colors import ListedColormap
from matplotlib import cm
i=0
k=1
fig= plt.figure(figsize=(18,20))
for date in events:
    first=True
    for scenario in ['base period','future','change']:
        ax=fig.add_subplot(5,3,k)
        
#         dr= pd.date_range(start=date, freq='H', periods=len(splotter.depth))
        if scenario=='change':
            base= SWWs[i-2].depth
            future=SWWs[i-1].depth
            itime, inds= np.where(base>0.3)
            inundation_time_base= np.zeros((_depth.shape[1]))
            for j in np.unique(sorted(inds)):
                inundation_time_base[j]= np.nanmin(itime[inds==j])     
            
            itime, inds= np.where(future>0.3)
            inundation_time_future= np.zeros((_depth.shape[1]))
            for j in np.unique(sorted(inds)):
                inundation_time_future[j]= np.nanmin(itime[inds==j])      
            diff= inundation_time_future- inundation_time_base
            masks= (np.nanmax(base, axis=0)>0.3) & (np.nanmax(future,axis=0)>0.3)
            diff= diff[(~np.isnan(diff)) & masks]
            ax.hist(diff, color='grey', edgecolor='k', density=True, bins=20, log=True)    
            ax.vlines(0,0,3,color='r',linestyle='dashed')
            ax.vlines(diff.mean(),0,3,color='k',linestyle='dashed')
            ax.set_xlabel('Difference (hours)')
            ax.set_ylabel('Density')
#             ax.set_xticks(np.array(list(ax.get_xticks()) + [diff.mean()]).astype(int))
            print('event %s, mean difference in hours %.2f, positive percentage %.2f, negative percentage %.2f'%(date, diff.mean(),
                                                                                                                float((diff>0).sum())/len(diff)*100.,
                                                                                                                float((diff<0).sum())/len(diff)*100.))
            k+=1
        else:
            splotter=SWWs[i]
            _depth= splotter.depth.copy()
            itime, inds= np.where(_depth>0.3)
            inundation_time= np.zeros((_depth.shape[1]))
            for j in np.unique(sorted(inds)):
                inundation_time[j]= np.nanmin(itime[inds==j])
            splotter.triang.set_mask(inundation_time<1)
            plt.tripcolor(splotter.triang, inundation_time,  cmap=cm.get_cmap('jet',11), vmin=0,vmax=220)
            plt.title(scenario, fontsize=15, weight='bold');
            if first:
                plt.ylabel(str(date))
                first=False
            cbar=plt.colorbar(extend='both', ticks=np.linspace(0,220,12))
#             plt.axis('off');
            plt.xticks([])
            plt.yticks([])
            i+=1
            k+=1
        
# ================================HISTOGRAM====================

fig = plt.figure(figsize=(12,20))
for i, date in enumerate(['20040819','20061015','20080913','20100907','20130920']):
    _reanalysis= SWWs[2*i]
    _future= SWWs[2*i+1]
    _diff= _future.depth - _reanalysis.depth
    _diff= _diff[~np.isnan(_diff)]
    ax= fig.add_subplot(5,2,i*2+1)
    ax.hist(_diff.reshape(-1), color='grey', edgecolor='k', density=True, bins=20, log=True)
    ax.vlines(0,0,3,color='r',linestyle='dashed')
    ax.vlines(_diff.mean(),0,3,color='k',linestyle='dashed')
    ax.set_xlabel('Depth difference (m)')
    ax.set_ylabel(date)
    ax= fig.add_subplot(5,2,i*2+2)
    _diff= _future.speed - _reanalysis.speed
    _diff= _diff[~np.isnan(_diff)]
    ax.hist(_diff.reshape(-1),color='grey',edgecolor='k', density=True, bins=20, log=True)
    ax.vlines(0,0,3,color='r',linestyle='dashed')
    ax.vlines(_diff.mean(),0,3,color='k',linestyle='dashed')
    ax.set_xlabel('Speed difference (m/s)')
plt.tight_layout();

# ================================FLOOD IMPACT CLASSIFY================
def classify(H,V):
    haz=np.ones(len(H))
#     print H.shape, V.shape
    haz[(V<=2.0) | (H<=0.3) | (H*V<0.3)]=1
#     if (V<2.0) & (H<=0.5) & (H*V<0.6):
    haz[((0.3<H) & (H<=0.5)) | ((0.3<H*V) & (H*V<=0.6) & (V<2.0))]=2
#     if (V<2.0) & (H<=1.2) & (H*V<0.6):
    haz[((0.5<H) & (H<=1.2)) | ((0.3<H*V) & (H*V<=0.6) & (V<=2.0))]=3
#     if (V<2.0) & (H<=2.0) & (H*V<=1.0):
    haz[((1.2<H) & (H<=2.0)) | ((0.6<H*V) & (H*V<=1.0) & (V<=2.0))]=4
#     if (V<4.0) & (H<=4.0) & (H*V<=4.0):
    haz[((V<=4.0) & (V>2.0)) | ((2.0<H) & (H<=4.0)) | ((1.0<H*V) & (H*V<=4.0))]=5        
#     if H*V>4:
    haz[(H*V>4)|(H>4.0)|(V>4.0)]=6
    return haz
  
df= pd.DataFrame(index=['20040819','20061015','20080913','20100907','20130920'])
harzads_reanalysis={}
hazards_future= {}

for i, date in enumerate(['20040819','20061015','20080913','20100907','20130920']):
    first=True
    _reanalysis= SWWs[2*i]
    _future= SWWs[2*i+1]
    harzads_reanalysis[date]=0
    hazards_future[date]=0
    for t in range(_reanalysis.depth.shape[0]):
        _H= _reanalysis.depth[t,:]
        _V= _reanalysis.speed[t,:]
        _V=_V[_H>0.1]
        _H= _H[_H>0.1]
        hazards= classify(_H, _V)
        for j in range(7):
            if first:
                df.loc[date, 'reanalysis'+'_%d'%j]= (hazards==j).sum()
            else:
                df.loc[date, 'reanalysis'+'_%d'%j]+= (hazards==j).sum()
        _H= _future.depth[t,:]
        _V= _future.speed[t,:]
        _V=_V[_H>0.1]
        _H= _H[_H>0.1]      
        hazards= classify(_H, _V)
        for j in range(7):
            if first:
                df.loc[date, 'future'+'_%d'%j]= (hazards==j).sum()
#                 first=False
            else:
                df.loc[date, 'future'+'_%d'%j]+= (hazards==j).sum()
        first=False
colors= ["#7D0112","#A3355C","#C16092","#D68ABE","#E4B2E1","#EDD5F7"][::-1]
from matplotlib.patches import Patch
fig=plt.figure(figsize=(12,6))
ax=fig.add_subplot(111)
df.iloc[:,1:7].plot(kind='barh', stacked=True, width=0.2,position=np.arange(1,6),ax=ax,legend=False,
                    color=colors, edgecolor='k',hatch='/',linewidth=2)
df.iloc[:,8:].plot(kind='barh',stacked=True, width=0.2,position=np.arange(1,6)+1,ax=ax,color=colors,
                   edgecolor='k', hatch="\\",linewidth=2,legend=False)
# ax.set_xscale('log')
ax.set_yticks(np.linspace(-0.2,3.0,5))
ax.set_yticklabels(['20040819','20061015','20080913','20100907','20130920'])
elements= [Patch(facecolor=colors[0],label='Category 1', edgecolor='k'),
          Patch(facecolor=colors[1],label='Category 2', edgecolor='k'),
          Patch(facecolor=colors[2],label='Category 3', edgecolor='k'),
          Patch(facecolor=colors[3],label='Category 4', edgecolor='k'),
          Patch(facecolor=colors[4],label='Category 5', edgecolor='k'),
          Patch(facecolor=colors[5],label='Category 6', edgecolor='k'),
          Patch(facecolor='white',label='CTL', edgecolor='k',hatch='/'),
          Patch(facecolor='white',label='PWG', edgecolor='k',hatch="\\")]
ax.set_xticks(np.linspace(0,8000000,8))
ax.set_xticklabels([" $%d\\times 10^6$"%i for i in range(9)])
ax.set_xlabel('Counts')
ax.legend(handles=elements);

