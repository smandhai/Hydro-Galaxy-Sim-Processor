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
import os
#========================= SETTINGS ======================================================#

"Range of snapshots to process"
snapshot_max = 127
snapshot_min = 50
box_size  = 3 #Mpc 

snapdir_folder = 'snapdir_{}'
snapdir = "Data_proc/"+snapdir_folder
file_name =  "snapshot_{}.{}.hdf5"
group_file = "Data/groups_{}/fof_subhalo_tab_{}.0.hdf5" #Load in the 0th part

pos_header = 'Coordinates' #name of positional information
pos_tol = 0.1 #Tolerance value for the position - in Mpc

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
	os.sync()
	"""To-Do: 
	- Load in copied file - Done
	- Loop over each part type - if a position is found move to the next step
	- Convert all coordinates to the frame of "gal_pos"
	- Cut the box
	- Reset all the attributes to the original values
	- Sanity check: Load galaxy box into pynbody and see if it works
	"""
	with h5py.File(temp_filename,'r+') as f:
		
		print(f.keys()) #Confirms all headers are present
		h_box = f["Parameters"].attrs["HubbleParam"] #Find the hubble parameter for the box
		for key in f.keys(): #Loop over keys
			sub_keys = list(f[key].keys()) #Make list of keys
			if pos_header in f[key]: #Check positional information is present
				#print(key,True)
				"Change coordinates"
				new_coords = f[key][pos_header]/h_box - gal_pos+pos_tol #Converts coordinates to Mpc from Mpc/h
				x_cond = np.abs(np.asarray(new_coords.T[0]))<box_size/2
				y_cond = np.abs(np.asarray(new_coords.T[1]))<box_size/2
				z_cond = np.abs(np.asarray(new_coords.T[2]))<box_size/2
				cond = np.where(x_cond&y_cond&z_cond) #Find coordinates out of bounds
				for sub_k in sub_keys:
					temp_data = f[key][sub_k] #Set current dataset to a temporary variable
					"Temporarily store the old information"
					f[key][sub_k+"_temp"]  = temp_data #Store data to a temp dataset
					f[key][sub_k+"_temp"].attrs.update(temp_data.attrs) #Copy attributes
					temp_array = np.asarray(temp_data) #Create a numpy array of temp data
					"Remove coordinates out of desired bounds"
					#if len(temp_array.shape)>1: #Check to see if the data is multidimensional (should be 1 or 3)
					#	new_array = (temp_array[cond]).reshape(len(cond[0])//new_coords.shape[1],new_coords.shape[1])
					#else:

					if sub_k == pos_header: #If the current dataset is equivalent to the positional information - apply the hubble multiplier
						new_array = new_coords[cond]*h_box
					else:
						new_array = temp_array[cond]

					"Delete original array"
					f.__delitem__('{}/{}'.format(key,sub_k))
					"Renew array and attributes"
					#f[key][sub_k] = new_array
					f[key].create_dataset(sub_k,data=new_array,compression="gzip", compression_opts=9)
					f[key][sub_k].attrs.update(f[key][sub_k+"_temp"].attrs)
					"Clear temporary data"
					f.__delitem__('{}/{}'.format(key,sub_k+"_temp"))

		
				
				

				
	
	
