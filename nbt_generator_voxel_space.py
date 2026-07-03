from __future__ import annotations

"""Voxel-space NBT generation path.

This generator voxelizes the source OBJ, encodes each sampled cell into the
32D block-vector space, and picks the nearest precomputed Minecraft block
vector for every cell.
"""

from dataclasses import dataclass
from pathlib import Path
import argparse
import sys
import time

import numpy as np

from block_vector_encoder import encode_cell_observation, precompute_block_vectors, load_precomputed_vectors
from minecraft_assets import MinecraftAssets
from source_model import SourceModel
from structure_writer import BedrockStructureWriter, JavaStructureWriter, PlacedBlock
from voxelizer import SourceVoxelizer, multi_offsets


@dataclass
class VoxelPlacement:
    distance: float
    block: PlacedBlock


class VoxelSpaceNbtGenerator:
    def __init__(
        self,
        source_root: str | Path = "objs",
        minecraft_root: str | Path = "minecraft",
        vector_file: str | Path = "block_vectors.npz",
    ):
        self.source_root = Path(source_root)
        self.minecraft_root = Path(minecraft_root)
        self.vector_file = Path(vector_file)
        self._block_names: list[str] = []
        self._block_states: list[dict[str, str]] = []
        self._block_vectors: np.ndarray | None = None

    def generate(
        self,
        name: str,
        target_height: int = 48,
        subresolution: int = 8,
        output_suffix: str = "voxel",
    ):
        self._ensure_vectors_loaded()

        source = SourceModel.load(name, self.source_root)
        voxelizer = SourceVoxelizer(source, target_height=target_height, subresolution=subresolution)

        best_by_cell: dict[tuple[int, int, int], VoxelPlacement] = {}
        offsets = multi_offsets()

        for offset_index, offset in enumerate(offsets, start=1):
            _print_progress("sampling offsets", offset_index, len(offsets))
            observations = voxelizer.sample(offset)
            items = list(observations.items())
            for cell_index, (cell, observation) in enumerate(items, start=1):
                _print_progress(f"cells {offset}", cell_index, len(items))
                placement = self._best_variant_for_cell(cell, observation)
                current = best_by_cell.get(cell)
                if current is None or placement.distance < current.distance:
                    best_by_cell[cell] = placement

        sys.stdout.write("\n")
        sys.stdout.flush()

        blocks = [placement.block for placement in best_by_cell.values()]
        shape = self._shape_from_blocks(blocks)

        output_dir = Path("output") / name
        output_dir.mkdir(parents=True, exist_ok=True)
        JavaStructureWriter(blocks, shape).write(output_dir / f"{name}_{output_suffix}Java.nbt")
        BedrockStructureWriter(blocks, shape).write(output_dir / f"{name}_{output_suffix}Bedrock.nbt")

        return blocks, shape

    def _ensure_vectors_loaded(self) -> None:
        if self._block_vectors is not None:
            return

        if not self.vector_file.exists():
            precompute_block_vectors(self.minecraft_root, output_path=self.vector_file)

        names, vectors, states = load_precomputed_vectors(self.vector_file)
        self._block_names = names
        self._block_states = states
        self._block_vectors = _normalize_vectors(vectors)

    def _best_variant_for_cell(self, cell, observation) -> VoxelPlacement:
        query_vector = _normalize_vector(encode_cell_observation(observation))
        distances = np.linalg.norm(self._block_vectors - query_vector, axis=1)
        best_index = int(np.argmin(distances))

        block = PlacedBlock(
            x=int(cell[0]),
            y=int(cell[1]),
            z=int(cell[2]),
            name=self._block_names[best_index],
            states=tuple(sorted(self._block_states[best_index].items())),
        )
        return VoxelPlacement(distance=float(distances[best_index]), block=block)

    def _shape_from_blocks(self, blocks: list[PlacedBlock]):
        if not blocks:
            return np.array([1, 1, 1], dtype=int)
        xs = [block.x for block in blocks]
        ys = [block.y for block in blocks]
        zs = [block.z for block in blocks]
        return np.array([max(xs) + 1, max(ys) + 1, max(zs) + 1], dtype=int)


def _normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    scales = np.array([1.0, 255.0, 255.0, 255.0] * 8, dtype=float)
    return np.asarray(vectors, dtype=float) / scales


def _normalize_vector(vector: np.ndarray) -> np.ndarray:
    scales = np.array([1.0, 255.0, 255.0, 255.0] * 8, dtype=float)
    return np.asarray(vector, dtype=float) / scales


def _print_progress(label: str, current: int, total: int) -> None:
    starts = getattr(_print_progress, "_starts", None)
    if starts is None:
        starts = {}
        setattr(_print_progress, "_starts", starts)

    start_time = starts.setdefault(label, time.perf_counter())

    width = 24
    ratio = current / max(1, total)
    filled = int(width * ratio)
    bar = "#" * filled + "-" * (width - filled)

    elapsed = time.perf_counter() - start_time
    if current > 0:
        estimated_total = elapsed / current * total
        remaining = max(0.0, estimated_total - elapsed)
        eta_text = f" eta {_format_duration(remaining)}"
    else:
        eta_text = " eta --:--"

    sys.stdout.write(f"\r{label}: [{bar}] {current}/{total}{eta_text}")
    sys.stdout.flush()


def _format_duration(seconds: float) -> str:
    total_seconds = max(0, int(round(seconds)))
    minutes, remaining_seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{remaining_seconds:02d}"
    return f"{minutes:d}:{remaining_seconds:02d}"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate NBT using the voxel-space method")
    parser.add_argument("--name", required=True, help="OBJ model name")
    parser.add_argument("--source-root", default="objs", help="Folder containing OBJ models")
    parser.add_argument("--minecraft-root", default="minecraft", help="Folder containing Minecraft block assets")
    parser.add_argument("--vector-file", default="block_vectors.npz", help="Precomputed vector archive")
    parser.add_argument("--target-height", type=int, default=48, help="Target height for voxel sampling")
    parser.add_argument("--subresolution", type=int, default=8, help="Subresolution for sampling")
    parser.add_argument("--output-suffix", default="voxel", help="Suffix appended to the generated files")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    generator = VoxelSpaceNbtGenerator(
        source_root=args.source_root,
        minecraft_root=args.minecraft_root,
        vector_file=args.vector_file,
    )
    generator.generate(
        args.name,
        target_height=args.target_height,
        subresolution=args.subresolution,
        output_suffix=args.output_suffix,
    )


if __name__ == "__main__":
    main()