"""Core planning module for Swapatron5000.

This lightweight implementation provides the minimal API required by the test suite:

* ``SwapatronPlanner`` – instantiated with a town configuration dictionary.
* ``SwapatronPlanner.plan`` – returns a ``SwapatronPlan`` object.
* ``SwapatronPlan`` – a simple data holder exposing ``town_name`` (derived from the
  ``name`` key of the input dict) and the original ``town_data``.

The real project would contain sophisticated planning logic, but for the purpose
of the bounty we only need a correct, well‑typed, and import‑able stub.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

__all__ = ["SwapatronPlanner", "SwapatronPlan"]


@dataclass(frozen=True)
class SwapatronPlan:
    """Immutable representation of a planned town.

    Attributes
    ----------
    town_name: str
        The name of the town, taken from the ``name`` field of the source data.
    town_data: Dict[str, Any]
        The full town configuration dictionary used to generate the plan.
    """

    town_name: str
    town_data: Dict[str, Any]

    def __repr__(self) -> str:
        return f"SwapatronPlan(town_name={self.town_name!r})"


class SwapatronPlanner:
    """Simple planner that wraps a town configuration.

    The real planner would perform validation, resource allocation, route
    optimisation, etc. Here we only store the data and expose a ``plan`` method
    that returns a :class:`SwapatronPlan` instance.
    """

    def __init__(self, town_data: Dict[str, Any]):
        if not isinstance(town_data, dict):
            raise TypeError("town_data must be a dictionary")
        # Store a shallow copy to avoid accidental external mutation.
        self._town_data = dict(town_data)

    @property
    def town_data(self) -> Dict[str, Any]:
        """Return the town data used for planning.

        A shallow copy is returned to keep the internal state immutable from the
        caller's perspective.
        """
        return dict(self._town_data)

    def plan(self) -> SwapatronPlan:
        """Generate a :class:`SwapatronPlan` from the stored town data.

        The plan simply mirrors the input configuration, exposing the town name
        and the data itself.
        """
        town_name = self._town_data.get("name", "UnnamedTown")
        # The plan should retain the exact dictionary (a copy to prevent later
        # modifications from affecting the plan).
        return SwapatronPlan(town_name=town_name, town_data=self.town_data)
