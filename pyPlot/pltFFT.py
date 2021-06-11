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

with open ("U","r") as f:
    lines = f.read().replace("(",'')
    lines = lines.replace(")","")
    dataVel = np.loadtxt(StringIO(lines),skiprows=4)

(nSample, ndim) = dataVel.shape

nProbe = (ndim-1)/3

# Time step
T = (dataVel[-1,0]-dataVel[0,0])/(nSample-1)

x = dataVel[:,0]
y = dataVel[:,9]

# Perform Fast Fourier Transform
## 
yf = fft(y)
xf = fftfreq(nSample,T)[:nSample//2]

fig, ax = plt.subplots()
ax.plot(xf, 2.0/nSample * np.abs(yf[:nSample//2]))
ax.plot(xf, np.power(xf,-5.0/3.0)*100)

# log for both x and y
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_ylim(1e-5,1e1)
ax.set_xlabel('Frequency/Hz')
ax.set_ylabel('Energy/(m2/s2)')

plt.show()

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
