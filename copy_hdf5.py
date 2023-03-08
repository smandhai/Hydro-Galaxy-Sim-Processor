import h5py
import numpy as np
import glob
import os

data_dir=data_dir = 'Data/snapdir_{}/snapshot_{}.{}.hdf5'
max_snap = 127
max_part = 31

#Current Snapshot -  will be broadened to map over all snapshots
curr_snap = 126

out_dir = 'Data_proc/'
new_dir = out_dir + '/'.join((data_dir.split('/'))[1:-1]) #Mimics the folder hierarchy
if os.path.isdir(new_dir.format(curr_snap)) == False:
	os.mkdir(new_dir.format(curr_snap)) #Creates the folder
new_file = new_dir.format(curr_snap)+'/'+data_dir.split('/')[-1].format(curr_snap,'copy')


with h5py.File(new_file,mode='w') as comb:
	print(glob.glob('/'.join((data_dir.split('/'))[:-1]).format(curr_snap)+'/'+'*.hdf5'))
	for f in glob.glob('/'.join((data_dir.split('/'))[:-1]).format(curr_snap)+'/'+'*.hdf5'):
		temp = h5py.File(f,'r')
		for obj in temp.keys():
			temp.copy(obj,comb)

print('Writing file to: ' + new_file)
