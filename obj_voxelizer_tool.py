from __future__ import annotations

"""Voxelize an OBJ source model and export voxel cells for plotting.

This script samples the source mesh with the existing SourceVoxelizer and
stores a compact per-cell representation that can be plotted later in 2D or
3D.

Example:
    python3 obj_voxelizer_tool.py --name mountain --output mountain_voxels.npz
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import argparse

import numpy as np

from source_model import SourceModel
from voxelizer import CellObservation, SourceVoxelizer, multi_offsets


@dataclass(frozen=True)
class VoxelCell:
    x: int
    y: int
    z: int
    fullness: float
    color: tuple[float, float, float]
    sample_count: int


def voxelize_source_model(
    name: str,
    source_root: str | Path = "objs",
    target_height: int = 48,
    subresolution: int = 8,
    sample_steps: int = 4,
) -> list[VoxelCell]:
    """Voxelize an OBJ model into per-cell observations.

    The voxelizer samples the model from multiple half-block offsets and keeps
    the most-sampled observation for each cell.
    """
    source = SourceModel.load(name, source_root)
    voxelizer = SourceVoxelizer(
        source,
        target_height=target_height,
        subresolution=subresolution,
        sample_steps=sample_steps,
    )

    best_by_cell: dict[tuple[int, int, int], CellObservation] = {}

    for offset in multi_offsets():
        observations = voxelizer.sample(offset)
        for cell, observation in observations.items():
            current = best_by_cell.get(cell)
            if current is None or observation.sample_count > current.sample_count:
                best_by_cell[cell] = observation

    cells: list[VoxelCell] = []
    for x, y, z in sorted(best_by_cell):
        observation = best_by_cell[(x, y, z)]
        cells.append(
            VoxelCell(
                x=x,
                y=y,
                z=z,
                fullness=float(np.mean(observation.counts > 0)),
                color=_mean_color(observation),
                sample_count=int(observation.sample_count),
            )
        )

    return cells


def save_voxel_cells(path: str | Path, cells: Iterable[VoxelCell], *, target_height: int, subresolution: int) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    cells = list(cells)
    positions = np.array([(cell.x, cell.y, cell.z) for cell in cells], dtype=int) if cells else np.zeros((0, 3), dtype=int)
    fullness = np.array([cell.fullness for cell in cells], dtype=float) if cells else np.zeros((0,), dtype=float)
    colors = np.array([cell.color for cell in cells], dtype=float) if cells else np.zeros((0, 3), dtype=float)
    sample_counts = np.array([cell.sample_count for cell in cells], dtype=int) if cells else np.zeros((0,), dtype=int)

    np.savez_compressed(
        path,
        positions=positions,
        fullness=fullness,
        colors=colors,
        sample_counts=sample_counts,
        target_height=int(target_height),
        subresolution=int(subresolution),
    )


def load_voxel_cells(path: str | Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    data = np.load(path, allow_pickle=True)
    return (
        np.asarray(data["positions"], dtype=int),
        np.asarray(data["fullness"], dtype=float),
        np.asarray(data["colors"], dtype=float),
        np.asarray(data["sample_counts"], dtype=int),
    )


def _mean_color(observation: CellObservation) -> tuple[float, float, float]:
    if observation.sample_count <= 0:
        return (255.0, 255.0, 255.0)
    mean = observation.color_sum / float(observation.sample_count)
    return float(mean[0]), float(mean[1]), float(mean[2])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Voxelize an OBJ source model and export the voxel cells")
    parser.add_argument("--name", required=True, help="OBJ model name inside the source root")
    parser.add_argument("--source-root", default="objs", help="Folder containing the OBJ source models")
    parser.add_argument("--target-height", type=int, default=48, help="Target voxel height used during sampling")
    parser.add_argument("--subresolution", type=int, default=8, help="Sub-voxel resolution used during sampling")
    parser.add_argument("--sample-steps", type=int, default=4, help="Triangle sampling steps")
    parser.add_argument("--output", required=True, help="Output .npz file")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    cells = voxelize_source_model(
        args.name,
        source_root=args.source_root,
        target_height=args.target_height,
        subresolution=args.subresolution,
        sample_steps=args.sample_steps,
    )
    save_voxel_cells(
        args.output,
        cells,
        target_height=args.target_height,
        subresolution=args.subresolution,
    )
    print(f"saved {len(cells)} cells to {args.output}")


if __name__ == "__main__":
    main()