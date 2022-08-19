from tqdm import tqdm

from EuclideanDistance import EuclideanDistance
from ConvertBlocksToArray import BlocksArray
from Texture import Texture
import collections



class Convert:
    def __init__(self, model, uSnap, snap, shape, height):
        self.blocksList = []
        self.model = model
        self.shape = shape
        self.snap = snap
        self.uSnap = uSnap
        self.dict = collections.defaultdict(list)
        blockPixels, blockTypes = BlocksArray().blockInfo

        self.findBlocks(model, height)
        self.matchTextures(uSnap, blockPixels, blockTypes)

    def matchTextures(self, uSnap, blockPixels, blockTypes):
        tex = Texture(self.model, self.shape, self.snap, self.dict)

        for i in tqdm(range(len(uSnap))):
            cube = uSnap[i]
            img = tex.getImage(cube)

            ec = EuclideanDistance(blockPixels)
            neighborIndex = ec.find_closest_neighbor(img)

            blockName = blockTypes[neighborIndex]
            self.blocksList.append(blockName)



    