from ctypes import Structure

from numpy import integer
from Block import Block
# pip install nbt
from nbtlib import *
import numpy as np

class NBTMakerJava:
    """def __init__(self, blocks, shape):
        self.shape = shape
        # make block palette from block types in input array, add air at the beginning
        self.palette = np.append('minecraft:air', np.unique(["minecraft:" + block.type for block in blocks]))
        self.palette = self.palette.tolist()
        # turn blocks set into array, substituting the block name for its index in the palette using np.where,
        # which for some reason returns it as [[index]]
        blocksArr = [[block.x, block.y, block.z, self.palette.index("minecraft:" + block.type)] for block in blocks]
        # all air to start
        self.blockIndices = [0] * np.prod(shape)
        # add in blocks
        for block in blocksArr:
            # get index by finding where it is along the 1d list based off of shape and coords
            self.blockIndices[block[0]*shape[1]*shape[2] + block[1]*shape[2] + block[2]] = block[3]
        
        # blockIndices has a second layer of all -1s, sometimes these are other numbers if blocks need a special value
        self.blockIndices = [self.blockIndices, [-1] * np.prod(shape)]"""

    def makeNBT(self, filename):
        Structure = schema('Structure', {
            'DataVersion': Int,
            'author': String,
            'size': List[Int],
            'palette': List[schema('State', {
                'Name': String,
                'Properties': Compound,
            })],
            'blocks': List[schema('Block', {
                'state': Int,
                'pos': List[Int],
                'nbt': Compound,
            })],
            'entities': List[schema('Entity', {
                'pos': List[Double],
                'blockPos': List[Int],
                'nbt': Compound,
            })],
        })

        new_structure = Structure({
            'DataVersion': 1139,
            'author': 'dinnerbone',
            'size': [1, 2, 1],
            'palette': [
                {'Name': 'minecraft:dirt'}
            ],
            'blocks': [
                {'pos': [0, 0, 0], 'state': 0},
                {'pos': [0, 1, 0], 'state': 0}
            ],
            'entities': [],
        })

        class StructureFile(File, Structure):
            def __init__(self, structure_data=None):
                super().__init__(structure_data or {})
                self.gzipped = False
            @classmethod
            def load(cls, filename, gzipped=False):
                return super().load(filename, gzipped)

        structure_file = StructureFile(new_structure)
        structure_file.save('new_structure.nbt')  # you can load it in a minecraft world!

NBTMakerJava().makeNBT("c")