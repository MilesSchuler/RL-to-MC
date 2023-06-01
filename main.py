import numpy as np
import pathlib
import time

from ObjReader import OBJ
from BasicConverter import snapVertices
from Texture import Texture
from Convert import Convert
from Block import Block
from NBTMakerBedrock import NBTMakerBedrock
from NBTMakerJava import NBTMakerJava

start_time = time.time()

name = 'bird'
# some obj files are sideways
rotate = True
model = OBJ(name)

print("OBJ File read after: ", time.time() - start_time)

h = 24

shape, snap, uSnap = snapVertices(model, h)

print("Vertices snapped after: ", time.time() - start_time)

tex = Texture(model, shape, snap)

print("Textures initialized after: ", time.time() - start_time)

classes = Convert(uSnap, tex)
blockTypes = classes.blocksList

# print("Blocks classified after: ", time.time() - start_time)

if rotate:
    shape = np.array([shape[0], shape[2], shape[1]])

n = len(blockTypes)
blocks = np.array([])

for i in range(n):
    blockType = blockTypes[i]
    [x, y, z] = uSnap[i]

    if rotate:
        block = Block(int(x), int(z), int(y), blockType)
    else:
        block = Block(int(x), int(y), int(z), blockType)

    blocks = np.append(blocks, block)

new_dir = pathlib.Path("Output/" + name)
if not new_dir.exists():
    new_dir.mkdir(parents=True)


br_file = new_dir / (name + "Bedrock.nbt")
creator = NBTMakerBedrock(blocks, shape)
creator.makeNBT(br_file)

java_file = new_dir / (name + "Java.nbt")
creator2 = NBTMakerJava(blocks, shape)
creator2.makeNBT(java_file)

print("Total runtime: ", time.time() - start_time)
