#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 16:48:56 2023

This file will read in the compiled galaxy particle data and cut around the galaxy 
based on the defined length.

It will:
- Read in the group information for the 0th part of the snapshot
- Find the location  of the centre of mass
- Cut around the centre of mass of the main galaxy
- Cut a box around the galaxy in xyz
- Store the part separately for further processing

@author: Soheb Mandhai
"""
import numpy as np
import h5py
import pandas as pd
import shutil as sh
import glob
#========================= SETTINGS ======================================================#

"Range of snapshots to process"
snapshot_max = 127
snapshot_min = 50
box_size  = 6 #Mpc 

snapdir_folder = 'snapdir_{}'
snapdir = "Data_proc/"+snapdir_folder
file_name =  "snapshot_{}.{}.hdf5"
group_file = "Data/groups_{}/fof_subhalo_tab_{}.0.hdf5" #Load in the 0th part

#========================================================================================#
"Find the center of the potential"
with h5py.File(group_file.format(snapshot_max,snapshot_max),"r") as fof_main:
	"Stores the positional information of the galaxy within the latest snapshot"
	gal_pos = fof_main["Group/GroupCM"][0:][0]/fof_main["Header"].attrs["HubbleParam"]

"Create copies of the snapshot for editing"
"Find the current existing snapshots"
snaps = glob.glob(snapdir.split(snapdir_folder)[0]+'*',recursive=True)
"Convert them to integers to store"
snap_nums = np.sort(np.unique(np.asarray([s.split("_")[-1] for s in snaps]).astype(int)))

for s in snap_nums:
	temp_filename = snapdir.format(s)+"/"+file_name.format(s,"cut")
	sh.copy(snapdir.format(s)+"/"+file_name.format(s,"full")
	,temp_filename)
	"""To-Do: 
	- Load in copied file
	- Loop over each part type - if a position is found move to the next step
	- Convert all coordinates to the frame of "gal_pos"
	- Cut the box
	- Reset all the attributes to the original values
	- Sanity check: Load galaxy box into pynbody and see if it works
	"""
	
	
	
