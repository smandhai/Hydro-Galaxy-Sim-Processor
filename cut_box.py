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

"Range of snapshots to process"
snapshot_max = 127
snapshot_min = 50

snapdir = "Data_proc/snapdir_{}"
file_name =  "snapshot_{}.full.hdf5"
group_file = "Data/groups_{}/fof_subhalo_tab_{}.0.hdf5" #Load in the 0th part


"Find the center of the potential"
with h5py.File(group_file.format(snapshot_max,snapshot_max),"r") as fof_main:
	"Stores the positional information of the galaxy within the latest snapshot"
	gal_pos = fof_main["Group/GroupCM"][0:][0]/fof_main["Header"].attrs["HubbleParam"]

	
