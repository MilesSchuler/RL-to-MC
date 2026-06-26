from __future__ import annotations

import itertools
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class AppliedModel:
    model_ref: str
    x: int = 0
    y: int = 0
    z: int = 0
    uvlock: bool = False


@dataclass(frozen=True)
class BlockVariant:
    block_name: str
    states: tuple[tuple[str, str], ...]
    applied_models: tuple[AppliedModel, ...]


@dataclass(frozen=True)
class ResolvedModel:
    name: str
    textures: dict[str, str]
    elements: tuple[dict[str, Any], ...]


class MinecraftAssets:
    def __init__(self, root: str | Path = "minecraft"):
        self.root = Path(root)
        self.blockstates = self.root / "blockstates"
        self.models = self.root / "models" / "block"
        self.textures = self.root / "textures" / "block"

    def load_variants(self, block_name: str) -> list[BlockVariant]:
        blockstate_path = self.blockstates / f"{block_name}.json"
        if not blockstate_path.exists():
            return []

        data = _load_json(blockstate_path)
        variants: list[BlockVariant] = []

        if "variants" in data:
            for state_key, entry in data["variants"].items():
                state_pairs = _parse_state_key(state_key)
                entries = entry if isinstance(entry, list) else [entry]
                for item in entries:
                    variants.append(
                        BlockVariant(
                            block_name=block_name,
                            states=state_pairs,
                            applied_models=(
                                AppliedModel(
                                    model_ref=item["model"],
                                    x=int(item.get("x", 0)),
                                    y=int(item.get("y", 0)),
                                    z=int(item.get("z", 0)),
                                    uvlock=bool(item.get("uvlock", False)),
                                ),
                            ),
                        )
                    )
        elif "multipart" in data:
            variants.extend(self._expand_multipart(block_name, data["multipart"]))

        return variants

    def all_variants(self) -> list[BlockVariant]:
        variants: list[BlockVariant] = []
        for path in sorted(self.blockstates.glob("*.json")):
            variants.extend(self.load_variants(path.stem))
        return variants

    def resolve_model(self, model_ref: str) -> ResolvedModel:
        return self._resolve_model_cached(model_ref)

    @lru_cache(maxsize=None)
    def _resolve_model_cached(self, model_ref: str) -> ResolvedModel:
        model_path = self._model_path(model_ref)
        data = _load_json(model_path)

        textures: dict[str, str] = {}
        elements: tuple[dict[str, Any], ...] = tuple(data.get("elements", []))

        parent_ref = data.get("parent")
        if parent_ref:
            parent = self._resolve_model_cached(parent_ref)
            textures.update(parent.textures)
            if not elements:
                elements = parent.elements

        textures.update(data.get("textures", {}))

        return ResolvedModel(model_path.stem, textures, elements)

    def resolve_variant_mask(self, variant: BlockVariant, resolution: int = 8) -> np.ndarray:
        return self._resolve_variant_mask_cached(variant, resolution)

    @lru_cache(maxsize=None)
    def _resolve_variant_mask_cached(self, variant: BlockVariant, resolution: int) -> np.ndarray:
        mask = np.zeros((resolution, resolution, resolution), dtype=bool)
        for model in variant.applied_models:
            resolved = self.resolve_model(model.model_ref)
            model_mask = _elements_to_mask(resolved.elements, resolution)
            model_mask = _apply_model_rotations(model_mask, model.x, model.y, model.z)
            mask |= model_mask
        return mask

    def resolve_variant_complexity(self, variant: BlockVariant, resolution: int = 8) -> float:
        return float(_mask_complexity(self.resolve_variant_mask(variant, resolution=resolution)))

    def resolve_variant_color(self, variant: BlockVariant) -> np.ndarray:
        return self._resolve_variant_color_cached(variant)

    @lru_cache(maxsize=None)
    def _resolve_variant_color_cached(self, variant: BlockVariant) -> np.ndarray:
        colors = []
        variances = []
        for model in variant.applied_models:
            resolved = self.resolve_model(model.model_ref)
            for texture_ref in _resolved_texture_refs(resolved.textures):
                image_path = self._texture_path(texture_ref)
                if image_path.exists():
                    image = Image.open(image_path).convert("RGB")
                    pixels = np.asarray(image, dtype=float)
                    colors.append(pixels.mean(axis=(0, 1)))
                    variances.append(pixels.var(axis=(0, 1)))
        if not colors:
            return np.array([255.0, 255.0, 255.0, 0.0, 0.0, 0.0], dtype=float)
        mean_color = np.mean(np.asarray(colors, dtype=float), axis=0)
        mean_variance = np.mean(np.asarray(variances, dtype=float), axis=0) if variances else np.zeros(3, dtype=float)
        return np.concatenate([mean_color, mean_variance])

    def _texture_path(self, texture_ref: str) -> Path:
        normalized = _normalize_texture_ref(texture_ref)
        return self.textures / f"{normalized}.png"

    def _model_path(self, model_ref: str) -> Path:
        normalized = model_ref.replace("minecraft:", "")
        if normalized.startswith("block/"):
            normalized = normalized[len("block/") :]
        return self.models / f"{normalized}.json"

    def _expand_multipart(self, block_name: str, multipart: list[dict[str, Any]]) -> list[BlockVariant]:
        condition_keys: dict[str, set[str]] = {}
        parsed_parts: list[tuple[dict[str, str], tuple[AppliedModel, ...]]] = []

        for part in multipart:
            when = part.get("when", {})
            apply = part["apply"]
            conditions = _normalize_conditions(when)
            for key, value in conditions.items():
                condition_keys.setdefault(key, set()).add(value)
            parsed_parts.append((conditions, (_parse_applied_models(apply))))

        domains: dict[str, tuple[str, ...]] = {}
        for key, values in condition_keys.items():
            if values <= {"true", "false"}:
                domains[key] = ("false", "true")
            else:
                domains[key] = tuple(sorted(values))

        variants: list[BlockVariant] = []
        if not domains:
            active_parts = [models for _, models in parsed_parts]
            combined = tuple(model for models in active_parts for model in models)
            variants.append(BlockVariant(block_name, tuple(), combined))
            return variants

        keys = sorted(domains)
        for values in itertools.product(*(domains[key] for key in keys)):
            state = dict(zip(keys, values))
            active_models: list[AppliedModel] = []
            for conditions, models in parsed_parts:
                if all(state.get(key) == value for key, value in conditions.items()):
                    active_models.extend(models)
            if active_models:
                variants.append(BlockVariant(block_name, tuple(sorted(state.items())), tuple(active_models)))

        return variants


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _parse_state_key(key: str) -> tuple[tuple[str, str], ...]:
    if not key:
        return tuple()
    pairs = []
    for token in key.split(","):
        if "=" not in token:
            continue
        state_key, state_value = token.split("=", 1)
        pairs.append((state_key.strip(), state_value.strip()))
    return tuple(sorted(pairs))


