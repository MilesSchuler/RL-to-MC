from PIL import Image, ImageDraw
import numpy as np

class TextureTesting:
    # figuring out how texture mapping works and how we want to use it
    # not even sure how we are going to call this class I just wanted a space to mess around

    def __init__(self, model, snap):
        self.vertices = model.getVertices()
        self.textures = model.getTextures()
        self.faces = model.getFaces()
        self.snap = snap
        
        materials = model.getMaterials()

        # assume theres only one material
        mtl = materials[0]
        # file name can be a full path but we just want the name
        # actually, we want them in the same folder just for ease of access so we should edit the name in the file
        mapName = mtl['map_Kd'].split("\\")[-1]
        mapPath = model.getName() + "/" + mapName
        self.map = Image.open(mapPath)
        pixels = self.map.load()
        self.width, self.height = self.map.size
        
        self.draw = ImageDraw.Draw(self.map)
        
        uSnap = np.unique(snap, axis=0)
        # should be set to len(uSnap), 10 is just for demo
        for i in [2]:
            cube = uSnap[i]
            # name to save file
            name = str(i) + "cropped.png"
            # get faces
            vIndices, indices = self.facesInCube(cube[0], cube[1], cube[2])
            # save texture of the cube
            #self.saveTexture(vIndices, indices, name)
            self.drawBlob(vIndices, indices)
        

    # get all the faces that have vertices in a given cube
    def facesInCube(self, x, y, z):
        # should be able to use np.where but can't figure out how :/
        indices = []
        for i in range(len(self.snap)):
            cube = self.snap[i]
            if all(np.equal([x, y, z], cube)):
                indices.append(i)
        
        # if we gave a bad x y z, return empty list
        if len(indices) == 0:
            print("no faces here")
            return [], []
        # obj doesn't use 0-based counting
        indices = [i+1 for i in indices]
        
        faceIndices = np.concatenate([np.unique(np.where(self.faces == i)[0]) for i in indices])
                
        return indices, faceIndices

    # crop and save portion of texture file based on face indices
    def saveTexture(self, vIndices, indices, name):
        xs = []
        ys = []
        for i in indices:
            f = self.faces[i]
            # facesInCube can return faces where the index is there but not in the spot we care about
            if not any(v in [k[0] for k in f] for v in vIndices):
                continue
            # point in face can be (v, vt) or (v, vt, vn), we want vt
            tIndex = [point[1] for point in f]
            # 0 vs 1 based counting
            tIndex = [t-1 for t in tIndex]
            t = [self.textures[i] for i in tIndex]
            # vt points are 0-1, so multiply by dimensions to get coords
            for i in t:
                xs.append(int(self.width * i[0]))
                ys.append(int(self.height * i[1]))
                
        coords = [min(xs), min(ys), max(xs), max(ys)]
        cropped = self.map.crop(coords)
        cropped.save(name)

    def drawBlob(self, vIndices, indices):
        for i in indices:
            xs = []
            ys = []
            f = self.faces[i]
            # facesInCube can return faces where the index is there but not in the spot we care about
            if not any(v in [k[0] for k in f] for v in vIndices):
                continue
            # point in face can be (v, vt) or (v, vt, vn), we want vt
            tIndex = [point[1] for point in f]
            # 0 vs 1 based counting
            tIndex = [t-1 for t in tIndex]
            t = [self.textures[i] for i in tIndex]
            # vt points are 0-1, so multiply by dimensions to get coords
            for i in t:
                xs.append(int(self.width * i[0]))
                ys.append(int(self.height * i[1]))
            
            self.draw.polygon([(xs[0], ys[0]), (xs[1], ys[1]), (xs[2], ys[2])], fill=(255, 0, 0))
            self.map.save("new.png")