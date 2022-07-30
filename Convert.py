import numpy

from EuclideanDistance import EuclideanDistance
from ConvertBlocksToArray import BlocksArray

class Convert:
    blocksList = []
    def __init__(self, snap, texture):
        uSnap = numpy.unique(snap, axis = 0)
        for cube in uSnap:
            img = texture.getImage(cube)
            
            ec = EuclideanDistance()
            neighborIndex = ec.find_closest_neighbor(img)
            blockName = BlocksArray.classBlocksNames[neighborIndex]
            print(blockName)
            self.blocksList.append(blockName)