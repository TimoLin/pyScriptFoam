#!/usr/bin/python

#This python script is made for OpenFOAM lagrangian particle data's post process.

# ------------------What file does I need?--------------------
# working directory: $CASE_DIR/$TIME/lagrangian/sprayCloud
#             files: d         ----  particles diameter in this time step
#                    T         ----  particles Temperature 
#                    positions ----  particles postions (x,y,z) in the unit of 'm'
#                    U         ----  particles veloctiy (u,v,w) in the unit of 'm/s'

# -----------------What statistical data will this script get?-------------
#  diameter radial profiles in a given plane
#  velocity radial profiles in a given plane
#  Temperature raidal profiles in a given plane
#  SMD along the stream line
#  SMD of the whole domain

import sys
import os

import numpy as np

# timeStep's data to be processed
timeStep = [
        0.12372876,
        0.12374876,
        0.12376876,
        0.12378876,
        0.12380876,
        0.12382876
        ]

d = [] #diameter

x = [] # x cooridnate
y = [] # y 
z = [] # z 

T = [] # temperature

u = [] # velocitys
v = []
w = []

n_particles = 0

def read_particle_file(file):
    global n_particles,x,y,z,T,u,v,w

    f = open(file,'r')

    line = ''
    
    # read the file header 18 lines in total
    for i in range(16):
        line = f.readline()
    # read blank lines
    line = '\n'
    while(line == '\n'):
        line = f.readline()

    # read the particles number
    for temp in line.split():
        if temp.isdigit():
            n_particles = int(temp)
    # read the left bracket (
    line = f.readline() 
    
    # read the particle data
    if (file == 'd' or file == 'T'):
        for i in range(n_particles):
            line = f.readline()
            for temp in line.split():
                    if file == 'd':
                        d.append(float(temp))
                    elif file == 'T':
                        T.append(float(temp))
    elif (file == 'positions' or file=='U'):
        for i in range(n_particles):
            line = f.readline()
            # remove '(' and ')' in the string
            line = line.replace('(','')
            line = line.replace(')','')
            temp_var = []

            for temp in line.split():
                temp_var.append(float(temp))
            if file == 'positions':
                x.append(temp_var[0])
                y.append(temp_var[1])
                z.append(temp_var[2])
            elif file == 'U':
                u.append(temp_var[0])
                v.append(temp_var[1])
                w.append(temp_var[2])
    f.close()
    #print ' Finished reading file: ', file

root_dir = os.getcwd()

for time in timeStep:
    # cd into the timeStep dir 
    time_dir = str(time)
    os.chdir(time_dir)

    read_particle_file('d')
    #read_particle_file('T')
    read_particle_file('positions')
    read_particle_file('U')
    
    print 'Finished reading step: ', time, ' Particles: ', n_particles 

    # cd back to the root dir
    os.chdir(root_dir)

print ' ** Total particles: ',len(x),' ** '

def output_tecplot():
    # First output the particles data into a tecplot ASCII file
    # The droplets can be seen when 'scatter' is activated
    tecplot_scatter_file = 'droplet.plt'
    f = open(tecplot_scatter_file, 'w')
    var_name = "\"X\", \"Y\", \"Z\", \"X Velocity\", \"Y Velocity\", \"Z Velocity\", \"Diameter\""
    f.write("Variables = "+var_name+'\n')
    f.write("Zone T=\" Droplet data \" \n")
    for i in range(n_particles):
        #header = str(x[i])+'\t'+str(y[i])+'\t'+str(z[i])+'\t'+str(u[i])+'\t'+str(v[i])+'\t'+str(w[i])+'\t'+str(T[i])+'\t'+str(d[i])+'\n'
        header = str(x[i])+'\t'+str(y[i])+'\t'+str(z[i])+'\t'+str(u[i])+'\t'+str(v[i])+'\t'+str(w[i])+'\t'+str(d[i])+'\n'
        f.write(header)
    f.close()
    print( 'Finished writting the particle data into tecplot format file')
    print( '\n')

# uncommented the following line if you want to output the scatter file
#output_tecplot()

# Second get the diameter radial profiles

z_slice = [5.0, 7.0, 10.0, 13.0, 16.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0]
slice_thick = 1.0 # process droplets located in z_slice[i]0.5*slice_thick range

r = [0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0,13.0,14.0,15.0,
        16.0,17.0,18.0,19.0,20.0,21.0,22.0,23.0,24.0,25.0,26.0,27.0,28.0,29.0,30.0]
