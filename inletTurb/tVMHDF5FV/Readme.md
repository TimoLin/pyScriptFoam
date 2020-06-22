precursorHDF5
======
Pre-processor for boundary condition: [precursorHDF5](https://github.com/TimoLin/precursorHDF5).

The scripts are taken and modified from [timofeymukha/eddylicious](https://github.com/timofeymukha/eddylicious).  

## Prerequisite
### Python
```sh
pip3 install numpy h5py mpi4py argparse

```
### OpenFOAM
#### hd5f library

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
### 1. Show help message
```sh
python3 ~/github/pyScriptFoam/inletTurb/tVMHDF5FV/foam2Hdf5.py -h
```
Output:
```
usage: foam2Hdf5.py [-h] --precursor PRECURSOR --surface SURFACE --nsamples
                    NSAMPLES --norm NORM --location LOCATION --filename
                    FILENAME

A utility for converting a database stored as a collection of foamFile-
formatted files to a single HDF5 file.

optional arguments:
  -h, --help            show this help message and exit
  --precursor PRECURSOR
                        The location of the precusor case.
  --surface SURFACE     The name of the surface that contains the data.
  --nsamples NSAMPLES   The number of the sampled time data.
  --norm NORM           Normal direction of the main surface patch.
  --location LOCATION   Start axial location of the main surface patch.
  --filename FILENAME   The name hdf5 file to create.
```
### 2. Example
```sh
python3 ~/github/pyScriptFoam/inletTurb/tVMHDF5FV/foam2Hdf5.py --precursor ./ --surface xD04 --nsamples 10001 --norm 100 --location 0 --filename test.hdf5
```
**Note:**
It's recommended to set `--nsamples` as **N+1** so that data at time `0` is also included.

## Todo
- [ ] `mpi` mode needs to be implemented.
