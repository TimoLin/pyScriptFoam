#!/usr/bin/env python3

# 2019/10/28 15:49:54  zt
# Post-Processing sampled Lagrangian data from CloudFunction:ParticleStatistic.

import numpy as np
import argparse
import sys
import os

rStep = 0.5

dGroup = [10,20,30,40,50]#um

def isFloat(x):
    # check whether the string consists of float only
    try:
        float(x)
        return True
    except ValueError:
        return False

def strClean(s):
    strNew = s.replace("(","")
    strNew = strNew.replace(")","")
    strNew = strNew.replace("#","")
    return strNew

def data2line(data):
    line = ''
    for temp in data:
        line += str(temp)+'\t'
    #line += '\n'
    return line

def data2lineCSV(data):
    line = ''
    for temp in data:
        line += str(temp)+','
    return line

def radial(rEnd):
    #rStep = 0.2 #mm
    r = []
    if (int(rEnd/rStep) > 0):
        n = int(rEnd/rStep)+1
        for i in range(n):
            r.append(0.0+rStep*i)
    return r

def loc(dlist,d):
    if d <= dlist[0]:
        return 0
    if d > dlist[-1]:
        return -1
    for n in range(1,len(dlist)):
        if d > dlist[n-1] and d<=dlist[n]:
            return n

def cylinder(x1,x2,Ux1,Ux2):
    theta = np.arctan2(x2,x1)
    Ur = Ux1*np.cos(theta)+Ux2*np.sin(theta)


def readData(file):

    f = open(file,'r')
    lines = f.readlines()
    
    header = strClean(lines[0])
    variables = header.split()
    subdata = []
    for line in lines[1:]:
        newLine = strClean(line)
        dataLine = []
        for temp in newLine.split():
            if isFloat(temp):
                dataLine.append(float(temp))
        subdata.append(dataLine)

    return variables, subdata

def writeScatter(plane, variables, data):

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

    f = open('./postProcessing/'+plane+'-pdf.dat','w')
    line = 'Variables="d", "Counts PDF", "Volume PDF"\n'
    f.write(line)
    for n in range(len(dGroup)):
        line = str(dGroup[n])+"\t"+str(PSD[n])+"\t"+str(PDF[n])+"\n"
        f.write(line)
    f.close()


def process(plane, variables, data):

    indx = variables.index("Px")
    indy = variables.index("Py")
    indz = variables.index("Pz")
    ind_nP = variables.index("nParticle")
    ind_d = variables.index("d")
    ind_Ux = variables.index("Ux")

    rData = radial(10.0) #mm
    
    d_Profile = []
    d32_Profile = []

    Ua_Profile = []
    Ur_Profile = []
    nP_Profile = []

    for i in range(len(rData)):
        if i == 0:
            r1 = 0
            r2 = rStep/2.0
        else:
            r1 = rData[i]-rStep/2.0 ## lower bound
            r2 = rData[i]+rStep/2.0 ## upper bound

        UaGroup = [0.0]*(len(dGroup)+1) # +1 for global average
        UrGroup = [0.0]*(len(dGroup)+1)
        mGroup = [0.0]*(len(dGroup)+1)
        nParticle = [0.0]*(len(dGroup)+1)

        d1 = 0.0
        d2 = 0.0
        d3 = 0.0
 
 
        for p in data: # p means particle
            r = np.sqrt(p[indy]**2+p[indz]**2)*1000
            if (r >= r1 and r <= r2):
 
                d1 += p[ind_nP]*p[ind_d]
                d2 += p[ind_nP]*np.power(p[ind_d],2.0)
                d3 += p[ind_nP]*np.power(p[ind_d],3.0)

                dGroupLoc = loc(dGroup, p[ind_d]*np.power(10,6))
                if (dGroupLoc != -1):
                    UaGroup[dGroupLoc] += p[ind_nP]*np.power(p[ind_d],3.0)*p[ind_Ux]
                    UrGroup[dGroupLoc] += p[ind_nP]*np.power(p[ind_d],3.0)*(
                            # See issue #1 for more information
                            (p[ind_Ux+1]*p[indy]+p[ind_Ux+2]*p[indz])/(r/1000)
                            )
                    mGroup[dGroupLoc] += p[ind_nP]*np.power(p[ind_d],3.0)
                    nParticle[dGroupLoc] += p[ind_nP]
                UaGroup[-1] +=  p[ind_nP]*np.power(p[ind_d],3.0)*p[ind_Ux]
                UrGroup[-1] += p[ind_nP]*np.power(p[ind_d],3.0)*(
                            (p[ind_Ux+1]*p[indy]+p[ind_Ux+2]*p[indz])/(r/1000)
                            )
                mGroup[-1] += p[ind_nP]*np.power(p[ind_d],3.0)
                nParticle[-1] += p[ind_nP]
 
        if nParticle[-1] > 0:
            mean_d10 = d1/nParticle[-1]
            mean_d32 = d3/d2
        else:
            mean_d10 = 0.0
            mean_d32 = 0.0
        for n in range(len(UaGroup)):
            if nParticle[n] >0:
                UaGroup[n] /= mGroup[n]
                UrGroup[n] /= mGroup[n]
            else:
                UaGroup[n] = 0.0
                UrGroup[n] = 0.0


        d_Profile.append(mean_d10)
        d32_Profile.append(mean_d32)
        Ua_Profile.append(UaGroup)
        Ur_Profile.append(UrGroup)
        nP_Profile.append(nParticle)
    if '-csv' in sys.argv:
        writeCSV(plane, rData, d_Profile, d32_Profile, Ua_Profile, Ur_Profile, nP_Profile)

    if '-tecplot' in sys.argv:
        writeTecplot(plane, rData, d_Profile, d32_Profile, Ua_Profile, Ur_Profile, nP_Profile)

