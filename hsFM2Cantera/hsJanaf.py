import sys
import os
class flamelet():
    def __init__(self ):
        self.name = []
        self.data = []
        self.nSpecies = 0
        self.hs = []
    def readName(self, _name):
        self.name.append(_name)
    def readData(self, _data):
        self.data.append(_data)
    def readChi(self, _chi):
        self.chi_st = _chi
    def setHs(self, _hs):
        self.hs = _hs
    def setNspecise(self, n):
        self.nSpecies = n

def readFM(fname, fm):
    f = open(fname,'r')

    # no use header lines
    line = f.readline()
    while ('chi_st' not in line):
        line = f.readline()
   
    chi_st = float(line.split()[2])
    fm.readChi(chi_st)

    while ('numOfSpecies' not in line):
        line = f.readline()
    
    n_species = int(line.split()[2])
    fm.setNspecise(n_species)

    line = f.readline()
    n_grid = int(line.split()[2])
    
    while ('body' not in line):
        line = f.readline()

    # Variable name Z
    line = f.readline()
    fm.readName(line.split()[0])
    
    data= []
    for n in range( int(n_grid/5) + 1):
        line = f.readline()
        for temp in line.split():
            data.append(temp)
    fm.readData(data)

    # Variable name Temperature
    line = f.readline()
    fm.readName('T')
    data = []
    for n in range( int(n_grid/5) + 1):
        line = f.readline()
        for temp in line.split():
            data.append(temp)
    fm.readData(data)


    # read species
    for n_s in range(n_species):
        # Variable name Temperature
        line = f.readline()
        specie = line.split()[0]
        fm.readName(specie[specie.index('-')+1:])
        
        data = []
        for n in range( int( n_grid/5) + 1):
            line = f.readline()
            for temp in line.split():
                data.append(temp)
        fm.readData(data)
    
    # end up here, don't need the rest part
    f.close()

def outputFM(outdir, f_dir, fname, fm):
    f = open(fname, 'r')
    lines = f.readlines()
    f.close()

    n_grid = len(fm.data[0])    

    ind = lines.index('trailer\n')
    lines.insert(ind,'SensibleEnthalpy [J/kg]\n')
    ind += 1
    nlines = int(n_grid/5)+1
    
    line = ''
    for n in range(n_grid):
        line += '\t'+str(fm.hs[n])
        if (n+1)%5==0 or n == n_grid-1:
            line += '\n'
            lines.insert(ind,line)
            ind += 1
            line = ''

    fname = fname.replace(f_dir,'')
    f = open(outdir+fname, 'w')
    f.writelines(lines)
    f.close()

def calcHs(fm, chi, Hs):
    for n, _chi in enumerate(chi):
        if fm.chi_st == _chi or abs(fm.chi_st -_chi)< 1e-10 :
            fm.hs = Hs[n]
            flag = True
            break
        else:
            flag = False
    if flag == False:
        print('Cant find Hs for ', fm.chi_st, ' -to- ', _chi)

def main():
    if '-dir' in sys.argv:
        f_dir = sys.argv[sys.argv.index('-dir')+1]
        f_list = os.listdir(f_dir)
        for n in range(len(f_list)):
            f_list[n] = f_dir+'/'+f_list[n]

    #os.chdir(f_dir)
    fms = []
    
    outdir = 'HsJanaf'

    foamlog = 'log'
    f = open(foamlog, 'r')
    lines = f.readlines()
    f.close()

    # parse log
    chi=[]
    Hs=[]
    for n, line in enumerate(lines):
        if 'This is chi' in line:
            chi.append(float(lines[n+1]))
            temp = lines[n+4]
            _hs = temp.split(',')[0:]
            Hs.append(_hs[0:len(_hs)-1])

    for fname in f_list:
        fms.append(flamelet())
        readFM(fname, fms[-1])   
        #calcHs(fms[-1])
        calcHs(fms[-1], chi, Hs)
        outputFM(outdir, f_dir, fname, fms[-1])

       
if __name__ == '__main__':
    main()
