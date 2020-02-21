#!/usr/bin/env python
"""
Convert FlameMaster Solution Enthalpy to Sensible Enthalpy
by using Cantera.
"""

import sys
import os 
import cantera as ct

class flamelet():
    def __init__(self ):
        self.name = []
        self.data = []
        self.nSpecies = 0
        self.hs = []
    def readName(self, _name):
        self.name.append(_name)
    def readData(self, _data):
        self.data.append(_data)
    def readChi(self, _chi):
        self.chi_st = _chi
    def readP(self, _P):
        self.P = _P
    def setHs(self, _hs):
        self.hs = _hs
    def setNspecise(self, n):
        self.nSpecies = n


def readFM(fname, fm):
    f = open(fname,'r')

    # no use header lines
    line = f.readline()
    while ('pressure' not in line):
        line = f.readline()
   
    P = float(line.split()[2]) # in bar
    fm.readP(P)

    while ('chi_st' not in line):
        line = f.readline()
   
    chi_st = float(line.split()[2])
    fm.readChi(chi_st)

    while ('numOfSpecies' not in line):
        line = f.readline()
    
    n_species = int(line.split()[2])
    fm.setNspecise(n_species)

    line = f.readline()
    n_grid = int(line.split()[2])
    
    while ('body' not in line):
        line = f.readline()

    # Variable name Z
    line = f.readline()
    fm.readName(line.split()[0])
    
    data= []
    for n in range( int(n_grid/5) + 1):
        line = f.readline()
        for temp in line.split():
            data.append(temp)
    fm.readData(data)

    # Variable name Temperature
    line = f.readline()
    fm.readName('T')
    data = []
    for n in range( int(n_grid/5) + 1):
        line = f.readline()
        for temp in line.split():
            data.append(temp)
    fm.readData(data)


    # read species
    for n_s in range(n_species):
        # Variable name Temperature
        line = f.readline()
        specie = line.split()[0]
        fm.readName(specie[specie.index('-')+1:])
        
        data = []
        for n in range( int( n_grid/5) + 1):
            line = f.readline()
            for temp in line.split():
                data.append(temp)
        fm.readData(data)
    
    # end up here, don't need the rest part
    f.close()

def calcHs(gas, fm):
    #gas = ct.Solution(ct_input)

    n_grid = len(fm.data[0])

    _ht = [] # Total enthalpy
    _hf = [] # Formation/Chemical enthalpy
    _hs = [] # Sensible enthalpy
    for grid in range(n_grid):
        Yi = []
        for n in range(fm.nSpecies):
            Yi.append(float(fm.data[n+2][grid]))
        gas.set_unnormalized_mass_fractions(Yi)
        gas.TP = float(fm.data[1][grid]), fm.P*ct.one_atm
        _ht.append(gas.enthalpy_mass)
        gas.TP = 298.15, fm.P*ct.one_atm
        _hf.append(gas.enthalpy_mass)

    for n in range(n_grid):
        _hs.append(_ht[n]-_hf[n])

    fm.setHs(_hs)

def outputFM(outdir, f_dir, fname, fm):
    f = open(fname, 'r')
    lines = f.readlines()
    f.close()

    n_grid = len(fm.data[0])    

    ind = lines.index('trailer\n')
    lines.insert(ind,'SensibleEnthalpy [J/kg]\n')
    ind += 1
    nlines = int(n_grid/5)+1
    
    line = ''
    for n in range(n_grid):
        line += '\t'+str(fm.hs[n])
        if (n+1)%5==0 or n == n_grid-1:
            line += '\n'
            lines.insert(ind,line)
            ind += 1
            line = ''

    fname = fname.replace(f_dir,'')
    f = open(outdir+fname, 'w')
    f.writelines(lines)
    f.close()



def main():

    help = " Usage:\n" \
          +"   python3 hsNasa.py -dir <FM-Solution-dir> -cti <Cantera-input-file>"
    
    if '-h' in sys.argv or '--help' in sys.argv:
        print(help)
        sys.exit()

    if '-dir' in sys.argv:
        f_dir = sys.argv[sys.argv.index('-dir')+1]
        f_list = os.listdir(f_dir)
        for n in range(len(f_list)):
            f_list[n] = f_dir+'/'+f_list[n]
    else:
        print(" Error!\n  FM solutions folder shall be given!")
        print(help)
        sys.exit()
        

    if '-cti' in sys.argv:
        ct_input = sys.argv[sys.argv.index('-cti')+1]
    else:
        print(" Error!\n  Cantera input file shall be given!\n  Use 'ck2cti' to convert chemkin files to Cantera format.")
        print(help)
        sys.exit()

    # Check output Dir
    outputDir = 'HsNasa'
    if os.path.exists(outputDir):
        if os.listdir(outputDir):
            print(" Output Folder '"+outputDir+"' is not emmpty!\n It's better to clean it up.\n Abort")
            sys.exit()
    else:
        os.makedirs(outputDir)

    # Read FM solutions to fms
    fms = []
    fname_list = []

    for fname in f_list:
        if 'chi' in fname:
            fms.append(flamelet())
            readFM(fname,fms[-1])
            # Kick out non-solution files 
            fname_list.append(fname)

    gas = ct.Solution(ct_input)
    for n,flame in enumerate(fms):
        calcHs(gas, flame)
        outputFM(outputDir, f_dir, fname_list[n], flame)

    #os.chdir('../')
    print(' Done!')
    
if __name__ == '__main__':
    main()
