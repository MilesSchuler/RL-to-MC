from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class ObjVertexRef:
    vertex_index: int
    texture_index: int | None


@dataclass(frozen=True)
class ObjFace:
    vertices: tuple[ObjVertexRef, ...]
    material: str | None


@dataclass(frozen=True)
class SourceMaterial:
    name: str
    map_kd: str | None


class SourceModel:
    def __init__(self, name: str, root: Path, vertices, textures, faces, materials):
        self.name = name
        self.root = root
        self.vertices = np.asarray(vertices, dtype=float)
        self.textures = np.asarray(textures, dtype=float)
        self.faces = faces
        self.materials = materials

    @classmethod
    def load(cls, name: str, root: str | Path = "archive/Data") -> "SourceModel":
        root_path = Path(root) / name
        obj_path = root_path / f"{name}.obj"

        vertices: list[list[float]] = []
        textures: list[list[float]] = []
        faces: list[ObjFace] = []
        materials: list[SourceMaterial] = []

        active_material: str | None = None

        with obj_path.open("r", encoding="utf-8") as obj_file:
            for line in obj_file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split()
                keyword = parts[0]

                if keyword == "v":
                    vertices.append([float(value) for value in parts[1:4]])
                elif keyword == "vt":
                    textures.append([float(value) for value in parts[1:4]])
                elif keyword == "usemtl":
                    active_material = parts[1]
                elif keyword == "mtllib":
                    materials.extend(_load_mtl(root_path / parts[1]))
                elif keyword == "f":
                    refs: list[ObjVertexRef] = []
                    for token in parts[1:]:
                        fields = token.split("/")
                        vertex_index = int(fields[0])
                        texture_index = int(fields[1]) if len(fields) > 1 and fields[1] else None
                        refs.append(ObjVertexRef(vertex_index, texture_index))
                    faces.append(ObjFace(tuple(refs), active_material))

        return cls(name, root_path, vertices, textures, faces, materials)

    @property
    def texture_path(self) -> Path:
        for material in self.materials:
            if material.map_kd:
                return self.root / Path(material.map_kd).name
        raise FileNotFoundError(f"No map_Kd texture found for {self.name}")

    @property
    def texture_image(self) -> Image.Image:
        return Image.open(self.texture_path).convert("RGBA")

    def triangulated_faces(self) -> Iterable[tuple[np.ndarray, np.ndarray, str | None]]:
        for face in self.faces:
            if len(face.vertices) < 3:
                continue
            v0 = face.vertices[0]
            for index in range(1, len(face.vertices) - 1):
                v1 = face.vertices[index]
                v2 = face.vertices[index + 1]
                vertices = np.array([
                    self.vertices[v0.vertex_index - 1],
                    self.vertices[v1.vertex_index - 1],
                    self.vertices[v2.vertex_index - 1],
                ], dtype=float)
                textures = np.array([
                    self._texture_coords(v0.texture_index),
                    self._texture_coords(v1.texture_index),
                    self._texture_coords(v2.texture_index),
                ], dtype=float)
                yield vertices, textures, face.material

    def _texture_coords(self, texture_index: int | None) -> np.ndarray:
        if texture_index is None or texture_index <= 0 or texture_index > len(self.textures):
            return np.array([0.0, 0.0, 0.0], dtype=float)
        coords = self.textures[texture_index - 1]
        if coords.shape[0] == 2:
            coords = np.array([coords[0], coords[1], 0.0], dtype=float)
        return np.asarray(coords[:3], dtype=float)


def _load_mtl(path: Path) -> list[SourceMaterial]:
    materials: list[SourceMaterial] = []
    current_name: str | None = None
    current_map: str | None = None

    with path.open("r", encoding="utf-8") as mtl_file:
        for raw_line in mtl_file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            keyword = parts[0]
            if keyword == "newmtl":
                if current_name is not None:
                    materials.append(SourceMaterial(current_name, current_map))
                current_name = parts[1]
                current_map = None
            elif keyword == "map_Kd":
                current_map = parts[1]

    if current_name is not None:
        materials.append(SourceMaterial(current_name, current_map))

    return materials