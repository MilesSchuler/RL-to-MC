import numpy as np

from EuclideanDistance import EuclideanDistance
from ConvertBlocksToArray import BlocksArray

class Convert:
    def __init__(self, uSnap, texture):
        self.blocksList = []
        blockPixels, blockTypes = BlocksArray().blockInfo

        for i in range(len(uSnap)):
            cube = uSnap[i]
            img = texture.getImage(cube)

            ec = EuclideanDistance(blockPixels)
            neighborIndex = ec.find_closest_neighbor(img)

            blockName = blockTypes[neighborIndex]
            self.blocksList.append(blockName)

            #print("block #" + str(i) + " at (" + str(cube[0]) + ", " + str(cube[1]) + ", " + str(cube[2]) + ") is " + blockName)