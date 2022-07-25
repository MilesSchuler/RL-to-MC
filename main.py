from ObjReader import OBJ
from BasicConverter import BasicConverter
from NBTMakerBedrock import NBTMakerBedrock
from TextureTesting import TextureTesting

model = OBJ("mountain")

v = model.getVertices()
t = model.getTextures()
f = model.getFaces()

texture = TextureTesting(model)

converter = BasicConverter

h = 50

blocks, shape = converter.convertModel(v, t, f, h)

#creator = NBTMakerBedrock(blocks, shape)

#creator.makeNBT("rock.nbt")

