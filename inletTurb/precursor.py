#!/usr/bin/python3
# 2019/09/26 15:09:14  zt
# Post-process surfaceSampling velocity libray for 
#   timeVaryingMappedFixedValue inlet condition

import sys
import os
import configparser 

def main():
    helpMsg = " Usgae:\n" \
            + "   python3 precursor.py [-help] -config config.ini\n" \
            + "   Process surfaceSampling velocity libray for timeVaryingMappedFixedVaule\n" \
            + "   Configs:\n" \
            + "      src:        source folder\n" \
            + "      dst:        output folder\n" \
            + "      vector:     convert velocity vector for different coordination system\n" \
            + "      dt:         timestep\n" \
            + "      startTime:  source start time \n" \
            + "      outputTime: output start time \n" \
            + "      steps:      how many steps \n" \
            + "      meanU:      Mean velocity field"
    if '-help' in sys.argv:
        print(helpMsg)
        sys.exit()

    if "-config" in sys.argv:
        ini = sys.argv[sys.argv.index('-config')+1]
        config = configparser.ConfigParser()
        config.read(ini)

        # Required values
        src = config['base']['src']
        surface = config['base']['surface']
        dt = float(config['base']['dt'])
        startTime = float(config['base']['startTime'])
        outputTime = float(config['base']['outputTime'])
        steps = int(config['base']['steps'])
        patch = config['base']['patch']
        meanU = config['base']['meanU']

        # Default values
        try:
            dst = config['base']['dst']
        except KeyError:
            dst = os.getcwd()
        try:
            vector = config['base']['vector']
            if ("x" not in vector or "y" not in vector or "z" not in vector):
                print("Error: Please check vector:", vector," and make sure it's correct")
                sys.exit()
        except KeyError:
            vector = "(x,y,z)"
        try:
            transplant = config['base']['transplant']
            transplant = transplant.replace("(","")
            transplant = transplant.replace(")","")
            trans = [float(transplant.split()[0]), float(transplant.split()[1]), float(transplant.split()[2])]
            print (trans)
        except KeyError:
            transplant = "(0.0 0.0 0.0)"
            trans = [0.0,0.0,0.0]
            
        vector = vector.replace(" ","")
        d = dict([('x',0),('y',1),('z',2)])
        conv = [d[vector[1]], d[vector[3]], d[vector[5]]] 

    else:
        print("Error: The config file '-config' is not given !")
        sys.exit()



    # output these parameters 
    print("sourceDir:", src)
    print("outputDir:", dst)
    print("samplingSurface:", surface)
    print("Vecotr convert:", "(x,y,z) -> ", vector, conv)
    print("Time step:", dt)
    print("Source start time:", startTime)
    print("Output start time:", outputTime)
    print("Steps:",steps)
    print("Inlet Patch:",patch)
    print("Mean velocity field:", meanU)
    print("Transplant points:", transplant)

    src = src+"/surfaceSampling/"
    if not os.path.exists(src):
        print(" Source directory is not valid: ", src)
        sys.exit()

    # output dir
    dst = dst+"/boundaryData/"
    if not os.path.exists(dst):
        os.makedirs(dst)
    dst = dst+"/"+patch
    if not os.path.exists(dst):
        os.makedirs(dst)
    
    header = "FoamFile\n" \
          +  "{\n" \
          +  "version        2.0;\n" \
          +  "format         ascii;\n" \
          +  "class          vectorAverageField;\n" \
          +  "object         values;\n" \
          +  "}\n" \
          +  "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n" 

    # +1 to make the data is from 0 to steps*dt
    steps = steps+1
    for i in range(steps):
        srcTime = startTime+dt*i
        # source file
        srcFile = src+'/'+str(format(srcTime,'.7f')).rstrip("0.")+'/'+surface+'/vectorField/U'

        f = open(srcFile, "r")
        lines = f.readlines()
        f.close()
        
        # destination file
        dstDir = dst+'/'+str(format(srcTime-startTime+outputTime,'.7f')).rstrip("0.")
        if not os.path.exists(dstDir):
            os.makedirs(dstDir)
        dstFile = dstDir+"/U"

        f = open(dstFile,"w")
        f.write(header)
        if vector == "(x,y,z)":
            f.write(meanU+"\n")
            f.writelines(lines)
            f.close()
        else:
            f.write(meanU+"\n")
            f.writelines(lines[0:3])
            for n, line in enumerate(lines):
                if line == ")\n":
                    f.write(line)
                    break
                else:
                    if n>2:
                        line = line.replace("(", "")
                        line = line.replace(")", "")
                        newline = "("+line.split()[conv[0]]+" "+line.split()[conv[1]]+" "+line.split()[conv[2]]+")\n"
                        f.write(newline)
            f.close()
        if (i%1000 == 0):
            # Output info every 1000 files
            print(i,": ",format(srcTime,'.7f'), " -> ", dstFile[dstFile.find(patch):])

    # points file. In this case we use 'points' file
    srcFile = src+'/'+str(format(srcTime,'.7f')).rstrip("0.")+'/'+surface+'/points'
    dstFile = dst+"/points"

    f = open(srcFile,'r') 
    lines = f.readlines()
    f.close()
    
    header = "FoamFile\n" \
           + "{\n"\
           + "    version        2.0;\n"\
           + "    format         ascii;\n"\
           + "    class          vectorField;\n"\
           + "    object         points;\n"\
           + "}\n"\
           + "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n"
           
    f = open(dstFile,'w')
    f.write(header)
    f.write("(\n")
    for n, line in enumerate(lines):
        if line ==")\n":
            f.write(line)
            break
        else:
            if n>2:
                line = line.replace("(", "")
                line = line.replace(")", "")
                x = float(line.split()[conv[0]])-trans[0]
                y = float(line.split()[conv[1]])-trans[1]
                z = float(line.split()[conv[2]])-trans[2]
                newline = "("+str(x)+" "+str(y)+" "+str(z)+")\n"
                f.write(newline)
    f.close()
    
    print(" Done!")


if __name__ == '__main__':
    main()
