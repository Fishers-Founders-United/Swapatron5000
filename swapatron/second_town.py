"""Utility for generating a second town plan based on the existing Swapatron configuration.

This module provides a thin wrapper around the core `SwapatronPlanner` to create a distinct
second town without modifying the original town data. It is deliberately simple – it
offsets the town's coordinates and appends a suffix to the town name – but it showcases
how multiple towns can be supported.
"""

from __future__ import annotations

import copy
from typing import Dict, Any

from .planner import SwapatronPlanner, SwapatronPlan

# Default offset applied to the second town's coordinates (e.g., 10 units east and north)
DEFAULT_OFFSET = {"x": 10, "y": 10}


def _apply_offset(coordinates: Dict[str, Any], offset: Dict[str, int]) -> Dict[str, Any]:
    """Return a new coordinate mapping with the given offset applied.

    Args:
        coordinates: Mapping containing at least ``x`` and ``y`` keys.
        offset: Mapping with ``x`` and ``y`` integer offsets.
    """
    new_coords = copy.deepcopy(coordinates)
    new_coords["x"] = new_coords.get("x", 0) + offset.get("x", 0)
    new_coords["y"] = new_coords.get("y", 0) + offset.get("y", 0)
    return new_coords


def generate_second_town_plan(base_town_data: Dict[str, Any], *, offset: Dict[str, int] = DEFAULT_OFFSET) -> SwapatronPlan:
    """Generate a `SwapatronPlan` for a second town derived from ``base_town_data``.

    The function performs a shallow copy of the input data, modifies the town name by
    appending ``"_2"`` and offsets all coordinate entries using ``offset``.

    Args:
        base_town_data: The original town configuration dictionary expected by
            ``SwapatronPlanner``.
        offset: Optional custom offset for the second town's coordinates.

    Returns:
        An instance of ``SwapatronPlan`` representing the planned second town.
    """
    # Deep‑copy to avoid mutating caller data
    second_town = copy.deepcopy(base_town_data)

    # Rename the town to indicate it is the second instance
    original_name = second_town.get("name", "town")
    second_town["name"] = f"{original_name}_2"

    # Apply coordinate offset to every location entry that contains x/y
    for key, value in second_town.items():
        if isinstance(value, dict) and {"x", "y"}.issubset(value.keys()):
            second_town[key] = _apply_offset(value, offset)
        elif isinstance(value, list):
            # Handle list of location dicts (e.g., buildings, resources)
            new_list = []
            for item in value:
                if isinstance(item, dict) and {"x", "y"}.issubset(item.keys()):
                    new_list.append(_apply_offset(item, offset))
                else:
                    new_list.append(item)
            second_town[key] = new_list

    planner = SwapatronPlanner(second_town)
    return planner.plan()
