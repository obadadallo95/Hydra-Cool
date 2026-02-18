"""
Hydra-Cool Simulation v25.0 — TECHNOLOGY SHOWDOWN
====================================================
Pure physics head-to-head: Hydra-Cool's thermosiphon principle
versus every real cooling technology used by data centers today.

No construction costs. No permits. Just thermodynamics.

We compare:
  1. Vapor-Compression Chiller (AWS, most data centers)
  2. Evaporative Cooling (Google)
  3. Free Air Cooling (Meta Lulea, Sweden)
  4. Liquid Immersion Cooling (Microsoft)
  5. Rear-Door Heat Exchangers (Enterprise DCs)
  6. SWAC - Seawater Air Conditioning (Honolulu, real system)
  7. Absorption Chiller (waste heat driven)
  8. District Cooling (Dubai, Singapore)
  9. OTEC - Ocean Thermal Energy Conversion (Makai, Hawaii)
  10. Hydra-Cool Thermosiphon (our concept)

Metrics:
  - COP (Coefficient of Performance)
  - Specific Power (kW consumed per kW of cooling)
  - Carnot Efficiency (% of theoretical maximum)
  - Water Consumption (L/kWh of cooling)
  - Temperature Operating Range
  - Energy Source
  - Waste Heat Recovery Potential

Sources:
  - ASHRAE Handbook: HVAC Systems & Equipment (2024)
  - DOE Better Buildings: Data Center Cooling Best Practices
  - Incropera et al., "Fundamentals of Heat & Mass Transfer" (8th ed)
  - NREL: "OTEC Technology Assessment" (2023)
  - Makai Ocean Engineering: OTEC operational data
  - Microsoft Research: "Two-Phase Immersion Cooling" (2023)
  - Google Data Center Efficiency Reports
  - Emerson/Vertiv: "Data Center Cooling Technologies Guide"

Author: Obada Dallo
Copyright (c) 2024. All Rights Reserved.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

# ══════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════

# Thermodynamic reference temperatures
T_SERVER_HOT = 50.0   # °C — typical server exhaust / hot water temp
T_COLD_DEEP  = 5.0    # °C — deep ocean at 400-500m
T_AMBIENT_HOT = 35.0  # °C — hot climate ambient air (Dubai summer)
T_AMBIENT_MILD = 20.0 # °C — temperate climate
T_AMBIENT_COLD = -5.0 # °C — Nordic winter

# Convert to Kelvin for Carnot
def to_K(c): return c + 273.15

# Carnot COP for cooling: COP_carnot = T_cold / (T_hot - T_cold)
def carnot_cop(T_cold_C, T_hot_C):
    T_c = to_K(T_cold_C)
    T_h = to_K(T_hot_C)
    if T_h <= T_c:
        return float('inf')  # No work needed
    return T_c / (T_h - T_c)


# ══════════════════════════════════════════════════════════════
#  TECHNOLOGY DATABASE (Real-World Published Data)
# ══════════════════════════════════════════════════════════════

TECHNOLOGIES = {
    # ─── 1. Vapor-Compression Chiller ───
    # The industry workhorse. Uses refrigerant (R-134a, R-410A) in a
    # compressor → condenser → expansion → evaporator cycle.
    # Source: ASHRAE 90.1, Carrier/Trane published data
    "Vapor-Compression\nChiller": {
        "real_cop": 5.5,           # Typical centrifugal chiller COP (ASHRAE)
        "best_cop": 7.5,           # Best-in-class magnetic bearing (Danfoss Turbocor)
        "specific_power_kw": 0.18, # kW per kW of cooling (1/COP)
        "t_cold": 7,               # Chilled water supply temp °C
        "t_hot": T_AMBIENT_HOT,    # Condenser rejection temp
        "water_l_kwh": 3.8,        # Cooling tower water (evaporative condenser)
        "carnot_pct": 0,           # Calculated below
        "energy_source": "Electricity (100%)",
        "waste_heat_recovery": "Limited (condenser heat, low grade)",
        "operating_range": "All climates, all seasons",
        "used_by": "AWS, most enterprise DCs",
        "color": "#FF9900",
        "category": "Active (Mechanical)",
    },
    
    # ─── 2. Evaporative Cooling ───
    # Water evaporated over pads/media cools air adiabatically.
    # Only works in dry climates (low wet-bulb temperature).
    # Source: Google Data Center Best Practices, SPX Cooling
    "Evaporative\nCooling": {
        "real_cop": 15.0,          # Very high COP — only fan energy
        "best_cop": 25.0,          # With economizer in ideal conditions
        "specific_power_kw": 0.07, # kW per kW of cooling
        "t_cold": 18,              # Achievable air temp (wet-bulb limited)
        "t_hot": T_AMBIENT_HOT,
        "water_l_kwh": 5.5,        # Heavy water consumption
        "carnot_pct": 0,
        "energy_source": "Electricity (fans only, ~5%)",
        "waste_heat_recovery": "None (heat goes to atmosphere)",
        "operating_range": "Dry climates only (WB < 21°C)",
        "used_by": "Google (multiple sites)",
        "color": "#4285F4",
        "category": "Passive-Assist (Evaporative)",
    },
    
    # ─── 3. Free Air Cooling (Economizer) ───
    # Direct outside air blown through servers when ambient < 27°C.
    # Source: Meta Lulea DC, ASHRAE TC9.9 expanded envelope
    "Free Air\nCooling": {
        "real_cop": 30.0,          # Extremely high — fan energy only
        "best_cop": 50.0,          # Near-zero energy in cold climates
        "specific_power_kw": 0.03, # kW per kW of cooling (Nordic)
        "t_cold": T_AMBIENT_COLD,  # As cold as outside air
        "t_hot": 27,               # ASHRAE A1 allowable server inlet
        "water_l_kwh": 0.0,        # No water used
        "carnot_pct": 0,
        "energy_source": "Electricity (fans only, ~2-3%)",
        "waste_heat_recovery": "Limited (warm exhaust for office heating)",
        "operating_range": "Cold climates ONLY (ambient < 27°C, 40-70% of hours)",
        "used_by": "Meta (Lulea, Sweden), many Nordic DCs",
        "color": "#1877F2",
        "category": "Passive (Air)",
    },
    
    # ─── 4. Liquid Immersion Cooling ───
    # Servers submerged in engineered dielectric fluid (3M Novec/Fluorinert).
    # Two-phase: fluid boils at ~49°C, vapor condenses on cold plate.
    # Source: Microsoft Research, GRC (Green Revolution Cooling)
    "Liquid Immersion\n(Two-Phase)": {
        "real_cop": 8.0,           # Better than chiller (no air handling)
        "best_cop": 12.0,          # Two-phase with optimized condenser
        "specific_power_kw": 0.12, # kW per kW of cooling
        "t_cold": 49,              # Fluid boiling point
        "t_hot": 60,               # Condenser temp
        "water_l_kwh": 0.0,        # No water (closed dielectric loop)
        "carnot_pct": 0,
        "energy_source": "Electricity (pumps ~8%)",
        "waste_heat_recovery": "HIGH — 49°C fluid → district heating",
        "operating_range": "All climates (enclosed system)",
        "used_by": "Microsoft (Project Natick, Azure)",
        "color": "#00A4EF",
        "category": "Active (Liquid)",
    },
    
    # ─── 5. Rear-Door Heat Exchanger ───
    # Water-cooled doors on back of server racks.
    # Remove ~60-80% of rack heat at the source.
    # Source: CoolIT Systems, Vertiv/Liebert
    "Rear-Door\nHeat Exchanger": {
        "real_cop": 10.0,          # Better than room-level AC
        "best_cop": 14.0,
        "specific_power_kw": 0.10, # kW per kW of cooling
        "t_cold": 18,              # Chilled water supply
        "t_hot": 35,               # Return water temp
        "water_l_kwh": 1.5,        # Reduced vs full chiller (smaller plant)
        "carnot_pct": 0,
        "energy_source": "Electricity (pumps ~7%)",
        "waste_heat_recovery": "Moderate (35°C return water)",
        "operating_range": "All climates (supplemental AC still needed)",
        "used_by": "Many enterprise DCs, co-location facilities",
        "color": "#66BB6A",
        "category": "Active (Liquid)",
    },
    
    # ─── 6. SWAC — Seawater Air Conditioning ───
    # Cold deep-sea water pumped to shore for air conditioning.
    # OPERATIONAL: Honolulu Seawater AC since 2014 (~25,000 tons).
    # Source: Honolulu Seawater Air Conditioning LLC, Makai OE
    "SWAC\n(Seawater AC)": {
        "real_cop": 12.0,          # Documented at Honolulu plant
        "best_cop": 18.0,          # Theoretical with optimized pumping
        "specific_power_kw": 0.08, # kW per kW of cooling (pump energy)
        "t_cold": 5,               # Deep seawater temp
        "t_hot": 25,               # Building supply air
        "water_l_kwh": 0.0,        # Seawater (not freshwater)
        "carnot_pct": 0,
        "energy_source": "Electricity (pumps ~6-8%)",
        "waste_heat_recovery": "Low (warm seawater returned at 12-15°C)",
        "operating_range": "Coastal only, deep water within 3-5 km",
        "used_by": "Honolulu downtown (operational since 2014)",
        "color": "#26C6DA",
        "category": "Semi-Passive (Pumped Seawater)",
    },
    
    # ─── 7. Absorption Chiller ───
    # Uses waste heat (steam, hot water) to drive cooling cycle.
    # LiBr-water pair or ammonia-water.
    # Source: Carrier/York absorption chiller catalogs
    "Absorption\nChiller": {
        "real_cop": 1.2,           # Single-effect LiBr (typical)
        "best_cop": 1.8,           # Double-effect (higher-grade heat)
        "specific_power_kw": 0.05, # Parasitic electrical only
        "t_cold": 7,               # Chilled water supply
        "t_hot": 90,               # Generator heat source required
        "water_l_kwh": 4.5,        # Cooling tower water
        "carnot_pct": 0,
        "energy_source": "Waste heat + electricity (pumps ~5%)",
        "waste_heat_recovery": "IS waste heat recovery (uses 80-120°C heat)",
        "operating_range": "Requires waste heat source (CHP, process)",
        "used_by": "Combined Heat & Power plants, industrial sites",
        "color": "#FFA726",
        "category": "Active (Heat-Driven)",
    },
    
    # ─── 8. District Cooling ───
    # Centralized chilled water plant serving multiple buildings.
    # Source: Empower (Dubai, world's largest), SP Group (Singapore)
    "District\nCooling": {
        "real_cop": 6.0,           # Centralized = larger, more efficient
        "best_cop": 8.0,           # With thermal energy storage
        "specific_power_kw": 0.17, # kW per kW of cooling
        "t_cold": 5,               # Chilled water supply
        "t_hot": T_AMBIENT_HOT,
        "water_l_kwh": 4.0,        # Large cooling towers
        "carnot_pct": 0,
        "energy_source": "Electricity (centralized plant)",
        "waste_heat_recovery": "Moderate (some district heating)",
        "operating_range": "Hot climates (Dubai, Singapore, Abu Dhabi)",
        "used_by": "Dubai (Empower — 1.8M tons), Singapore",
        "color": "#EF5350",
        "category": "Active (Centralized)",
    },
    
    # ─── 9. OTEC — Ocean Thermal Energy Conversion ───
    # Uses ocean thermal gradient to GENERATE electricity.
    # Not just cooling — actual power production.
    # Source: Makai Ocean Engineering (100kW demo), NREL studies
    "OTEC\n(Ocean Thermal)": {
        "real_cop": float('inf'),  # NET ENERGY PRODUCER
        "best_cop": float('inf'),
        "specific_power_kw": -0.03, # NEGATIVE — produces 30W per kW thermal
        "t_cold": 5,               # Deep ocean
        "t_hot": 25,               # Surface ocean (tropical)
        "water_l_kwh": 0.0,        # Seawater
        "carnot_pct": 0,
        "energy_source": "Ocean thermal gradient (PRODUCES power)",
        "waste_heat_recovery": "N/A — it IS energy recovery",
        "operating_range": "Tropical coastal only (ΔT > 20°C)",
        "used_by": "Makai OE Hawaii (100kW demo), French Polynesia",
        "color": "#AB47BC",
        "category": "Passive (Thermal Gradient)",
    },
    
    # ─── 10. Hydra-Cool Thermosiphon ───
    # Natural convection driven by density difference between
    # hot (50°C) and cold (5°C) water in a vertical loop.
    # The key question: how does it ACTUALLY compare?
    "Hydra-Cool\nThermosiphon": {
        "real_cop": 20.0,          # Estimated — minimal pump assist
        "best_cop": 50.0,          # Theoretical pure passive (short pipe)
        "specific_power_kw": 0.05, # kW per kW (pump assist for long pipe)
        "t_cold": 5,               # Deep ocean intake
        "t_hot": T_SERVER_HOT,     # Server exhaust
        "water_l_kwh": 0.0,        # Seawater closed loop
        "carnot_pct": 0,
        "energy_source": "Gravity + thermal gradient (~5% pump)",
        "waste_heat_recovery": "HIGH — 50°C hot water available",
        "operating_range": "Coastal only, deep water access",
        "used_by": "Concept (TRL 2, no operational system)",
        "color": "#00FFCC",
        "category": "Passive (Thermosiphon)",
    },
}


# ══════════════════════════════════════════════════════════════
#  ANALYSIS 1: Carnot Efficiency — Theoretical Maximum
# ══════════════════════════════════════════════════════════════

def analyze_carnot():
    """
    Carnot COP = T_cold / (T_hot - T_cold) [Kelvin]
    This is the THEORETICAL MAXIMUM efficiency for any cooling cycle.
    Real systems achieve 20-60% of Carnot.
    """
    print("\n" + "=" * 70)
    print("  [1/6] CARNOT EFFICIENCY — How Close to Theoretical Perfect?")
    print("=" * 70)
    
    print(f"\n  Carnot COP = T_cold / (T_hot - T_cold) for cooling cycles")
    print(f"  Higher COP = less energy needed per unit of cooling")
    print(f"\n  {'Technology':<25} {'T_cold':>7} {'T_hot':>7} {'Carnot':>8} {'Real':>8} {'%Carnot':>8} {'Rating'}")
    print(f"  {'-'*75}")
    
    for name, tech in TECHNOLOGIES.items():
        t_c = tech["t_cold"]
        t_h = tech["t_hot"]
        c_cop = carnot_cop(t_c, t_h)
        r_cop = tech["real_cop"]
        
        if c_cop == float('inf') or r_cop == float('inf'):
            pct_carnot = 100.0  # Net producer or no work needed
            rating = "N/A"
        else:
            pct_carnot = min((r_cop / c_cop) * 100, 100)
            if pct_carnot > 60:
                rating = "EXCELLENT"
            elif pct_carnot > 40:
                rating = "Good"
            elif pct_carnot > 20:
                rating = "Average"
            else:
                rating = "Poor"
        
        tech["carnot_pct"] = pct_carnot
        
        cop_str = f"{c_cop:.1f}" if c_cop != float('inf') else "∞"
        rcop_str = f"{r_cop:.1f}" if r_cop != float('inf') else "∞ (producer)"
        pct_str = f"{pct_carnot:.0f}%"
        
        label = name.replace("\n", " ")
        print(f"  {label:<25} {t_c:>5.0f}°C {t_h:>5.0f}°C {cop_str:>8} {rcop_str:>8} {pct_str:>8} {rating}")
    
    print(f"\n  KEY INSIGHT:")
    print(f"    Hydra-Cool's advantage is the ENORMOUS temperature delta: ΔT = 45°C.")
    print(f"    This gives a high Carnot COP. But it's the SAME delta SWAC uses.")
    print(f"    The real question: does the thermosiphon mechanism beat pumped SWAC?")


# ══════════════════════════════════════════════════════════════
#  ANALYSIS 2: Energy Efficiency — kW per kW of Cooling
# ══════════════════════════════════════════════════════════════

def analyze_energy_efficiency():
    """
    Specific power consumption: how many kW of electricity
    do you need to remove 1 kW of heat?
    
    Lower = better (0.0 = perfectly passive).
    """
    print("\n" + "=" * 70)
    print("  [2/6] ENERGY EFFICIENCY — kW Electricity per kW Cooling")
    print("=" * 70)
    
    print(f"\n  For a 100 MW IT load (=100 MW of heat to remove):")
    print(f"  {'Technology':<25} {'kW_e/kW_c':>10} {'Power for 100MW':>16} {'Category'}")
    print(f"  {'-'*65}")
    
    sorted_techs = sorted(TECHNOLOGIES.items(), 
                          key=lambda x: x[1]["specific_power_kw"])
    
    for name, tech in sorted_techs:
        sp = tech["specific_power_kw"]
        power_100mw = sp * 100_000  # kW for 100MW cooling
        cat = tech["category"]
        label = name.replace("\n", " ")
        
        if sp < 0:
            print(f"  {label:<25} {sp:>10.3f}  PRODUCES {abs(power_100mw)/1000:.0f} MW  {cat}")
        elif sp == 0:
            print(f"  {label:<25} {sp:>10.3f}  {'0 MW':>16}  {cat}")
        else:
            print(f"  {label:<25} {sp:>10.3f}  {power_100mw/1000:>13.1f} MW  {cat}")
    
    # PUE calculation from specific power
    print(f"\n  RESULTING PUE (for cooling-only contribution):")
    print(f"  PUE = 1 + specific_power  (simplified)")
    for name, tech in sorted_techs:
        sp = tech["specific_power_kw"]
        if sp >= 0:
            pue = 1.0 + sp
            label = name.replace("\n", " ")
            print(f"    {label:<25}: PUE = {pue:.2f}")
    
    print(f"\n  HONEST ASSESSMENT:")
    print(f"    Free Air Cooling (PUE ~1.03) BEATS Hydra-Cool (PUE ~1.05)")
    print(f"    when ambient temperature is below 27°C.")
    print(f"    But Free Air only works ~40-70% of hours even in cold climates.")
    print(f"    Hydra-Cool works 24/7/365 regardless of weather.")


# ══════════════════════════════════════════════════════════════
#  ANALYSIS 3: Water Consumption
# ══════════════════════════════════════════════════════════════

def analyze_water():
    """Compare freshwater consumption across technologies."""
    print("\n" + "=" * 70)
    print("  [3/6] WATER CONSUMPTION — The Hidden Resource Cost")
    print("=" * 70)
    
    print(f"\n  {'Technology':<25} {'L/kWh cooling':>14} {'Annual (100MW)':>15} {'Type'}")
    print(f"  {'-'*60}")
    
    annual_mwh = 100 * 8760  # 100MW for a year
    
    sorted_techs = sorted(TECHNOLOGIES.items(),
                          key=lambda x: x[1]["water_l_kwh"], reverse=True)
    
    for name, tech in sorted_techs:
        water = tech["water_l_kwh"]
        annual_liters = water * annual_mwh * 1000  # MWh to kWh
        annual_M = annual_liters / 1e6
        label = name.replace("\n", " ")
        wtype = "FRESHWATER" if water > 0 else "None/Seawater"
        
        if water > 0:
            print(f"  {label:<25} {water:>12.1f}L  {annual_M:>12.0f}M L  ❌ {wtype}")
        else:
            print(f"  {label:<25} {water:>12.1f}L  {annual_M:>12.0f}M L  ✅ {wtype}")
    
    print(f"\n  WATER VERDICT:")
    print(f"    Evaporative Cooling consumes 5.5 L per kWh — a city's worth of water.")
    print(f"    Hydra-Cool, SWAC, OTEC, Free Air, Immersion use ZERO freshwater.")
    print(f"    On water alone, Hydra-Cool genuinely excels.")
    print(f"    But it SHARES this advantage with 4 other technologies.")


# ══════════════════════════════════════════════════════════════
#  ANALYSIS 4: Operating Range — When Does Each Technology Work?
# ══════════════════════════════════════════════════════════════

def analyze_operating_range():
    """Which technologies work where, and when?"""
    print("\n" + "=" * 70)
    print("  [4/6] OPERATING RANGE — Where & When Does Each Work?")
    print("=" * 70)
    
    # Climate zones × technology suitability
    climates = ["Dubai\n(45°C)", "Singapore\n(32°C)", "LA\n(25°C)", "Amsterdam\n(12°C)", "Lulea\n(-20°C)"]
    climate_temps = [45, 32, 25, 12, -20]
    
    # Suitability score 0-5 for each tech in each climate
    suitability = {
        "Vapor-Compression Chiller":  [4, 4, 5, 5, 5],  # Works everywhere
        "Evaporative Cooling":        [2, 1, 3, 4, 5],  # Bad in humid climates
        "Free Air Cooling":           [0, 0, 2, 4, 5],  # Only in cold climates
        "Liquid Immersion (Two-Phase)":[5, 5, 5, 5, 5],  # Works everywhere
        "Rear-Door Heat Exchanger":   [4, 4, 5, 5, 5],  # Works everywhere
        "SWAC (Seawater AC)":         [4, 5, 4, 3, 2],  # Needs warm surface water
        "Absorption Chiller":         [3, 3, 3, 3, 3],  # Needs waste heat
        "District Cooling":           [5, 5, 3, 2, 1],  # Best in hot climates
        "OTEC (Ocean Thermal)":       [4, 5, 3, 1, 0],  # Needs tropical waters
        "Hydra-Cool Thermosiphon":    [5, 5, 4, 3, 2],  # Needs coastal + deep water
    }
    
    print(f"\n  Suitability Score (0=Impossible, 5=Ideal)")
    print(f"  {'Technology':<30} {'Dubai':>7} {'Singap':>7} {'LA':>7} {'AMS':>7} {'Lulea':>7} {'Total':>7}")
    print(f"  {'-'*73}")
    
    for tech, scores in sorted(suitability.items(), key=lambda x: sum(x[1]), reverse=True):
        total = sum(scores)
        s_str = "  ".join(f"{s:>5}" for s in scores)
        print(f"  {tech:<30} {s_str}  {total:>5}/25")
    
    print(f"\n  VERSATILITY VERDICT:")
    print(f"    Liquid Immersion and Vapor-Compression work EVERYWHERE (25/25).")
    print(f"    Hydra-Cool scores 19/25 — limited by coastal requirement.")
    print(f"    Free Air Cooling: 11/25 — only cold climates.")
    print(f"    OTEC: 13/25 — only tropical.")


# ══════════════════════════════════════════════════════════════
#  ANALYSIS 5: Waste Heat Recovery Potential
# ══════════════════════════════════════════════════════════════

def analyze_waste_heat():
    """
    Data centers produce enormous amounts of waste heat.
    Which technologies can capture and reuse this heat?
    Higher grade heat (higher temperature) = more useful.
    """
    print("\n" + "=" * 70)
    print("  [5/6] WASTE HEAT RECOVERY — Can We Use the Heat?")
    print("=" * 70)
    
    heat_data = [
        ("Liquid Immersion",          49,   "HIGH",    "District heating, greenhouses, desalination"),
        ("Hydra-Cool Thermosiphon",   50,   "HIGH",    "Hot seawater for aquaculture, desal, heating"),
        ("Absorption Chiller",        90,   "HIGHEST", "IS heat recovery — uses waste heat as fuel"),
        ("Rear-Door HX",             35,    "MODERATE","Low-grade: floor heating"),
        ("OTEC",                      25,   "LOW",     "Warm discharge for aquaculture"),
        ("SWAC",                      15,   "VERY LOW","Return water barely above ambient"),
        ("Vapor-Compression",         35,   "LOW",     "Condenser heat is low-grade"),
        ("Evaporative",               0,    "NONE",    "Heat goes to atmosphere (evaporation)"),
        ("Free Air",                  25,   "LOW",     "Warm exhaust air for adjacent heating"),
        ("District Cooling",          40,   "MODERATE","Return water for heating system"),
    ]
    
    print(f"\n  {'Technology':<25} {'Heat Grade':>11} {'Potential':>10} {'Applications'}")
    print(f"  {'-'*75}")
    
    for tech, temp, grade, apps in heat_data:
        print(f"  {tech:<25} {temp:>8}°C  {grade:>10} {apps}")
    
    print(f"\n  WASTE HEAT VERDICT:")
    print(f"    Hydra-Cool has EXCELLENT waste heat recovery (50°C hot water).")
    print(f"    Liquid Immersion is comparable (49°C fluid).")
    print(f"    Absorption Chiller is the KING — it consumes waste heat as fuel.")
    print(f"    This is a genuine Hydra-Cool strength.")


# ══════════════════════════════════════════════════════════════
#  ANALYSIS 6: THE HEAD-TO-HEAD — Closest Competitors
# ══════════════════════════════════════════════════════════════

def head_to_head():
    """
    The most honest comparison: Hydra-Cool vs ITS CLOSEST RIVALS.
    SWAC, Liquid Immersion, and Free Air are the real competition.
    """
    print("\n" + "=" * 70)
    print("  [6/6] HEAD-TO-HEAD — Hydra-Cool vs Closest Rivals")
    print("=" * 70)
    
    rivals = {
        "SWAC (Honolulu)": {
            "advantage": "Operational since 2014 — PROVEN technology (TRL 7-8)",
            "disadvantage": "Requires large pumps (6-8% energy), higher OPEX",
            "cop": 12.0,
            "sp": 0.08,
            "water": 0.0,
            "verdict": "HC has slight efficiency edge but SWAC is PROVEN",
        },
        "Liquid Immersion (Microsoft)": {
            "advantage": "Works ANYWHERE, high heat recovery, no geography limit",
            "disadvantage": "Expensive dielectric fluid, server redesign required",
            "cop": 8.0,
            "sp": 0.12,
            "water": 0.0,
            "verdict": "HC wins on efficiency; LI wins on location flexibility",
        },
        "Free Air (Meta Lulea)": {
            "advantage": "Near-zero energy, proven at scale, PUE 1.03",
            "disadvantage": "Only works in cold climates, 40-70% of hours",
            "cop": 30.0,
            "sp": 0.03,
            "water": 0.0,
            "verdict": "Free Air BEATS HC on efficiency when available",
        },
        "Evaporative (Google)": {
            "advantage": "Proven, scalable, low energy, works in dry climates",
            "disadvantage": "Massive water consumption, fails in humid climates",
            "cop": 15.0,
            "sp": 0.07,
            "water": 5.5,
            "verdict": "HC wins on water; Evap wins on maturity and cost",
        },
    }
    
    hc_cop = TECHNOLOGIES["Hydra-Cool\nThermosiphon"]["real_cop"]
    hc_sp = TECHNOLOGIES["Hydra-Cool\nThermosiphon"]["specific_power_kw"]
    
    for name, data in rivals.items():
        print(f"\n  ┌── {name} ─{'─' * (55 - len(name))}┐")
        print(f"  │  COP: {data['cop']:.0f} vs HC {hc_cop:.0f}  |  kW/kW: {data['sp']:.3f} vs HC {hc_sp:.3f}")
        print(f"  │  ✅ {data['advantage']}")
        print(f"  │  ❌ {data['disadvantage']}")
        print(f"  │  VERDICT: {data['verdict']}")
        print(f"  └{'─' * 60}┘")
    
    print(f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║                  THE HONEST TECHNOLOGY VERDICT              ║
  ╠══════════════════════════════════════════════════════════════╣
  ║                                                              ║
  ║  Hydra-Cool's thermosiphon is NOT a revolutionary new        ║
  ║  physics principle — it's a clever COMBINATION of:           ║
  ║                                                              ║
  ║    1. Deep-sea cold water (same as SWAC, OTEC)               ║
  ║    2. Natural convection (known for centuries)               ║
  ║    3. Passive operation (similar to heat pipes)              ║
  ║                                                              ║
  ║  WHERE IT GENUINELY WINS:                                    ║
  ║    ✅ Zero freshwater (vs Evaporative, Chiller)              ║
  ║    ✅ High COP (~20) with minimal pumping                    ║
  ║    ✅ Excellent waste heat grade (50°C)                      ║
  ║    ✅ 24/7 operation (vs Free Air's weather dependence)      ║
  ║    ✅ Lower specific power than most active systems          ║
  ║                                                              ║
  ║  WHERE IT HONESTLY LOSES:                                    ║
  ║    ❌ Free Air beats it on pure efficiency (COP 30 vs 20)   ║
  ║    ❌ Liquid Immersion works anywhere (no coast needed)      ║
  ║    ❌ SWAC is already proven and operational                 ║
  ║    ❌ Vapor-Compression is universally available             ║
  ║    ❌ Its 'unique' physics aren't unique — SWAC is similar  ║
  ║                                                              ║
  ║  THE REAL INNOVATION:                                        ║
  ║    Not the cold water. Not the convection.                   ║
  ║    The innovation is the PASSIVE thermosiphon at DC scale.   ║
  ║    If it works at 100MW without pumps, it's a breakthrough.  ║
  ║    But v23 showed that pure passive at 100MW is physically   ║
  ║    impossible with realistic pipe lengths.                   ║
  ║                                                              ║
  ║  WITH PUMPS (realistic), Hydra-Cool is essentially a        ║
  ║  MORE EFFICIENT version of SWAC — which already exists.     ║
  ║                                                              ║
  ╚══════════════════════════════════════════════════════════════╝
    """)


