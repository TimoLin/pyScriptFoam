# 2024/10/24 17:26:34  zt
'''lagrangianToCsv.py
This script is used to convert the lagrangian data (in OpenFOAM ascii format)
to csv format.
In Paraview:
    - load csv
    - Apply Filters: Table to Points
    - Treat them as lagrangian droplets
'''

import os
import sys

import numpy as np

fieldClass = {
        'labelField': 'label',
        'scalarField': 'scalar',
        'vectorField': 'vector',
        'Cloud<passiveParticle>': 'vector',
        }
vectors = ["positions", "U", "UTurb"]

def readFile(file):
    '''
    Read the given file under lagrangian folder
    '''
    key = file.split("/")[-1]
    print("Reading data ", key, "...")
    with open(file,'r') as f:
        lines = f.readlines()

        n = 0
        ns = 0
        for n, line in enumerate(lines):
            if "class" in line:
                _type = line.split()[-1]
                _type = _type.replace(";", "")
                data_type = fieldClass[_type]
            if line.startswith("("):
                ns = n
                break
        if (ns == 0):
            print("No data found in file")
            return key, data_type, None
        else:
            npoints = int(lines[ns-1])
            print("Number of points: ", npoints)

            ns = ns+1

            if data_type == 'scalar' or data_type == 'label':
                data = np.zeros(npoints)
                for i, line in enumerate(lines[ns:ns+npoints]):
                    data[i] = float(line.strip())
            elif data_type == 'vector':
                data = np.zeros((npoints, 3))
                for i in range(npoints):
                    line = lines[ns+i]
                    _data = line.replace("(", "").replace(")", "").split()
                    for j in range(3):
                        data[i,j] = float(_data[j])
            return key, data_type, data

def main():

    # List the given path
    path = sys.argv[1]
    cloud_path = os.path.join(path, "sprayCloud")
    files = os.listdir(cloud_path)

    # Create a new folder to store the csv file
    Data = {}
    for file in files:
        file_name = os.path.join(cloud_path, file)
        key, data_type, data = readFile(file_name)
        if data is not None:
            if data_type == 'vector':
                if key == "positions":
                    Data.update({"x": data[:,0]})
                    Data.update({"y": data[:,1]})
                    Data.update({"z": data[:,2]})
                elif key == "U":
                    Data.update({"Ux": data[:,0]})
                    Data.update({"Uy": data[:,1]})
                    Data.update({"Uz": data[:,2]})
                elif key == "UTurb":
                    Data.update({"UTurbx": data[:,0]})
                    Data.update({"UTurby": data[:,1]})
                    Data.update({"UTurbz": data[:,2]})
            else:
                Data.update({key: data})

    # Write the data to one csv file
    csv_file = os.path.join(path, "lagrangian.csv")
    with open(csv_file, 'w') as f:
        header = ",".join(Data.keys())+"\n"
        f.write(header)
        for i in range(len(Data["x"])):
            line = ",".join([str(Data[key][i]) for key in Data.keys()])+"\n"
            f.write(line)


    return
if __name__ == "__main__":
    main()
