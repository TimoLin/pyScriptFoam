"""
Generate Digital Filtering BC files using Experimental data 
"""
import numpy as np
import sys, os
import argparse

def main():

    parser = argparse.ArgumentParser(
                description="A script to generate FilteredNoiseInflowGenerator boundaryData files."
                )
    parser.add_argument('--input',
                        type=str,
                        help='The outlet patch data in ASCII format',
                        required=True
                        )
    parser.add_argument('--norm',
                        type=str,
                        help='Normal direction of the main simulation inlet patch',
                        default='100',
                        required=False
                        )
    parser.add_argument('--location',
                        type=float,
                        help='Start axial location of the main simulation inlet patch',
                        default=0.0,
                        required=False
                        )

    args = parser.parse_args()

    dataFile = args.input
    norm = args.norm
    normVec = np.array([int(norm[0]),int(norm[1]),int(norm[2])])
    loc = args.location

    data = np.genfromtxt(dataFile,dtype=float,delimiter=',',names=True)

    expFile = "/home/zt/Documents/ValidationCases/SandiaD/TUD_LDV_DEF/TUD_LDV_D.exit"
    profile = np.genfromtxt(expFile,dtype=float,skip_header=13)

    # 1. Points file
    points = np.array(
            [data["xcoordinate"],data["ycoordinate"],data["zcoordinate"]]
            )

    ## Translate corrdinates
    one = np.ones(3)
    #for n in enumerate(points[:,]):
    for n in range(len(points[0])):
        temp = [points[0][n],points[1][n],points[2][n]]
        temp = temp*(one-normVec)+loc*normVec
        points[0][n] = temp[0]
        points[1][n] = temp[1]
        points[2][n] = temp[2]


    # 2. Ref file (velocity components)
    ref = np.array(
            [data["xvelocity"],data["yvelocity"],data["zvelocity"]]
            )

    R = np.array(
            [data["uureynoldsstress"],data["uvreynoldsstress"],data["uwreynoldsstress"],
                data["vvreynoldsstress"],data["vwreynoldsstress"],data["wwreynoldsstress"]]
            )

    nPoints = len(points[0])

    for n in range(nPoints):
        r = np.sqrt(points[1][n]**2+points[2][n]**2)
        u, RR = uProfile(r,profile)
        ref[0,n] = u
        ref[1,n] = 0.0
        ref[2,n] = 0.0
        R[0,n] = RR[0]
        R[1,n] = RR[1]
        R[2,n] = RR[2]
        R[3,n] = RR[3]
        R[4,n] = RR[4]
        R[5,n] = RR[5]
    # 4. Length scale file
    L = data["turbkineticenergy"]
    for n,k in enumerate(L):
        L[n] = np.power(k,1.5)/data["turbdissrate"][n]

    # Output files

    foamWriter("vectorField","points", points, len(points[0]))
    foamWriter("vectorField","ref", ref, len(points[0]))
    foamWriter("symmTensorField","R", R , len(points[0]))
    foamWriter("scalarField","L", L , len(points[0]))


def uProfile(r,profile):

    D = 0.0072
    rD = profile[:,0]*D
    uP = profile[:,1]

    uR1 = profile[:,2]
    uR2 = profile[:,4]
    uR3 = profile[:,5]
    for i in range(len(rD)):
        if r>= 0.5*D:
           u = 0.0
           RR = [0.0,0.0,0.0,0.0,0.0,0.0]

    # linear interpolation
    for n in range(len(rD)):
        if r>= rD[n] and r< rD[n+1]:
            u = (uP[n+1]-uP[n])/(rD[n+1]-rD[n])*(r-rD[n]) + uP[n]
            R1 = (uR1[n+1]-uR1[n])/(rD[n+1]-rD[n])*(r-rD[n]) + uR1[n]        
            R2 = (uR2[n+1]-uR2[n])/(rD[n+1]-rD[n])*(r-rD[n]) + uR2[n]        
            R3 = (uR3[n+1]-uR3[n])/(rD[n+1]-rD[n])*(r-rD[n]) + uR3[n]        
            #RR = [R1,R3,R3,R2,R3,R2]
            RR = [R1,0.0,0.0,R2,0.0,R2]

    return u, RR


def foamWriter(fieldType, fieldName, field, size):
    header = "FoamFile\n{\n\tversion\t2.0;\n\tformat\tascii;\n\tclass\t"+ \
        fieldType+";\n\tobject\t"+fieldName+";\n}\n"
                
    f = open(fieldName,"w")
    f.write(header)
    f.write(str(size)+"\n")
    f.write("(\n")
    for n in range(size):
        if (fieldName != "L"):
            f.write(tensor2str(field[:,n]))
        else:
            f.write(str(field[n])+"\n")


    f.write(")\n")

def tensor2str(tensor):
    line = "("
    for t in tensor:
        line += " "+str(t)
    line += ")\n"
    return line

if __name__=="__main__":
    main()
