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
from galpy.util.conversion import _G,parse_length,parse_mass
import galpy.potential as pot
import pickle
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
	- Loop over each part type - if a position is found move to the next step - Done
	- Convert all coordinates to the frame of "gal_pos" - Done
	- Cut the box - Done
	- Reset all the attributes to the original values - Unneeded in this variant
	- Sanity check: Load galaxy box into pynbody and see if it works
	"""
	data = pb.load(temp_name)
	print("First checkpoint: ",data["pos"])

	"Process snapshot data"
	data._arrays['mass'] =  data['mass']
	#data.s['phi'] = pb.array.SimArray(data.s['GravPotential'],'km^2 s^-2',dtype=np.float64)
	data['pos'] = pb.array.SimArray(data['pos'],dtype=np.float64)
	data._arrays['pos'] = pb.array.SimArray(data['pos'],dtype=np.float64)
	data.s['eps'] = pb.array.SimArray(np.tile(0.369,len(data.s['mass'])),'kpc',dtype=np.float64)
	data.g['eps'] = pb.array.SimArray(np.tile(0.369,len(data.g['mass'])),'kpc',dtype=np.float64)
	data.dm['eps'] = pb.array.SimArray(np.tile(0.369,len(data.dm['mass'])),'kpc',dtype=np.float64)
	data.bh['eps'] = pb.array.SimArray(np.tile(0.369,len(data.bh['mass'])),'kpc',dtype=np.float64)
	"Convert to float64"
	for k in data._arrays.keys():
	    data._arrays[k] = data[k].astype(np.float64)
	"Prepare interpolator"
	g= pb.array.SimArray(_G/1000.)
	g.units= 'kpc Msol**-1 km**2 s**-2 G**-1'
	data._arrays['mass']= data._arrays['mass']*g

	os.sync()
	data.physical_units()
	print("Second checkpoint: ",data["pos"])
	#data["pos"] -= gal_pos*1000
	#print("Third checkpoint: "data["pos"])
	data_cut = data[pb.filt.BandPass('x', '-1000 kpc','1000 kpc')]
	data_cut = data_cut[pb.filt.BandPass('y', '-1000 kpc','1000 kpc')]
	data_cut = data_cut[pb.filt.BandPass('z', '-1000 kpc','1000 kpc')]
	data_cut = data_cut[pb.filt.BandPass('z', '-1000 kpc','1000 kpc')]
	"Remove stellar wind particles"     
	data_cut.s["GFM_StellarFormationTime"].units = "Gyr"
	data_cut.s = data_cut.s[pb.filt.HighPass("GFM_StellarFormationTime",'0 Gyr')]
	print("Third Checkpoint: ",data_cut["pos"])
	pb.analysis.angmom.faceon(data_cut.s)
	#pb.plot.sph.image(data_cut.s,qty='rho',units="g cm^-3",width=100,cmap='Greys')
	#plt.savefig("test_plot_ss-{}.png".format(s))
	





	"Create potentials and then pickle them"	
	spi= pot.InterpSnapshotRZPotential(data_cut.s,rgrid=(np.log10(1e-4),np.log10(1e3),101),logR=True,zgrid=(-60.,60.,101),interpepifreq=True,
	interpverticalfreq=True,interpPot=True,zsym=False,enable_c=True,numcores=4)

	delattr(spi,'_s')
	delattr(spi,'_origPot')

	"For the Stellar disc"
	with open("stellar_disc_ss-{}.pkl".format(s),"wb") as f:
		pickle.dump(spi,f)   
 
	"Create dictionary only version"	
	dic = {'pos': data_cut.s['pos'], 'mass':data_cut.s['mass'],'eps':data_cut.s['eps']}
	with open("stellar_disc_ss-{}_dic.pkl".format(s),"wb") as f:
		pickle.dump(dic,f)    


	"For the dark matter halo and the galaxy potential"
	spi_dm= pot.InterpSnapshotRZPotential(data_cut.d,rgrid=(np.log10(1e-4),np.log10(1e3),101),logR=True,zgrid=(-60.,60.,101),interpPot=True,zsym=False,enable_c=True,numcores=4)
	spi_gas= pot.InterpSnapshotRZPotential(data_cut.g,rgrid=(np.log10(1e-4),np.log10(1e3),101),logR=True,zgrid=(-60.,60.,101),interpepifreq=True,
	interpverticalfreq=True,interpPot=True,zsym=False,enable_c=True,numcores=4)

	delattr(spi_dm,'_s')
	delattr(spi_dm,'_origPot')
	delattr(spi_gas,'_s')
	delattr(spi_gas,'_origPot')


	dic = {'pos': data_cut.g['pos'], 'mass':data_cut.g['mass'],'eps':data_cut.g['eps']}
	with open("gas_pot_ss-{}_dic.pkl".format(s),"wb") as f:
		pickle.dump(dic,f)    

	dic = {'pos': data_cut.d['pos'], 'mass':data_cut.d['mass'],'eps':data_cut.d['eps']}
	with open("DM_pot_ss-{}_dic.pkl".format(s),"wb") as f:
		pickle.dump(dic,f)    


	with open("DM_pot_ss-{}.pkl".format(s),"wb") as f:
		pickle.dump(spi_dm,f)    
	with open("gas_pot_ss-{}.pkl".format(s),"wb") as f:
		pickle.dump(spi_gas,f)    
	

				

				
	
	
