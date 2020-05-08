timeVaryingMappedHDF5FixedValue
======

## Prerequisite
### hd5f library

Intallation note:  
```sh
# Install path
cd $HOME/software
mkdir hdf5
cd hdf5
# Get hdf5-1.8.3 binary release
wget https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.8/hdf5-1.8.3/bin/linux-x86_64/5-1.8.3-linux-x86_64-shared.tar.gz
# Unpack 
tar xzf 5-1.8.3-linux-x86_64-shared.tar.gz
rm 5-1.8.3-linux-x86_64-shared.tar.gz
# Make a symbolic link "latest"
ln -s 5-1.8.3-linux-x86_64-shared latest
# Redeploy script
cd latest/bin
./h5redeploy
```
Set `hdf5` path in `.zshrc` or `.bashrc`:
```sh
export HDF5_DIR=$HOME/software/hdf5/latest
```
## How to use
Just run:
```sh
wmake
```
Then `libtimeVaryingMappedHDF5FixedValue.so` will be in `FOAM_USER_LIBBIN`.  

Add this line to `controlDict` when using tVMHDF5FV:
```c
libs ("libtimeVaryingMappedHDF5FixedValue")
```

