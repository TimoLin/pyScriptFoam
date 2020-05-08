#!/usr/bin/env python3

"""
Convert FlameMaster Laminar Flamelet Solutions to Cantera CSV format
"""

import sys
import os 


class flamelet():
    def __init__(self ):
        self.name = []
        self.data = []
    def readName(self, _name):
        self.name.append(_name)
    def readData(self, _data):
        self.data.append(_data)
    def readChi(self, _chi):
        self.chi_st = _chi


def readFM(fname, fm):
    f = open(fname,'r')

    # no use header lines
    line = f.readline()
    while ('chi_st' not in line):
        line = f.readline()
    
    chi_st = float(line.split()[2])
    fm.readChi(chi_st)
    

    while ('numOfSpecies' not in line):
        line = f.readline()
    
    n_species = int(line.split()[2])

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

def writeCSV(fname,fm):
    f = open(fname, 'w')
    header = ''
    for n in range(1,len(fm.name)):
        header += fm.name[n]+','
    header += fm.name[0] +'\n'

    f.write(header)
    
    n_grid = len(fm.data[0])

    for grid in range(n_grid):
        line = ''
        for n in range(1,len(fm.name)):
            line += fm.data[n][grid]+','
        line += fm.data[0][grid] +'\n'
        f.write(line)

    f.close()
    
def main():
    
    help = " Usage:\n" \
          +"   python3 fm2Cantera.py -dir <FM-Solution-dir>"

    if_list = []
    of_list = []
    
    if '-dir' in sys.argv:
        f_dir = sys.argv[sys.argv.index('-dir')+1]
        f_list = os.listdir(f_dir)
    else:
        print(help)
        sys.exit()

    os.chdir(f_dir)
    
    fms = []

    for fname in f_list:
        if 'chi' in fname:
            fms.append(flamelet())
            readFM(fname, fms[-1])
    os.chdir('../')
    
    outputDir = 'tables'

    if os.path.exists(outputDir):
        if os.listdir(outputDir):
            print(" Output Folder '"+ outputDir+"' is not empty!\n It's better to clean it up. \n Abort!")
            sys.exit()
    else:
        os.makedirs(outputDir)
    
    for n in range(len(fms)):
        fname = outputDir + '/'+'Table_'+'{:g}'.format(fms[n].chi_st)+'.csv'
        writeCSV(fname, fms[n])

    # get chi order 
    chi = []
    for n in range(len(fms)):
        chi.append(fms[n].chi_st)
    chi.sort()
    f= open('chi_parm','w')
    for n in range(len(chi)):
        f.write(str(chi[n])+'\n')
    f.close()



if __name__ == '__main__':
    main()
