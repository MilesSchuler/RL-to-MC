import numpy as np
from ConvertBlocksToArray import BlocksArray

class EuclideanDistance:

    def __init__(self):
        ba = BlocksArray()
        self.blocksPixels = ba.blocksPixels
        self.blocksNames = ba.classBlocksNames

    def find_closest_neighbor(self, inBlock):

        n = self.blocksPixels.shape[1]
        minDistance = np.inf
        minBlock = 0

        for i in range(n):
            block = self.blocksPixels[i]
            dot = np.dot(block, inBlock)

            if dot < minDistance:
                minDistance = dot
                minBlock = i

        return minBlock

