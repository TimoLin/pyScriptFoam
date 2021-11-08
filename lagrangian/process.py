# 2021/11/08 22:12:04  zt

from particle_readers import *
from libs import *

rStep = 0.5 # mm
def process(args, plane, variables, data):
    """Process the sampling data

    Arguments:
        plane:     plane's name
        variables: variables' list
        data:      droplet data array 

    Returns:
        None
    """

    #args = getArgs()

    # Referenced length for normalization
    d_ref = args.diameter
    # Flag for CSV/Tecplot format output
    flagCsv = args.csv
    flagTec = args.tecplot
    # Axial origin of the sampling data
    origin = np.array([float(args.origin.split(",")[0]),float(args.origin.split(",")[1]),float(args.origin.split(",")[2])])
    print(origin)
    # Normal direction of the sampling plane
    norm = np.array([int(args.norm[0]),int(args.norm[1]),int(args.norm[2])])

    dGroup = [int(d) for d in args.sizeGroup.split(',')]
    dGroup.sort()
    rMax = args.rMax

    one = np.ones(3)

    indx = variables.index("Px")
    indy = variables.index("Py")
    indz = variables.index("Pz")
    ind_nP = variables.index("nParticle")
    ind_d = variables.index("d")
    ind_Ux = variables.index("Ux")
    ind_T = variables.index("T")

    rData = radial(rStep,rMax) #mm
    
    d_Profile = []
    d32_Profile = []

    Ua_Profile = []
    Ur_Profile = []
    nP_Profile = []

    T_Profile = []

    for i in range(len(rData)):
        if i == 0:
            r1 = 0
            r2 = rStep/2.0
        else:
            r1 = rData[i]-rStep/2.0 ## lower bound
            r2 = rData[i]+rStep/2.0 ## upper bound

        UaGroup = [0.0]*(len(dGroup)+1) # +1 for global average
        UrGroup = [0.0]*(len(dGroup)+1)
        mGroup = [0.0]*(len(dGroup)+1)
        nParticle = [0.0]*(len(dGroup)+1)

        d1 = 0.0
        d2 = 0.0
        d3 = 0.0
        d7_3 = 0.0
        Tp = 0.0
 
        for p in data: # p means particle
            # get radius in milimeter
            res = one-norm

            # Coordinate transform: relative_[x,y,z]
            rel_x = p[indx]-origin[0]
            rel_y = p[indy]-origin[1]
            rel_z = p[indz]-origin[2]

            r = np.sqrt(
                    (rel_x*res[0])**2+(rel_y*res[1])**2+(rel_z*res[2])**2
                    )*1000
            if (r >= r1 and r <= r2):
 
                d1 += p[ind_nP]*p[ind_d]
                d2 += p[ind_nP]*np.power(p[ind_d],2.0)
                d3 += p[ind_nP]*np.power(p[ind_d],3.0)

                # Temperature average using 7/3 law
                d7_3 += p[ind_nP]*np.power(p[ind_d],7.0/3.0)
                Tp += p[ind_nP]*p[ind_T]*np.power(p[ind_d],7.0/3.0)

                dGroupLoc = loc(dGroup, p[ind_d]*np.power(10,6))
                if (dGroupLoc != -1):
                    # get axial velocity
                    UaGroup[dGroupLoc] += p[ind_nP]*np.power(p[ind_d],3.0)*(
                            p[ind_Ux]*norm[0]+p[ind_Ux+1]*norm[1]+p[ind_Ux+2]*norm[2]
                            )
                    # get radial velocity
                    UrGroup[dGroupLoc] += p[ind_nP]*np.power(p[ind_d],3.0)*(
                            # See issue #1 for more information
                            #(p[ind_Ux+1]*p[indy]+p[ind_Ux+2]*p[indz])/(r/1000)
                            radialVel(p[indx:indx+3],p[ind_Ux:ind_Ux+3],norm,r)
                            )
                    mGroup[dGroupLoc] += p[ind_nP]*np.power(p[ind_d],3.0)
                    nParticle[dGroupLoc] += p[ind_nP]
                # global average
                UaGroup[-1] +=  p[ind_nP]*np.power(p[ind_d],3.0)*(
                            p[ind_Ux]*norm[0]+p[ind_Ux+1]*norm[1]+p[ind_Ux+2]*norm[2]
                            )
                UrGroup[-1] += p[ind_nP]*np.power(p[ind_d],3.0)*(
                            radialVel(p[indx:indx+3],p[ind_Ux:ind_Ux+3],norm,r)
                            )
                mGroup[-1] += p[ind_nP]*np.power(p[ind_d],3.0)
                nParticle[-1] += p[ind_nP]
 
        if nParticle[-1] > 0:
            mean_d10 = d1/nParticle[-1]
            mean_d32 = d3/d2
            mean_Tp = Tp/d7_3
        else:
            mean_d10 = 0.0
            mean_d32 = 0.0
            mean_Tp = 0.0
        for n in range(len(UaGroup)):
            if nParticle[n] >0:
                UaGroup[n] /= mGroup[n]
                UrGroup[n] /= mGroup[n]
            else:
                UaGroup[n] = 0.0
                UrGroup[n] = 0.0


        d_Profile.append(mean_d10)
        d32_Profile.append(mean_d32)
        Ua_Profile.append(UaGroup)
        Ur_Profile.append(UrGroup)
        nP_Profile.append(nParticle)
        T_Profile.append(mean_Tp)

    if flagCsv:
        writeCSV(plane, dGroup, rData/d_ref, d_Profile, d32_Profile, Ua_Profile, Ur_Profile, nP_Profile, T_Profile)

    if flagTec:
        writeTecplot(plane, dGroup, rData/d_ref, d_Profile, d32_Profile, Ua_Profile, Ur_Profile, nP_Profile, T_Profile)

    return

