hsFM2Cantera
============
Calculate Sensible Enthalpy using `canteraToFoam` and add the data to FM solutions  

## fm2Cantera.py
Convert FlameMaster solutions to CSV format which is read by canteraToFoam.  

## hsJanaf.py
Add sensible enthalpy dat (from canteraToFoam, calculated using Janaf polynomial)to FM solution files.  

## hsNasa.py
Calculate sensible enthalpy using Cantera (Python version) which uses NASA polynomial  

## Usage
These scripts are for my own personal use. So just ignore this if you don't know what this is.  
1. Convert FM solutions to csv.
    - `python3 fm2Cantera.py -dir <FM_Solution_dir>`
    - `cp -r chi_parm tables* ~/OpenFOAM/calc/heGen`     
    - replace chi in tableProperties
    - replace mechanism and thermo data files in `chemkin` folder
2. Calculate using modified canteraToFoam
    - `cd ~/OpenFOAM/calc/heGen/`
    - `canteraToFoam > log`
3. Add sensible enthalpy data to FM solutions
    - `python3 hsJanaf.py -dir <FM_Solution_dir> -log <cantera2Foam_log_file>`
4. Done
