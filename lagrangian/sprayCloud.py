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
    for line in lines[16:]:
        if line != '\n':
            break
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

        data0.append(float(line.split()[0]))
        data1.append(float(line.split()[1]))
        data2.append(float(line.split()[2]))
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
    print( '   Finished writting to: '+tec_file)

def rwTecplot(time_list, spray_dir):
    '''
    Description:
      Read the spray cloud data and write to Tecplot
      To save memory, we read and write timestep one by one
      Only read 'd' 'U' 'positions' and 'T' file of the spray data
    '''
    for n, _time in enumerate(time_list):
    
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
        if len(x) > 0:
            print(' Time '+_time+ 's contains '+str(len(x))+ ' particles.')
            tec_file = 'Tecplot/droplet'+_time+'.plt'
            output_tecplot(tec_file, x, y, z, d, u, v, w, T, _time)
        else:
            print(' Skipping Time '+_time + ' with no particle!' )

    return

def readData(runtime, post_time, spray_dir, direc, axial, r):
    '''
    Read spray cloud data to list and post-process them
    '''
    
    d = []
    u = []
    v = []
    w = []
    T = []
    x = []
    y = []
    z = []
    
    for _time in post_time:
        n = runtime.index(_time)
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
    
    # start post-process
    if len(x) > 0:
        print(" Total particles: ", len(x), ".")
        print(" Post-processing ...")
        postProcess(direc, x, y, z, d, u, v, w, axial, r)
    else:
        print(" Error: There isn't any particles in your timesteps!")
        print("   Check it again!")

def postProcess(direc, x, y, z, d, u, v, w, axial, r):
    '''
    Description:
        Post-process the droplet data and get SMD, diameter and velocity distribution
    '''
    slice_thick = 1.0 # unit mm

    # Fisrt: radial profiles
    d_profiles = []
    droplet_no_profiles = []
    Ua_profiles = []
    Ur_profiles = []

    for a_temp in axial:

        a1 = (a_temp - slice_thick)*0.001
        a2 = (a_temp + slice_thick)*0.001

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
            for i in range(len(x)):
                if direc == '100':
                    # x is axial direction
                    a_i = x[i]
                    r_i = np.sqrt(y[i]*y[i]+z[i]*z[i])
                    ua_i = u[i]
                    ur_i = np.sqrt(v[i]*v[i]+w[i]*w[i])
                elif direc == '010':
                    # y is axial direction
                    a_i = y[i]
                    r_i = np.sqrt(x[i]*x[i]+z[i]*z[i])
                    ua_i = v[i]
                    ur_i = np.sqrt(u[i]*u[i]+w[i]*w[i])
                elif direc == '001':
                    # z is axial direction
                    a_i = z[i]
                    r_i = np.sqrt(x[i]*x[i]+y[i]*y[i])
                    ua_i = w[i]
                    ur_i = np.sqrt(u[i]*u[i]+v[i]*v[i])
                else:
                    # will not reach here
                    print(" Error: Wrong direction definition: ", direc)
                    sys.exit()

                if (a_i >= a1 and a_i <= a2) :
                    if (r_i >= r1 and r_i <= r2):
                        drops.append(d[i])
                        
                        mUa_sum += np.power(d[i],3.0)*ua_i
                        mUr_sum += np.power(d[i],3.0)*ur_i
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

    # Second: SMD along axial line, axial locations from postDict is used here
    smd = []
    n_drops = []
    for i in range(len(axial)):
        a1 = (axial[i] - slice_thick)*0.001
        a2 = (axial[i] + slice_thick)*0.001
        d3 = 0.0
        d2 = 0.0
        nd = 0
        for n in range(len(x)):
            if direc == "100":
                a_n = x[i]
            elif direc == "010":
                a_n = y[i]
            else:
                a_n = z[i]
            if a_n >= a1 and a_n <= a2:
                d3 += np.power(d[n],3.0)
                d2 += np.power(d[n],2.0)
                nd += 1
        if nd > 0:
            smd.append(d3/d2*1e6)
        else:
            smd.append(0.0)
        n_drops.append(nd)

    
    # output radial profile data into tecplot ASCII file
    profile_file = 'postSpray/sprayProfile.plt'
    f = open(profile_file,'w')
    f.write("Variables = \"Radial coordinate(mm)\", \" Droplet diameter\", \"NDrop\", \"Axial velocity\", \"Radial velocity \" \n")
    for n in range(len(axial)):
        if direc == '100':
            f.write( "Zone T= \"X-"+str(axial[n])+"mm\"\n")
        elif direc == '010':
            f.write( "Zone T= \"Y-"+str(axial[n])+"mm\"\n")
        else:
            f.write( "Zone T= \"Z-"+str(axial[n])+"mm\"\n")

        temp_d = d_profiles[n]
        temp_nd = droplet_no_profiles[n]
        temp_Ua = Ua_profiles[n]
        temp_Ur = Ur_profiles[n]
        for i in range(len(r)):
            line = str(r[i])+'\t'+str(temp_d[i])+'\t'+str(temp_nd[i])+'\t'+str(temp_Ua[i])+'\t'+str(temp_Ur[i])+'\t'+'\n'
            f.write(line)
    f.close()

    print('   Finshed writing Diameter and Velocity profiles!')

    ## output smd data into tecplot ASCII file
    smd_file = 'postSpray/axialSMD.plt'
    f = open(smd_file,'w')
    f.write("Variables = \"Z (mm) \",\"SMD\",\"NDrop\"\n")
    for i in range(len(axial)):
        line = str(axial[i])+'\t'+str(smd[i])+'\t'+str(n_drops[i])+'\t\n'
        f.write(line)
    f.close()
    print('   Finished writing smd profile along axial direction into tecplot file ')
    
    # Finally get the SMD of the whole domain and output it in terminal
    smd_whole = 0.0
    d3 = 0.0
    d2 = 0.0
    for n in range(len(x)):
        d3 += np.power(d[n],3)
        d2 += np.power(d[n],2)
    smd_whole = d3/d2*1e6
    print("   SMD of the whole domain is: ", smd_whole)
    print("   Mean D10 of the whole domain is: ",np.mean(d)*1e6)

    return

