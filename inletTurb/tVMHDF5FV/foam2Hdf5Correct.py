import os
import numpy as np
import h5py
from mpi4py import MPI
from readers import read_structured_points_foamfile
from readers import read_structured_velocity_foamfile
import argparse
import time

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

    #parser.add_argument('--nsamples',
                        #type=str,
                        #help='The number of the sampled time data.',
                        #required=True)
    parser.add_argument('--nMean',
                        type=str,
                        help='Inital averaged data: nMean[0], Forcing profile data: nMean[1]. Sampling data: nMean[2]. eg: "2000,4000,4000"',
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
    #nSamples = int(args.nsamples)

    nMean = args.nMean.split(",")
    nInitial = int(nMean[0])
    nForce = int(nMean[1])
    nSamples = int(nMean[2])

    # Total time files to be read
    nTimes = nInitial+nForce+nSamples

    fileName = args.filename
    normal = args.norm
    normVec = np.array([int(normal[0]), int(normal[1]),int(normal[2])])
    loc= float(args.location)

# start timestamp
    start_time = time.time()

# Case root dir, postProcessing dir, "surfaceSampling" or "sampledSurface"
    dataDir = os.path.join( precursorCaseDir, "postProcessing",
                            "surfaceSampling")

# Grab the existing times and sort
    times = os.listdir(dataDir)
    times = np.sort(times)   

    if len(times) >= nTimes:
        times = times[0:nTimes]
    else:
        print(" postProcessing/surfaceSampling data contains:",times.size,' files, less than needed: ',nTimes,' files!')
        return

# Read in the points
## "faceCenters" or "points"
    #[pointsX,pointsY,pointsZ] = read_structured_points_foamfile(
    points = read_structured_points_foamfile(
        os.path.join(dataDir, times[0], surfaceName, "points"), normVec, loc
        )

    nPoints = len(points[:,0])


##  Mean profile related arrays
    meanU = np.arange(nPoints,dtype=float)
    meanUP2 = np.arange(nPoints,dtype=float)

    meanU_New = np.arange(nPoints,dtype=float)
    meanUP2_New = np.arange(nPoints,dtype=float)

    meanU[:] = 0.0
    meanUP2[:] = 0.0

    meanU_New[:] = 0.0
    meanUP2_New[:] = 0.0


# Allocate arrays for the fluctuations
    if rank == 0:
        if os.path.isfile(fileName):
            print("HDF5 file already exists. It it will be overwritten.")
            os.remove(fileName)

    dbFile = h5py.File(fileName, 'a')
    
    dbFile.create_dataset("points",data=points)

    dbFile.create_dataset("times", data=[float(times[i])-float(times[nInitial+nForce])
                                                for i in range(nInitial+nForce,nTimes)])
    
    velocity = dbFile.create_dataset("velocity",(nSamples,nPoints,3),
                                        dtype=np.float64)

    print("Sampled data contains:",nPoints,"points")

    dbFile.attrs["nPoints"] = nPoints

    readFunc = read_structured_velocity_foamfile(dataDir, surfaceName)
    
    for n in range(len(times)):
        if (  np.mod(n,int(len(times)/20)) ==0 ):
            print(" Converted about "+ "{:.1f}".format(n/len(times)*100)+"%")            
        nS = n+1

        [uXVal, uYVal, uZVal] = readFunc(times[n])

        if n < nInitial:
            # calculate 'good' mean value
            meanU = (meanU*(nS-1)+uXVal)/nS
            meanUP2 = (meanUP2*(nS-1)+np.square(uXVal-meanU))/nS
        else: 
            # start force velocity profile
            for i in range(nPoints):
                # r = sqrt(y^2+z^2)
                r = np.sqrt(points[i,1]**2+points[i,2]**2)
                u, rms = uProfile(r)
                uXVal[i] = rms/(np.sqrt(meanUP2[i]))*(uXVal[i]-meanU[i])+u
            meanU = (meanU*(nS-1)+uXVal)/nS
            meanUP2 = (meanUP2*(nS-1)+np.square(uXVal-meanU))/nS

            if n >= nInitial+nForce:
                nN = n-(nInitial+nForce)+1
                meanU_New = (meanU_New*(nN-1)+uXVal)/nN
                meanUP2_New = (meanUP2*(nN-1)+np.square(uXVal-meanU_New))/nN
                
                # start taking samples
                nData = n-(nInitial+nForce)
                velocity[nData, :, 0] = uXVal
                velocity[nData, :, 1] = uYVal
                velocity[nData, :, 2] = uZVal 

    if rank == 0:
        print("Process 0 done, waiting for the others...")

    dbFile.close()
    
    # Write profile compare files
    f = open('profile.csv','w')
    f.write("r,U,Urms,U-Tail,Urms-Tail\n")
    rD = np.arange(50,dtype=float)
    u1 = np.arange(50,dtype=float)
    u2 = np.arange(50,dtype=float)
    uN1 = np.arange(50,dtype=float)
    uN2 = np.arange(50,dtype=float)
    nP = np.arange(50,dtype=float)
    u1[:] = 0
    u2[:] = 0
    uN1[:] = 0
    uN2[:] = 0
    nP[:] = 0
    for i in range(len(rD)):
        rD[i] = 0.0036/len(rD)*(i+1)
    for n in range(50):
        for i in range(nPoints):
            r = points[i,1]**2.0+points[i,2]**2
            r = np.sqrt(r)
            if r >= rD[n]-0.0036/50 and r<=rD[n]+0.0036/50:
                u1[n] += meanU[i]
                u2[n] += np.sqrt(meanUP2[i])
                uN1[n] += meanU_New[i]
                uN2[n] += np.sqrt(meanUP2_New[i])
                nP[n] += 1
    for n in range(50):
        if nP[n] > 0:
            u1[n] /= nP[n]
            u2[n] /= nP[n]
            uN1[n] /= nP[n]
            uN2[n] /= nP[n]
        line = str(rD[n]/0.0072)+","+str(u1[n])+","+str(u2[n])+","+str(uN1[n])+","+str(uN2[n])+"\n"
        f.write(line)
    f.close()


 # end timestamp
    end_time = time.time()

    print("Done! Execution time: %.2f s."%(end_time-start_time))   

def uProfile(r):
    rP = [0, 0.0005, 0.001,0.0015,0.002,0.0025,0.003,0.0035,0.0036]
    uP = [62.95434,62.54625,61.36625,59.21267,56.73949,53.34622,48.80521,41.9943,0]
    rmsP = [2.47555400062289,2.49604099926263,2.87647200055902,3.52868200040752,3.99146699973832,4.54595099951594,4.9499979999996,6.1157099996648,0]
    
    if r >= rP[-1]:
        u = uP[-1]
        rms = rmsP[-1]
        return u, rms

    # linear interpolation
    for n in range(len(rP)):
        if r>= rP[n] and r< rP[n+1]:
            u = (uP[n+1]-uP[n])/(rP[n+1]-rP[n])*(r-rP[n]) + uP[n]
            rms = (rmsP[n+1]-rmsP[n])/(rP[n+1]-rP[n])*(r-rP[n]) + rmsP[n]
    return u, rms


if __name__ == "__main__":
    main()
