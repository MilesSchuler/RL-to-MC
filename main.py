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
from FindBlocks import FindBlocks

start_time = time.time()

name = 'BigBen'
# some obj files are sideways
rotate = True
textured = True
model = OBJ(name)

print("OBJ File read after: ", time.time() - start_time)

h = 16

shape, snap, uSnap = snapVertices(model, h)
converter = FindBlocks(model, h)
blockFaces, blockCoords, mins = converter.convertModel()


# find difference between usnap and blockcoords
b = np.array([str(i)[1:-1] for i in blockCoords])
a = np.array([str(i)[1:-1] for i in uSnap])

result = np.setdiff1d(b, a)
result = [i.split(" ") for i in result]
# print(result)


print("Vertices snapped after: ", time.time() - start_time)


# print("Textures initialized after: ", time.time() - start_time)
if textured:
    classes = Convert(model, blockFaces, blockCoords, mins, shape, h)
    blockTypes = classes.blocksList
else:
    blockTypes = ['stone'] * len(blockCoords)

# print("Blocks classified after: ", time.time() - start_time)

if rotate:
    shape = np.array([shape[0], shape[2], shape[1]])

n = len(blockTypes)
blocks = np.array([])

for i in range(n):
    blockType = blockTypes[i]
    [x, y, z] = blockCoords[i]

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

