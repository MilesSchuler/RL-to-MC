from ctypes import Structure
from unicodedata import name

from numpy import integer
from Block import Block
# pip install nbt
from nbtlib import *


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
    'size': [2, 2, 2],
    'structure': {
        'block_indices': [[0, 0, 0, 0, 0, 0, 0, 0], [-1, -1, -1, -1, -1, -1, -1, -1]],
        'entities': [],
        'palette': {
            'default': {
                'block_palette': [
                   {'name': 'minecraft:dirt', 'states': {}, 'version': 17959425}
                ],
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
structure_file.save('new_structure.nbt', byteorder='little')  # you can load it in a minecraft world!
