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
        mapName = mtl['map_Kd'].split("\\")[-1]
        mapPath = model.getName() + "/" + mapName
        map = Image.open(mapPath)
        pixels = map.load()
        width, height = map.size
        
        draw = ImageDraw.Draw(map)
        
        # get faces
        vIndices, indices = self.facesInCube(0, 8, 1)
        #print("Vertex indices: ", vIndices)
        #print("Face indices: ", indices)
        # get texture points and color triangles red
        for i in indices:
            f = self.faces[i]
            # facesInCube can return faces where the index is there but not in the spot we care about
            if not any(v in [k[0] for k in f] for v in vIndices):
                continue
            # point in face can be (v, vt) or (v, vt, vn)
            tIndex = [point[1] for point in f]
            # 0 vs 1 based counting
            tIndex = [t-1 for t in tIndex]
            t = [self.textures[i] for i in tIndex]
            # vt points are 0-1
            xs = [int(width * i[0]) for i in t]
            ys = [int(height * i[1]) for i in t]
            #print(xs, ys, tIndex)
            #for i in range(len(xs)):
            #    pixels[(xs[i], ys[i])] = (255, 0, 0)
            draw.polygon([(xs[0], ys[0]), (xs[1], ys[1]), (xs[2], ys[2])], fill = (255,255,0))
        
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
        
        # if we gave a bad x y z, return empty list
        if len(indices) == 0:
            print("no faces here")
            return [], []
        # obj doesn't use 0-based counting
        indices = [i+1 for i in indices]
        
        faceIndices = np.concatenate([np.unique(np.where(self.faces == i)[0]) for i in indices])
                
        return indices, faceIndices
