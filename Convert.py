import numpy

from EuclideanDistance import EuclideanDistance
from Texture import Texture
from ConvertBlocksToArray import BlocksArray

class Convert:
    blocksList = []
    def __init__(self, snap):
        uSnap = numpy.unique(snap, axis = 0)
        for cube in uSnap:
            img = Texture.getImage(cube)

            neighborIndex = EuclideanDistance.find_closest_neighbor(img)
            blockName = BlocksArray.classBlocksNames[neighborIndex]
            print(blockName)
            self.blocksList.append(blockName)


c = Convert()