from ObjReader import OBJ
from BasicConverter import BasicConverter
from NBTMakerBedrock import NBTMakerBedrock
from Texture import Texture
import time

start_time = time.time()

name = 'mountain'
model = OBJ(name)

v = model.getVertices()
t = model.getTextures()
f = model.getFaces()

converter = BasicConverter

h = 10

blocks, shape, snap = converter.convertModel(v, t, f, h)  

texture = Texture(model, snap)

a = texture.getImage(0)

#creator = NBTMakerBedrock(blocks, shape)

#creator.makeNBT(name + ".nbt")

print(time.time() - start_time)