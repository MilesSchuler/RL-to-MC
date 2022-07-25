from tkinter.font import ROMAN
from PIL import Image

class TextureTesting:
    # figuring out how texture mapping works and how we want to use it
    # not even sure how we are going to call this class I just wanted a space to mess around


    def __init__(self, model):
        vertices = model.getVertices()
        textures = model.getTextures()
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
            v = [vertices[i] for i in vIndex]
            t = [textures[i] for i in tIndex]
            xs = [int(width * i[0]) for i in t]
            ys = [int(height * i[1]) for i in t]
            print(xs)
            print(ys)
            for i in range(3):
                pixels[(xs[i], ys[i])] = (255, 0, 0)
            print(vIndex)
            
        map.save('new.png')
        #for y in range(height):
        #    for x in range(width):
        #        print(pixels[(x, y)])
