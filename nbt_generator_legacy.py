from __future__ import annotations

"""Legacy NBT generation path.

This wraps the existing heuristic converter so it can be used side-by-side
with the newer voxel-space generator.
"""

from pathlib import Path
import argparse

from converter import ModelConverter


class LegacyNbtGenerator:
    def __init__(self, source_root: str | Path = "objs", minecraft_root: str | Path = "minecraft"):
        self.converter = ModelConverter(source_root=source_root, minecraft_root=minecraft_root)

    def generate(
        self,
        name: str,
        target_height: int = 48,
        subresolution: int = 8,
        output_suffix: str = "legacy",
    ):
        blocks, shape = self.converter.convert(name, target_height=target_height, subresolution=subresolution)
        self._rename_outputs(name, output_suffix)
        return blocks, shape

    def _rename_outputs(self, name: str, output_suffix: str) -> None:
        output_dir = Path("output") / name
        source_java = output_dir / f"{name}Java.nbt"
        source_bedrock = output_dir / f"{name}Bedrock.nbt"
        target_java = output_dir / f"{name}_{output_suffix}Java.nbt"
        target_bedrock = output_dir / f"{name}_{output_suffix}Bedrock.nbt"

        if source_java.exists():
            source_java.replace(target_java)
        if source_bedrock.exists():
            source_bedrock.replace(target_bedrock)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate NBT using the legacy heuristic method")
    parser.add_argument("--name", required=True, help="OBJ model name")
    parser.add_argument("--source-root", default="objs", help="Folder containing OBJ models")
    parser.add_argument("--minecraft-root", default="minecraft", help="Folder containing Minecraft block assets")
    parser.add_argument("--target-height", type=int, default=48, help="Target height for voxel sampling")
    parser.add_argument("--subresolution", type=int, default=8, help="Subresolution for sampling")
    parser.add_argument("--output-suffix", default="legacy", help="Suffix appended to the generated files")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    generator = LegacyNbtGenerator(source_root=args.source_root, minecraft_root=args.minecraft_root)
    generator.generate(
        args.name,
        target_height=args.target_height,
        subresolution=args.subresolution,
        output_suffix=args.output_suffix,
    )


if __name__ == "__main__":
    main()