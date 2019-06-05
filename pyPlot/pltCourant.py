#!/usr/bin/env python3
# 2019/06/05 16:12:03  zt
# This python script is made for ploting Max Courant number along with time step.

import sys
import os

import matplotlib.pyplot as plt

help_msg = 'Usgage:\n  python3 pltCourant.py -log <log.file>'

if '-log' in sys.argv:
    log_file = sys.argv[sys.argv.index('-log')+1]
else:
    print(help_msg)
    sys.exit()

f = open(log_file, 'r')
lines = f.readlines()

time = []
co = []

for n, line in enumerate(lines):
    if 'Courant Number mean' in line and 'Time' in lines[n+1]:
        time.append(float(lines[n+1].split()[-1]))
        temp = float(line.split()[-1])
        co.append(temp)

plt.plot(time, co, 'b')
plt.xlabel("Time(s)")
plt.ylabel("Max Courant No.")
plt.show()
