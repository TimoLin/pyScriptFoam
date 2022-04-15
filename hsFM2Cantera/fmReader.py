#!/usr/bin/env python
"""
FlameMaster flamelet solution reader.
"""

import sys
import os 

class flamelet():
    '''Including flamelet data
    '''
    def __init__(self ):
        self.name = []
        self.data = []
        self.nSpecies = 0
        self.ha = []
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
    def setHa(self, _ha):
        self.ha = _ha
    def setNspecise(self, n):
        self.nSpecies = n


def readFM(fname, fm):
    '''Read flamelet solutions
    '''
    f = open(fname,'r')
    print(fname)
    # no use header lines
    line = f.readline()
    while ('title' not in line):
        line = f.readline()
    flame = line.split('"')[1]

    while ('pressure' not in line):
        line = f.readline()
   
    P = float(line.split()[2]) # in bar
    fm.readP(P)

    # chi_ref: Transient flamelet
    # chi_st : Steady flamelet
    while ('chi_st' not in line and 'chi_ref' not in line):
        line = f.readline()
   
    chi_st = float(line.split()[2])
    fm.readChi(chi_st)

    while ('numOfSpecies' not in line):
        line = f.readline()
    
    n_species = int(line.split()[2])
    fm.setNspecise(n_species)

    line = f.readline()
    n_grid = int(line.split()[2])

    # When n_grid%5 == 0, error occurs
    n_grid -= 1
    
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
    if 'zeta' in line:
        # transient flame data
        for n in range( int(n_grid/5) + 1):
            line = f.readline()
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

    while (True):
        # Name
        line = f.readline()
        if ("ProdRateProgVar" not in line):
            readDummy(f,n_grid)
        else:
            fm.readName("PREMIX_YCDOT")
            fm.readData(readBlock(f,n_grid))
            break
    
    n_grid += 1
    # end up here, don't need the rest part
    f.close()

def readDummy(f,n_grid):
    '''Read to dummy
    '''
    for n in range( int( n_grid/5) + 1):
        # Data
        line = f.readline()
    return

def readBlock(f,n_grid):
    '''Read data block
    '''
    d = []
    for n in range( int( n_grid/5) + 1):
        # Data
        line = f.readline()
        for temp in line.split():
            d.append(temp)
    return (d)

