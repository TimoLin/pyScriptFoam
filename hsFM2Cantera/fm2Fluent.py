'''
Convert FlameMaster solutions to Fluent format.
'''

import sys
import os
from fmReader import *
import numpy as np

def headerString(chi):

    header  = "HEADER\n"
    header += "STOICH_SCADIS    "+str(chi)+"\n"
    header += "NUMOFSPECIES	53\n"
    header += "GRIDPOINTS	141\n"
    header += "STOICH_Z	3.528931E-01\n"
    header += "PRESSURE	1.006250E+05\n"
    header += "BODY\n"
    return header

def writeBlock(f,d):
    '''Write data block
    '''
    nGrid = len(d)
    for i in range(nGrid):
        if ((i+1)%5 == 0):
            f.write(str(d[i])+"\n")
        else:
            f.write(str(d[i])+"\t")
    f.write("\n")
        

def flaWriter(fName, fms):
    '''Fluent flamelet file writer
    '''
    with open(fName,"w") as f:
        for fm in fms:
            f.write(headerString(fm.chi_st))
            f.write("Z\n")
            writeBlock(f,fm.data[0])
            f.write("TEMPERATURE\n")
            writeBlock(f,fm.data[1])
            for n in range(53):
                f.write("massfraction-"+fm.name[n+2]+"\n")
                writeBlock(f,fm.data[n+2])
            #f.write("PREMIX_YCDOT\n")
            #writeBlock(f,fm.data[-1])
            f.write("\n")

    return

def main():
    '''Main function
    '''

    if '-dir' in sys.argv:
        root = sys.argv[sys.argv.index('-dir')+1]
    else:
        print(" Error!\n FM solutions folder should be given to me!")
        sys.exit()

# Read flamelet solutions
    fms = []
    for fname in os.listdir(root):
        if ('chi' in fname) and ("noC" not in fname) and ("swp" not in fname):
            flamelet_name = root+'/'+fname
            fm = flamelet()
            readFM(flamelet_name,fm)
            fms.append(fm)

    # Sort flamelet solutions by scalar disspation rate
    chi = [fm.chi_st for fm in fms]
    ind = np.argsort(chi)
    flamelets = [fms[i] for i in ind]

    #for fm in flamelets:
        #print(fm.chi_st)

    # Wrap all fm solutions into one fla file
    outputFileName = "sdf.fla"
    flaWriter(outputFileName,flamelets)

if __name__ == "__main__":
    main()
