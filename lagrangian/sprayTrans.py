#!/usr/bin/env python3
# 2019/05/14 17:29:09  zt
# Description:
#   This script is designed for converting sprayCloud:rhoTrans_* file into Tecplot readable format.
#     Only parse the liquid concentration's rhoTrans.
#     Eg: rhoTrans_C2H5OH (will generate this new file)

# Todo:
#   Add parallel data process support

import sys
import os

def isFloat(x):
    # check whether the string consists of float only
    try:
        float(x)
        return True
    except ValueError:
        return False

def getBoundaryPatch(boundary):
    '''
    read in $caseroot/constant/polymesh/boundary file and return boudary patches
    '''
    f = open(boundary, 'r')
    lines = f.readlines()
    patch = []
    lineNo = []
    for nStart, line in enumerate(lines):
        if '(' in line:
            break

    lines = lines[nStart+1:]
    for n, line in enumerate(lines):
        if "{" in line:
            lineNo.append(n-1)
    for nLine in lineNo:
        patch.append(lines[nLine])

    f.close()

    return patch

def parseSprayTransFile(transFile, newTransFile):
    '''
    slightly modify rhoTrans_[liquidPhase] file
    '''

    f = open(transFile, 'r')
    lines = f.readlines()
    f.close()
    for n, line in enumerate(lines):
        if 'volScalarField::DimensionedInternalField' in line:
            lines[n] = '    class       volScalarField;\n'
            # first line
        elif 'object' in line:
            lines[n] = '    object      '+line[line.index(':')+1:]
            # second line
        elif 'value' in line:
            lines[n] = 'internalField   nonuniform List<scalar>\n'
            # final line
            break
        
    f = open(newTransFile, 'w')
    f.writelines(lines)
    f.close()

def addBoudaryPatch(transFile, patch):
    '''
    add boudary data into rhoTrans_[liquidPhase] file
    '''
    # wrap patch part
    boundaryField = 'boundaryFilde\n' + '{\n'
    content = '{\n'+'type calculated;\n' +'value uniform 0;\n' +'}\n'

    for boundary in patch:
        boundaryField += boundary +content
    
    boundaryField += '}'
    
    # append this to the end 
    f = open(transFile,'a')
    f.write(boundaryField)
    f.close()

def main():

    help = "Usage: \n" \
           "  python3 sprayTrans.py -liquid <phaseName> [-latestTime] [-parallel] [-help] \n" \
           "    -liquid <phaseName>: specific the liquid mixture name \n" \
           "    -latestTime: only parse the latest solution \n" \
           "    -parallel:   parse the parallel data \n" \
           "    -help:       show this message \n"
    if '-help' in sys.argv:
        print(help)
        sys.exit()

    if '-liquid' in sys.argv:
        liquid = sys.argv[sys.argv.index('-liquid')+1]
    else:
        print(' I need you give me the liquid phase specie name!')
        print(help)
        sys.exit()
    
    # Are we in a Openfoam case root dir
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

    rhoTrans_dir = []
    rhoTrans_file = 'sprayCloud:rhoTrans_'+liquid
    new_rhoTrans_file = 'rhoTrans_'+liquid

    for _time in runtime:
        _time_rhoTrans = []
        for _dir in proc_dir:
            proc_time_dir = _dir +'/'+_time+'/'
            if rhoTrans_file in os.listdir(proc_time_dir):
                _time_rhoTrans.append(proc_time_dir)
            else:
                print(' Error: I can\'t find '+rhoTrans_file+' in '+proc_time_dir+' !')
                sys.exit()
        rhoTrans_dir.append(_time_rhoTrans)

    patch = getBoundaryPatch('./constant/polyMesh/boundary')

    for n, _time in enumerate(runtime):
        for proc in rhoTrans_dir[n]:
            _temp_rhoTrans_file = proc+rhoTrans_file
            _temp_new_rhoTrans_file = proc+new_rhoTrans_file
            # copy file
            #cp_file_cmd = 'cp '+_temp_rhoTrans_file+'  '+_temp_new_rhoTrans_file 
            #os.system(cp_file_cmd)

            # slightly modify the keywords
            parseSprayTransFile(_temp_rhoTrans_file, _temp_new_rhoTrans_file)

            # append boundary data
            addBoudaryPatch(_temp_new_rhoTrans_file, patch)

        # output info
        print( ' Time '+_time+'s '+'sprayCloud:rhoTrans_'+liquid+' has been translated! ')

if __name__ == '__main__':
    main()            
