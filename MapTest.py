from ObjReader import OBJ
from PIL import Image, ImageDraw

name = 'bird'
model = OBJ(name)


vertices = model.getVertices()
textures = model.getTextures()
faces = model.getFaces()
materials = model.getMaterials()

# assume there is only one material
mtl = materials[0]
# file name is a full path but we just want the name
mapName = mtl['map_Kd'].split("\\")[-1]
mapPath = "./Data/" + model.getName() + "/" + mapName
textmap = Image.open(mapPath)
pixels = textmap.load()
width, height = textmap.size

"""
LOTS OF FUN STUFF
"""



