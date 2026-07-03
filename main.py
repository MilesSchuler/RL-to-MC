from __future__ import annotations

import argparse

from nbt_generator_legacy import LegacyNbtGenerator
from nbt_generator_voxel_space import VoxelSpaceNbtGenerator


def main():
    parser = argparse.ArgumentParser(description="Generate Minecraft NBT using legacy or voxel-space matching")
    parser.add_argument("--name", default="cat", help="OBJ model name")
    parser.add_argument("--method", choices=("legacy", "voxel"), default="voxel", help="Generation method")
    parser.add_argument("--source-root", default="objs", help="Folder containing OBJ models")
    parser.add_argument("--minecraft-root", default="minecraft", help="Folder containing Minecraft block assets")
    parser.add_argument("--target-height", type=int, default=48, help="Target height for voxel sampling")
    parser.add_argument("--subresolution", type=int, default=8, help="Subresolution for sampling")
    parser.add_argument("--vector-file", default="block_vectors.npz", help="Precomputed vector archive for voxel-space mode")
    args = parser.parse_args()

    if args.method == "legacy":
        generator = LegacyNbtGenerator(source_root=args.source_root, minecraft_root=args.minecraft_root)
        generator.generate(args.name, target_height=args.target_height, subresolution=args.subresolution)
    else:
        generator = VoxelSpaceNbtGenerator(
            source_root=args.source_root,
            minecraft_root=args.minecraft_root,
            vector_file=args.vector_file,
        )
        generator.generate(args.name, target_height=args.target_height, subresolution=args.subresolution)


if __name__ == "__main__":
    main()