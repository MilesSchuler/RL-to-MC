import pathlib
import time

import numpy as np

from archive.BasicConverter import snapVertices
from archive.Block import Block
from archive.ConvertBlocksToArray import BlocksArray
from archive.EuclideanDistance import EuclideanDistance
from archive.NBTMakerBedrock import NBTMakerBedrock
from archive.NBTMakerJava import NBTMakerJava
from archive.ObjReader import OBJ
from archive.Texture import Texture


OPAQUE_FALLBACK_BLOCK = "white_concrete"
TRANSPARENT_BLOCKS = {
    "ice",
    "packed_ice",
    "blue_ice",
    "slime_block",
    "ochre_froglight",
    "pearlescent_froglight",
    "verdant_froglight",
}


def build_blocks(name: str, height: int = 24, rotate: bool = True):
    model = OBJ(name)
    shape, snap, uSnap = snapVertices(model, height)

    if rotate:
        shape = np.array([shape[0], shape[2], shape[1]])

    texture = Texture(model, shape, snap)
    block_pixels, block_types = BlocksArray().blockInfo
    matcher = EuclideanDistance(block_pixels)

    blocks = []
    for cube in uSnap:
        image = texture.getImage(cube)
        block_index = matcher.find_closest_neighbor(image)
        block_type = block_types[block_index]
        if block_type in TRANSPARENT_BLOCKS:
            block_type = OPAQUE_FALLBACK_BLOCK

        x, y, z = cube
        if rotate:
            blocks.append(Block(int(x), int(z), int(y), block_type))
        else:
            blocks.append(Block(int(x), int(y), int(z), block_type))

    return np.array(blocks), shape


def save_structure(name: str, blocks, shape):
    output_dir = pathlib.Path("Output") / name
    output_dir.mkdir(parents=True, exist_ok=True)

    bedrock_file = output_dir / f"{name}Bedrock.nbt"
    NBTMakerBedrock(blocks, shape).makeNBT(bedrock_file)

    java_file = output_dir / f"{name}Java.nbt"
    NBTMakerJava(blocks, shape).makeNBT(java_file)


def convert(name: str = "bird", height: int = 24, rotate: bool = True):
    start_time = time.time()
    blocks, shape = build_blocks(name=name, height=height, rotate=rotate)
    save_structure(name, blocks, shape)
    print("Total runtime:", time.time() - start_time)


if __name__ == "__main__":
    convert()