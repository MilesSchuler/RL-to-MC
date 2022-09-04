from tqdm import tqdm
from EuclideanDistance import EuclideanDistance
from ConvertBlocksToArray import BlocksArray
from Texture import Texture
import numpy as np


class Convert:
    def __init__(self, model, blockFaces, coords, mins, shape, height, tex):
        self.blocksList = []
        self.model = model
        self.shape = shape
        self.blockCoords = coords

        self.dict = blockFaces
        blockPixels, blockTypes = BlocksArray().blockInfo

        self.tex = tex
        self.matchTextures(blockPixels, blockTypes, mins)


    def matchTextures(self, blockPixels, blockTypes, mins):
        ec = EuclideanDistance(blockPixels)

        for i in tqdm(range(len(self.blockCoords))):
            cube = self.blockCoords[i]
            img = self.tex.getImage(cube)
            neighborIndex = ec.find_closest_neighbor(img)

            blockName = blockTypes[neighborIndex]
            self.blocksList.append(blockName)
        