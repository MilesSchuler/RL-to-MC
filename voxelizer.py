from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path

import numpy as np
from PIL import Image

from source_model import SourceModel


@dataclass
class CellObservation:
    counts: np.ndarray
    color_sum: np.ndarray
    color_sq_sum: np.ndarray
    sample_count: int


class SourceVoxelizer:
    def __init__(self, model: SourceModel, target_height: int, subresolution: int = 8, sample_steps: int = 4):
        self.model = model
        self.target_height = target_height
        self.subresolution = subresolution
        self.sample_steps = sample_steps

        vertices = model.vertices
        self.min_bounds = vertices.min(axis=0)
        self.max_bounds = vertices.max(axis=0)
        self.scale_factor = (self.max_bounds[1] - self.min_bounds[1]) / target_height

        self.texture = Image.open(model.texture_path).convert("RGB")
        self.texture_pixels = self.texture.load()
        self.texture_width, self.texture_height = self.texture.size

    def sample(self, offset: tuple[float, float, float]) -> dict[tuple[int, int, int], CellObservation]:
        observations: dict[tuple[int, int, int], CellObservation] = {}

        for vertices, textures, _material in self.model.triangulated_faces():
            for barycentric in self._triangle_samples(self.sample_steps):
                point = _barycentric_point(vertices, barycentric)
                uv = _barycentric_point(textures, barycentric)
                color = self._sample_texture(uv)

                scaled = (point - self.min_bounds) / self.scale_factor + np.asarray(offset, dtype=float)
                cell = tuple(np.floor(scaled).astype(int).tolist())
                local = scaled - np.asarray(cell, dtype=float)
                sub = np.clip((local * self.subresolution).astype(int), 0, self.subresolution - 1)
                self._add_sample(observations, cell, sub, color)

        return observations

    def _triangle_samples(self, steps: int):
        for i in range(steps + 1):
            for j in range(steps + 1 - i):
                u = i / steps if steps else 0.0
                v = j / steps if steps else 0.0
                w = 1.0 - u - v
                yield np.array([w, u, v], dtype=float)

    def _sample_texture(self, uv: np.ndarray) -> np.ndarray:
        u = float(uv[0])
        v = float(uv[1])
        x = int(np.clip(u * (self.texture_width - 1), 0, self.texture_width - 1))
        y = int(np.clip((1.0 - v) * (self.texture_height - 1), 0, self.texture_height - 1))
        return np.asarray(self.texture_pixels[x, y], dtype=float)

    def _add_sample(self, observations, cell, sub, color):
        if cell not in observations:
            observations[cell] = CellObservation(
                counts=np.zeros((self.subresolution, self.subresolution, self.subresolution), dtype=np.int32),
                color_sum=np.zeros(3, dtype=float),
                color_sq_sum=np.zeros(3, dtype=float),
                sample_count=0,
            )

        observation = observations[cell]
        observation.counts[sub[0], sub[1], sub[2]] += 1
        observation.color_sum += color[:3]
        observation.color_sq_sum += np.square(color[:3])
        observation.sample_count += 1


def multi_offsets() -> list[tuple[float, float, float]]:
    return [tuple(values) for values in product((0.0, 0.5), repeat=3)]


def _barycentric_point(points: np.ndarray, barycentric: np.ndarray) -> np.ndarray:
    return (points[0] * barycentric[0]) + (points[1] * barycentric[1]) + (points[2] * barycentric[2])