from __future__ import annotations

"""Precompute 32D block vectors for shape/color matching.

The vector layout is 8 octants, each with 4 values:
- fullness
- red
- green
- blue

This is a first-pass encoder. For Minecraft block variants, the RGB values are
the block's visible texture color repeated per octant, while fullness comes
from the resolved model occupancy mask.

For source cells, fullness and RGB are derived from the voxelizer's sampled
occupancy/color observations.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import argparse
import json

import numpy as np

from minecraft_assets import BlockVariant, MinecraftAssets
from voxelizer import CellObservation


OCTANT_COUNT = 8
VECTOR_DIMENSION = 32


@dataclass(frozen=True)
class EncodedBlock:
    name: str
    states: tuple[tuple[str, str], ...]
    vector: np.ndarray


def encode_cell_observation(observation: CellObservation) -> np.ndarray:
    """Encode a sampled source cell into the 32D octant vector space."""
    return _encode_octant_grid(
        occupancy=observation.counts > 0,
        color_sum=observation.color_sum,
        color_sq_sum=observation.color_sq_sum,
        sample_count=observation.sample_count,
    )


def encode_block_variant(assets: MinecraftAssets, variant: BlockVariant, resolution: int = 8) -> np.ndarray:
    """Encode a Minecraft block variant into the same 32D space.

    The occupancy is based on the resolved model mask. The color channel uses
    the variant's visible texture color repeated across occupied octants.
    """
    mask = assets.resolve_variant_mask(variant, resolution=resolution)
    color_stats = assets.resolve_variant_color(variant)
    color = color_stats[:3]

    octant_occupancy = _octant_means(mask.astype(float))
    color_grid = np.repeat(color[np.newaxis, :], OCTANT_COUNT, axis=0)

    vector = np.zeros(VECTOR_DIMENSION, dtype=float)
    for octant_index in range(OCTANT_COUNT):
        base = octant_index * 4
        vector[base] = octant_occupancy[octant_index]
        vector[base + 1 : base + 4] = color_grid[octant_index]
    return vector


def precompute_block_vectors(
    minecraft_root: str | Path = "minecraft",
    resolution: int = 8,
    output_path: str | Path | None = None,
) -> list[EncodedBlock]:
    """Precompute and optionally persist all block variant vectors."""
    assets = MinecraftAssets(minecraft_root)
    encoded_blocks = [
        EncodedBlock(
            name=variant.block_name,
            states=variant.states,
            vector=encode_block_variant(assets, variant, resolution=resolution),
        )
        for variant in assets.all_variants()
    ]

    if output_path is not None:
        _write_precomputed_vectors(output_path, encoded_blocks, resolution=resolution)

    return encoded_blocks


def load_precomputed_vectors(path: str | Path) -> tuple[list[str], np.ndarray, list[dict[str, str]]]:
    """Load vectors written by this module."""
    data = np.load(path, allow_pickle=True)
    names = [str(value) for value in data["names"].tolist()]
    vectors = np.asarray(data["vectors"], dtype=float)
    states = [dict(item) for item in data["states"].tolist()]
    return names, vectors, states


def _write_precomputed_vectors(
    path: str | Path,
    encoded_blocks: Iterable[EncodedBlock],
    resolution: int,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    encoded_blocks = list(encoded_blocks)
    names = np.array([block.name for block in encoded_blocks], dtype=object)
    states = np.array([dict(block.states) for block in encoded_blocks], dtype=object)
    vectors = np.stack([block.vector for block in encoded_blocks], axis=0) if encoded_blocks else np.zeros((0, VECTOR_DIMENSION), dtype=float)

    np.savez_compressed(
        path,
        names=names,
        states=states,
        vectors=vectors,
        resolution=int(resolution),
    )


def _encode_octant_grid(
    occupancy: np.ndarray,
    color_sum: np.ndarray,
    color_sq_sum: np.ndarray,
    sample_count: int,
) -> np.ndarray:
    occupancy = np.asarray(occupancy, dtype=float)
    if occupancy.ndim != 3:
        raise ValueError(f"expected a 3D occupancy grid, got {occupancy.shape}")

    octant_occupancy = _octant_means(occupancy)
    if sample_count > 0:
        mean_color = np.asarray(color_sum, dtype=float) / float(sample_count)
    else:
        mean_color = np.array([255.0, 255.0, 255.0], dtype=float)

    vector = np.zeros(VECTOR_DIMENSION, dtype=float)
    for octant_index in range(OCTANT_COUNT):
        base = octant_index * 4
        vector[base] = octant_occupancy[octant_index]
        vector[base + 1 : base + 4] = mean_color
    return vector


def _octant_means(grid: np.ndarray) -> np.ndarray:
    """Collapse any cubic 3D grid into 8 octant means."""
    grid = np.asarray(grid, dtype=float)
    if grid.ndim != 3:
        raise ValueError(f"expected a 3D grid, got {grid.shape}")

    octants = np.zeros(OCTANT_COUNT, dtype=float)
    index = 0
    x_parts = np.array_split(np.arange(grid.shape[0]), 2)
    y_parts = np.array_split(np.arange(grid.shape[1]), 2)
    z_parts = np.array_split(np.arange(grid.shape[2]), 2)

    for x_indices in x_parts:
        for y_indices in y_parts:
            for z_indices in z_parts:
                octants[index] = float(np.mean(grid[np.ix_(x_indices, y_indices, z_indices)]))
                index += 1
    return octants


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Precompute 32D vectors for Minecraft block variants")
    parser.add_argument("--minecraft-root", default="minecraft", help="Path to the Minecraft asset root")
    parser.add_argument("--resolution", type=int, default=8, help="Resolution used to resolve block masks")
    parser.add_argument("--output", default=None, help="Optional .npz path to write the precomputed vectors")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    encoded_blocks = precompute_block_vectors(
        minecraft_root=args.minecraft_root,
        resolution=args.resolution,
        output_path=args.output,
    )

    print(json.dumps({"blocks": len(encoded_blocks), "dimension": VECTOR_DIMENSION, "output": args.output}, indent=2))


if __name__ == "__main__":
    main()