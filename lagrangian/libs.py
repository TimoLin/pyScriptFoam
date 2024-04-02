# 2021/11/08 22:02:00  zt

import numpy as np
import sys
import os

from particle_readers import *

def writeScatter(plane, variables, data):
    """Write scatter field in tecplot format
    Arguments:
        plane:     plane's name
        variables: variables' list
        data:      droplet data array 

    Returns:
        None
    """

    indx = variables.index("Px")
    indy = variables.index("Py")
    indz = variables.index("Pz")
    ind_nP = variables.index("nParticle")
    ind_d = variables.index("d")
    ind_Ux = variables.index("Ux")

    f = open('./postProcessing/'+plane+'-scatter.dat','w')
    line = "Variables='x','y','z','d'\n"
    f.write(line)
    for p in data:
        line = str(p[indx])+"\t"+str(p[indy])+'\t'+str(p[indz])+"\t"+str(p[ind_d])+"\n"
        f.write(line)
    f.close()
    return

def dropletSizePDF(plane, variables, data):
    """Calculate droplet PDF in the sampled plane

    Arguments:
        plane:     plane's name
        variables: variables' list
        data:      droplet data array 

    Returns:
        None
    """
    ind_np = variables.index("nParticle")
    ind_d = variables.index("d")
    
    # Will be adjusted for user defined parameters
    dStep = 5
    dGroup = list(range(0,85,5)) # in um

    PSD = [0.0]*len(dGroup) # Particle size distributions, PSD or counts PDF
    PDF = [0.0]*len(dGroup) # Volume probability density funciton

    for p in data:
        for n, d in enumerate(dGroup):
            d1 = (d - dStep/2.0)/(10**6)
            d2 = (d + dStep/2.0)/(10**6)
            if (p[ind_d] >= d1) and (p[ind_d] < d2):
                PSD[n] += p[ind_np]
                PDF[n] += p[ind_d]**3.0 * p[ind_np]

    # Normalize
    PSD /= np.sum(PSD)
    PDF /= np.sum(PDF)
    
    '''Tecplot format
    f = open('./postProcessing/'+plane+'-pdf.dat','w')
    line = 'Variables="d", "Counts PDF", "Volume PDF"\n'
    f.write(line)
    for n in range(len(dGroup)):
        line = str(dGroup[n])+"\t"+str(PSD[n])+"\t"+str(PDF[n])+"\n"
        f.write(line)
    f.close()
    '''
    # CSV format
    f = open('./postProcessing/pdf-'+plane+'.csv','w')
    line = 'd, Counts-PDF, Volume-PDF\n'
    f.write(line)
    for n in range(len(dGroup)):
        line = str(dGroup[n])+","+str(PSD[n])+","+str(PDF[n])+"\n"
        f.write(line)
    f.close()

    return

def writeCSV(plane, dGroup, rData, d_Profile, d32_Profile, Ua_Profile, Ur_Profile, nP_Profile, T_Profile, volFlux_Profile):
    """Write the processed data in CSV format

    Arguments:
        plane:       plane's name 
        rData:       radial locations
        d_Profile:   D10 profiles
        d32_Profile: D32 profiles
        Ua_Profile:  Axial velocity profile
        Ur_Profile:  Radial velocity profile
        nP_Profile:  Droplets number profile
        T_Profile:   Droplet temperature profile
        volFlux_Profile: Volume flux profile

    Return:
        None

    """
    f = open('./postProcessing/'+plane+'.csv','w')
    header = 'r/D,d,d32,'
    for d in dGroup:
        header += 'Ua-d'+str(d)+','
    header += 'Ua-dall,'
    for d in dGroup:
        header += 'Ur-d'+str(d)+','
    header += 'Ur-dall,'
    for d in dGroup:
        header += 'nP-d'+str(d)+','
    header += 'nP-dall,'
    header += 'T,'
    header += "VolFlux"

    f.write(header+"\n")

    for n in range(len(rData)):
        line = data2lineCSV([rData[n],d_Profile[n]*np.power(10,6),d32_Profile[n]*np.power(10,6)]) \
             + data2lineCSV(Ua_Profile[n]) \
             + data2lineCSV(Ur_Profile[n]) \
             + data2lineCSV(nP_Profile[n]) \
             + data2lineCSV([T_Profile[n]])\
             + data2lineCSV([volFlux_Profile[n]])
        line = line[:-1]
        f.write(line+'\n')
    f.close()
    

def writeTecplot(plane, dGroup, rData, d_Profile, d32_Profile, Ua_Profile, Ur_Profile, nP_Profile, T_Profile, volFlux_Profile):
    """Write the processed data in Tecplot format

    Arguments:
        plane:       plane's name 
        rData:       radial locations
        d_Profile:   D10 profiles
        d32_Profile: D32 profiles
        Ua_Profile:  Axial velocity profile
        Ur_Profile:  Radial velocity profile
        nP_Profile:  Droplets number profile
        T_Profile:   Droplet temperature profile
        volFlux_Profile: Volume flux profile

    Return:
        None

    """

    f = open('./postProcessing/'+plane+'.dat','w')
    header = ''
    for d in dGroup:
        header += '"Ua'+str(d)+'",'
    header += '"Ua",'
    for d in dGroup:
        header += '"Ur'+str(d)+'",'
    header += '"Ur",'
    for d in dGroup:
        header += '"nP'+str(d)+'",'
    header += '"nP,"'
    header += '"T",'
    header += "VolFlux"

    line = 'variables="r/D","d","d32",'+header+'\n'
    f.write(line)
    line = 'zone t="'+plane+'"\n'
    f.write(line)
    for n in range(len(rData)):
        line = data2line([rData[n],d_Profile[n]*np.power(10,6),d32_Profile[n]*np.power(10,6)]) \
             + data2line(Ua_Profile[n]) \
             + data2line(Ur_Profile[n]) \
             + data2line(nP_Profile[n]) \
             + data2line([T_Profile[n]])\
             + data2line([volFlux_Profile[n]])
        f.write(line+'\n')
    f.close()

