#!/usr/bin/env python3

# 2019/10/28 15:49:54  zt
# Post-Processing sampled Lagrangian data from CloudFunction:ParticleStatistic.

# This is as tutorial script to process sampled data from LES of EtF6.

import numpy as np
import argparse
import sys
import os

from particle_readers import *
from process import *
from libs import *


def getArgs():
    """ Define the command-line arguments
    Arguments:
        None
    Returns:
        args: Commandline arguments
    """
    parser = argparse.ArgumentParser(
                description = "Post-Processing sampled Lagrangian data from CloudFunction:ParticleStatistic."
                )

    parser.add_argument('--process',
                        help='Post-process sampled lagrangian data and get radial profiles',
                        action="store_true"
                        )

    parser.add_argument('--time',
                        type=str,
                        default='0:',
                        help='Time ranges',
                        required=False
                        )

    parser.add_argument('--diameter',
                        type=float,
                        help='Normalized Reference diamter or length for the case (mm)',
                        required=True
                        )

    parser.add_argument('--rMax',
                        type=float,
                        help='Max radial location of the spray data (mm)',
                        required=True
                        )

    parser.add_argument('--sizeGroup',
                        type=str,
                        default='10,20,30,40,50',
                        help='Diameter groups for conditioned properties (um)',
                        required=False,
                        )

    parser.add_argument('--origin',
                        type=str,
                        default='0,0,0',
                        help="Co-ordinate of the injector's center",
                        required=False
                        )

    parser.add_argument('--norm',
                        type=str,
                        default='100',
                        choices=['100','010','001'],
                        help='Normal direction of the plane (default: %(default)s)',
                        required=False
                        )

    parser.add_argument('--pdf',
                        help='Get droplete droplet size PDF and volume PDF for sampled planes',
                        action="store_true"
                        )

    parser.add_argument('--csv',
                        help='Output in csv format',
                        action="store_true"
                        )

    parser.add_argument('--tecplot',
                        help='Output in Tecplot ascii format',
                        action="store_true"
                        )

    parser.add_argument('--merge',
                        help='Merge sampled data for each plane',
                        action="store_true"
                        )

    return(parser.parse_args())

if __name__ == '__main__':

    args = getArgs()
    flagProcess = args.process
    flagPdf = args.pdf
    flagMerge = args.merge

    [startTime, endTime] = args.time.split(":")
    if endTime=='':
        endTime=1.0e6
    else:
        endTime=float(endTime)
    if startTime=='':
        startTime=0.0
    else:
        startTime=float(startTime)

    global dGroup
    dGroup = [int(d) for d in args.sizeGroup.split(',')]
    dGroup.sort()
    print(" Diameter group: ",dGroup)

    global rMax
    rMax = args.rMax


    if (not flagProcess) and (not flagPdf) and (not flagMerge):
        print(" It seems that you didn't give me any flags\n")
        sys.exit()

    pwd = os.listdir()

    # The 'sprayCloud' may be different
    cloud = './postProcessing/lagrangian/sprayCloud/'
    if 'postProcessing' not in pwd:
        print("Fatal Error: Can't find 'postProcessing' in current folder!" )
        sys.exit()

    planes = os.listdir(cloud)
    timeDirs = os.listdir(cloud+planes[0])

    times = []
    for time in timeDirs:
        if isFloat(time):
            if float(time) >= startTime and float(time) <= endTime:
                times.append(time)
    
    # Calculate the statistical time period
    timeList = [float(time) for time in times]
    period = (max(timeList)-min(timeList))/(len(times)-1)*len(times)
    print(" Time range: {0} ~ {1}s".format(min(timeList),max(timeList)))
    print(" Statistical period: {0}s".format(period))
    
    for plane in planes:
        print("Processing plane: {0} ...".format(plane) )
        data = []
        # gather particles in the sampled plane
        for time in times:
            fileName = cloud+'/'+plane+'/'+time+'/statistic.dat'
            var, subdata = readData(fileName)
            data.extend(subdata)

        ind_nP = var.index("nParticle")

        print("  Parcels: {0:.1f}k, Particles: {1:.1f}k ..".format(len(data)/1000, sum([d[ind_nP] for d in data])/1000))

        if (flagProcess):
            process(args, plane, var, data, period)
            #processLine(args, plane, var, data)
        if (flagPdf):
            dropletSizePDF(plane, var, data)
        if (flagMerge):
            mergeData(plane, var, data)


