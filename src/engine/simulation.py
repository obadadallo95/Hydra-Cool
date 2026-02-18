"""
Hydra-Cool: Core Physics & Financial Simulation Engine
=======================================================
Implements Thermosiphon flow, Joukowsky Water Hammer,
Strouhal Resonance, and 10-Year Financial Forecasting.

Author: Obada Dallo
Copyright (c) 2024. All Rights Reserved.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict


# ── Data Models ──────────────────────────────────────────

@dataclass
class LocationProfile:
    """Defines the environmental and economic profile of a deployment site."""
    name: str
    ambient_temp_c: float
    seismic_g: float
    energy_price_kwh: float
    pipe_depth_m: float = 150.0
    flow_velocity_ms: float = 2.5
    pipe_diameter_m: float = 2.0


@dataclass
class SimulationResult:
    """Stores all computed outputs for a single location."""
    location: str
    # Physics
    thermosiphon_delta_p_pa: float = 0.0
    water_hammer_surge_mpa: float = 0.0
    vortex_frequency_hz: float = 0.0
    intake_temp_c: float = 0.0
    net_power_mw: float = 0.0
    # Financials
    capex_usd: float = 0.0
    opex_annual_usd: float = 0.0
    revenue_annual_usd: float = 0.0
    profit_10y_usd: float = 0.0
    roi_pct: float = 0.0
    # Verdict
    safety_status: str = "STABLE"
    build_verdict: str = "BUILD"


# ── Physics Engine ───────────────────────────────────────

class PhysicsEngine:
    """
    Core thermodynamic and fluid-dynamics calculations.

    References:
        - Joukowsky, N. (1898) "Water Hammer" (Hydraulic Transients)
        - Strouhal, V. (1878) "Vortex Shedding Frequency"
    """

    G = 9.81           # Gravitational acceleration (m/s²)
    RHO_SURFACE = 997  # Water density at surface (kg/m³)
    RHO_DEEP = 999     # Water density at depth (kg/m³)
    C_WAVE = 1480      # Speed of sound in seawater (m/s)
    ST = 0.22          # Strouhal number for cylinders

    @classmethod
    def thermosiphon_pressure(cls, depth_m: float) -> float:
        """Natural convection driving pressure from thermal density gradient."""
        return (cls.RHO_DEEP - cls.RHO_SURFACE) * cls.G * depth_m

    @classmethod
    def joukowsky_surge(cls, velocity_ms: float) -> float:
        """Joukowsky Equation: ΔP = ρ × c × ΔV  →  returns MPa."""
        surge_pa = cls.RHO_SURFACE * cls.C_WAVE * velocity_ms
        return round(surge_pa / 1e6, 2)

    @classmethod
    def strouhal_frequency(cls, velocity_ms: float, diameter_m: float) -> float:
        """Vortex shedding frequency: f = St × V / D."""
        return round((cls.ST * velocity_ms) / diameter_m, 3)

    @classmethod
    def intake_temperature(cls, ambient_c: float, depth_m: float) -> float:
        """Deep-water intake temp drops ~0.01°C per meter of depth."""
        return round(ambient_c - (depth_m * 0.01), 2)


# ── Financial Engine ─────────────────────────────────────

class FinancialEngine:
    """10-Year Total Cost of Ownership & ROI model."""

    BASE_CAPEX = 50e6          # Base capital expenditure ($50M)
    DEPTH_COST_PER_M = 12000   # $/m of pipe depth
    SEISMIC_HARDENING = 15e6   # Additional cost for seismic zones
    OPEX_RATE = 0.03           # 3% of CAPEX annually
    LOAD_MW = 85.0             # Rated cooling load
    PROJECTION_YEARS = 10

    @classmethod
    def calculate(cls, profile: LocationProfile) -> dict:
        """Compute full financial projection for a location."""
        capex = cls.BASE_CAPEX + (profile.pipe_depth_m * cls.DEPTH_COST_PER_M)
        if profile.seismic_g > 0.3:
            capex += cls.SEISMIC_HARDENING

        opex = capex * cls.OPEX_RATE
        revenue = cls.LOAD_MW * 1000 * 24 * 365 * profile.energy_price_kwh
        profit = (revenue - opex) * cls.PROJECTION_YEARS - capex
        roi = (profit / capex) * 100

        return {
            "capex": round(capex, 2),
            "opex": round(opex, 2),
            "revenue": round(revenue, 2),
            "profit": round(profit, 2),
            "roi": round(roi, 1),
        }


# ── Main Simulation Orchestrator ─────────────────────────

class CoolingSystem:
    """
    Primary simulation controller.
    Runs physics + financials for all deployment zones.
    """

    # Pre-configured deployment profiles
    PROFILES = [
        LocationProfile("Dubai",       ambient_temp_c=21.0, seismic_g=0.10, energy_price_kwh=0.15, pipe_depth_m=150),
        LocationProfile("Helsinki",    ambient_temp_c=5.0,  seismic_g=0.05, energy_price_kwh=0.22, pipe_depth_m=50),
        LocationProfile("Los Angeles", ambient_temp_c=16.5, seismic_g=0.45, energy_price_kwh=0.18, pipe_depth_m=120),
    ]

    def __init__(self):
        self.results: List[SimulationResult] = []

    def run_all(self) -> List[SimulationResult]:
        """Execute simulation for all configured locations."""
        self.results = []
        for profile in self.PROFILES:
            result = self._simulate_location(profile)
            self.results.append(result)
        return self.results

    def _simulate_location(self, p: LocationProfile) -> SimulationResult:
        """Run full physics + financial analysis for one location."""
        res = SimulationResult(location=p.name)

        # ── Physics ──
        res.thermosiphon_delta_p_pa = PhysicsEngine.thermosiphon_pressure(p.pipe_depth_m)
        res.water_hammer_surge_mpa = PhysicsEngine.joukowsky_surge(p.flow_velocity_ms)
        res.vortex_frequency_hz = PhysicsEngine.strouhal_frequency(p.flow_velocity_ms, p.pipe_diameter_m)
        res.intake_temp_c = PhysicsEngine.intake_temperature(p.ambient_temp_c, p.pipe_depth_m)
        res.net_power_mw = round(p.ambient_temp_c - res.intake_temp_c, 2) * 10  # Simplified net output

        # ── Safety Verdict ──
        if p.pipe_depth_m > 800:
            res.safety_status = "CRITICAL - Water Hammer Risk"
        elif p.seismic_g > 0.3 and p.pipe_depth_m > 100:
            res.safety_status = "STRUCTURAL STRAIN - Seismic Zone"
        else:
            res.safety_status = "STABLE"

        # ── Financials ──
        fin = FinancialEngine.calculate(p)
        res.capex_usd = fin["capex"]
        res.opex_annual_usd = fin["opex"]
        res.revenue_annual_usd = fin["revenue"]
        res.profit_10y_usd = fin["profit"]
        res.roi_pct = fin["roi"]
        res.build_verdict = "BUILD" if fin["roi"] > 25 else "REVIEW"

        return res

    def print_summary(self):
        """Print a formatted console summary."""
        print("\n" + "=" * 60)
        print("  HYDRA-COOL SIMULATION RESULTS")
        print("=" * 60)
        for r in self.results:
            print(f"\n  📍 {r.location}")
            print(f"     Net Power:  {r.net_power_mw} MW")
            print(f"     CAPEX:      ${r.capex_usd:,.0f}")
            print(f"     10Y Profit: ${r.profit_10y_usd:,.0f}")
            print(f"     ROI:        {r.roi_pct}%")
            print(f"     Surge:      {r.water_hammer_surge_mpa} MPa")
            print(f"     Safety:     {r.safety_status}")
            print(f"     Verdict:    {'✅' if r.build_verdict == 'BUILD' else '⚠️'}  {r.build_verdict}")
        print("\n" + "=" * 60)
