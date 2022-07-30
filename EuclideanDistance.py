import numpy as np
from BlocksArray import blocksArray

class EuclideanDistance:

    def __init__(self):
        self.blocks = blocksArray

    def find_closest_neighbor(self, inBlock):

        n = blocksArray.shape[1]
        minDistance = np.inf
        minBlock = 0

        for i in range(n):
            block = blocksArray[i]
            dot = np.dot(block, inBlock)

            if dot < minDistance:
                minDistance = dot
                minBlock = i

        return minBlock

