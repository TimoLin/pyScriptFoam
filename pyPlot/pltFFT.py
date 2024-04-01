#!/usr/bin/env python3
# 2021/04/09 09:57:31  zt
# This python script is designed for performing a FFT transform of 
#   a OF probe dataset. e.g. Velocity probe dat.

import sys
import os

from scipy.fftpack import fft, fftfreq
import numpy as np
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,NullFormatter,
                               AutoMinorLocator,LogLocator)
import argparse

def read_points(f):
    
    lines = f.readlines()
    header = lines[0:3]

    p = []
    x = header[0].split()[2:]
    y = header[1].split()[2:]
    z = header[2].split()[2:]

    for i in range(len(x)):
        p.append( (float(x[i]),float(y[i]),float(z[i])))

    return p

def use_fft(dataVel, T, nP, axis):

    """Do fft of the given dataset
    """

    (nSample, ndim) = dataVel.shape
    
    index = 3*nP+(axis+1)
    print(index)

    x = dataVel[:,0]
    y = dataVel[:,index]
    
    # Perform Fast Fourier Transform
    ## 
    yf = fft(y)
    xf = fftfreq(nSample,T)[:nSample//2]

    return xf, yf
def getArgs():
    """ Define the command-line arguments
    Arguments:
        None
    Returns:
        args: Commandline arguments
    """
    parser = argparse.ArgumentParser(
                description = "Perform FFT of the given velocity probe data."
                )

    parser.add_argument('--files',
                        type=str,
                        help='Velocity probe files',
                        required=True
                        )

    parser.add_argument('--uvw',
                        type=int,
                        help='Velocity component to be processed.',
                        required=True
                        )

    parser.add_argument('--points',
                        type=str,
                        help='Point list to be processed',
                        required=True
                        )

    parser.add_argument('--cases',
                        type=str,
                        help='Case name of the coresponding probe file.',
                        required=True
                        )

    return(parser.parse_args())


def main():

    args = getArgs()

    fileNames = args.files
    fileNames = fileNames.split(",")

    cases = args.cases
    cases = cases.split(",")

    points = args.points
    points = [int(x) for x in points.split(",")]

    uvw = args.uvw

    data = {}

    for n, fName in enumerate(fileNames):
        with open (fName,"r") as f:
            lines = f.read().replace("(",'')
            lines = lines.replace(")","")
            dataVel = np.loadtxt(StringIO(lines),skiprows=4)

        with open (fName,"r") as f:
            p = read_points(f)

        (nSample, ndim) = dataVel.shape
        
        nProbe = (ndim-1)/3
        
        # Time step
        T = (dataVel[-1,0]-dataVel[0,0])/(nSample-1)

        data.update(
                {cases[n]:dataVel}
                )
    
    ## plot Settings
    # use TEX for interpreter
    plt.rc('text',usetex=True)
    # use serif font
    plt.rc('font',family='serif')
    # figure and axes parameters
    # total width is fixed
    plot_width      =19.0
    subplot_h       =4.0
    margin_left     =1.6
    margin_right    =0.3
    margin_bottom   =1.2
    margin_top      =0.7
    space_width     =0.0
    space_height    =1
    ftsize          =8
    # total height determined by the number of vars
    plot_height     =((subplot_h+space_height)*1
                      -space_height+margin_top+margin_bottom)+2
    
    print(plot_height)

    fig, ax = plt.subplots(1,3,
            sharey='row',
            figsize=(plot_width/2.54,plot_height/2.54)
            )

    #xlim1 = [250, 200,  200, 200, 75,  75, 200,  200, 200,  75,  50, 30]
    #xlim2 = [1500,1250, 1250,1250,501, 501,1250, 1250,1250, 501, 501, 501]
    #xlim3 = [7e6, 2e6,  2e6, 2e6, 1e6, 1e6, 3e6, 3e6,  3e6, 2e6, 1e6, 1e6]

    xlim1 = [250, 200, 30]
    xlim2 = [1500,1250, 501]
    xlim3 = [7e6, 3e6,  1e6]
    
    lines = {0:"-",1:"--",2:"-.",3:":"}

    colors = {0:"#1f77b4ff",1:"#ff7f0eff",2:"#2ca02cff",3:"#d62728ff"}
    for i in range(1):
        for j in range(3):
            nP = j+i*2
            for n, case in enumerate(cases):
                dataVel = data[case]

                if nP < 11:
                    print(nP, i, j) 
                    xf, yf = use_fft(dataVel, T, points[nP], axis=uvw)
                    ax[j].plot(xf, 2.0/nSample * np.abs(yf[:nSample//2]),lines[n],color=colors[n],label=case,linewidth=1.0)
            ax[j].plot(xf[xlim1[nP]:xlim2[nP]], np.power(xf[xlim1[nP]:xlim2[nP]],-5.0/3.0)*xlim3[nP],"-k",label="-5/3 law",linewidth=1.0)
        
            # log for both x and y
            ax[j].set_xscale('log')
            ax[j].set_xlim(0,np.max(xf))
            ax[j].set_xlabel(r'$f/Hz$')
            ax[0].set_ylabel(r'$E/(m2/s2)$')
            # legend
            ax[-1].legend(fontsize=ftsize,
                          numpoints=1,
                          frameon=False)

    ax[0].set_ylim(1e-5,1e1)
    ax[0].minorticks_on()
    ax[0].set_yscale('log')

    ax[0].set_title(r'Probe:$(0,0,0)$')
    ax[1].set_title(r'Probe:$(1D,0.25D,0)$')
    ax[2].set_title(r'Probe:$(15D,0.5D,0)$')
    plt.subplots_adjust(left    =margin_left/plot_width,
                        bottom  =margin_bottom/plot_height,
                        right   =1.0-margin_right/plot_width,
                        top     =1.0-margin_top/plot_height,
                        wspace  =space_width/plot_width,
                        hspace  =space_height/plot_height)    

    plt.savefig('FFT-400.png',dpi=200)
    #plt.savefig('FFT-1200.jpg',dpi=1200)
    #plt.savefig('FFT-1200.png',dpi=1200)
    ##plt.show()
    
    # Perform Power Spectral Density 
    '''
    from scipy import signal
    f, psd = signal.welch(y)
    fig, ax = plt.subplots()
    ax.plot(f,psd)
    ax.set_xscale('log')
    #ax.set_yscale('log')
    
    plt.show()
    '''

if __name__ == "__main__":
    main()
