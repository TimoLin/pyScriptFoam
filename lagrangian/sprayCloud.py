#!/usr/bin/env python3
# 2019/04/24 21:17:46  zt
#This python script is made for converting OpenFOAM lagrangian particle data to tecplot format

import numpy as np
import sys
import os


def isFloat(x):
    # check whether the string consists of float only
    try:
        float(x)
        return True
    except ValueError:
        return False

def readScalar(file):
    data = []
    f = open(file, 'r')
    lines = f.readlines()

    # read particle number
    line = lines[18]
    for temp in line.split():
        if temp.isdigit():
            n_particles = int(temp)
    # read data
    n_start = lines.index('(\n')
    for line in lines[n_start+1:n_particles+n_start+1]:
        for temp in line.split():
            data.append(float(temp))
    # done
    f.close()
    return data

def readVector(file):
    data0 = []
    data1 = []
    data2 = []

    f = open(file, 'r')
    lines = f.readlines()

    # read particle number
    for line in lines[16:]:
        if line != '\n':
            break
    for temp in line.split():
        if temp.isdigit():
            n_particles = int(temp)
    # read data
    n_start = lines.index('(\n')
    for line in lines[n_start+1:n_particles+n_start+1]:
        # remove '(' and ')' in the string
        line = line.replace('(', '')
        line = line.replace(')', '')

        data0.append(line.split()[0])
        data1.append(line.split()[1])
        data2.append(line.split()[2])
    # done
    f.close()
    return data0, data1, data2

def output_tecplot(tec_file, x, y, z, d, u, v, w, T, _time):
    # First output the particles data into a tecplot ASCII file
    # The droplets can be seen when 'scatter' is activated
    f = open(tec_file, 'w')
    var_name = "\"X\", \"Y\", \"Z\", \"X Velocity\", \"Y Velocity\", \"Z Velocity\", \"Diameter\", \" Temperature\""
    f.write("Variables = "+var_name+'\n')
    f.write("Zone T=\" Droplet-" +_time+" \" \n")
    f.write(" SOLUTIONTIME="+_time+'\n')

    for i in range(len(x)):
        #header = str(x[i])+'\t'+str(y[i])+'\t'+str(z[i])+'\t'+str(u[i])+'\t'+str(v[i])+'\t'+str(w[i])+'\t'+str(T[i])+'\t'+str(d[i])+'\n'
        header = str(x[i])+'\t'+str(y[i])+'\t'+str(z[i])+'\t'+str(u[i])+'\t'+str(v[i])+'\t'+str(w[i])+'\t'+str(d[i])+'\t'+str(T[i])+'\n'
        f.write(header)
    f.close()
    print( ' Finished writting to: '+tec_file)

def main():
    help = " Usage:\n" \
        + "   python3 sprayCloud.py [-parallel] [-latestTime] [-help]\n" \
        + "     -parallel:    process the parallel data\n" \
        + "     -latestTime:  only process the latestTime solution\n" \
        + "     -help:        print this message\n"
    if '-help' in sys.argv:
        print(help)
        sys.exit()

    # Search the current directory for OpenFOAM case
    pwd = os.listdir()
    if 'system' not in pwd:
        print(" Error: This is not an OpenFOAM case root directory !")
        sys.exit()
    
    ## First check 'Are we handling parallel data?'
    if '-parallel' in sys.argv:
        if 'processor1' in pwd:
            print(" We are parsing parallel data !")
            # get parallel dirs
            proc_dir = []
            for _dir in pwd:
                if 'processor' in _dir:
                    proc_dir.append(_dir)
        else:
            print(" It seems we are not in a parallel case\n")
            sys.exit()
    else:
        proc_dir = ['./']
    
    runtime = []
    timelist = []
    proc_dir_list = os.listdir(proc_dir[0])
    for _dir in proc_dir_list:
        if isFloat(_dir):
            if _dir != '0':
                # don't parse the 0 dir
                runtime.append(_dir)
                timelist.append(float(_dir))
    timelist.sort()
    
    if (runtime == []):
        print(" Error: It seems we don't have any solution data in this case!")
        if '-parallel' not in sys.argv:
            print(" Try using -parallel option.")
        print(help)
        sys.exit()

    print(' There are '+str(len(timelist))+' timesteps solution! ')
    print('   Ranged from '+str(min(timelist))+' to '+str(max(timelist)))
    
    if '-latestTime' in sys.argv:
        # only the latest time solution will be processed
        for _time in runtime:
            if float(_time) == timelist[-1]:
                break
        runtime = [ _time ]
    else:
        # sort the runtime dir by ascending order
        _runtime = []
        for __time in timelist:
            for _time in runtime:
                if float(_time) == __time:
                    _runtime.append(_time)
                    break
        runtime = _runtime
    
    if len(runtime) == 1 and '0' in runtime:
        print(" It seems this is a fresh new case! ")
        print(" ** Abort due to lack of runtime data ** ")
        sys.exit()
    
    ## Will not reach here if exit
    spray_dir = []
    for _time in runtime:
        _time_spray = []
        for _dir in proc_dir:
            proc_time_dir = _dir +'/'+_time
            if 'lagrangian' in os.listdir(proc_time_dir):
                temp = _dir+'/'+_time+'/lagrangian/sprayCloud/'
                _time_spray.append(temp)
        spray_dir.append(_time_spray)
    #print(spray_dir)
    ## Only read 'd' 'U' 'positions' and 'T' file of the spray data
    
    # create tecplt dir
    if 'Tecplot' not in pwd:
        os.mkdir('Tecplot')
    
    for n, _time in enumerate(runtime):
    
        d = []
        u = []
        v = []
        w = []
        T = []
        x = []
        y = []
        z = []
        for proc in spray_dir[n]: 
            d_file = proc+'d'
            T_file = proc+'T'
            U_file = proc+'U'
            X_file = proc+'positions'
            
            d.extend(readScalar(d_file))
        
            T.extend(readScalar(T_file))
            
            u0, v0, w0 = readVector(U_file)
            u.extend(u0)
            v.extend(v0)
            w.extend(w0)
        
            x0, y0, z0 = readVector(X_file)
            x.extend(x0)
            y.extend(y0)
            z.extend(z0)
        
        # output to tecplot format
        print(' Time '+_time+ 's contains '+str(len(x))+ ' particles.')
        tec_file = 'Tecplot/droplet'+_time+'.plt'
        output_tecplot(tec_file, x, y, z, d, u, v, w, T, _time)

if __name__ == '__main__':
    main()
