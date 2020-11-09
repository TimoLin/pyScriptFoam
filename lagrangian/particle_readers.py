
# 2020/09/22 15:08:16  zt

"""Modules for reading the Lagrangian data created by CloudFunction:ParticleStatistic.
"""

import numpy as np

def isFloat(x):
    '''
    check whether the string consists of float only
    '''
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

def radial(rStep,rEnd):
    # in mm
    r = np.array([])
    if (int(rEnd/rStep) > 0):
        n = int(rEnd/rStep)+1
        r = np.zeros(n)
        for i in range(n):
            r[i] = 0.0+rStep*i
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

def radialVel(x,U,norm,r):
    res = np.ones(3)-norm
    Ur = (x[0]*res[0]*U[0]+x[1]*res[1]*U[1]+x[2]*res[2]*U[2])/(r/1000)
    return Ur

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


