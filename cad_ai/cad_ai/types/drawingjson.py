"""DrawingJSON data contract."""

from __future__ import annotations

from typing import Any, TypedDict, Literal


EntityType = Literal["LINE", "ARC", "TEXT", "DIM", "BLOCK"]


class DrawingEntity(TypedDict, total=False):
    type: EntityType
    layer: str
    geometry: dict[str, Any]
    text: dict[str, Any]
    dim: dict[str, Any]


class BlockDefinition(TypedDict, total=False):
    name: str
    entities: list[DrawingEntity]


class BlockInstance(TypedDict, total=False):
    name: str
    insert: dict[str, Any]


class DrawingJSON(TypedDict):
    page_size: str
    units: str
    entities: list[DrawingEntity]
    blocks: dict[str, list[dict[str, Any]]]
    layers: dict[str, dict[str, Any]]
    metadata: dict[str, Any]


def create_placeholder_drawing(metadata: dict[str, Any]) -> DrawingJSON:
    return {
        "page_size": "A3",
        "units": "mm",
        "entities": [],
        "blocks": {
            "definitions": [],
            "instances": [],
        },
        "layers": {},
        "metadata": metadata,
    }
