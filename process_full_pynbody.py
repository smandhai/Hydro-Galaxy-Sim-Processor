#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 16:48:56 2023

This file will skip over the cutting box script and work with the full
snapshot file directly using pynbody. Processing can't be saved with 
this script but it may be sufficient to produce the GalPy potentials.

It will:
- Read the file
- Produce an image of the galaxy (to ensure everything is working as intended)
- Add in missing parameters
- Filter out wind particles
- Create a box around the galaxy
- Create galpy potential

@author: Soheb Mandhai
"""
import numpy as np
import h5py
import pandas as pd
import shutil as sh
import glob
import os
import matplotlib.pyplot as plt
import pynbody as pb
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
	temp_name = snapdir.format(s)+"/"+file_name.format(s,"cut")
	"""To-Do: 
	- Load in copied file - Done
	- Loop over each part type - if a position is found move to the next step
	- Convert all coordinates to the frame of "gal_pos"
	- Cut the box
	- Reset all the attributes to the original values
	- Sanity check: Load galaxy box into pynbody and see if it works
	"""
	data = pb.load(temp_name)
	print(data["pos"])
	os.sync()
	data.physical_units()
	print(data["pos"])
	#data["pos"] -= gal_pos*1000
	print(data["pos"])
	data_cut = data[pb.filt.BandPass('x', '-1000 kpc','1000 kpc')]
	data_cut = data_cut[pb.filt.BandPass('y', '-1000 kpc','1000 kpc')]
	data_cut = data_cut[pb.filt.BandPass('z', '-1000 kpc','1000 kpc')]
	print(data_cut["pos"])
	pb.analysis.angmom.faceon(data_cut.s)
	pb.plot.sph.image(data_cut.s,qty='rho',units="g cm^-3",width=100,cmap='Greys')
	plt.savefig("test_plot_ss-{}.png".format(s))
	
	

				

				
	
	
