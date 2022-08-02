import numpy as np
# https://github.com/rsalmei/alive-progress
from alive_progress import alive_bar

from EuclideanDistance import EuclideanDistance
from ConvertBlocksToArray import BlocksArray

class Convert:
    def compute(self, uSnap, texture, blockPixels, blockTypes):
        for i in range(len(uSnap)):
            cube = uSnap[i]
            img = texture.getImage(cube)

            ec = EuclideanDistance(blockPixels)
            neighborIndex = ec.find_closest_neighbor(img)

            blockName = blockTypes[neighborIndex]
            self.blocksList.append(blockName)

            yield

    def __init__(self, uSnap, texture):
        self.blocksList = []
        blockPixels, blockTypes = BlocksArray().blockInfo

        with alive_bar(len(uSnap)) as bar:
            for _ in self.compute(uSnap, texture, blockPixels, blockTypes):
                bar()

            #print("block #" + str(i) + " at (" + str(cube[0]) + ", " + str(cube[1]) + ", " + str(cube[2]) + ") is " + blockName)