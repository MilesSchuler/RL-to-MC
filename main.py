from Point import Point
from ObjReader import OBJ
from BasicConverter import BasicConverter
from NBTMaker import NBTMaker

model = OBJ("dwayne.obj")

v = model.getVertices()
t = model.getTextures()
f = model.getFaces()

converter = BasicConverter

h = 50

blocks = converter.convertModel(v, t, f, h)

creator = NBTMaker

structureFile = creator.makeNBT(blocks)

