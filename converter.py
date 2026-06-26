from __future__ import annotations

from dataclasses import dataclass
import sys
from pathlib import Path

import numpy as np

from minecraft_assets import MinecraftAssets, BlockVariant
from source_model import SourceModel
from structure_writer import BedrockStructureWriter, JavaStructureWriter, PlacedBlock
from voxelizer import SourceVoxelizer, multi_offsets


@dataclass
class ScoredPlacement:
    score: float
    block: PlacedBlock


class ModelConverter:
    def __init__(self, source_root: str | Path = "objs", minecraft_root: str | Path = "minecraft"):
        self.source_root = Path(source_root)
        self.minecraft_assets = MinecraftAssets(minecraft_root)

    def convert(self, name: str, target_height: int = 48, subresolution: int = 8):
        source = SourceModel.load(name, self.source_root)
        voxelizer = SourceVoxelizer(source, target_height=target_height, subresolution=subresolution)
        variants = self._build_variants(subresolution)

        best_by_cell: dict[tuple[int, int, int], ScoredPlacement] = {}

        offsets = multi_offsets()
        for offset_index, offset in enumerate(offsets, start=1):
            _print_progress("sampling offsets", offset_index, len(offsets))
            observations = voxelizer.sample(offset)
            items = list(observations.items())
            for cell_index, (cell, observation) in enumerate(items, start=1):
                _print_progress(f"cells {offset}", cell_index, len(items))
                placement = self._best_variant_for_cell(cell, observation, variants)
                current = best_by_cell.get(cell)
                if current is None or placement.score > current.score:
                    best_by_cell[cell] = placement

        sys.stdout.write("\n")
        sys.stdout.flush()

        blocks = [placement.block for placement in best_by_cell.values()]
        shape = self._shape_from_blocks(blocks)

        output_dir = Path("output") / name
        output_dir.mkdir(parents=True, exist_ok=True)
        JavaStructureWriter(blocks, shape).write(output_dir / f"{name}Java.nbt")
        BedrockStructureWriter(blocks, shape).write(output_dir / f"{name}Bedrock.nbt")

        return blocks, shape

    def _build_variants(self, resolution: int) -> list[tuple[BlockVariant, np.ndarray, np.ndarray, np.ndarray, float, float]]:
        compiled = []
        for variant in self.minecraft_assets.all_variants():
            if variant.block_name == "white_concrete":
                continue
            mask = self.minecraft_assets.resolve_variant_mask(variant, resolution=resolution)
            color_stats = self.minecraft_assets.resolve_variant_color(variant)
            color = color_stats[:3]
            variance = color_stats[3:]
            fill_ratio = float(mask.mean())
            complexity = self.minecraft_assets.resolve_variant_complexity(variant, resolution=resolution)
            compiled.append((variant, mask, color, variance, fill_ratio, complexity))
        return compiled

    def _best_variant_for_cell(self, cell, observation, variants):
        source_mask = observation.counts > 0
        source_color = observation.color_sum / max(1, observation.sample_count)
        source_variance = np.maximum((observation.color_sq_sum / max(1, observation.sample_count)) - np.square(source_color), 0.0)
        source_fill = float(source_mask.mean())
        source_complexity = _mask_complexity(source_mask)

        filtered = sorted(
            variants,
            key=lambda item: _coarse_distance(source_color, source_variance, source_fill, source_complexity, item[2], item[3], item[4], item[5]),
        )[:64]

        best_score = float("-inf")
        best_block = PlacedBlock(cell[0], cell[1], cell[2], "minecraft:bone_block", tuple())

        for variant, mask, color, variance, fill_ratio, complexity in filtered:
            resized_mask = _resize_mask(mask, source_mask.shape)
            color_score = 1.0 / (1.0 + np.linalg.norm(source_color - color) / 255.0)
            variance_score = 1.0 / (1.0 + np.linalg.norm(source_variance - variance) / 255.0)
            shape_score = 1.0 - np.mean(np.logical_xor(source_mask, resized_mask))
            fill_score = 1.0 - abs(source_fill - fill_ratio)
            complexity_score = 1.0 - abs(source_complexity - _mask_complexity(resized_mask))
            score = (shape_score * 0.35) + (complexity_score * 0.25) + (color_score * 0.15) + (variance_score * 0.15) + (fill_score * 0.10)

            if score > best_score:
                best_score = score
                best_block = PlacedBlock(
                    x=int(cell[0]),
                    y=int(cell[1]),
                    z=int(cell[2]),
                    name=variant.block_name,
                    states=variant.states,
                )

        return ScoredPlacement(best_score, best_block)

    def _shape_from_blocks(self, blocks: list[PlacedBlock]):
        if not blocks:
            return np.array([1, 1, 1], dtype=int)
        xs = [block.x for block in blocks]
        ys = [block.y for block in blocks]
        zs = [block.z for block in blocks]
        return np.array([max(xs) + 1, max(ys) + 1, max(zs) + 1], dtype=int)


def _coarse_distance(source_color, source_variance, source_fill, source_complexity, variant_color, variant_variance, variant_fill, variant_complexity) -> float:
    color = np.linalg.norm(source_color - variant_color) / 255.0
    variance = np.linalg.norm(source_variance - variant_variance) / 255.0
    fill = abs(source_fill - variant_fill)
    complexity = abs(source_complexity - variant_complexity)
    return color + variance + fill + complexity


def _mask_complexity(mask: np.ndarray) -> float:
    if mask.size == 0:
        return 0.0
    transitions = 0
    for axis in range(3):
        transitions += np.count_nonzero(mask != np.roll(mask, 1, axis=axis))
    return transitions / float(mask.size * 3)


def _resize_mask(mask: np.ndarray, shape: tuple[int, int, int]) -> np.ndarray:
    if mask.shape == shape:
        return mask

    x_idx = np.linspace(0, mask.shape[0] - 1, shape[0]).round().astype(int)
    y_idx = np.linspace(0, mask.shape[1] - 1, shape[1]).round().astype(int)
    z_idx = np.linspace(0, mask.shape[2] - 1, shape[2]).round().astype(int)
    return mask[np.ix_(x_idx, y_idx, z_idx)]


def _print_progress(label: str, current: int, total: int) -> None:
    width = 24
    ratio = current / max(1, total)
    filled = int(width * ratio)
    bar = "#" * filled + "-" * (width - filled)
    sys.stdout.write(f"\r{label}: [{bar}] {current}/{total}")
    sys.stdout.flush()