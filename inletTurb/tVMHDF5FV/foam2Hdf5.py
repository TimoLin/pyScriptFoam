

import os
import numpy as np
import h5py
from mpi4py import MPI
from readers import read_structured_points_foamfile
from readers import read_structured_velocity_foamfile
import argparse



def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nProcs = comm.Get_size()
# Define the command-line arguments
    parser = argparse.ArgumentParser(
                description="A utility for converting a database stored \
                            as a collection of foamFile-formatted files to \
                            a single HDF5 file."
                                    )

    parser.add_argument('--precursor',
                        type=str,
                        help='The location of the precusor case.',
                        required=True)
    parser.add_argument('--surface',
                        type=str,
                        help='The name of the surface that contains the data.',
                        required=True)
    parser.add_argument('--nsamples',
                        type=str,
                        help='The number of the sampled time data.',
                        required=True)
    parser.add_argument('--norm',
                        type=str,
                        help='Normal direction of the main surface patch.',
                        required=True)
    parser.add_argument('--location',
                        type=str,
                        help='Start axial location of the main surface patch.',
                        required=True)
    parser.add_argument('--filename',
                        type=str,
                        help='The name hdf5 file to create.',
                        required=True)

    args = parser.parse_args()
    
    precursorCaseDir = args.precursor
    surfaceName = args.surface
    nSamples = int(args.nsamples)
    fileName = args.filename
    normal = args.norm
    normVec = np.array([int(normal[0]), int(normal[1]),int(normal[2])])
    loc= float(args.location)


# Case root dir, postProcessing dir, "surfaceSampling" or "sampledSurface"
    dataDir = os.path.join( precursorCaseDir, "postProcessing",
                            "surfaceSampling")

# Grab the existing times and sort
    times = os.listdir(dataDir)
    times = np.sort(times)    

    if len(times) > nSamples:
        times = times[0:nSamples]

# Read in the points
## "faceCenters" or "points"
    #[pointsX,pointsY,pointsZ] = read_structured_points_foamfile(
    points = read_structured_points_foamfile(
        os.path.join(dataDir, times[0], surfaceName, "points"), normVec, loc
        )

    nPoints = len(points[:,0])

# Allocate arrays for the fluctuations
    if rank == 0:
        if os.path.isfile(fileName):
            print("HDF5 file already exists. It it will be overwritten.")
            os.remove(fileName)    

    dbFile = h5py.File(fileName, 'a')
    
    dbFile.create_dataset("points",data=points)

    dbFile.create_dataset("times", data=[float(times[i])-float(times[0])
                                                for i in range(times.size)])
    
    velocity = dbFile.create_dataset("velocity",(len(times),nPoints,3),
                                        dtype=np.float64)

    print(nPoints)

    dbFile.attrs["nPoints"] = nPoints

    readFunc = read_structured_velocity_foamfile(dataDir, surfaceName)

# Read in the fluctuations
    # Read in U
    for n in range(len(times)):
        if (  np.mod(n,int(len(times)/20)) ==0 ):
            print(" Converted about "+ "{:.1f}".format(n/len(times)*100)+"%")

        [uXVal, uYVal, uZVal] = readFunc(times[n])

        velocity[n, :, 0] = uXVal
        velocity[n, :, 1] = uYVal
        velocity[n, :, 2] = uZVal
    if rank == 0:
        print("Process 0 done, waiting for the others...")

    dbFile.close()

    print("Done")

if __name__ == "__main__":
    main()
