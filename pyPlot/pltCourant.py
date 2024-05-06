#!/usr/bin/env python3
# 2019/06/05 16:12:03  zt
# This python script is made for ploting Max Courant number along with time step.

import sys
import os


help_msg = 'Usgage:\n  python3 pltCourant.py -log <log.file>'

if '-log' in sys.argv:
    log_file = sys.argv[sys.argv.index('-log')+1]
else:
    print(help_msg)
    sys.exit()

import matplotlib.pyplot as plt

f = open(log_file, 'r')
lines = f.readlines()

time = []
co = []

for n, line in enumerate(lines):
    if 'Courant Number mean' in line:
        co.append(float(line.split()[-1]))
    if 'Time =' == line[0:6]:
        time.append(float(line.split()[-1]))

# Let the length of time and Co be the same
if len(co) < len(time):
    time = time[0:len(co)]
else:
    co = co[0:len(time)]

plt.plot(time, co, 'b')
plt.xlabel("Time(s)")
plt.ylabel("Max Courant No.")
plt.show()
