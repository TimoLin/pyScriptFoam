#!/usr/bin/python3

# Workflow:
#   1. Fluent: Using Reynolds Stress model to simulate a pipe flow until it's convergent
#   2. Fluent: Output the outlet data using ASCII format with Location(Cell Center) and 
#              Delimiter(Comma). Quantities include velocity components, Reynolds stress
#              components, Turbulent kinetic energy(k) and dissipation rate(epsilon)
#   3. Use this script to generate L, R, points and ref files in foam format

# Note:
#   This script is designed for decayingTurbulenceInflowGeneratorMod method.
#   Interpolation is not introduced here, since this bc has a default method
#   of plannarInterpolation for the mapped data.

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
    ## Rotate velocity components
    #for n, vel in enumerate(ref):
        #ref[n] = 

    # 3. Reynolds stress file
    ## R(Rxx, Rxy, Rxz, Ryy, Ryz, Rzz)
    R = np.array(
            [data["uureynoldsstress"],data["uvreynoldsstress"],data["uwreynoldsstress"],
                data["vvreynoldsstress"],data["vwreynoldsstress"],data["wwreynoldsstress"]]
            )

    # 4. Length scale file
    L = data["turbkineticenergy"]
    for n,k in enumerate(L):
        L[n] = np.power(k,1.5)/data["turbdissrate"][n]

    # Output files

    foamWriter("vectorField","points", points, len(points[0]))
    foamWriter("vectorField","ref", ref, len(points[0]))
    foamWriter("symmTensorField","R", R , len(points[0]))
    foamWriter("scalarField","L", L , len(points[0]))


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
