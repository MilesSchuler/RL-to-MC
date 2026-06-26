from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path as FilePath

import numpy as np
from nbtlib import Compound, Double, File, Int, List, String, schema


@dataclass(frozen=True)
class PlacedBlock:
    x: int
    y: int
    z: int
    name: str
    states: tuple[tuple[str, str], ...] = tuple()


class JavaStructureWriter:
    def __init__(self, blocks: list[PlacedBlock], shape):
        self.blocks = blocks
        self.shape = shape

    def write(self, filename: FilePath):
        palette_entries = [("minecraft:air", tuple())]
        for block in self.blocks:
            palette_entry = (block.name, block.states)
            if palette_entry not in palette_entries:
                palette_entries.append(palette_entry)

        palette_index = {entry: index for index, entry in enumerate(palette_entries)}

        Structure = schema(
            "Structure",
            {
                "DataVersion": Int,
                "author": String,
                "size": List[Int],
                "palette": List[schema("State", {"Name": String, "Properties": Compound})],
                "blocks": List[schema("Block", {"state": Int, "pos": List[Int], "nbt": Compound})],
                "entities": List[schema("Entity", {"pos": List[Double], "blockPos": List[Int], "nbt": Compound})],
            },
        )

        class StructureFile(File, Structure):
            def __init__(self, structure_data=None):
                super().__init__(structure_data or {})
                self.gzipped = True

            @classmethod
            def load(cls, filename, gzipped=True):
                return super().load(filename, gzipped)

        new_structure = Structure(
            {
                "DataVersion": 3465,
                "author": "copilot",
                "size": list(map(int, self.shape)),
                "palette": [
                    {
                        "Name": name,
                        "Properties": Compound({key: String(value) for key, value in states}),
                    }
                    for name, states in palette_entries
                ],
                "blocks": [
                    {
                        "pos": [block.x, block.y, block.z],
                        "state": palette_index[(block.name, block.states)],
                        "nbt": Compound(),
                    }
                    for block in self.blocks
                ],
                "entities": [],
            }
        )

        structure_file = StructureFile(new_structure)
        structure_file.save(filename, byteorder="big")


class BedrockStructureWriter:
    def __init__(self, blocks: list[PlacedBlock], shape, mapping_path: str | FilePath = "archive/Data/block/java2bedrock.json"):
        self.blocks = blocks
        self.shape = shape
        self.mapping_path = FilePath(str(mapping_path))
        self.mapping = self._load_mapping()

    def write(self, filename: FilePath):
        java_palette = [("minecraft:air", tuple())]
        for block in self.blocks:
            palette_entry = (block.name, block.states)
            if palette_entry not in java_palette:
                java_palette.append(palette_entry)

        bedrock_palette = []
        states = []
        for name, state_items in java_palette:
            mapped = self.mapping.get(name.replace("minecraft:", ""), {})
            bedrock_palette.append(mapped.get("bedrock_identifier", name))
            states.append(mapped.get("bedrock_states", {}))

        palette_index = {entry: index for index, entry in enumerate(java_palette)}
        block_indices = [0] * int(np.prod(self.shape))
        for block in self.blocks:
            index = block.x * int(self.shape[1]) * int(self.shape[2]) + block.y * int(self.shape[2]) + block.z
            block_indices[index] = palette_index[(block.name, block.states)]

        block_indices = [block_indices, [-1] * int(np.prod(self.shape))]

        Structure = schema(
            "Structure",
            {
                "format_version": Int,
                "size": List[Int],
                "structure": schema(
                    "structure",
                    {
                        "block_indices": List[List[Int]],
                        "entities": List[Compound],
                        "palette": schema(
                            "palette",
                            {
                                "default": schema(
                                    "default",
                                    {
                                        "block_palette": List[
                                            schema(
                                                "block_state",
                                                {
                                                    "name": String,
                                                    "states": schema("states", {}),
                                                    "version": Int,
                                                },
                                            )
                                        ],
                                        "block_position_data": Compound,
                                    },
                                )
                            },
                        ),
                    },
                ),
                "structure_world_origin": List[Int],
            },
        )

        class StructureFile(File, Structure):
            def __init__(self, structure_data=None):
                super().__init__(structure_data or {})
                self.gzipped = False

            @classmethod
            def load(cls, name, gzipped=False, byteorder="big"):
                return super().load(name, gzipped, byteorder)

        new_structure = Structure(
            {
                "format_version": 1,
                "size": list(map(int, self.shape)),
                "structure": {
                    "block_indices": block_indices,
                    "entities": [],
                    "palette": {
                        "default": {
                            "block_palette": [
                                {"name": bedrock_palette[i], "states": states[i], "version": 17959425}
                                for i in range(len(bedrock_palette))
                            ],
                            "block_position_data": {},
                        }
                    },
                },
                "structure_world_origin": [0, 0, 0],
            }
        )

        StructureFile(new_structure).save(filename, byteorder="little")

    def _load_mapping(self):
        if not self.mapping_path.exists():
            return {}
        with self.mapping_path.open("r", encoding="utf-8") as file:
            return json.load(file)