from ctypes import Structure
from unicodedata import name

from numpy import integer
from Block import Block
# pip install nbt
from nbtlib import *
import numpy as np

class NBTMakerBedrock:
    def __init__(self, blocks, shape):
        self.shape = shape
        # make block palette from block types in input array, add air at the beginning
        self.palette = np.append('minecraft:air', np.unique(["minecraft:" + block.type for block in blocks]))
        # turn blocks set into array, substituting the block name for its index in the palette using np.where,
        # which for some reason returns it as [[index]]
        blocksArr = np.asarray([[block.x, block.y, block.z, np.where(self.palette == block.type)[0][0]] for block in blocks])
        # remove dupes and sort. it actually doesn't need to be sorted but np.unique does that automatically
        sortedBlocks = np.unique(blocksArr, axis=0)
        # all air to start
        self.blockIndices = [0] * np.prod(shape)
        # add in blocks
        for block in sortedBlocks:
            # get index by finding where it is along the 1d list based off of shape and coords
            self.blockIndices[block[0]*shape[1]*shape[2] + block[1]*shape[2] + block[2]] = block[3]
        
        # blockIndices has a second layer of all -1s, sometimes these are other numbers if blocks need a special value
        self.blockIndices = [self.blockIndices, [-1] * np.prod(shape)]

    def makeNBT(self, filename):
        Structure = schema('Structure', {
            'format_version': Int,
            'size': List[Int],
            'structure': schema('structure', {
                'block_indices': List[List[Int]],
                'entities': List[Compound],
                'palette': schema('palette', {
                    'default': schema('default', {
                        'block_palette': List[schema('block_state', {
                            'name': String,
                            'states': schema('states', {
                            }),
                            'version': Int
                        })],
                        'block_position_data': Compound
                    })
                })
            }),
            'structure_world_origin': List[Int]
        })

        new_structure = Structure({
            'format_version': 1,
            'size': self.shape,
            'structure': {
                'block_indices': self.blockIndices,
                'entities': [],
                'palette': {
                    'default': {
                        'block_palette': 
                        [{'name': self.palette[i], 'states': {}, 'version': 17959425} for i in range(len(self.palette))],
                        'block_position_data': {}
                    }
                }
            },
            'structure_world_origin': [0, 0, 0]
        })

        class StructureFile(File, Structure):
            def __init__(self, structure_data=None):
                super().__init__(structure_data or {})
                self.gzipped = False
            @classmethod
            def load(cls, filename, gzipped=False):
                return super().load(filename, gzipped)

        structure_file = StructureFile(new_structure)
        structure_file.save(filename, byteorder='little')