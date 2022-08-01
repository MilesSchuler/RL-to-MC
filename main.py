import numpy as np
import time

from ObjReader import OBJ
from BasicConverter import BasicConverter
from Texture import Texture
from Convert import Convert
from Block import Block
from NBTMakerBedrock import NBTMakerBedrock


start_time = time.time()

name = 'mountain'
model = OBJ(name)

print("OBJ File read after: ", time.time() - start_time)

converter = BasicConverter()
h = 4
shape, snap, uSnap = converter.convertModel(model, h)

print("Vertices snapped after: ", time.time() - start_time)

tex = Texture(model, shape, snap)

print("Textures initialized after: ", time.time() - start_time)

classes = Convert(uSnap, tex)
blockTypes = classes.blocksList

print("Blocks classified after: ", time.time() - start_time)

n = len(blockTypes)
blocks = np.array([], dtype=Block)

for i in range(n):
    blockType = blockTypes[i]
    [x, y, z] = uSnap[i]

    block = Block(int(x), int(y), int(z), blockType)

    blocks = np.append(blocks, block)

#creator = NBTMakerBedrock(blocks, shape)
#creator.makeNBT(name + ".nbt")

print("Total runtime: ", time.time() - start_time)
print(blocks[0].to_string())

