import h5py
import numpy as np
import glob
import os
import shutil as sh
import subprocess as subproc

data_dir = 'Data/groups_{}/fof_subhalo_tab_{}.{}.hdf5'#'Data/snapdir_{}/snapshot_{}.{}.hdf5'
max_snap = 127
max_part = 31
copy_first = True #copy the first snapshot
abandon_missing = True #Abandon missing files
skip=False
#Current Snapshot -  will be broadened to map over all snapshots
curr_snap = 127
create_new= True #Create a new file

out_dir = 'Data_proc/'
new_dir = out_dir + '/'.join((data_dir.split('/'))[1:-1]) #Mimics the folder hierarchy
if os.path.isdir(new_dir.format(curr_snap)) == False:
	os.mkdir(new_dir.format(curr_snap)) #Creates the folder
new_file = new_dir.format(curr_snap)+'/'+data_dir.split('/')[-1].format(curr_snap,'full')


snap_files = glob.glob('/'.join((data_dir.split('/'))[:-1]).format(curr_snap)+'/'+'*.hdf5')
#print(snap_files)

if (copy_first==False)|(create_new==True):
	print("Creating blank file")
	try:
		main_f = h5py.File(new_file,'w')
	except:
		if create_new == True:
			os.remove(new_file)
			main_f = h5py.File(new_file,'w')

for i,sp in enumerate(snap_files):
	with h5py.File(sp,'r') as h5f:
		print("Current file: {} [{}/{}]".format(sp,i+1,len(snap_files)))
		snap_keys = h5f.keys()
#		if i == 0:
			#Recreate hierachy for blank file
#			main_f.keys = h5f.keys()
		if (i==0)&(copy_first==True):
			"Copies the first file and sets it as the main file"
			if create_new:
				main_f.close()
			sh.copy(sp,new_file)
			print("File copied")
			#subproc.call("cp "+sp+' '+new_file,shell=True)
			main_f = h5py.File(new_file,'r+')
			main_f.attrs
			#print(list(h5f.keys()))
			#print(list(main_f.keys()))

			continue #Proceeds to i==1
		for j,key in enumerate(list(snap_keys)):
#			print(key)
#			print(h5f[key])
#			print(list(h5f[key]))
			print("Key: {}".format(key))
			if (i==0)&(copy_first==False):
				#main_f.create_group(key)#h5f[key]
				print("Copying keys (template copy is off)...")
				h5f.copy(h5f[key],main_f,key)
			if (i==0)&(j==0):
				main_f.attrs.update(h5f.attrs)
			

			if i==0:
				main_f[key].attrs.update(h5f[key].attrs)
			else:
				"Copy data from main_file"
				#print(list(main_f[key]))
				if len(list(h5f[key]))>0:
					print("Appending datasets...")

					for k in range(len(list(h5f[key]))):
						if key not in list(main_f.keys()):
							if abandon_missing: #Abandon missing parameters
								skip=True
							print("Skipping key... {}".format(key))

#						try:
						if (skip == False):
							#print("Processing datasets...\n")
							col_name = list(h5f[key])[k]
							print("Col: {}".format(col_name))
							#if i>1: #For debugging
							#	break
#								if i==1:
#									main_f["{}/{}".format(key,list(main_f[key])[k])].attrs.update(h5f["{}/{}".format(key,list(main_f[key])[k])].attrs)
							#print(main_f["{}/{}".format(key,list(main_f[key])[k])].attrs.keys())
							"Combining main data with the current part"
							temp_data_snap = h5f["{}/{}".format(key,list(h5f[key])[k])]
							if col_name in main_f[key]:
								temp_data_main  = main_f["{}/{}".format(key,list(main_f[key])[k])]
								#print(temp_data_main.shape,temp_data_snap.shape)
								new_data = np.concatenate([temp_data_main,temp_data_snap])
								main_f.__delitem__('{}/{}'.format(key,col_name))
							else: #if the main arrays are empty
								new_data = np.concatenate([temp_data_snap])

							main_f['{}/{}'.format(key,col_name)] = new_data
							#if i==1:
							main_f["{}/{}".format(key,list(main_f[key])[k])].attrs.update(h5f["{}/{}".format(key,list(main_f[key])[k])].attrs)

#						except KeyError:
#							print("Error with input, key: {}".format(key))
#							try:
#								h5f.copy(h5f[key],main_f,key)
#							except:
#								try:
#									h5f.copy(h5f[key],main_f,key)
#								except:
#									print("Failed to recover input... moving on")
#									pass
						skip=False
							
				else:
					pass
						
			"Append data from new file"
			"Delete data stored in hd5f file"
			"Set new data in place of old file"			
	"Lists the hierarchy"
#	for i,key in enumerate(list(snap_keys)):
#		print(key)
#		print(h5f[key])
#		print(list(h5f[key]))
#		if len(list(h5f[key]))>0:
#			print(list(h5f[key])[0])
#			sub_key = "{}/{}".format(key,list(h5f[key])[0])
#			print(sub_key)
#			print(h5f[sub_key])
#			print(list(h5f[sub_key])[0:100])

main_f.close()
print('Written file to: ' + new_file)
