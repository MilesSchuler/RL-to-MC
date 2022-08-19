from PIL import Image, ImageDraw
import numpy as np
import time


class Texture:

    def __init__(self, model, dict):
        self.vertices = model.getVertices()
        self.textures = model.getTextures()
        self.faces = model.getFaces()
        # texture index table where indexTable[i] is the texture indices that go with vertex i
        self.indexTable = self.reformat()

        self.dict = dict

        materials = model.getMaterials()

        # assume there is only one material
        mtl = materials[0]
        # file name is a full path but we just want the name
        mapName = mtl['map_Kd'].split("\\")[-1]
        mapPath = "./Data/" + model.getName() + "/" + mapName
        #mapPath = "new.jpg"
        self.map = Image.open(mapPath)
        self.pixels = self.map.load()
        self.width, self.height = self.map.size
        
        self.draw = ImageDraw.Draw(self.map)

    def reformat(self):
        # don't need the normals
        newFaces = self.faces[:,:,0:2]
        # don't need to split it up by faces
        newFaces = np.concatenate(newFaces)
        # don't need identical mappings (e.g. [1, 1] and [1, 1])
        newFaces = np.unique(newFaces, axis=0)
        # now we have vIndices and tIndices
        vIndices, tIndices = newFaces[:,0], newFaces[:,1]
        # return_index returns the list of indices that give you the unique array
        # so the [1] just gets that and the [1:] takes the 0 off the beginning because that will mess up the split
        splitIndices = np.unique(vIndices, return_index=True)[1][1:]
        # split the texture indices based on the vertices they are assigned to for easy lookups later
        tIndices = np.split(tIndices, splitIndices)
        return tIndices

    def getImage(self, blockCoords):
        x = str(blockCoords[0])
        y = str(blockCoords[1])
        z = str(blockCoords[2])

        tIndices = self.dict[x + " " + y + " " + z]
        # get texture of the cube
        coords = self.getTexture(tIndices)
        # stretch/shrink to 16x16 array
        coords = self.scale(coords)
        return coords

    # get all the faces that have vertices in a given cube, unused
    def facesInCube(self, indices):
        smallFaces = self.faces[:,:,0]
        faceIndices = np.concatenate([np.unique(np.where(smallFaces == i)[0]) for i in indices])
        return faceIndices

    # get portion of texture file based on face indices
    def getTexture(self, tIndices):
        xs = []
        ys = []
        # 0- vs 1-based counting
        t = [self.textures[i-1] for i in tIndices]
        
        # vt points are 0-1, so multiply by dimensions to get coords
        for i in t:
            xs.append(int(self.width * i[0]))
            ys.append(int(self.height * i[1]))
        coords = [min(xs), min(ys), max(xs), max(ys)]
        return coords

    # draw blob of where texture on block maps to on texture image, for testing
    def drawBlob(self, indices):
        for i in indices:
            xs = []
            ys = []
            f = self.faces[i]
            # point in face can be (v, vt) or (v, vt, vn), we want vt
            tIndex = [point[1] for point in f]
            # 0 vs 1 based counting
            t = [self.textures[i-1] for i in tIndex]
            # vt points are 0-1, so multiply by dimensions to get coords
            for i in t:
                xs.append(int(self.width * i[0]))
                ys.append(int(self.height * i[1]))
            self.draw.polygon([(xs[0], ys[0]), (xs[1], ys[1]), (xs[2], ys[2]), (xs[3], ys[3])], fill=(255, 0, 0))
        self.map.save("new.jpg")
    
    def scale(self, coords):
        block = np.array([], dtype=np.uint8)
        scaleX = (coords[2] - coords[0]) / 16
        scaleY = (coords[3] - coords[1]) / 16
        xs = np.around(scaleX * (np.arange(256) % 16))
        ys = np.around(scaleY * (np.arange(256) // 16))
        for i in range(256):
            block = np.append(block, self.pixels[xs[i], ys[i]])
        return block