"""Power budgeting utilities for solar, battery, and lighting calculations.

This module provides a small, pure‑Python API to model:
- Solar generation based on panel wattage and average sun hours.
- Constant power loads (e.g., lighting) expressed in watts and daily usage.
- Battery storage capacity in amp‑hours at a given voltage.

The core class, :class:`PowerBudget`, aggregates these components and offers
convenient properties to assess daily energy balance and required autonomy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PowerSource:
    """Solar panel specifications.

    Attributes
    ----------
    wattage : float
        Rated power of the panel under standard test conditions (W).
    sun_hours_per_day : float
        Average effective sun hours per day for the installation location.
    """

    wattage: float
    sun_hours_per_day: float

    @property
    def daily_generation_kwh(self) -> float:
        """Calculate daily energy generation in kilowatt‑hours.

        Returns
        -------
        float
            Energy produced per day (kWh).
        """
        return (self.wattage * self.sun_hours_per_day) / 1000.0


@dataclass(frozen=True)
class Battery:
    """Battery storage specifications.

    Attributes
    ----------
    amp_hours : float
        Capacity of the battery in amp‑hours (Ah).
    voltage : float
        Nominal voltage of the battery (V).
    depth_of_discharge : float, optional
        Maximum usable depth of discharge (0‑1). Defaults to 0.8 (80%).
    """

    amp_hours: float
    voltage: float
    depth_of_discharge: float = 0.8

    @property
    def usable_energy_kwh(self) -> float:
        """Usable energy considering depth of discharge.

        Returns
        -------
        float
            Usable energy in kilowatt‑hours.
        """
        return (self.amp_hours * self.voltage * self.depth_of_discharge) / 1000.0


@dataclass(frozen=True)
class Load:
    """Constant power load (e.g., lighting).

    Attributes
    ----------
    wattage : float
        Power consumption of the load (W).
    hours_per_day : float
        Number of hours the load operates each day.
    """

    wattage: float
    hours_per_day: float

    @property
    def daily_consumption_kwh(self) -> float:
        """Calculate daily energy consumption in kilowatt‑hours.

        Returns
        -------
        float
            Energy consumed per day (kWh).
        """
        return (self.wattage * self.hours_per_day) / 1000.0


@dataclass(frozen=True)
class PowerBudget:
    """Aggregates a solar source, battery, and load to evaluate the system.

    Parameters
    ----------
    source : PowerSource
        The solar generation source.
    battery : Battery
        Energy storage.
    load : Load
        The constant power demand.
    """

    source: PowerSource
    battery: Battery
    load: Load

    @property
    def daily_generation_kwh(self) -> float:
        return self.source.daily_generation_kwh

    @property
    def daily_consumption_kwh(self) -> float:
        return self.load.daily_consumption_kwh

    @property
    def surplus_kwh(self) -> float:
        """Net surplus (positive) or deficit (negative) per day.
        """
        return self.daily_generation_kwh - self.daily_consumption_kwh

    @property
    def is_self_sufficient(self) -> bool:
        """True if daily generation meets or exceeds consumption.
        """
        return self.surplus_kwh >= 0

    def required_autonomy_days(self, safety_factor: float = 1.0) -> Optional[float]:
        """Calculate how many days of autonomy the battery provides.

        Parameters
        ----------
        safety_factor : float, optional
            Multiplier to increase required days for safety (default 1.0).

        Returns
        -------
        Optional[float]
            Number of days the battery can sustain the load without solar input.
            Returns ``None`` if the load consumption is zero.
        """
        if self.daily_consumption_kwh == 0:
            return None
        return (self.battery.usable_energy_kwh / self.daily_consumption_kwh) * safety_factor

    def summary(self) -> dict:
        """Convenient dictionary summarising the budget.
        """
        return {
            "daily_generation_kwh": round(self.daily_generation_kwh, 3),
            "daily_consumption_kwh": round(self.daily_consumption_kwh, 3),
            "surplus_kwh": round(self.surplus_kwh, 3),
            "self_sufficient": self.is_self_sufficient,
            "autonomy_days": round(self.required_autonomy_days(), 2) if self.required_autonomy_days() is not None else None,
        }

# Example usage (removed from library code to keep module clean)
# if __name__ == "__main__":
#     src = PowerSource(wattage=200, sun_hours_per_day=5)
#     bat = Battery(amp_hours=100, voltage=12)
#     ld = Load(wattage=10, hours_per_day=8)
#     budget = PowerBudget(src, bat, ld)
#     print(budget.summary())
