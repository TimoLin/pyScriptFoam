
# 2020/09/22 15:08:16  zt

"""Modules for reading the Lagrangian data created by CloudFunction:ParticleStatistic.
"""

import numpy as np

def isFloat(x):
    """Check whether the string contains float only
    
    Parameters 
    ---------
    x : str
        The string we want to check

    Returns
    -------
    True/False: Bool
        True if it can convert to float
        False if it cann't convert to float
    """
    try:
        float(x)
        return True
    except ValueError:
        return False


def strClean(s):
    """Remove '()#' in the string

    Parameters
    ----------
    s : str

    Returns
    -------
    strNew : str
    """
    strNew = s.replace("(","")
    strNew = strNew.replace(")","")
    strNew = strNew.replace("#","")
    return strNew

def data2line(data):
    """Convert given list to string with 'Tab' as separator.
    Typically this is for Tecplot plt format output
    """
    line = ''
    for temp in data:
        line += str(temp)+'\t'
    #line += '\n'
    return line

def data2lineCSV(data):
    """Convert given list to string with ',' as separator.
    Typically this is for CSV format output
    """
    line = ''
    for temp in data:
        line += str(temp)+','
    return line

def radial(rStep,rEnd):
    """Construct Radial profile array

    Parameter
    ---------
    rStep : float
        Length step for radial profile
    rEnd : float
        Max Radius

    Returns
    -------
    r : Numpy array
        Radial locations array
    """
    # in mm
    r = np.array([])
    if (int(rEnd/rStep) > 0):
        n = int(rEnd/rStep)+1
        r = np.zeros(n)
        for i in range(n):
            r[i] = 0.0+rStep*i
    return r

def loc(dlist,d):
    """Find the location of the given diameter in the d group

    Parameter
    ---------
    dlist : list
        Diameter group list
    d : float
        Diameter of the particle we are processing
    """
    if d <= dlist[0]:
        return 0
    if d > dlist[-1]:
        return -1
    for n in range(1,len(dlist)):
        if d > dlist[n-1] and d<=dlist[n]:
            return n

def cylinder(x1,x2,Ux1,Ux2):
    """Convert Cartesian to Cylinder

    Parameter
    ---------
    x1,x2 : float
        2d coordinate of the point
    Ux1,Ux2 : float
        2d coordinate velocity of the point
        
    Returns
    -------
    theta : float
        Cylinder coordinate theta, in raidan
    Ur : float
        Cylinder coordinate Radial velocity
    """
    theta = np.arctan2(x2,x1)
    Ur = Ux1*np.cos(theta)+Ux2*np.sin(theta)
    return theta, Ur

def radialVel(x,U,norm,r):
    """Convert Cartesian to Cylinder and get radial velocity

    Parameters
    ----------
    x : float
        3d coordinate of the particle
    U : float
        3d velocity of the particle
    norm : numpy array (3*1)
        Normal direction of the plane or the axial direction
    r : float
        Radial loction of the particle, in Milimeter(mm)

    Returns
    ------
    Ur : float
        Radial velocity of the particle
    """
    res = np.ones(3)-norm
    Ur = (x[0]*res[0]*U[0]+x[1]*res[1]*U[1]+x[2]*res[2]*U[2])/(r/1000)
    return Ur

def readData(file):
    """Read sampled Lagrangian data

    Parameters
    ----------
    file : str
        Sampled data file to be read

    Returns
    -------
    varialbes : list(str)
        Variable names
    subdata : list
        Parcel data in the sampled data file
        Data structure:
        [
            [x,y,z,...  ], # 1st parcel
            [x,y,z,...  ], # 2nd parcel
            ...
            [x,y,z,...  ]  # Last parcel
        ]

    """

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


