import numpy as np

class FillHoles:

    def __init__(self, model):
        self.faces = model.getFaces()
        self.vertices = model.getVertices()
        self.textures = model.getTextures()
    
    def blocksInFace(self, fIndex):
        f = self.faces[fIndex]
        tIndices = f[:,1] - 1
        vIndices = f[:,0] - 1
        vertices = self.vertices[vIndices]
        box = [min(vertices[:,0]), min(vertices[:,1]), min(vertices[:,2]), max(vertices[:,0]), max(vertices[:,1]), max(vertices[:,2])]
        print(box)


