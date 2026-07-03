from __future__ import annotations

"""Visualize voxelized OBJ cells in 2D or 3D.

This viewer loads the compressed output from obj_voxelizer_tool.py and can
render either a 2D projection or a 3D scatter plot.

Examples:
    python3 obj_voxel_viewer.py --voxels mountain_voxels.npz --mode 3d
    python3 obj_voxel_viewer.py --voxels mountain_voxels.npz --mode 2d --projection xz
"""

from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import numpy as np

from obj_voxelizer_tool import load_voxel_cells


PROJECTIONS = {
    "xy": (0, 1),
    "xz": (0, 2),
    "yz": (1, 2),
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="View voxelized OBJ cells")
    parser.add_argument("--voxels", required=True, help="Path to the voxel archive produced by obj_voxelizer_tool.py")
    parser.add_argument("--mode", choices=("2d", "3d"), default="3d", help="Plot mode")
    parser.add_argument("--projection", choices=tuple(PROJECTIONS), default="xy", help="2D projection to use in 2D mode")
    parser.add_argument("--point-size", type=float, default=30.0, help="Marker size for scatter points")
    parser.add_argument("--color-by", choices=("fullness", "sample_count", "color"), default="fullness", help="How to color the points")
    return parser.parse_args()


def _point_colors(fullness: np.ndarray, colors: np.ndarray, sample_counts: np.ndarray, color_by: str) -> np.ndarray:
    if color_by == "fullness":
        return fullness
    if color_by == "sample_count":
        return sample_counts.astype(float)
    return colors / 255.0


def _plot_2d(positions: np.ndarray, values, color_by: str, projection: str, point_size: float) -> None:
    x_axis, y_axis = PROJECTIONS[projection]
    figure, axis = plt.subplots(figsize=(10, 8))
    if color_by == "color":
        scatter = axis.scatter(
            positions[:, x_axis],
            positions[:, y_axis],
            c=np.clip(values, 0.0, 1.0),
            s=point_size,
            alpha=0.9,
            edgecolors="none",
        )
        figure.colorbar(scatter, ax=axis, label="RGB")
    else:
        scatter = axis.scatter(
            positions[:, x_axis],
            positions[:, y_axis],
            c=values,
            cmap="viridis",
            s=point_size,
            alpha=0.9,
            edgecolors="none",
        )
        figure.colorbar(scatter, ax=axis, label=color_by)

    axis.set_xlabel(projection[0])
    axis.set_ylabel(projection[1])
    axis.set_title(f"Voxel projection: {projection.upper()}")
    axis.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.show()


def _plot_3d(positions: np.ndarray, values, color_by: str, point_size: float) -> None:
    figure = plt.figure(figsize=(11, 9))
    axis = figure.add_subplot(111, projection="3d")
    if color_by == "color":
        colors = np.clip(values, 0.0, 1.0)
        axis.scatter(
            positions[:, 0],
            positions[:, 1],
            positions[:, 2],
            c=colors,
            s=point_size,
            alpha=0.9,
            edgecolors="none",
        )
    else:
        scatter = axis.scatter(
            positions[:, 0],
            positions[:, 1],
            positions[:, 2],
            c=values,
            cmap="viridis",
            s=point_size,
            alpha=0.9,
            edgecolors="none",
        )
        figure.colorbar(scatter, ax=axis, shrink=0.75, pad=0.1, label=color_by)

    axis.set_xlabel("x")
    axis.set_ylabel("y")
    axis.set_zlabel("z")
    axis.set_title("Voxel scatter")
    plt.tight_layout()
    plt.show()


def main() -> None:
    args = _parse_args()
    positions, fullness, colors, sample_counts = load_voxel_cells(args.voxels)

    if positions.size == 0:
        raise ValueError("no voxel cells found in the input file")

    values = _point_colors(fullness, colors, sample_counts, args.color_by)

    if args.mode == "2d":
        _plot_2d(positions, values, args.color_by, args.projection, args.point_size)
    else:
        _plot_3d(positions, values, args.color_by, args.point_size)


if __name__ == "__main__":
    main()