"""Top‑level package for Swapatron5000.

Exports the primary planner and the new second‑town helper for convenient import.
"""

from .planner import SwapatronPlanner, SwapatronPlan
from .second_town import generate_second_town_plan

__all__ = [
    "SwapatronPlanner",
    "SwapatronPlan",
    "generate_second_town_plan",
]
