import numpy

from EuclideanDistance import EuclideanDistance
from ConvertBlocksToArray import BlocksArray

class Convert:
    blocksList = []
    def __init__(self, snap, texture):
        blockPixels, blockTypes = BlocksArray().blockInfo
        uSnap = numpy.unique(snap, axis = 0)
        for i in range(len(uSnap)):
            cube = uSnap[i]
            img = texture.getImage(cube)
            ec = EuclideanDistance(blockPixels)
            neighborIndex = ec.find_closest_neighbor(img)
            blockName = blockTypes[neighborIndex]
            self.blocksList.append(blockName)

            print("block #" + str(i) + " at (" + str(cube[0]) + ", " + str(cube[1]) + ", " + str(cube[2]) + ") is " + blockName)