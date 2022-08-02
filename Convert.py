from tqdm import tqdm

from EuclideanDistance import EuclideanDistance
from ConvertBlocksToArray import BlocksArray


class Convert:
    def compute(self, uSnap, texture, blockPixels, blockTypes):
        for i in tqdm(range(len(uSnap))):
            cube = uSnap[i]
            img = texture.getImage(cube)

            ec = EuclideanDistance(blockPixels)
            neighborIndex = ec.find_closest_neighbor(img)

            blockName = blockTypes[neighborIndex]
            self.blocksList.append(blockName)

    def __init__(self, uSnap, texture):
        self.blocksList = []
        blockPixels, blockTypes = BlocksArray().blockInfo

        self.compute(uSnap, texture, blockPixels, blockTypes)