def processLine(args, plane,variables,data):
    """Process the sampling data around the user specified line

    Arguments:
        plane:     plane's name
        variables: variables' list
        data:      droplet data array 

    Returns:
        None
    """
    
    global dGroup
    global rMax

    #args = getArgs()

    # Referenced length for normalization
    d_ref = args.diameter
    # Flag for CSV/Tecplot format output
    flagCsv = args.csv
    flagTec = args.tecplot
    # Axial origin of the sampling data
    origin = np.array([float(args.origin.split(",")[0]),float(args.origin.split(",")[1]),float(args.origin.split(",")[2])])
    print(origin)
    # Normal direction of the sampling plane
    norm = np.array([int(args.norm[0]),int(args.norm[1]),int(args.norm[2])])
    
    dGroup = [int(d) for d in args.sizeGroup.split(',')]
    dGroup.sort()
    rMax = args.rMax

    one = np.ones(3)

    indx = variables.index("Px")
    indy = variables.index("Py")
    indz = variables.index("Pz")
    ind_nP = variables.index("nParticle")
    ind_d = variables.index("d")
    ind_Ux = variables.index("Ux")
    ind_T = variables.index("T")

    rData = radial(rStep,rMax) #mm
    rDataMinus = -rData
    rData = np.append(rDataMinus[::-1], rData[1:], 0)
    
    d_Profile = []
    d32_Profile = []

    Ua_Profile = []
    Ur_Profile = []
    nP_Profile = []

    T_Profile = []

    for i in range(len(rData)):
        #if rData[i] == 0:
            #r1 = 0
            #r2 = rStep/2.0
        #else:
        r1 = rData[i]-rStep/2.0 ## lower bound
        r2 = rData[i]+rStep/2.0 ## upper bound

        UaGroup = [0.0]*(len(dGroup)+1) # +1 for global average
        UrGroup = [0.0]*(len(dGroup)+1)
        mGroup = [0.0]*(len(dGroup)+1)
        nParticle = [0.0]*(len(dGroup)+1)

        d1 = 0.0
        d2 = 0.0
        d3 = 0.0
        d7_3 = 0.0
        Tp = 0.0
 
        for p in data: # p means particle
            # get radius in milimeter
            res = one-norm

            # Coordinate transform: relative_[x,y,z]
            rel_x = p[indx]-origin[0]
            rel_y = p[indy]-origin[1]
            rel_z = p[indz]-origin[2]
            
            r = rel_y*1000
            #r = np.sqrt(
                    #(rel_x*res[0])**2+(rel_y*res[1])**2+(rel_z*res[2])**2
                    #)*1000
            if ( (r >= r1 and r <= r2) and (rel_z>=-rStep*5*1e-3 and (rel_z<=rStep*5*1e-3))):
 
                d1 += p[ind_nP]*p[ind_d]
                d2 += p[ind_nP]*np.power(p[ind_d],2.0)
                d3 += p[ind_nP]*np.power(p[ind_d],3.0)

                # Temperature average using 7/3 law
                d7_3 += p[ind_nP]*np.power(p[ind_d],7.0/3.0)
                Tp += p[ind_nP]*p[ind_T]*np.power(p[ind_d],7.0/3.0)

                dGroupLoc = loc(dGroup, p[ind_d]*np.power(10,6))
                if (dGroupLoc != -1):
                    # get axial velocity
                    UaGroup[dGroupLoc] += p[ind_nP]*np.power(p[ind_d],3.0)*(
                            p[ind_Ux]*norm[0]+p[ind_Ux+1]*norm[1]+p[ind_Ux+2]*norm[2]
                            )
                    # get radial velocity
                    UrGroup[dGroupLoc] += p[ind_nP]*np.power(p[ind_d],3.0)*(
                            # See issue #1 for more information
                            #(p[ind_Ux+1]*p[indy]+p[ind_Ux+2]*p[indz])/(r/1000)
                            radialVel(p[indx:indx+3],p[ind_Ux:ind_Ux+3],norm,r)
                            )
                    mGroup[dGroupLoc] += p[ind_nP]*np.power(p[ind_d],3.0)
                    nParticle[dGroupLoc] += p[ind_nP]
                # global average
                UaGroup[-1] +=  p[ind_nP]*np.power(p[ind_d],3.0)*(
                            p[ind_Ux]*norm[0]+p[ind_Ux+1]*norm[1]+p[ind_Ux+2]*norm[2]
                            )
                UrGroup[-1] += p[ind_nP]*np.power(p[ind_d],3.0)*(
                            radialVel(p[indx:indx+3],p[ind_Ux:ind_Ux+3],norm,r)
                            )
                mGroup[-1] += p[ind_nP]*np.power(p[ind_d],3.0)
                nParticle[-1] += p[ind_nP]
 
        if nParticle[-1] > 0:
            mean_d10 = d1/nParticle[-1]
            mean_d32 = d3/d2
            mean_Tp = Tp/d7_3
        else:
            mean_d10 = 0.0
            mean_d32 = 0.0
            mean_Tp = 0.0
        for n in range(len(UaGroup)):
            if nParticle[n] >0:
                UaGroup[n] /= mGroup[n]
                UrGroup[n] /= mGroup[n]
            else:
                UaGroup[n] = 0.0
                UrGroup[n] = 0.0


        d_Profile.append(mean_d10)
        d32_Profile.append(mean_d32)
        Ua_Profile.append(UaGroup)
        Ur_Profile.append(UrGroup)
        nP_Profile.append(nParticle)
        T_Profile.append(mean_Tp)

    if flagCsv:
        writeCSV(plane, dGroup, rData/d_ref, d_Profile, d32_Profile, Ua_Profile, Ur_Profile, nP_Profile, T_Profile)

    if flagTec:
        writeTecplot(plane, dGroup, rData/d_ref, d_Profile, d32_Profile, Ua_Profile, Ur_Profile, nP_Profile, T_Profile)

    return
