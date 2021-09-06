pyScriptFoam
=============
My python scripts for OpenFOAM data post-processing.  

# Prerequisites
## Ubuntu
```shell
sudo apt install python3 python3-pip cantera-python3
sudo pip3 install numpy
```
## CentOS 7  
Here is a 'SCL' way to install python3 on CentOS 7.
```shell
sudo yum install centos-release-scl
sudo yum install rh-python36
# enable python3.6 environment in your shell
## For bash
scl enable rh-python36 bash 
## For zsh
scl enable rh-python36 zsh
# install numpy
sudo pip install numpy
```
[Install Cantera with Anaconda under CentOS](https://cantera.org/install/conda-install.html)

# lagrangian  
## ~~postLagrangian.py~~
~~A python script to process lagrangian data and get droplets' diameter or velocity radial distributions.~~  
This script has been merged to sprayCloud.    
## sprayCloud.py
A python script to read the lagrangian droplets data and output them to a Tecplot format file. It can also do post-process like radial profiles of droplet diameter at different axial locations and SMD distribution alongside axial direction.  
### Usage:
```
python3 sprayCloud.py [-parallel] [-latestTime] [-post] [-help]"
```
  -parallel:    process the parallel data  
  -latestTime:  only process the latestTime solution  
  -post:        post-process the droplet data  
  -help:        print this message  
### Eg:
This will read all parallel Lagrangian spray data and output them in Tecplot format. A folder name `Tecplot` will be created to save these files.  
```
python3 sprayCloud.py -parallel
```
This will only output the latestTimes's spray data in Tecplot format.  
```
python3 sprayCloud.py -parallel -latestTime
```
This will post-process parallel Lagrangian spray data and get profiles. A `postDict` should be given under `postSpray` folder, like this [example](https://github.com/TimoLin/pyScriptFoam/blob/master/lagrangian/postSpray/postDict).  
```
python3 sprayCloud.py -parallel -post
```

## sprayTrans.py
A python script to converte sprayCloud:rhoTrans__[liquidPhase] file (source term) into Tecplot readable OpenFOAM format(like T, U etc).  
A new file named: rhoTrans__[liquidPhase] will be generated.  
### Usage:  
```
python3 sprayTrans.py -liquid <phaseName> [-latestTime] [-parallel] [-help]
```
  -liquid <phaseName>: specific the liquid mixture name  
  -latestTime: only parse the latest solution  
  -parallel:   parse the parallel data  
  -help:       show this message  

### Eg:  
```
python3 sprayTrans.py -liquid C2H5OH -latestTime
```

## particleStatistic.py
Post-Processing sampled Lagrangian data from CloudFunction:ParticleStatistic  
### Usage:
```
python3 particleStatistic.py [-help] [-process] [-pdf]
```
  -process: Post-process sampled lagrangian data and get radial profiles  
  -pdf:     Get droplete droplet size PDF and volume PDF for sampled planes  
  -help:    Print this message  

# pyPlot
## Prerequisites  
```shell
sudo pip3 install matplotlib
```
## pltCourant.py
Plot Max Courant number.  
### Usage:
```
python3 pltCourant.py -log <log.file>
```
 log.file is the OpenFOAM application output  
