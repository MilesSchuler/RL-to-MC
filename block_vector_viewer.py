from __future__ import annotations

"""Interactive viewer for precomputed block vectors.

This tool loads the compressed vector archive produced by
block_vector_encoder.py and plots any two dimensions against each other.

Example:
    python3 block_vector_viewer.py --vectors block_vectors.npz --x-axis 0 --y-axis 8
"""

from dataclasses import dataclass
from pathlib import Path
import argparse
import math

import matplotlib.pyplot as plt
import numpy as np

from block_vector_encoder import VECTOR_DIMENSION, load_precomputed_vectors


@dataclass(frozen=True)
class VectorRecord:
    name: str
    states: dict[str, str]
    vector: np.ndarray


AXIS_NAMES = [
    "octant 0 fullness",
    "octant 0 red",
    "octant 0 green",
    "octant 0 blue",
    "octant 1 fullness",
    "octant 1 red",
    "octant 1 green",
    "octant 1 blue",
    "octant 2 fullness",
    "octant 2 red",
    "octant 2 green",
    "octant 2 blue",
    "octant 3 fullness",
    "octant 3 red",
    "octant 3 green",
    "octant 3 blue",
    "octant 4 fullness",
    "octant 4 red",
    "octant 4 green",
    "octant 4 blue",
    "octant 5 fullness",
    "octant 5 red",
    "octant 5 green",
    "octant 5 blue",
    "octant 6 fullness",
    "octant 6 red",
    "octant 6 green",
    "octant 6 blue",
    "octant 7 fullness",
    "octant 7 red",
    "octant 7 green",
    "octant 7 blue",
]


def load_vector_records(path: str | Path) -> list[VectorRecord]:
    names, vectors, states = load_precomputed_vectors(path)
    records: list[VectorRecord] = []
    for name, vector, state in zip(names, vectors, states):
        records.append(VectorRecord(name=name, states=state, vector=np.asarray(vector, dtype=float)))
    return records


def axis_label(axis_index: int) -> str:
    if axis_index < 0 or axis_index >= VECTOR_DIMENSION:
        raise ValueError(f"axis index must be between 0 and {VECTOR_DIMENSION - 1}, got {axis_index}")

    return AXIS_NAMES[axis_index]


def parse_axis_value(axis_value: str) -> int:
    text = axis_value.strip().lower()
    if text.isdigit():
        axis_index = int(text)
        if 0 <= axis_index < VECTOR_DIMENSION:
            return axis_index
        raise ValueError(f"axis index must be between 0 and {VECTOR_DIMENSION - 1}, got {axis_index}")

    normalized = text.replace(".", " ").replace("_", " ")
    if normalized in AXIS_NAMES:
        return AXIS_NAMES.index(normalized)

    for index, axis_name in enumerate(AXIS_NAMES):
        if normalized == axis_name:
            return index

    raise ValueError(f"unknown axis '{axis_value}'. Use --list-axes to see valid names.")


def plot_vector_pairs(records: list[VectorRecord], x_axis: int, y_axis: int, annotate: bool = True) -> None:
    if not records:
        raise ValueError("no vectors to plot")

    x_values = np.array([record.vector[x_axis] for record in records], dtype=float)
    y_values = np.array([record.vector[y_axis] for record in records], dtype=float)
    occupancy = np.array([record.vector[0::4].mean() for record in records], dtype=float)

    figure, axis = plt.subplots(figsize=(12, 9))
    scatter = axis.scatter(
        x_values,
        y_values,
        c=occupancy,
        cmap="viridis",
        s=28,
        alpha=0.85,
        edgecolors="none",
        picker=True,
    )

    axis.set_title(f"Block vectors: {axis_label(x_axis)} vs {axis_label(y_axis)}")
    axis.set_xlabel(axis_label(x_axis))
    axis.set_ylabel(axis_label(y_axis))
    colorbar = figure.colorbar(scatter, ax=axis)
    colorbar.set_label("mean occupancy across octants")
    axis.grid(True, alpha=0.2)

    if annotate:
        _enable_hover_annotations(axis, scatter, records)

    plt.tight_layout()
    plt.show()


def _enable_hover_annotations(axis, scatter, records: list[VectorRecord]) -> None:
    annotation = axis.annotate(
        "",
        xy=(0, 0),
        xytext=(12, 12),
        textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.7", alpha=0.95),
        arrowprops=dict(arrowstyle="->", color="0.5"),
    )
    annotation.set_visible(False)

    points = scatter.get_offsets()

    def update_annotation(index: int) -> None:
        matching_indices = _records_at_point(points, records, index)
        matching_records = [records[item] for item in matching_indices]
        annotation.xy = points[index]
        if len(matching_records) == 1:
            annotation.set_text(_format_record_summary(matching_records[0]))
        else:
            header = f"{len(matching_records)} blocks at this point"
            lines = [_format_record_summary(record) for record in matching_records[:8]]
            if len(matching_records) > 8:
                lines.append(f"... and {len(matching_records) - 8} more")
            annotation.set_text("\n\n".join([header, *lines]))
        annotation.set_visible(True)

    def on_move(event) -> None:
        if not event.inaxes or event.inaxes != axis:
            if annotation.get_visible():
                annotation.set_visible(False)
                axis.figure.canvas.draw_idle()
            return

        contains, info = scatter.contains(event)
        if not contains:
            if annotation.get_visible():
                annotation.set_visible(False)
                axis.figure.canvas.draw_idle()
            return

        indices = info.get("ind", [])
        if not indices:
            return

        update_annotation(indices[0])
        axis.figure.canvas.draw_idle()

    axis.figure.canvas.mpl_connect("motion_notify_event", on_move)


def _format_record_summary(record: VectorRecord) -> str:
    state_text = ", ".join(f"{key}={value}" for key, value in sorted(record.states.items())) or "default"
    return f"{record.name}\n{state_text}"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="View precomputed Minecraft block vectors")
    parser.add_argument("--vectors", required=True, help="Path to the .npz file generated by block_vector_encoder.py")
    parser.add_argument("--x-axis", default="0", help=f"Vector axis index or name for the x axis (0-{VECTOR_DIMENSION - 1})")
    parser.add_argument("--y-axis", default="4", help=f"Vector axis index or name for the y axis (0-{VECTOR_DIMENSION - 1})")
    parser.add_argument("--no-hover", action="store_true", help="Disable hover labels")
    parser.add_argument("--list-axes", action="store_true", help="Print all available axis names and exit")
    return parser.parse_args()


def _records_at_point(points: np.ndarray, records: list[VectorRecord], point_index: int, tolerance: float = 1e-9) -> list[int]:
    target = points[point_index]
    matches: list[int] = []
    for index, point in enumerate(points):
        if np.allclose(point, target, atol=tolerance, rtol=0.0):
            matches.append(index)
    return matches


def main() -> None:
    args = _parse_args()
    if args.list_axes:
        for index, axis_name in enumerate(AXIS_NAMES):
            print(f"{index:2d}: {axis_name}")
        return

    records = load_vector_records(args.vectors)

    x_axis = parse_axis_value(args.x_axis)
    y_axis = parse_axis_value(args.y_axis)

    if x_axis == y_axis:
        raise ValueError("x-axis and y-axis must be different")

    plot_vector_pairs(records, x_axis=x_axis, y_axis=y_axis, annotate=not args.no_hover)


if __name__ == "__main__":
    main()