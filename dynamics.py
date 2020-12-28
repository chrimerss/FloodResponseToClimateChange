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


