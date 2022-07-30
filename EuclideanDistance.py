import numpy as np
from ConvertBlocksToArray import BlocksArray

class EuclideanDistance:

    def __init__(self):
        self.blocks = BlocksArray.blocks

    def find_closest_neighbor(self, inBlock):

        n = self.blocks.shape[1]
        minDistance = np.inf
        minBlock = 0

        for i in range(n):
            block = self.blocks[i]
            dot = np.dot(block, inBlock)

            if dot < minDistance:
                minDistance = dot
                minBlock = i

        return minBlock

