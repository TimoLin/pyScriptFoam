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

def main():

    with open ("U","r") as f:
        lines = f.read().replace("(",'')
        lines = lines.replace(")","")
        dataVel = np.loadtxt(StringIO(lines),skiprows=4)

    with open ("U","r") as f:
        p = read_points(f)
    

    (nSample, ndim) = dataVel.shape
    
    nProbe = (ndim-1)/3
    
    # Time step
    T = (dataVel[-1,0]-dataVel[0,0])/(nSample-1)
    
    ## plot Settings
    # use TEX for interpreter
    plt.rc('text',usetex=True)
    # use serif font
    plt.rc('font',family='serif')
    # figure and axes parameters
    # total width is fixed
    plot_width      =19.0
    subplot_h       =4.0
    margin_left     =2.0
    margin_right    =0.3
    margin_bottom   =1.5
    margin_top      =1.0
    space_width     =2.0
    space_height    =2.0
    ftsize          =8
    # total height determined by the number of vars
    plot_height     =((subplot_h+space_height)*1.0
                      -space_height+margin_top+margin_bottom)    

    fig, ax = plt.subplots(2,3,
                             sharex='col',sharey='row')

    for i in range(2):
        for j in range(3):
            nP = j+i*3
            if nP < len(p):
                print(nP, i, j) 
                xf, yf = use_fft(dataVel, T, nP, axis=2)
                ax[i,j].plot(xf, 2.0/nSample * np.abs(yf[:nSample//2]))
                ax[i,j].plot(xf, np.power(xf,-5.0/3.0)*100)
        
                # log for both x and y
                ax[i,j].set_xscale('log')
                ax[i,j].set_yscale('log')
                ax[i,j].set_ylim(1e-5,1e1)
                ax[1,j].set_xlabel('Frequency/Hz')
                ax[i,0].set_ylabel('Energy/(m2/s2)')
                
                ax[i,j].set_title('Point='+str(p[nP]))

    plt.subplots_adjust(left    =margin_left/plot_width,
                        bottom  =margin_bottom/plot_height,
                        right   =1.0-margin_right/plot_width,
                        top     =1.0-margin_top/plot_height,
                        wspace  =space_width/plot_width,
                        hspace  =space_height/plot_height)    

    plt.savefig('FFT.png',dpi=400)
    #plt.show()
    
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
