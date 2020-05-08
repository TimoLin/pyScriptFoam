#!/usr/bin/env python
"""
Run FlameMaster transient flame solver for a series of chi values
in the upper branch with consideration of radiation.
"""

import sys, os, subprocess

def listTool(solFolder):
    # Call FlameMaster ListTool to get "chi_st" vs "Tmax"
    if 'syms' not in os.listdir("./"):
        # Create syms file
        with open('syms','w') as f:
            f.write("chi_st\nTmax")

    else:
        # Check syms file content
        with open('syms','r') as f:
            lines = f.readlines()
        if lines[0] != 'chi_st\n':
            # Create syms file
            with open('syms','w') as f:
                f.write("chi_st\nTmax")
            
    status = subprocess.call('$HOME/FlameMaster/Bin/bin/ListTool -M -s syms -r temp.dout '+solFolder+'/*', shell=True) 
    
    chi_upper = []
    if status == 0:
        from operator import itemgetter
        chi_st = []
        Tmax   = []
        with open('temp.dout', 'r') as f:
            lines = f.readlines()
        for line in lines[2:]:
            chi_st.append(float(line.split()[0]))
            Tmax.append(float(line.split()[1]))

        indexT = sorted(enumerate(Tmax), key=itemgetter(1),reverse=True)
        
        for i,value in indexT:
            chi_upper.append(chi_st[i])
            if chi_st[i] == max(chi_st):
                break

    return chi_upper

def transFM(chiUpperBranch, startFile):
    # Run transient flame solver for upper branch with radiation

    # Prepare FM transient flame solver input file
    # Here we use "FMUnsteady.input"
    
    # Check settings in the input file
    with open('FMUnsteady-template.input') as f:
        lines = f.readlines()
    flagRad = False
    for line in lines:
        if 'NumberOfOutputs' in line:
            nOutputs = int(line.split('=')[-1])
            if nOutputs > 50:
                print(" Warning: NumberOfOutputs is too many. Consider reducing it to 20~50?")
        elif 'ComputeWithRadiation is' in line:
            if line.split()[-1] != "TRUE" or "#" in line:
                print(" Error: Radiation flag shall be 'TRUE'")
                print("   Setting in file: "+line)
                print(" Abort!")
                sys.exit()
            else:
                flagRad = True

    if not flagRad:
        print(" Error: Radiation flag shall be set like below")
        print("   ComputeWithRadiation is True")
        print(" Abort!")
        sys.exit()

    print(" FMUnsteay.input check passed! Hah")

    for i, chi in enumerate(chiUpperBranch):
        outDir = "Chi-"+str(chi)
        if not os.path.exists(outDir):
            os.makedirs(outDir)
        chi_st = str(chi)

        # Generate input file from template
        sedCmd = 'sed -e s#@Output@#'+outDir+'#'+ \
                 '    -e s#@Startfile@#'+startFile[i]+'#' \
                 '    -e s#@chi_st@#'+str(chi)+'#' \
                 '    FMUnsteady-template.input > FMUnsteady-'+str(chi)+'.input'

        #print(sedCmd)
        status = subprocess.call(sedCmd,shell=True)
        #print(status)
        if status != 0:
            print(" Error in command: "+sedCmd)
            print(" Abort!")
            sys.exit()
        fmCmd = '$HOME/FlameMaster/Bin/bin/FlameMan -i'+' FMUnsteady-'+str(chi)+'.input'
        status = subprocess.call(fmCmd,shell=True)
        if status != 0:
            print(" Error in command: "+fmCmd)
            print(" Abort!")
            sys.exit()




def startfileList(chiUpperBranch, solFolder):
    # Find start FM files for the transient flame solver
    fileList = os.listdir(solFolder)
    startFile = [""]*len(chiUpperBranch)
    for file in fileList:
        if 'chi' in file and 'Tst' in file:
            # Get chi value from file name
            # e.g.: CH4_p01_0chi00005tf0300to0300Tst1944
            chi = float(file[file.index('chi')+3:file.index('tf')])
            if chi in chiUpperBranch:
                startFile[chiUpperBranch.index(chi)] = solFolder+'/'+file 

    
    for i in range(len(startFile)):
        if startFile[i] == "":
            print( " Can't find start file for Chi_st:",chiUpperBranch[i])

    if "" in startFile:
        print(" Abort!")
        sys.exit()

    return startFile

def main():
    
    solFolder = sys.argv[sys.argv.index('-dir')+1]

    chiUB = listTool(solFolder)

    sFiles = startfileList(chiUB, solFolder)

    transFM(chiUB,sFiles)

if __name__ == '__main__':
    main()
    
