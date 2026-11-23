"""Testy jednostkowe dla modułu rocket_telemetry."""

import pytest

from rocket_telemetry import (
    calculate_delta_v,
    check_fuel_margin,
    estimate_burn_time,
    format_mission_report,
)


def test_delta_v_basic():
    dv = calculate_delta_v(isp=300.0, wet_mass=2000.0, dry_mass=1000.0)
    assert dv == pytest.approx(2039.21, rel=1e-3)


def test_delta_v_zero_fuel():
    dv = calculate_delta_v(isp=300.0, wet_mass=1000.0, dry_mass=1000.0)
    assert dv == 0.0


@pytest.mark.parametrize(
    "isp,wet_mass,dry_mass",
    [
        (0, 2000, 1000),
        (-10, 2000, 1000),
        (300, 2000, 0),
        (300, 900, 1000),
    ],
)
def test_delta_v_invalid_inputs(isp, wet_mass, dry_mass):
    with pytest.raises(ValueError):
        calculate_delta_v(isp=isp, wet_mass=wet_mass, dry_mass=dry_mass)


def test_fuel_margin():
    assert check_fuel_margin(wet_mass=3000.0, dry_mass=1000.0, min_ratio=2.0) is True
    assert check_fuel_margin(wet_mass=1400.0, dry_mass=1000.0, min_ratio=1.5) is False


def test_estimate_burn_time():
    assert estimate_burn_time(fuel_mass=7500.0, burn_rate=125.0) == pytest.approx(60.0)


def test_estimate_burn_time_invalid():
    with pytest.raises(ValueError):
        estimate_burn_time(fuel_mass=-1.0, burn_rate=10.0)
    with pytest.raises(ValueError):
        estimate_burn_time(fuel_mass=100.0, burn_rate=0.0)


def test_format_mission_report():
    report = format_mission_report("TEST-01", 3200.5, 45.0, ready=True)
    assert "TEST-01" in report
    assert "3200.50 m/s" in report
    assert "GO FOR LAUNCH" in report