def writeCSV(plane, rData, d_Profile, d32_Profile, Ua_Profile, Ur_Profile, nP_Profile):
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
    header += 'nP-dall'

    f.write(header+"\n")

    for n in range(len(rData)):
        line = data2lineCSV([rData[n]/10.5,d_Profile[n]*np.power(10,6),d32_Profile[n]*np.power(10,6)]) \
             + data2lineCSV(Ua_Profile[n]) \
             + data2lineCSV(Ur_Profile[n]) \
             + data2lineCSV(nP_Profile[n])
        line = line[:-1]
        f.write(line+'\n')
    f.close()
    

def writeTecplot(plane, rData, d_Profile, d32_Profile, Ua_Profile, Ur_Profile, nP_Profile):
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
    header += '"nP"'

    line = 'variables="r/D","d","d32",'+header+'\n'
    f.write(line)
    line = 'zone t="'+plane+'"\n'
    f.write(line)
    for n in range(len(rData)):
        line = data2line([rData[n]/10.5,d_Profile[n]*np.power(10,6),d32_Profile[n]*np.power(10,6)]) \
             + data2line(Ua_Profile[n]) \
             + data2line(Ur_Profile[n]) \
             + data2line(nP_Profile[n])
        f.write(line+'\n')
    f.close()

def main():

    help = "python3 particleStatistic.py [-help] [-process] [-pdf] [-csv] [-tecplot]\n" \
            "  -process: Post-process sampled lagrangian data and get radial profiles\n" \
            "  -pdf:     Get droplete droplet size PDF and volume PDF for sampled planes\n" \
            "  -help:    Print this message"
    if "-help" in sys.argv:
        print(help)
        sys.exit()
    
    if "-process" in sys.argv:
        flagProcess = True
    else:
        flagProcess = False

    if "-pdf" in sys.argv:
        flagPdf = True
    else:
        flagPdf = False
    
    if (not flagProcess) and (not flagPdf):
        print(" It seems that you didn't give me any flags\n")
        print(help)
        sys.exit()


    pwd = os.listdir()

    # The 'sprayCloud' may be different
    cloud = './postProcessing/lagrangian/sprayCloud/'
    if 'postProcessing' not in pwd:
        print("Fatal Error: Can't find 'postProcessing' in current folder!" )
        sys.exit()

    planes = os.listdir(cloud)
    times = os.listdir(cloud+planes[0])
    
    for plane in planes:
        data = []
        # gather particles in the sampled plane
        for time in times:
            fileName = cloud+'/'+plane+'/'+time+'/statistic.dat'
            var, subdata = readData(fileName)
            data.extend(subdata)
            #print(time)

        if (flagProcess):
            process(plane, var,data)
        if (flagPdf):
            dropletSizePDF(plane, var, data)

        print("Done post-processing: ",plane)

if __name__ == '__main__':
    main()
