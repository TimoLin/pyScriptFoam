
import numpy as np
import sys, os
import argparse

def main():
    

    parser = argparse.ArgumentParser(
                description="A script to generate FilteredNoiseInflowGenerator boundaryData files."
                )
    parser.add_argument('--input',
                        type=str,
                        help='The outlet patch data in Tecplot text format',
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

    varName = []
    size = 0
    nStart = 0
    with open(dataFile) as f:
        while True:
            line = f.readline()
            nStart += 1
            if line[0] in 'V"':
                varName.append( (line.replace('\n','')).replace('"','') )
            if 'Nodes=' in line:
                size = int(line[line.index("=")+1:line.index(",")])
            if "DT=" in line:
                break
    
    varName[0] = varName[0][12:]

    # construct varname dict
    varDict = {}
    for n, var in enumerate(varName):
        varDict.update( {var:n} )
    print(varDict)

    data = np.genfromtxt(dataFile,delimiter=" ",skip_header=nStart,max_rows=size)

    xInd = varName.index("X")
    yInd = varName.index("Y")
    zInd = varName.index("Z")
    uInd = varName.index("X Velocity")
    vInd = varName.index("Y Velocity")
    wInd = varName.index("Z Velocity")
    kInd = varName.index("Turbulent Kinetic Energy")
    eInd = varName.index("Turbulent Dissipation Rate")

    # 1. Points file
    points = np.array(
            [ data[:,varDict["X"]],data[:,varDict["Y"]],data[:,varDict["Z"]]]
            )
    ## TRanslate coordinates
    one = np.ones(3)
    for n in range(len(points[0])):
        temp = [points[0][n],points[1][n],points[2][n]]
        temp = temp*(one-normVec)+loc*normVec
        points[0][n] = temp[0]
        points[1][n] = temp[1]
        points[2][n] = temp[2]

    # 2. Ref file (velocity components)
    ref = np.array(
            [data[:,varDict["X Velocity"]],data[:,varDict["Y Velocity"]],data[:,varDict["Z Velocity"]]]
            )

    # 3. Reynolds stress file
    ## R(Rxx, Rxy, Rxz, Ryy, Ryz, Rzz)
    R = np.array(
            [data[:,varDict["UU Stress"]], data[:,varDict["UV Stress"]],data[:,varDict["UW Stress"]],
                data[:,varDict["VV Stress"]],data[:,varDict["VW Stress"]], data[:,varDict["WW Stress"]] ]
            )

    # 4. Length scale file
    L = data[:,varDict["Turbulent Kinetic Energy"]]
    for n,k in enumerate(L):
        L[n] = np.power(k,1.5)/data[n,varDict["Turbulent Dissipation Rate"]]
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

if __name__ == "__main__":
    main()
