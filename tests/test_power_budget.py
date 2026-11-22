import pytest
from src.power_budget import PowerSource, Battery, Load, PowerBudget

def test_daily_generation():
    src = PowerSource(wattage=250, sun_hours_per_day=4)
    assert pytest.approx(src.daily_generation_kwh, 0.001) == 1.0  # 250W * 4h = 1000Wh = 1kWh

def test_daily_consumption():
    ld = Load(wattage=20, hours_per_day=5)
    assert pytest.approx(ld.daily_consumption_kwh, 0.001) == 0.1  # 20W * 5h = 100Wh = 0.1kWh

def test_battery_usable_energy():
    bat = Battery(amp_hours=200, voltage=12, depth_of_discharge=0.5)
    # 200Ah * 12V * 0.5 = 1200Wh = 1.2kWh
    assert pytest.approx(bat.usable_energy_kwh, 0.001) == 1.2

def test_power_budget_self_sufficient():
    src = PowerSource(wattage=300, sun_hours_per_day=5)  # 1.5kWh generation
    bat = Battery(amp_hours=100, voltage=12)           # 0.96kWh usable (100*12*0.8/1000)
    ld = Load(wattage=50, hours_per_day=10)            # 0.5kWh consumption
    budget = PowerBudget(src, bat, ld)
    assert budget.is_self_sufficient is True
    assert pytest.approx(budget.surplus_kwh, 0.001) == 1.0  # 1.5 - 0.5
    # Autonomy days = usable battery / daily consumption = 0.96 / 0.5 = 1.92 days
    assert pytest.approx(budget.required_autonomy_days(), 0.01) == 1.92

def test_power_budget_deficit():
    src = PowerSource(wattage=100, sun_hours_per_day=2)  # 0.2kWh generation
    bat = Battery(amp_hours=50, voltage=12)             # 0.48kWh usable
    ld = Load(wattage=200, hours_per_day=4)             # 0.8kWh consumption
    budget = PowerBudget(src, bat, ld)
    assert budget.is_self_sufficient is False
    assert pytest.approx(budget.surplus_kwh, 0.001) == -0.6  # 0.2 - 0.8
    # Autonomy days = 0.48 / 0.8 = 0.6 days
    assert pytest.approx(budget.required_autonomy_days(), 0.01) == 0.6

def test_zero_load_autonomy_returns_none():
    src = PowerSource(wattage=100, sun_hours_per_day=5)
    bat = Battery(amp_hours=100, voltage=12)
    ld = Load(wattage=0, hours_per_day=0)
    budget = PowerBudget(src, bat, ld)
    assert budget.required_autonomy_days() is None
