from tqdm import tqdm
from EuclideanDistance import EuclideanDistance
from ConvertBlocksToArray import BlocksArray
from Texture import Texture


class Convert:
    def __init__(self, model, blockFaces, coords, mins, shape, height):
        self.blocksList = []
        self.model = model
        self.shape = shape
        self.blockCoords = coords

        self.dict = blockFaces
        blockPixels, blockTypes = BlocksArray().blockInfo

        self.matchTextures(blockPixels, blockTypes, mins)


    def matchTextures(self, blockPixels, blockTypes, mins):
        tex = Texture(self.model, self.dict, mins)
        ec = EuclideanDistance(blockPixels)

        for i in tqdm(range(len(self.blockCoords))):
            cube = self.blockCoords[i]
            img = tex.getImage(cube)
            neighborIndex = ec.find_closest_neighbor(img)

            blockName = blockTypes[neighborIndex]
            self.blocksList.append(blockName)



    