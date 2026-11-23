"""Prosty moduł telemetrii rakietowej do demonstracji Forgejo Actions CI."""

import math

STANDARD_GRAVITY = 9.80665


def calculate_delta_v(isp: float, wet_mass: float, dry_mass: float) -> float:
    """Oblicza przyrost prędkości (delta-v) w m/s ze wzoru Ciołkowskiego."""
    if isp <= 0:
        raise ValueError("Impuls właściwy (isp) musi być dodatni.")
    if dry_mass <= 0:
        raise ValueError("Masa sucha (dry_mass) musi być dodatnia.")
    if wet_mass < dry_mass:
        raise ValueError("Masa startowa (wet_mass) nie może być mniejsza niż masa sucha.")

    return isp * STANDARD_GRAVITY * math.log(wet_mass / dry_mass)


def check_fuel_margin(wet_mass: float, dry_mass: float, min_ratio: float = 1.5) -> bool:
    """Sprawdza, czy stosunek masy startowej do suchej spełnia wymagany margines."""
    if dry_mass <= 0:
        raise ValueError("Masa sucha (dry_mass) musi być dodatnia.")
    return (wet_mass / dry_mass) >= min_ratio


def estimate_burn_time(fuel_mass: float, burn_rate: float) -> float:
    """Oblicza czas pracy silnika w sekundach."""
    if fuel_mass < 0:
        raise ValueError("Masa paliwa nie może być ujemna.")
    if burn_rate <= 0:
        raise ValueError("Tempo spalania musi być dodatnie.")
    return fuel_mass / burn_rate


def format_mission_report(
    mission_name: str, delta_v: float, burn_time: float, ready: bool
) -> str:
    """Generuje czytelny raport gotowości misji do wyświetlenia w logach CI."""
    status_badge = "\033[92m[GO FOR LAUNCH]\033[0m" if ready else "\033[91m[NO-GO]\033[0m"
    lines = [
        "╔══════════════════════════════════════════════════════╗",
        f"║  🚀 MISJA: {mission_name:<42}║",
        "╠══════════════════════════════════════════════════════╣",
        f"║  Delta-v        : {delta_v:>10.2f} m/s                   ║",
        f"║  Czas spalania  : {burn_time:>10.2f} s                     ║",
        f"║  Status         : {status_badge:<45}║",
        "╚══════════════════════════════════════════════════════╝",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    isp = 311.0
    dry_mass = 2500.0
    fuel_mass = 7500.0
    wet_mass = dry_mass + fuel_mass
    burn_rate = 125.0

    dv = calculate_delta_v(isp=isp, wet_mass=wet_mass, dry_mass=dry_mass)
    bt = estimate_burn_time(fuel_mass=fuel_mass, burn_rate=burn_rate)
    ready = check_fuel_margin(wet_mass=wet_mass, dry_mass=dry_mass, min_ratio=2.0)

    print(format_mission_report("PROXMOX-ORBIT-01", dv, bt, ready))
