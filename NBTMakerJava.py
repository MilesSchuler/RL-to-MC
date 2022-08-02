# pip install nbt
from nbtlib import *
import numpy as np


class NBTMakerJava:
    def __init__(self, blocks, shape):
        self.palette = np.append('minecraft:air', np.unique(["minecraft:" + block.type for block in blocks]))
        self.palette = self.palette.tolist()

        self.shape = shape
        self.blocks = blocks

    def makeNBT(self, filename):

        Structure = schema("Structure", {
            "DataVersion": Int,
            "author": String,
            "size": List[Int],
            "palette": List[schema("State", {
                "Name": String,
                "Properties": Compound,
            })],
            "blocks": List[schema("Block", {
                "state": Int,
                "pos": List[Int],
                "nbt": Compound,
            })],
            "entities": List[schema("Entity", {
                "pos": List[Double],
                "blockPos": List[Int],
                "nbt": Compound,
            })],
        })

        class StructureFile(File, Structure):
            def __init__(self, structure_data=None):
                super().__init__(structure_data or {})
                self.gzipped = True
            @classmethod
            def load(cls, filename, gzipped=True):
                return super().load(filename, gzipped)

        new_structure = Structure({
            "DataVersion": 2730,
            "size": self.shape,
            "palette": [
                {"Name": self.palette[i]} for i in range(len(self.palette))
            ],
            "blocks": [
                {"pos": [block.x, block.y, block.z], "state": self.palette.index("minecraft:" + block.type)} for block in self.blocks
            ],
            "entities": []
        })

        structure_file = StructureFile(new_structure)
        structure_file.save(filename, byteorder="big")