from PIL import Image, ImageDraw
import numpy as np
import collections

class Texture:

    def __init__(self, model, snap, mins, blockLength):
        self.vertices = model.getVertices()
        self.textures = model.getTextures()
        self.faces = model.getFaces()
        self.blockLength = blockLength
        self.mins = mins
        # texture index table where indexTable[i] is the texture indices that go with vertex i
        self.indexTable, self.bigFaces = self.reformat()
        
        self.dict = collections.defaultdict(list)
        
        # create dict with values from snap,
        # this will have holes that we fill in later
        for i in range(len(snap)):
            x = str(snap[i][0])
            y = str(snap[i][1])
            z = str(snap[i][2])
            for index in self.indexTable[i]:
                self.dict[x + " " + y + " " + z].append(index)
        
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
        smallFaces = []
        bigFaces = []
        
        # split the faces between small and big
        for f in self.faces:
            v = self.vertices[f[:,0] - 1]
            x = abs(max(v[:,0]) - min(v[:,0]))
            y = abs(max(v[:,1]) - min(v[:,1]))
            z = abs(max(v[:,2]) - min(v[:,2]))
            
            # cutoff for small vs big face could be something else
            if x > self.blockLength or y > self.blockLength or z > self.blockLength:
                bigFaces.append(f)
            else:
                smallFaces.append(f)
        
        bigFaces = np.array(bigFaces)

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
        return tIndices, bigFaces

    def getImage(self, block):
        # dict was made before we new what the mins were so it is shifted
        #block += self.mins
        x = str(block[0])
        y = str(block[1])
        z = str(block[2])
        faceInfo = self.dict[x + " " + y + " " + z]
        # faceInfo for big faces is [fIndex, lengthScale, [u, v]]
        # for small faces, its a list of texture indices
        # TODO there is a better way to do this for sure but I'm just checking whether its big or small
        # by using these ifs to check if it is in this format
        if len(faceInfo) == 3:
            if type(faceInfo[2]) == list:
                coords = self.getTextureBig(int(faceInfo[0]), faceInfo[1], faceInfo[2])
                coords = self.scale(coords)
                block -= self.mins
                return coords
        
        # get texture of the cube
        coords = self.getTexture(faceInfo)
        
        # stretch/shrink to 16x16 array
        coords = self.scale(coords)
    
        #block -= self.mins
        return coords

    # get all the faces that have vertices in a given cube, unused
    def facesInCube(self, indices):
        smallFaces = self.faces[:,:,0]
        faceIndices = np.concatenate([np.unique(np.where(smallFaces == i)[0]) for i in indices])
        return faceIndices

    # get portion of texture file based on face indices
    def getTexture(self, tIndices):
        # get all the texture indices and put them into one array
        #tIndices = np.concatenate(self.faces[fIndices,:,1])
        xs = []
        ys = []
        # 0- vs 1-based counting
        t = [self.textures[i-1] for i in tIndices]
        
        # vt points are 0-1, so multiply by dimensions to get coords
        for i in t:
            xs.append(int(self.width * i[0]))
            ys.append(int(self.height * i[1]))
        corners = [min(xs), min(ys), max(xs), max(ys)]
        return corners
    
    def getTextureBig(self, fIndex, lengthScale, faceCenter):
        # TODO test/look over this section
        # rn it is outputting coords that are all around 0 or really big ones
        # it is the really big ones causing the error but the ones around 0 are also wrong
        # get texture indices and shift to 0-based
        face = self.faces[fIndex]
        tIndices = face[:,0] - 1
        # get texture coords for points in this face
        fTextures = self.textures[tIndices]
        # define direction vectors u and v on 2d texture map
        u = fTextures[1] - fTextures[0]
        v = fTextures[2] - fTextures[0]
        # this is could be wrong i am very confused
        # in theory it is saying, start at one corner and then go a certain amount in u direction and a certain amount v direction
        p = fTextures[0] + faceCenter[0]*u + faceCenter[1]*v
        # get size of face to calculate length, also not sure if this is correct
        faceSize = max(fTextures[:,0]) - min(fTextures[:,1])
        length = int(faceSize * lengthScale)
        # get corners of square for scaling
        corners = [p[0]-length/2, p[1]-length/2, p[0]+length/2, p[1]+length/2]
        return corners
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
        # can be (r, g, b, a) but we only want rgb
        for i in range(256):
            try:
                block = np.append(block, self.pixels[xs[i], ys[i]][:3])
            except:
                # not working right now, ignore error about "operands could not be broadcast together..."
                # see TODO in getTextureBig
                print(coords)
                break
        return block