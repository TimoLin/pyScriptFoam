# This file is modified from eddylicious(Copyright: Timofey Mukka)

"""Functions for reading fields stored in the foamFile format

"""
import numpy as np
import os
__all__ = ["read_structured_points_foamfile",
           "read_structured_velocity_foamfile",
           "read_points_foamfile", "read_velocity_foamfile"]

def read_structured_points_foamfile(readPath, norm, location):
    """Read the coordinates of the points from a foamFile-format file.

    Reads in the locations of the face centers, stored in foamFile
    format by OpenFOAM, and transforms them into 2d numpy arrays.
    
    """
    with open(readPath) as pointsFile:
        points = [line.rstrip(')\n') for line in pointsFile]
    
    points = [line.lstrip('(') for line in points]
    points = points[3:-1]
    #points = np.genfromtxt(points,dtype='f8,str')
    points = np.genfromtxt(map(lambda s:s.encode('utf8'),points))
    
    # Translate coordinates
    one = np.ones(3)
    for n,p in enumerate(points):
        points[n] = p*(one-norm)+location*norm
    
    #return [points[:,0], points[:,1], points[:,2]]
    return points

def read_structured_velocity_foamfile(baseReadPath, surfaceName):
    
    def read(time):
        """
        A function that will actually perform the reading.

        Parameters
        ----------
        time, float or string
            The value of the time, will be converted to a string.

        Returns
        -------
        List of 2d arrays.
        The list contains three items, corresponding
        to the three components of the velocity field, the order of the
        components in the list is x, y and the z.

        """
        readUPath = os.path.join(baseReadPath, str(time), surfaceName,
                                 "vectorField", "U")
        with open(readUPath) as UFile:
            u = [line.rstrip(')\n') for line in UFile]

        u = [line.lstrip('(') for line in u]
        u = u[3:-1]
        #u = np.genfromtxt(u)
        u = np.genfromtxt(map(lambda s:s.encode('utf8'),u))

        # Reshape to 2d

        return [u[:,0],u[:,1],u[:,2]]

    read.reader = "foamFile"

    return read
