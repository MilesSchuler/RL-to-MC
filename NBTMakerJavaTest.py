from numpy import integer
from Block import Block
# pip install nbt
from nbtlib import *

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

new_structure = Structure({
    "DataVersion": 2730,
    "size": [1, 2, 1],
    "palette": [
        {"Name": "minecraft:dirt"}
    ],
    "blocks": [
        {"pos": [0, 0, 0], "state": 0},
        {"pos": [0, 1, 0], "state": 0}
    ],
    "entities": []
})

class StructureFile(File, Structure):
    def __init__(self, structure_data=None):
        super().__init__(structure_data or {})
        self.gzipped = True
    @classmethod
    def load(cls, filename, gzipped=True):
        return super().load(filename, gzipped)

structure_file = StructureFile(new_structure)
structure_file.save("test_structure.nbt", byteorder="big")  # you can load it in a minecraft world!