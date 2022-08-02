import numpy as np


class EuclideanDistance:

    def __init__(self, blocksPixels):
        self.blocksPixels = blocksPixels

    def find_closest_neighbor(self, inBlock):
        n = self.blocksPixels.shape[0]
        minDistance = np.inf
        minBlock = 0

        for i in range(n):
            block = self.blocksPixels[i]
            diff = np.subtract(block, inBlock)
            dist = np.dot(diff, diff)

            if dist < minDistance:
                minDistance = dist
                minBlock = i

        return minBlock
