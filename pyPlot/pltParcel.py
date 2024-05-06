#!/usr/bin/env python3

# 2021/07/27 10:37:50  zt
# Plot current number of parcels along with simulation time.

import sys
import argparse
import os
import matplotlib.pyplot as plt

def fileParser(fileName):
    time = []
    parcels = []
    with open(fileName) as f:
        lines = f.readlines()
        
        for line in lines:
            if "Time =" == line[0:6]:
                temp = float(line.split()[-1])
                time.append(temp)
            if "Current number of parcels" in line:
                temp = int(line.split()[-1])
                parcels.append(temp)
    # Let the length of time and parcels be the same
    if len(parcels) < len(time):
        time = time[0:len(parcels)]
    else:
        parcels = parcels[0:len(time)]
        
    return time, parcels

def getArgs():
    parser = argparse.ArgumentParser(
            description = "Plot current number of parcels along with simulation time."
            )

    parser.add_argument('-log',
            type = str,
            help = "Simulation log file.",
            required = True
            )
    return parser.parse_args()

if __name__ == "__main__":

    args = getArgs()
    logFile = args.log

    time, parcels = fileParser(logFile)

    plt.plot(time,parcels)
    plt.show()
