from tkinter.font import ROMAN
from PIL import Image
import numpy as np

class TextureTesting:
    # figuring out how texture mapping works and how we want to use it
    # not even sure how we are going to call this class I just wanted a space to mess around

    def __init__(self, model, snap):
        self.vertices = model.getVertices()
        self.textures = model.getTextures()
        self.faces = model.getFaces()
        self.snap = snap
        
        faces = model.getFaces()
        materials = model.getMaterials()

        # assume theres only one material
        mtl = materials[0]
        # file name can be a full path but we just want the name
        mapName = mtl['map_Kd'].split("\\")[-1]
        mapPath = model.getName() + "/" + mapName
        map = Image.open(mapPath)
        pixels = map.load()
        width, height = map.size

        # turns first vertices in faces list red
        for f in faces[:10]:
            vIndex = [point[0] for point in f]
            tIndex = [point[1] for point in f]
            v = [self.vertices[i] for i in vIndex]
            t = [self.textures[i] for i in tIndex]
            xs = [int(width * i[0]) for i in t]
            ys = [int(height * i[1]) for i in t]
            for i in range(3):
                pixels[(xs[i], ys[i])] = (255, 0, 0)

        # code to remove duplicates from snap but its slow and I don't think we need it
        """
        snap = snap.tolist()
        unique = []
        for i in snap:
            if i not in unique:
                unique.append(i)
        snap = unique
        """
        indices = self.facesInCube(-115, 0, -226)
        
        map.save('new.png')
        #for y in range(height):
        #    for x in range(width):
        #        print(pixels[(x, y)])

    # get all the faces that have vertices in a given cube
    def facesInCube(self, x, y, z):
        # should be able to use np.where but can't figure out how :/
        indices = []
        for i in range(len(self.snap)):
            cube = self.snap[i]
            if all(np.equal([x, y, z], cube)):
                indices.append(i)

        # obj doesn't use 0-based counting
        indices = [i+1 for i in indices]
        
        faceIndices = np.concatenate([np.unique(np.where(self.faces == i)[0]) for i in indices])
        
        return faceIndices
