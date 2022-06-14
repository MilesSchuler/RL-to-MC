from Point import Point
from ObjReader import OBJ
from BasicConverter import BasicConverter
from NBTMaker import NBTMaker

# example using new Point class
testPoint = Point(1.0, 1.5, 2.0)
testPoint.printLocation()

model = OBJ("dwayne.obj")

v = model.getVertices()
t = model.getTextures()
f = model.getFaces()

converter = BasicConverter

blocks = converter.convertModel(v, t, f)

creator = NBTMaker

structureFile = creator.makeNBT(blocks)

