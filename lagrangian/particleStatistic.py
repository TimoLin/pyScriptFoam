#!/usr/bin/env python3

# 2019/10/28 15:49:54  zt
# Post-Processing sampled Lagrangian data from CloudFunction:ParticleStatistic.

import numpy as np
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
                    UrGroup[dGroupLoc] += p[ind_nP]*np.power(p[ind_d],3.0)*(np.sqrt(p[ind_Ux+1]**2.0+p[ind_Ux+2]**2.0))
                    mGroup[dGroupLoc] += p[ind_nP]*np.power(p[ind_d],3.0)
                    nParticle[dGroupLoc] += p[ind_nP]
                UaGroup[-1] +=  p[ind_nP]*np.power(p[ind_d],3.0)*p[ind_Ux]
                UrGroup[-1] += p[ind_nP]*np.power(p[ind_d],3.0)*(np.sqrt(p[ind_Ux+1]**2.0+p[ind_Ux+2]**2.0))
                mGroup[-1] += p[ind_nP]*np.power(p[ind_d],3.0)
                nParticle[-1] += p[ind_nP]
 
        if nParticle[-1] > 0:
            mean_d10 = d1/nParticle[-1]
            mean_d32 = d3/d2
        for n in range(len(UaGroup)):
            if nParticle[n] >0:
                UaGroup[n] /= mGroup[n]
                UrGroup[n] /= mGroup[n]

        d_Profile.append(mean_d10)
        d32_Profile.append(mean_d32)
        Ua_Profile.append(UaGroup)
        Ur_Profile.append(UrGroup)
        nP_Profile.append(nParticle)

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

    line = 'variables="r","d","d32",'+header+'\n'
    f.write(line)
    line = 'zone t="'+plane+'"\n'
    f.write(line)
    for n in range(len(rData)):
        line = data2line([rData[n],d_Profile[n]*np.power(10,6),d32_Profile[n]*np.power(10,6)]) \
             + data2line(Ua_Profile[n]) \
             + data2line(Ur_Profile[n]) \
             + data2line(nP_Profile[n])
        f.write(line+'\n')
    f.close()

def main():
    
    pwd = os.listdir()

    # The 'sprayCloud' may be different
    cloud = './postProcessing/lagrangian/sprayCloud/'
    if 'postProcessing' not in pwd:
        print("Error")
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

        process(plane, var,data)
        print(plane)

if __name__ == '__main__':
    main()
