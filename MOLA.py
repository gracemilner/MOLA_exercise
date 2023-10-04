# -*- coding: utf-8 -*-
"""
Created on 23/2/2018
@author: Arthur Depicker
Updated: 04/22 by Grace Milner

***********************************
MOLA PROCEDURE, Hellenistic example
***********************************

This script performs the following: 
    1. loads in the data
    2. performs initial calculations to determine the number of pixels needed to be assigned to each LU type
    3. uses separate script to assign required number of pixels to each LU type (Assign.py)
    4. exports as final LU map

Sometimes you have to reload one of your function imports. Use following code:
    >>> import importlib
    >>> importlib.reload(packagename)
"""
#%% Basic cleaning and imports
import matplotlib.pyplot as plt
from osgeo import gdal # to work with spatial data
plt.close('all') #closing all figure windows that may be open

# set working directory
import os
os.chdir("PATH")

# change details depending on which time period you're doing
prefix = 'LRom'  #('Hel', 'ERom', or 'LRom')
full_prefix = 'Late_Roman'

# uncomment demand as required (determined previously):
# Hellenistic demand ->
# arable_demand = 3525
# forest_demand = 48242
# pasture_demand = 25850

# Early Roman demand ->
# arable_demand = 5970
# forest_demand = 27867
# pasture_demand = 43780

# Late Roman demand ->
arable_demand = 4575
forest_demand = 39492
pasture_demand = 33550


#%% Import your data
# open dataset with custom function that transforms the .tif format into arrays
# driver of allocation (probability maps) for one time period
import Import_files as Im
prob_Arable = Im.rst(f'{prefix}_A_prob.tif')
prob_Forest = Im.rst('F_prob.tif')  #Forest map doesn't need the 'prefix' to specify time period because they are all the same
prob_Pasture = Im.rst(f'{prefix}_P_prob.tif')

#testing:
#import numpy as np
#np.amax(prob_Arable)

#%% Number of cells needed for each land use type
# land use demand

total_N = sum(sum(prob_Pasture > 0)) #sum of all probabilities 
total_A = arable_demand + forest_demand + pasture_demand 
nr_Arable = int(round(arable_demand /total_A*total_N))
nr_Forest = int(round(forest_demand/total_A*total_N))
nr_Pasture = int(round(pasture_demand/total_A*total_N))

#%% Remove conflicts and assign land use types
import Assign as As #separate script to assign the LU types according to probabilities
LU = As.Assign_LU(prob_Arable, prob_Forest, prob_Pasture, nr_Arable, nr_Forest, nr_Pasture)

plt.imshow(LU)
plt.show() # show how it looks like

#%%
import Export_files
Example = gdal.Open('F_prob.tif') # we will use the same auxillary data for our own export product
Path_Name = f'{full_prefix}_LU_final.tif' #where to write the file + name
Export_files.array(LU, Example, Path_Name)