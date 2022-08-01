from ObjReader import OBJ
from BasicConverter import BasicConverter
from Texture import Texture
from Convert import Convert
from NBTMakerBedrock import NBTMakerBedrock

import time

start_time = time.time()

name = 'mountain'
model = OBJ(name)
v = model.getVertices()
t = model.getTextures()
f = model.getFaces()

converter = BasicConverter()
h = 10
blocks, shape, snap = converter.convertModel(v, t, f, h)
tex = Texture(model, shape, snap)

blockTypes = Convert(snap, tex).blocksList
for i in range(len(blocks)):
    blocks[i].type = blockTypes[i]

#creator = NBTMakerBedrock(blocks, shape)
#creator.makeNBT(name + ".nbt")

print(time.time() - start_time)






































"""name = 'mountain'
model = OBJ(name)
v = model.getVertices()
t = model.getTextures()
f = model.getFaces()

converter = BasicConverter
h = 10
blocks, shape, snap = converter.convertModel(v, t, f, h)  
texture = Texture(model, shape, snap)



blockTypes = Convert(snap).blocksList


# creator = NBTMakerBedrock(blocks, shape)

# creator.makeNBT(name + ".nbt")"""