def config_parser(config):
    # read in and parse post-process config (locate in system/postDict)
    f = open(config)
    lines = f.readlines()
    timesteps = []
    direc = ''
    axial = []
    radial = []
    for n, line in enumerate(lines):
        if 'Timesteps' in line:
            # n+2 means pass '(' line
            for line in lines[n+2:]:
                if ')' in line:
                    break
                for temp in line.split(','):
                    if isFloat(temp):
                        timesteps.append(temp)
            break

    for n, line in enumerate(lines):
        if 'Direction' in line:
            temp = line[line.index(':')+1:]
            temp = temp.replace('(','')
            temp = temp.replace(')','')
            temp = temp.replace(' ', '')
            direc = temp.replace('\n', '')
            break

    for n, line in enumerate(lines):
        if 'Axial' in line:
            for line in lines[n+2:]:
                if ')' in line:
                    break
                for temp in line.split(','):
                    if isFloat(temp):
                        axial.append(float(temp))
            break
        
    for n, line in enumerate(lines):
        if 'Radial' in line:
            for line in lines[n+2:]:
                if ')' in line:
                    break
                for temp in line.split(','):
                    if isFloat(temp):
                        radial.append(float(temp))
            break

    return timesteps, direc, axial, radial


def main():
    help = " Usage:\n" \
        + "   python3 sprayCloud.py [-parallel] [-latestTime] [-post] [-help]\n" \
        + "     -parallel:    process the parallel data\n" \
        + "     -latestTime:  only process the latestTime solution\n" \
        + "     -post:        post-process the droplet data\n" \
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
            print(" We are parsing parallel data. Woopie!")
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

    ## Second check 'Are we goint to post-process?'
    if '-post' in sys.argv:
        # check 'postDict' path
        if 'postSpray' not in pwd:
            print(" Error: I can't find postSpray folder! :(")
            sys.exit()
        else:
            if 'postDict' not in os.listdir('postSpray'):
                print(" Error: I cant't find postDict in postSpray folder! :(")
                sys.exit()
            else:
                # read postDict
                config_file = 'postSpray/postDict'
                post_time, direc, axial, radial = config_parser(config_file)
    
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
        # if -latestTime is specied in arguments, it will cover postdict timestep options
        post_time = [_time]
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
    else:
        if '-post' in sys.argv:
            for _post_time in post_time:
                if _post_time  not in runtime:
                    print(" Error: It seems Post-time:",_post_time," was not in your solutions! ")
                    print("    Your time list: ", ", ".join(post_time) )
                    print("    Available time list: ", ", ".join(runtime))
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
    
    # create tecplt dir
    if 'Tecplot' not in pwd:
        os.mkdir('Tecplot')

    if '-post' in sys.argv:
        # do post process
        readData(runtime, post_time, spray_dir, direc, axial, radial)
    else:
        # write data to Tecplot format
        rwTecplot(runtime, spray_dir)
    

if __name__ == '__main__':
    main()
