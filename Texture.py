from PIL import Image, ImageDraw
import numpy as np
import collections


class Texture:

    def __init__(self, model, shape, snap):
        self.vertices = model.getVertices()
        self.textures = model.getTextures()
        self.faces = model.getFaces()

        self.dict = collections.defaultdict(list)
        for i in range(len(snap)):

            x = str(snap[i][0])
            y = str(snap[i][1])
            z = str(snap[i][2])

            self.dict[x + " " + y + " " + z].append(i)

        materials = model.getMaterials()

        # assume there is only one material
        mtl = materials[0]
        # file name is a full path but we just want the name
        mapName = mtl['map_Kd'].split("\\")[-1]
        mapPath = "./Data/" + model.getName() + "/" + mapName
        self.map = Image.open(mapPath)
        self.pixels = self.map.load()
        self.width, self.height = self.map.size
        
        self.draw = ImageDraw.Draw(self.map)

    def getImage(self, blockCoords):
        x = str(blockCoords[0])
        y = str(blockCoords[1])
        z = str(blockCoords[2])

        # obj doesn't use 0-based counting
        vIndices = [int(i) + 1 for i in self.dict[x + " " + y + " " + z]]
        # get faces
        fIndices = self.facesInCube(vIndices)
        #print(vIndices)
        # get texture of the cube
        coords = self.getTexture(fIndices)
        #self.drawBlob(fIndices)

        # stretch/shrink to 16x16 array
        return self.scale(coords)

    # get all the faces that have vertices in a given cube
    def facesInCube(self, indices):
        smallFaces = self.faces[:,:,0]
        faceIndices = np.concatenate([np.unique(np.where(smallFaces == i)[0]) for i in indices])
        return faceIndices

    # get portion of texture file based on face indices
    def getTexture(self, indices):
        xs = []
        ys = []
        for i in indices:
            f = self.faces[i]
            # point in face can be (v, vt) or (v, vt, vn), we want vt
            tIndex = [point[1] for point in f]
            # 0 vs 1 based counting
            t = [self.textures[i-1] for i in tIndex]
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
        for i in range(256):
            x = np.around(scaleX * (i % 16))
            y = np.around(scaleY * (i // 16))
            block = np.append(block, self.pixels[(x, y)])
        return block
