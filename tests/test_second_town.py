"""Tests for the second‑town generation utility.

These tests ensure that the helper creates a distinct town configuration and that the
underlying planner can successfully produce a plan.
"""

import pytest

from swapatron import generate_second_town_plan, SwapatronPlanner

# A minimal but realistic town configuration used by the core planner.
BASE_TOWN = {
    "name": "AlphaTown",
    "center": {"x": 0, "y": 0},
    "market": {"x": 5, "y": -3},
    "buildings": [
        {"type": "house", "x": -2, "y": 4},
        {"type": "factory", "x": 3, "y": 3},
    ],
}


def test_second_town_name_is_modified():
    plan = generate_second_town_plan(BASE_TOWN)
    assert plan.town_name == "AlphaTown_2"


def test_coordinates_are_offset():
    plan = generate_second_town_plan(BASE_TOWN)
    # The planner stores the processed town dict on the plan for inspection
    town = plan.town_data
    assert town["center"] == {"x": 10, "y": 10}
    assert town["market"] == {"x": 15, "y": 7}
    assert town["buildings"][0] == {"type": "house", "x": 8, "y": 14}
    assert town["buildings"][1] == {"type": "factory", "x": 13, "y": 13}


def test_plan_is_valid_via_core_planner():
    # Ensure the core planner does not raise when planning the second town
    planner = SwapatronPlanner(generate_second_town_plan(BASE_TOWN).town_data)
    plan = planner.plan()
    assert isinstance(plan, type(generate_second_town_plan(BASE_TOWN)))