# ══════════════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════════════

def generate_charts(output_dir="assets"):
    """Generate the technology comparison dashboard."""
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(2, 3, figsize=(22, 14))
    fig.patch.set_facecolor("#0a0a0a")
    fig.suptitle("TECHNOLOGY SHOWDOWN: Every Cooling Method vs Hydra-Cool",
                 fontsize=18, fontweight="bold", color="#00FFCC", y=0.98)
    
    names = [n.replace("\n", " ") for n in TECHNOLOGIES.keys()]
    short = ["Chiller", "Evap", "Free Air", "Immersion", "RDHX", 
             "SWAC", "Absorb.", "District", "OTEC", "HC"]
    colors = [TECHNOLOGIES[n]["color"] for n in TECHNOLOGIES.keys()]
    
    # ── Chart 1: COP Comparison ──
    ax = axes[0, 0]
    ax.set_facecolor("#111")
    cops = []
    for n in TECHNOLOGIES.keys():
        c = TECHNOLOGIES[n]["real_cop"]
        cops.append(min(c, 35))  # Cap for display
    bars = ax.bar(short, cops, color=colors, edgecolor="white", linewidth=0.5, alpha=0.85)
    for b, v, orig in zip(bars, cops, [TECHNOLOGIES[n]["real_cop"] for n in TECHNOLOGIES.keys()]):
        label = f"{orig:.0f}" if orig != float('inf') else "∞"
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.3, label,
                ha="center", color="white", fontweight="bold", fontsize=8)
    ax.set_ylabel("COP (higher = better)", color="white", fontweight="bold")
    ax.set_title("Coefficient of Performance", color="white", fontweight="bold", fontsize=12)
    ax.tick_params(colors="white", labelsize=7)
    for s in ax.spines.values(): s.set_color("#333")
    
    # ── Chart 2: Specific Power ──
    ax = axes[0, 1]
    ax.set_facecolor("#111")
    sp_vals = [TECHNOLOGIES[n]["specific_power_kw"] for n in TECHNOLOGIES.keys()]
    bars = ax.bar(short, sp_vals, color=colors, edgecolor="white", linewidth=0.5, alpha=0.85)
    ax.axhline(y=0, color="white", linewidth=0.5)
    for b, v in zip(bars, sp_vals):
        ax.text(b.get_x()+b.get_width()/2, 
                max(b.get_height(), 0) + 0.005 if v >= 0 else b.get_height() - 0.015,
                f"{v:.3f}", ha="center", color="white", fontweight="bold", fontsize=8)
    ax.set_ylabel("kW_elec per kW_cooling", color="white", fontweight="bold")
    ax.set_title("Specific Power (lower = better)", color="white", fontweight="bold", fontsize=12)
    ax.tick_params(colors="white", labelsize=7)
    for s in ax.spines.values(): s.set_color("#333")
    
    # ── Chart 3: Water Consumption ──
    ax = axes[0, 2]
    ax.set_facecolor("#111")
    water_vals = [TECHNOLOGIES[n]["water_l_kwh"] for n in TECHNOLOGIES.keys()]
    bars = ax.bar(short, water_vals, color=colors, edgecolor="white", linewidth=0.5, alpha=0.85)
    for b, v in zip(bars, water_vals):
        label = f"{v:.1f}" if v > 0 else "0"
        ax.text(b.get_x()+b.get_width()/2, max(b.get_height(), 0) + 0.1,
                label, ha="center", color="white", fontweight="bold", fontsize=8)
    ax.set_ylabel("Liters / kWh cooling", color="white", fontweight="bold")
    ax.set_title("Freshwater Consumption", color="white", fontweight="bold", fontsize=12)
    ax.tick_params(colors="white", labelsize=7)
    for s in ax.spines.values(): s.set_color("#333")
    
    # ── Chart 4: Temperature Range ──
    ax = axes[1, 0]
    ax.set_facecolor("#111")
    for i, (name, tech) in enumerate(TECHNOLOGIES.items()):
        t_c = tech["t_cold"]
        t_h = tech["t_hot"]
        dt = t_h - t_c
        ax.barh(short[i], dt, left=t_c, color=tech["color"], edgecolor="white", 
                linewidth=0.5, alpha=0.85, height=0.6)
        ax.text(t_c + dt/2, i, f"{t_c}→{t_h}°C", ha="center", va="center",
                color="white" if dt > 10 else "black", fontsize=7, fontweight="bold")
    ax.set_xlabel("Temperature (°C)", color="white", fontweight="bold")
    ax.set_title("Operating Temperature Range", color="white", fontweight="bold", fontsize=12)
    ax.tick_params(colors="white", labelsize=7)
    for s in ax.spines.values(): s.set_color("#333")
    
    # ── Chart 5: Climate Suitability ──
    ax = axes[1, 1]
    ax.set_facecolor("#111")
    suitability = {
        "Chiller":   [4, 4, 5, 5, 5],
        "Evap":      [2, 1, 3, 4, 5],
        "Free Air":  [0, 0, 2, 4, 5],
        "Immersion": [5, 5, 5, 5, 5],
        "RDHX":      [4, 4, 5, 5, 5],
        "SWAC":      [4, 5, 4, 3, 2],
        "Absorb.":   [3, 3, 3, 3, 3],
        "District":  [5, 5, 3, 2, 1],
        "OTEC":      [4, 5, 3, 1, 0],
        "HC":        [5, 5, 4, 3, 2],
    }
    climates = ["Dubai", "Singap.", "LA", "AMS", "Lulea"]
    
    data_matrix = np.array(list(suitability.values()))
    im = ax.imshow(data_matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=5)
    ax.set_xticks(np.arange(len(climates)))
    ax.set_xticklabels(climates, fontsize=8, color="white")
    ax.set_yticks(np.arange(len(short)))
    ax.set_yticklabels(short, fontsize=7, color="white")
    for i in range(len(short)):
        for j in range(len(climates)):
            ax.text(j, i, str(data_matrix[i, j]), ha="center", va="center",
                    color="black", fontweight="bold", fontsize=9)
    ax.set_title("Climate Suitability (0-5)", color="white", fontweight="bold", fontsize=12)
    
    # ── Chart 6: Overall Score Radar ──
    ax = axes[1, 2]
    ax.set_facecolor("#111")
    
    # Score each tech 0-10 on 5 axes
    score_cats = ["Efficiency", "Water", "Versatility", "Maturity", "Heat\nRecovery"]
    scores = {
        "Chiller":   [5, 2, 10, 10, 2],
        "Evap":      [8, 0, 5,  9,  0],
        "Free Air":  [10,10, 3,  9,  2],
        "Immersion": [7, 10, 10, 6,  9],
        "SWAC":      [8, 10, 4,  7,  3],
        "HC":        [9, 10, 4,  1,  9],
    }
    
    x = np.arange(len(score_cats))
    width = 0.13
    subset_colors = ["#FF9900", "#4285F4", "#1877F2", "#00A4EF", "#26C6DA", "#00FFCC"]
    for i, (tech_name, vals) in enumerate(scores.items()):
        offset = (i - len(scores)/2 + 0.5) * width
        ax.bar(x + offset, vals, width, label=tech_name, 
               color=subset_colors[i], alpha=0.85)
    
    ax.set_ylabel("Score (0-10)", color="white", fontweight="bold")
    ax.set_title("Overall Technology Score", color="white", fontweight="bold", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(score_cats, fontsize=8, color="white")
    ax.legend(fontsize=7, facecolor="#222", edgecolor="gray", labelcolor="white", ncol=2)
    ax.set_ylim(0, 11)
    ax.tick_params(colors="white")
    for s in ax.spines.values(): s.set_color("#333")
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    path = os.path.join(output_dir, "v25_technology_showdown.png")
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="#0a0a0a")
    plt.close()
    print(f"\n  Chart saved: {path}")
    return path


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  HYDRA-COOL v25.0 — TECHNOLOGY SHOWDOWN")
    print("  10 Cooling Technologies. Head-to-Head. Pure Physics.")
    print("=" * 70)
    
    analyze_carnot()
    analyze_energy_efficiency()
    analyze_water()
    analyze_operating_range()
    analyze_waste_heat()
    head_to_head()
    
    print("  Generating Technology Showdown Dashboard...")
    generate_charts()
    
    print("\n" + "=" * 70)
    print("  SIMULATION v25.0 COMPLETE")
    print("=" * 70)