def _normalize_conditions(when: Any) -> dict[str, str]:
    if not when:
        return {}
    if isinstance(when, str):
        return {when: "true"}
    return {key: str(value).lower() for key, value in when.items()}


def _parse_applied_models(apply: Any) -> tuple[AppliedModel, ...]:
    if isinstance(apply, list):
        return tuple(_parse_applied_model(item) for item in apply)
    return (_parse_applied_model(apply),)


def _parse_applied_model(item: dict[str, Any]) -> AppliedModel:
    return AppliedModel(
        model_ref=item["model"],
        x=int(item.get("x", 0)),
        y=int(item.get("y", 0)),
        z=int(item.get("z", 0)),
        uvlock=bool(item.get("uvlock", False)),
    )


def _normalize_texture_ref(texture_ref: str) -> str:
    normalized = texture_ref.replace("minecraft:", "")
    normalized = normalized.replace("block/", "") if normalized.startswith("block/") else normalized
    if not normalized.startswith("block/"):
        normalized = f"block/{normalized}"
    return normalized


def _resolved_texture_refs(textures: dict[str, str]) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()

    for value in textures.values():
        resolved = _resolve_texture_value(value, textures, set())
        if resolved and resolved not in seen:
            seen.add(resolved)
            refs.append(resolved)

    return refs


def _resolve_texture_value(value: str, textures: dict[str, str], trail: set[str]) -> str | None:
    if value.startswith("#"):
        key = value[1:]
        if key in trail:
            return None
        trail = set(trail)
        trail.add(key)
        target = textures.get(key)
        if target is None:
            return None
        return _resolve_texture_value(target, textures, trail)
    return value


def _elements_to_mask(elements: tuple[dict[str, Any], ...], resolution: int) -> np.ndarray:
    mask = np.zeros((resolution, resolution, resolution), dtype=bool)
    step = 16.0 / resolution

    for element in elements:
        from_vec = np.asarray(element["from"], dtype=float)
        to_vec = np.asarray(element["to"], dtype=float)
        for x in range(resolution):
            center_x = (x + 0.5) * step
            if not (from_vec[0] <= center_x < to_vec[0]):
                continue
            for y in range(resolution):
                center_y = (y + 0.5) * step
                if not (from_vec[1] <= center_y < to_vec[1]):
                    continue
                for z in range(resolution):
                    center_z = (z + 0.5) * step
                    if from_vec[2] <= center_z < to_vec[2]:
                        mask[x, y, z] = True

    return mask


def _apply_model_rotations(mask: np.ndarray, x: int, y: int, z: int) -> np.ndarray:
    result = mask
    for _ in range((x // 90) % 4):
        result = np.rot90(result, axes=(1, 2))
    for _ in range((y // 90) % 4):
        result = np.rot90(result, axes=(0, 2))
    for _ in range((z // 90) % 4):
        result = np.rot90(result, axes=(0, 1))
    return result


def _mask_complexity(mask: np.ndarray) -> float:
    if mask.size == 0:
        return 0.0
    transitions = 0
    for axis in range(3):
        transitions += np.count_nonzero(mask != np.roll(mask, 1, axis=axis))
    return transitions / float(mask.size * 3)