d_profiles = []
droplet_no_profiles = []
Ua_profiles = []
Ur_profiles = []
for z_temp in z_slice:
    z1 = 0.0293+(z_temp - slice_thick)*0.001
    z2 = 0.0293+(z_temp + slice_thick)*0.001
    d_radial = []
    droplet_no = []
    Ua_radial = []
    Ur_radial = []
    for j in range(len(r)):
        if j == 0:
            r1 = 0
            r2 = 0.5
        else:
            r1 = (r[j]-0.5)*0.001
            r2 = (r[j]+0.5)*0.001
        drops = []
        mUa_sum = 0.0
        mUr_sum = 0.0 
        m_sum  = 0.0
        for i in range(n_particles):
            if (z[i] >= z1 and z[i] <= z2) :
                r_i = np.sqrt(x[i]*x[i]+y[i]*y[i])
                if (r_i >= r1 and r_i <= r2):
                    drops.append(d[i])
                    mUa_sum += np.power(d[i],3.0)*w[i]
                    mUr_sum += np.power(d[i],3.0)*(np.sqrt(u[i]*u[i]+v[i]*v[i]))
                    m_sum += np.power(d[i],3.0)
        if len(drops) > 0:
            mean_d10 = np.mean(drops)*1e6
            mean_Ua = mUa_sum/m_sum
            mean_Ur = mUr_sum/m_sum
        else:
            mean_d10 = 0.0
            mean_Ua = 0.0
            mean_Ur = 0.0
        d_radial.append(mean_d10)
        droplet_no.append(len(drops))
        Ua_radial.append(mean_Ua)
        Ur_radial.append(mean_Ur)

    d_profiles.append(d_radial)
    droplet_no_profiles.append(droplet_no)
    Ua_profiles.append(Ua_radial)
    Ur_profiles.append(Ur_radial)

print ' Finshed processing Diameter and Velocity profiles'

## output profile data into tecplot ASCII file
profile_file = 'profile.plt'
f = open(profile_file,'w')
f.write("Variables = \"Radial coordinate(mm)\", \" Droplet diameter\", \"NDrop\", \"Axial velocity\", \"Radial velocity \" \n")
for n in range(len(z_slice)):
    f.write("Zone T= \"Z-"+str(z_slice[n])+"mm\"\n")
    temp_d = d_profiles[n]
    temp_nd = droplet_no_profiles[n]
    temp_Ua = Ua_profiles[n]
    temp_Ur = Ur_profiles[n]
    for i in range(len(r)):
        line = str(r[i])+'\t'+str(temp_d[i])+'\t'+str(temp_nd[i])+'\t'+str(temp_Ua[i])+'\t'+str(temp_Ur[i])+'\t'+'\n'
        f.write(line)
f.close()

print ' Finshed writting Diameter and Velocityprofiles into tecplot file'

# Thirdly get the SMD along the streamwise
z_smd = [] #2,4,6,8,10......50
slice_thick = 1.0 # process droplets located in z_slice[i]0.5*slice_thick range

for i in range(25):
    z_smd.append(2*(i+1))
smd = []
n_drops = []
for i in range(len(z_smd)):
    z1 = 0.0293+(z_smd[i] - slice_thick)*0.001
    z2 = 0.0293+(z_smd[i] + slice_thick)*0.001
    d3 = 0.0
    d2 = 0.0
    nd = 0
    for n in range(n_particles):
        if z[n] >= z1 and z[n] <= z2:
            d3 += np.power(d[n],3.0)
            d2 += np.power(d[n],2.0)
            nd += 1
    if nd > 0:
        smd.append(d3/d2*1e6)
    else:
        smd.append(0.0)
    n_drops.append(nd)
## output smd data into tecplot ASCII file
smd_file = 'smd.plt'
f = open(smd_file,'w')
f.write("Variables = \"Z (mm) \",\"SMD\",\"NDrop\"\n")
for i in range(len(z_smd)):
    line = str(z_smd[i])+'\t'+str(smd[i])+'\t'+str(n_drops[i])+'\t\n'
    f.write(line)
f.close()
print ' Finished writing smd profile along streamwise into tecplot file '

# Fourth get the SMD of the whole domain
smd_whole = 0.0
d3 = 0.0
d2 = 0.0
for n in range(n_particles):
    d3 += np.power(d[n],3)
    d2 += np.power(d[n],2)
smd_whole = d3/d2*1e6
print ' ** SMD of the whole domain is: ', smd_whole,' ** '
print ' ** Mean D10 of the whole domain is: ',np.mean(d)*1e6, ' ** '
