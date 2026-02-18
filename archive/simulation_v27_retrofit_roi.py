"""
Hydra-Cool Simulation v27.0 — RETROFIT ROI
=============================================
Brownfield Business Case: Upgrading Existing Coastal Data Centers.

THE PIVOT: Stop trying to build from scratch.
Instead, prove that upgrading Google Hamina, Microsoft Dublin,
or AWS Cape Town with Hydra-Cool is a no-brainer.

Why Retrofit Wins:
  ✓ No land acquisition
  ✓ No building construction
  ✓ No grid connection
  ✓ No permitting hell (industrial modification, not new coastal build)
  ✓ Existing staff, existing infrastructure
  ✓ CAPEX drops from $614M to ~$150M

Target Facilities (Real Coastal DCs):
  - Google Hamina, Finland (seawater-cooled since 2011)
  - Microsoft Dublin, Ireland (coastal, 600MW campus)
  - AWS Cape Town, South Africa (coastal)
  - Meta Luleå, Sweden (near coast, cold climate)

Sources:
  - Google Environmental Report 2024 (Hamina PUE: 1.10)
  - Microsoft Sustainability Report 2024
  - Uptime Institute: "Cooling System Retrofit Guide" (2023)
  - ASHRAE 90.4: Energy Standard for Data Centers

Author: Obada Dallo
Copyright (c) 2024. All Rights Reserved.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

# ══════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════

FACILITY_MW     = 100
ANALYSIS_YEARS  = 10
ENERGY_PRICE    = 0.07     # $/kWh baseline
ENERGY_ESC      = 0.025    # 2.5%/yr escalation
WATER_PRICE_M3  = 2.50     # $/m³ municipal water
WATER_ESC       = 0.04     # 4%/yr escalation (scarcity premium)
CARBON_PRICE    = 50       # $/tonne
CARBON_ESC      = 0.08     # 8%/yr

HOURS_PER_YEAR  = 8760


# ══════════════════════════════════════════════════════════════
#  LEGACY SYSTEM (What They're Running Now)
# ══════════════════════════════════════════════════════════════

def model_legacy_costs():
    """
    Model the annual and 10-year costs of keeping the existing
    chiller-based cooling system.
    
    Typical 100MW facility legacy cooling:
      - Centrifugal chillers (COP ~5.5)
      - Cooling towers (evaporative)
      - CRAH units (air handlers)
      - Pumps, fans, controls
    
    Source: Uptime Institute Cooling Cost Benchmark 2024
    """
    print("\n" + "=" * 70)
    print("  LEGACY SYSTEM: What They're Paying Now")
    print("=" * 70)
    
    # Current PUE (typical well-run facility)
    legacy_pue = 1.30  # Industry average for chiller-based

    # Cooling overhead = (PUE - 1) × IT Load
    cooling_overhead_mw = FACILITY_MW * (legacy_pue - 1.0)  # 30 MW

    # Annual energy cost for cooling
    cooling_energy_kwh = cooling_overhead_mw * 1000 * HOURS_PER_YEAR

    # Water consumption (evaporative cooling towers)
    # ~5 L/kWh of cooling, based on US DOE data
    water_l_per_kwh = 5.0
    annual_water_liters = water_l_per_kwh * cooling_energy_kwh
    annual_water_m3 = annual_water_liters / 1000

    # Chiller maintenance (refrigerant, compressor overhaul, bearings)
    # Source: ASHRAE maintenance cost data
    chiller_maintenance = 3_500_000   # $/year for 100MW facility
    
    # Cooling tower maintenance (fills, fans, water treatment)
    tower_maintenance = 1_200_000
    
    # Water treatment chemicals (biocide, anti-scale, pH control)
    water_treatment = 800_000

    # 10-year total with escalation
    print(f"\n  Legacy Cooling Profile (100MW, PUE = {legacy_pue}):")
    print(f"    Cooling overhead:     {cooling_overhead_mw:.0f} MW")
    print(f"    Cooling energy:       {cooling_energy_kwh/1e6:.0f} GWh/year")
    print(f"    Water consumption:    {annual_water_m3:,.0f} m³/year ({annual_water_liters/1e9:.1f}B liters)")
    print(f"    Chiller maintenance:  ${chiller_maintenance/1e6:.1f}M/year")
    print(f"    Tower maintenance:    ${tower_maintenance/1e6:.1f}M/year")
    print(f"    Water treatment:      ${water_treatment/1e6:.1f}M/year")
    
    # Year-by-year with escalation
    print(f"\n  10-Year Legacy Cost Projection (with escalation):")
    print(f"  {'Year':>5} {'Energy $/kWh':>12} {'Energy $M':>10} {'Water $M':>10} {'Maint $M':>10} {'Carbon $M':>10} {'Total $M':>10}")
    print(f"  {'-'*68}")
    
    legacy_annual = []
    legacy_cumulative = 0
    
    for year in range(1, ANALYSIS_YEARS + 1):
        e_price = ENERGY_PRICE * (1 + ENERGY_ESC) ** (year - 1)
        w_price = WATER_PRICE_M3 * (1 + WATER_ESC) ** (year - 1)
        c_price = CARBON_PRICE * (1 + CARBON_ESC) ** (year - 1)
        
        energy_cost = cooling_energy_kwh * e_price
        water_cost = annual_water_m3 * w_price
        maint_cost = chiller_maintenance + tower_maintenance + water_treatment
        
        # Carbon tax: cooling energy × grid emission factor (0.4 t/MWh avg)
        carbon_cost = (cooling_energy_kwh / 1000) * 0.4 * c_price
        
        total = energy_cost + water_cost + maint_cost + carbon_cost
        legacy_annual.append(total)
        legacy_cumulative += total
        
        print(f"  {year:>5} ${e_price:>10.4f} ${energy_cost/1e6:>8.1f} ${water_cost/1e6:>8.1f} ${maint_cost/1e6:>8.1f} ${carbon_cost/1e6:>8.1f} ${total/1e6:>8.1f}")
    
    print(f"  {'═'*68}")
    print(f"  {'10-YEAR LEGACY TCO':<40} ${legacy_cumulative/1e6:>24.1f}")
    
    return {
        "annual_costs": legacy_annual,
        "cumulative": legacy_cumulative,
        "pue": legacy_pue,
        "cooling_mw": cooling_overhead_mw,
        "water_m3_yr": annual_water_m3,
    }


# ══════════════════════════════════════════════════════════════
#  RETROFIT INVESTMENT
# ══════════════════════════════════════════════════════════════

def model_retrofit_capex():
    """
    What does it actually cost to RETROFIT an existing coastal
    data center with Hydra-Cool?
    
    Key insight: We REUSE the building, land, grid, staff.
    We only add the thermosiphon components.
    """
    print("\n" + "=" * 70)
    print("  RETROFIT CAPEX: What We Actually Need to Build")
    print("=" * 70)
    
    retrofit_items = {
        # Subsea Infrastructure
        "Subsea intake pipe (3km, DN1200)":         35_000_000,
        "Intake screen & diffuser":                  6_000_000,
        "Outfall pipe (return, 1km)":                8_000_000,
        "HDD shore crossing":                       10_000_000,
        
        # Heat Exchange
        "Titanium plate HX (retrofit into existing)":18_000_000,
        "Bypass piping (tie-in to existing chilled water)": 5_000_000,
        "Isolation valves & controls":                3_000_000,
        
        # Pumping (assist, not primary)
        "Seawater circulation pumps (VFD, 2+1)":     4_000_000,
        "Pump house (prefab, on existing land)":      2_000_000,
        
        # Corrosion Protection
        "ICCP cathodic protection system":            3_000_000,
        "Anti-fouling chlorination system":           1_500_000,
        
        # Controls & Integration
        "SCADA integration with existing BMS":        2_000_000,
        "Instrumentation (flow, temp, pressure)":     1_200_000,
        
        # Installation
        "Pipe laying vessel (45 days)":              22_000_000,
        "Diving & ROV (tie-in, survey)":              4_000_000,
        "Mechanical installation (onshore)":          6_000_000,
        
        # Soft Costs
        "Engineering & PM (EPCM, 10%)":              13_000_000,
        "Permitting (industrial modification)":       2_000_000,
        "Insurance (construction period)":            3_000_000,
        
        # Contingency
        "Contingency (15%)":                         20_000_000,
    }
    
    total_retrofit = sum(retrofit_items.values())
    
    print(f"\n  Retrofit CAPEX Breakdown:")
    print(f"  {'Item':<52} {'Cost':>10}")
    print(f"  {'-'*63}")
    for item, cost in retrofit_items.items():
        print(f"  {item:<52} ${cost/1e6:>7.1f}M")
    print(f"  {'═'*63}")
    print(f"  {'TOTAL RETROFIT CAPEX':<52} ${total_retrofit/1e6:>7.1f}M")
    print(f"  {'Retrofit CAPEX per MW':<52} ${total_retrofit/FACILITY_MW/1e6:>7.2f}M")
    
    # Compare with greenfield
    greenfield_capex = 614_000_000  # From v26
    savings = greenfield_capex - total_retrofit
    
    print(f"\n  ╔══════════════════════════════════════════════════════════")
    print(f"  ║  RETROFIT vs GREENFIELD:")
    print(f"  ║    Greenfield CAPEX:  ${greenfield_capex/1e6:.0f}M  ($6.14M/MW)")
    print(f"  ║    Retrofit CAPEX:    ${total_retrofit/1e6:.0f}M  (${total_retrofit/FACILITY_MW/1e6:.2f}M/MW)")
    print(f"  ║    SAVINGS:           ${savings/1e6:.0f}M ({savings/greenfield_capex*100:.0f}%)")
    print(f"  ║")
    print(f"  ║  WHY SO MUCH CHEAPER:")
    print(f"  ║    ✓ No tower construction ($180M saved)")
    print(f"  ║    ✓ No land acquisition ($60M saved)")
    print(f"  ║    ✓ No grid connection ($30M saved)")
    print(f"  ║    ✓ No building ($0 — existing facility)")
    print(f"  ║    ✓ Shorter pipe (3km vs 5km — existing site is coastal)")
    print(f"  ║    ✓ Industrial permit vs full NEPA EIS")
    print(f"  ╚══════════════════════════════════════════════════════════")
    
    return {
        "total_capex": total_retrofit,
        "capex_per_mw": total_retrofit / FACILITY_MW,
        "items": retrofit_items,
    }


# ══════════════════════════════════════════════════════════════
#  POST-RETROFIT OPERATING COSTS
# ══════════════════════════════════════════════════════════════

def model_retrofit_opex():
    """
    Operating costs AFTER retrofit.
    The legacy chillers become standby/backup only.
    """
    print("\n" + "=" * 70)
    print("  POST-RETROFIT OPEX: The New Operating Cost")
    print("=" * 70)

    # Post-retrofit PUE (realistic, with pumps)
    retrofit_pue = 1.08  # Conservative estimate with pump assist
    cooling_overhead_mw = FACILITY_MW * (retrofit_pue - 1.0)  # 8 MW vs 30 MW

    cooling_energy_kwh = cooling_overhead_mw * 1000 * HOURS_PER_YEAR

    opex_items = {
        "Pump electricity (8 MW)":                    cooling_energy_kwh * ENERGY_PRICE,
        "Marine insurance (1.5% of retrofit CAPEX)":  168_700_000 * 0.015,
        "Pipe pigging & cleaning (2×/yr)":            160_000,
        "Diver/ROV inspection (2×/yr)":               70_000,
        "Anti-fouling chlorination":                   100_000,
        "HX cleaning (annual)":                        80_000,
        "CP system operation":                         45_000,
        "SCADA & monitoring":                          50_000,
        "Standby chiller maintenance (reduced)":      500_000,
        "Dedicated marine tech (2 FTE)":              300_000,
    }
    
    annual_opex = sum(opex_items.values())
    
    print(f"\n  Post-Retrofit Profile:")
    print(f"    PUE:                  {retrofit_pue}")
    print(f"    Cooling overhead:     {cooling_overhead_mw:.0f} MW (was 30 MW)")
    print(f"    Energy reduction:     {(30 - cooling_overhead_mw)/30*100:.0f}%")
    print(f"    Water consumption:    0 m³/year (seawater closed loop)")
    
    print(f"\n  Annual OPEX Breakdown:")
    print(f"  {'Item':<50} {'Cost':>10}")
    print(f"  {'-'*61}")
    for item, cost in opex_items.items():
        print(f"  {item:<50} ${cost/1000:>7.0f}K")
    print(f"  {'═'*61}")
    print(f"  {'TOTAL ANNUAL OPEX':<50} ${annual_opex/1e6:>7.2f}M")
    
    return {
        "annual_opex": annual_opex,
        "pue": retrofit_pue,
        "cooling_mw": cooling_overhead_mw,
        "items": opex_items,
    }


# ══════════════════════════════════════════════════════════════
#  PAYBACK ANALYSIS
# ══════════════════════════════════════════════════════════════

def payback_analysis(legacy, retrofit_capex, retrofit_opex):
    """
    Calculate payback period.
    Payback = Retrofit CAPEX / Annual Savings
    """
    print("\n" + "=" * 70)
    print("  PAYBACK ANALYSIS: When Does the Upgrade Pay for Itself?")
    print("=" * 70)
    
    capex = retrofit_capex["total_capex"]
    
    # Year-by-year comparison
    print(f"\n  {'Year':>5} {'Legacy $M':>10} {'Retrofit $M':>12} {'Savings $M':>12} {'Cum Savings':>12} {'Net (−CAPEX)':>13}")
    print(f"  {'-'*64}")
    
    retrofit_annual = []
    savings_annual = []
    cum_savings = 0
    net_values = []
    payback_year = None
    
    for year in range(1, ANALYSIS_YEARS + 1):
        e_price = ENERGY_PRICE * (1 + ENERGY_ESC) ** (year - 1)
        
        legacy_cost = legacy["annual_costs"][year - 1]
        
        # Retrofit OPEX scales with energy price
        base_opex = retrofit_opex["annual_opex"]
        # Scale pump energy with price escalation
        pump_energy_base = retrofit_opex["cooling_mw"] * 1000 * HOURS_PER_YEAR * ENERGY_PRICE
        pump_energy_yr = retrofit_opex["cooling_mw"] * 1000 * HOURS_PER_YEAR * e_price
        retrofit_cost = base_opex - pump_energy_base + pump_energy_yr
        
        annual_saving = legacy_cost - retrofit_cost
        cum_savings += annual_saving
        net_val = cum_savings - capex
        
        retrofit_annual.append(retrofit_cost)
        savings_annual.append(annual_saving)
        net_values.append(net_val)
        
        if payback_year is None and net_val >= 0:
            payback_year = year
        
        marker = "  ← PAYBACK" if payback_year == year else ""
        print(f"  {year:>5} ${legacy_cost/1e6:>8.1f} ${retrofit_cost/1e6:>10.1f} ${annual_saving/1e6:>10.1f} ${cum_savings/1e6:>10.1f} ${net_val/1e6:>11.1f}{marker}")
    
    # NPV of savings
    npv_savings = sum(s / (1 + 0.08)**yr for yr, s in enumerate(savings_annual, 1))
    npv_net = npv_savings - capex
    irr_approx = (npv_savings / capex - 1) / ANALYSIS_YEARS * 100
    
    print(f"\n  ╔══════════════════════════════════════════════════════════")
    print(f"  ║  PAYBACK RESULTS:")
    print(f"  ║    Retrofit CAPEX:        ${capex/1e6:.0f}M")
    print(f"  ║    Year 1 Savings:        ${savings_annual[0]/1e6:.1f}M")
    print(f"  ║    10-Year Cum Savings:   ${cum_savings/1e6:.0f}M")
    print(f"  ║    PAYBACK PERIOD:        {payback_year} years")
    print(f"  ║    NPV of Savings (8%):   ${npv_savings/1e6:.0f}M")
    print(f"  ║    NPV Net of CAPEX:      ${npv_net/1e6:.0f}M")
    print(f"  ║")
    if payback_year and payback_year <= 5:
        print(f"  ║    ✅ PAYBACK IN {payback_year} YEARS — Strongly Investable")
    elif payback_year:
        print(f"  ║    ⚠️ PAYBACK IN {payback_year} YEARS — Marginally Investable")
    else:
        print(f"  ║    ❌ NO PAYBACK WITHIN 10 YEARS")
    print(f"  ╚══════════════════════════════════════════════════════════")
    
    return {
        "payback_year": payback_year,
        "savings_annual": savings_annual,
        "net_values": net_values,
        "cum_savings": cum_savings,
        "npv_savings": npv_savings,
        "npv_net": npv_net,
        "legacy_annual": legacy["annual_costs"],
        "retrofit_annual": retrofit_annual,
    }


# ══════════════════════════════════════════════════════════════
#  COST OF INACTION
# ══════════════════════════════════════════════════════════════

def cost_of_inaction(payback_data, retrofit_capex):
    """
    Frame the decision: what does it cost to do NOTHING?
    Every year of delay forfeits the annual savings.
    """
    print("\n" + "=" * 70)
    print("  COST OF INACTION: What Doing Nothing Costs")
    print("=" * 70)
    
    annual_savings_avg = np.mean(payback_data["savings_annual"])
    
    print(f"\n  Average annual savings from retrofit: ${annual_savings_avg/1e6:.1f}M")
    print(f"\n  Every year you DELAY the retrofit decision:")
    print(f"    Year 1 delay:   ${payback_data['savings_annual'][0]/1e6:.1f}M wasted")
    print(f"    Year 2 delay:   ${sum(payback_data['savings_annual'][:2])/1e6:.1f}M wasted (cumulative)")
    print(f"    Year 3 delay:   ${sum(payback_data['savings_annual'][:3])/1e6:.1f}M wasted")
    print(f"    Year 5 delay:   ${sum(payback_data['savings_annual'][:5])/1e6:.1f}M wasted")
    
    # Water wasted
    annual_water = 131_400_000 * 5.0 / 1000  # m³ from legacy model
    print(f"\n  Water wasted per year of delay: {annual_water:,.0f} m³")
    print(f"    = {annual_water * 1000 / 1e9:.1f} billion liters of freshwater")
    
    # Carbon wasted
    annual_carbon = 131_400_000 / 1000 * 0.4  # MWh × emission factor
    print(f"  CO₂ emitted per year of delay: {annual_carbon:,.0f} tonnes")
    
    print(f"\n  ╔══════════════════════════════════════════════════════════")
    print(f"  ║  THE COST OF INACTION (10 years of doing nothing):")
    print(f"  ║    Money wasted:   ${payback_data['cum_savings']/1e6:.0f}M in excess cooling costs")
    print(f"  ║    Water wasted:   {annual_water * 10 / 1e6:.1f}M m³ of freshwater")
    print(f"  ║    CO₂ emitted:    {annual_carbon * 10 / 1000:.0f}K tonnes of CO₂")
    print(f"  ║")
    print(f"  ║    Retrofit CAPEX: ${retrofit_capex['total_capex']/1e6:.0f}M (one-time)")
    print(f"  ║    ROI:            {payback_data['cum_savings']/retrofit_capex['total_capex']*100:.0f}% over 10 years")
    print(f"  ║")
    print(f"  ║    NOT upgrading is the more expensive option.")
    print(f"  ╚══════════════════════════════════════════════════════════")


# ══════════════════════════════════════════════════════════════
#  MULTI-SITE ANALYSIS
# ══════════════════════════════════════════════════════════════

def multi_site_analysis():
    """Analyze retrofit potential across real coastal data centers."""
    print("\n" + "=" * 70)
    print("  MULTI-SITE: Real Coastal DC Retrofit Candidates")
    print("=" * 70)
    
    sites = [
        {
            "name": "Google Hamina",
            "country": "Finland",
            "capacity_mw": 90,
            "current_pue": 1.10,
            "cooling": "Seawater (already!)",
            "deep_water_km": 2.5,
            "retrofit_note": "Already uses seawater — easiest retrofit",
        },
        {
            "name": "Microsoft Dublin",
            "country": "Ireland",
            "capacity_mw": 150,
            "current_pue": 1.20,
            "cooling": "Chillers + Free Air",
            "deep_water_km": 4.0,
            "retrofit_note": "Irish Sea access, significant savings potential",
        },
        {
            "name": "AWS Cape Town",
            "country": "South Africa",
            "capacity_mw": 60,
            "current_pue": 1.25,
            "cooling": "Chillers",
            "deep_water_km": 3.0,
            "retrofit_note": "Benguela Current = very cold deep water",
        },
        {
            "name": "Equinix SG3",
            "country": "Singapore",
            "capacity_mw": 25,
            "current_pue": 1.35,
            "cooling": "Chillers (tropical)",
            "deep_water_km": 5.0,
            "retrofit_note": "Hot climate = highest savings potential",
        },
        {
            "name": "Meta Luleå",
            "country": "Sweden",
            "capacity_mw": 120,
            "current_pue": 1.05,
            "cooling": "Free Air + Hydro",
            "deep_water_km": 8.0,
            "retrofit_note": "Already very efficient — minimal savings",
        },
    ]
    
    print(f"\n  {'Site':<20} {'MW':>5} {'PUE':>5} {'ΔPW':>7} {'Deep km':>8} {'Annual Save':>12} {'Payback':>8}")
    print(f"  {'-'*70}")
    
    for site in sites:
        mw = site["capacity_mw"]
        pue_old = site["current_pue"]
        pue_new = max(1.08, pue_old - 0.15)  # Realistic improvement
        delta_mw = mw * (pue_old - pue_new)
        annual_save_mwh = delta_mw * 1000 * HOURS_PER_YEAR
        annual_save_usd = annual_save_mwh * ENERGY_PRICE
        
        # Retrofit CAPEX scales with capacity and pipe distance
        base_capex = 168_700_000
        scale_factor = mw / 100
        dist_factor = site["deep_water_km"] / 3.0
        retrofit_capex = base_capex * scale_factor * (0.5 + 0.5 * dist_factor)
        
        payback = retrofit_capex / annual_save_usd if annual_save_usd > 0 else float('inf')
        
        site["annual_save"] = annual_save_usd
        site["retrofit_capex"] = retrofit_capex
        site["payback"] = payback
        site["pue_new"] = pue_new
        
        pb_str = f"{payback:.1f}yr" if payback < 100 else "N/A"
        print(f"  {site['name']:<20} {mw:>5} {pue_old:>5.2f} {delta_mw:>5.1f}MW {site['deep_water_km']:>6.1f}km ${annual_save_usd/1e6:>9.1f}M {pb_str:>8}")
    
    return sites


# ══════════════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════════════

def generate_charts(payback_data, retrofit_capex, output_dir="assets"):
    """Generate the retrofit payback chart."""
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(1, 3, figsize=(20, 7))
    fig.patch.set_facecolor("#0a0a0a")
    fig.suptitle("RETROFIT ROI: The Upgrade Pays for Itself",
                 fontsize=18, fontweight="bold", color="#00FFCC", y=0.98)
    
    years = np.arange(1, ANALYSIS_YEARS + 1)
    
    # ── Chart 1: Legacy vs Retrofit Annual Cost ──
    ax = axes[0]
    ax.set_facecolor("#111")
    ax.plot(years, [c/1e6 for c in payback_data["legacy_annual"]], 
            color="#FF4444", linewidth=2.5, marker="o", markersize=5, label="Legacy (Keep)")
    ax.plot(years, [c/1e6 for c in payback_data["retrofit_annual"]], 
            color="#00FFCC", linewidth=2.5, marker="s", markersize=5, label="Retrofit (Upgrade)")
    ax.fill_between(years, 
                    [c/1e6 for c in payback_data["retrofit_annual"]],
                    [c/1e6 for c in payback_data["legacy_annual"]],
                    alpha=0.15, color="#00FFCC", label="Annual Savings")
    ax.set_xlabel("Year", color="white", fontweight="bold")
    ax.set_ylabel("Annual Operating Cost ($M)", color="white", fontweight="bold")
    ax.set_title("Annual Cost: Keep vs Upgrade", color="white", fontweight="bold", fontsize=12)
    ax.legend(fontsize=9, facecolor="#222", edgecolor="gray", labelcolor="white")
    ax.tick_params(colors="white")
    for s in ax.spines.values(): s.set_color("#333")
    
    # ── Chart 2: Cumulative Savings & Payback Crossover ──
    ax = axes[1]
    ax.set_facecolor("#111")
    
    cum_savings = np.cumsum(payback_data["savings_annual"]) / 1e6
    capex_line = np.full(len(years), retrofit_capex["total_capex"] / 1e6)
    
    ax.plot(years, cum_savings, color="#00FFCC", linewidth=2.5, marker="o", 
            markersize=5, label="Cumulative Savings")
    ax.axhline(y=retrofit_capex["total_capex"]/1e6, color="#FF4444", 
               linewidth=2, linestyle="--", label=f"Retrofit CAPEX (${retrofit_capex['total_capex']/1e6:.0f}M)")
    
    # Mark payback point
    if payback_data["payback_year"]:
        py = payback_data["payback_year"]
        ax.axvline(x=py, color="#FFAA00", linewidth=2, linestyle="-.")
        ax.annotate(f'PAYBACK\nYear {py}', xy=(py, retrofit_capex["total_capex"]/1e6),
                    xytext=(py + 1, retrofit_capex["total_capex"]/1e6 * 0.6),
                    color="#FFAA00", fontweight="bold", fontsize=12,
                    arrowprops=dict(arrowstyle="->", color="#FFAA00", lw=2))
    
    ax.fill_between(years, 0, cum_savings, alpha=0.1, color="#00FFCC")
    ax.set_xlabel("Year", color="white", fontweight="bold")
    ax.set_ylabel("Cumulative Savings ($M)", color="white", fontweight="bold")
    ax.set_title("Payback: When Savings Exceed Investment", color="white", fontweight="bold", fontsize=12)
    ax.legend(fontsize=9, facecolor="#222", edgecolor="gray", labelcolor="white")
    ax.tick_params(colors="white")
    for s in ax.spines.values(): s.set_color("#333")
    
    # ── Chart 3: Net Value (Savings − CAPEX) ──
    ax = axes[2]
    ax.set_facecolor("#111")
    net_vals = [n/1e6 for n in payback_data["net_values"]]
    colors_bar = ["#FF4444" if n < 0 else "#00FFCC" for n in net_vals]
    ax.bar(years, net_vals, color=colors_bar, edgecolor="white", linewidth=0.5, alpha=0.85)
    ax.axhline(y=0, color="#FFAA00", linewidth=1, linestyle="--")
    for yr, nv in zip(years, net_vals):
        ax.text(yr, nv + (5 if nv >= 0 else -8), f"${nv:.0f}M", 
                ha="center", color="white", fontweight="bold", fontsize=8)
    ax.set_xlabel("Year", color="white", fontweight="bold")
    ax.set_ylabel("Net Value ($M)", color="white", fontweight="bold")
    ax.set_title("Net ROI: Cumulative Savings − CAPEX", color="white", fontweight="bold", fontsize=12)
    ax.tick_params(colors="white")
    for s in ax.spines.values(): s.set_color("#333")
    
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    path = os.path.join(output_dir, "v27_retrofit_payback.png")
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="#0a0a0a")
    plt.close()
    print(f"\n  ✓ Chart saved: {path}")
    return path


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  HYDRA-COOL v27.0 — RETROFIT ROI")
    print("  'Don't build new. Upgrade what exists.'")
    print("=" * 70)
    
    legacy = model_legacy_costs()
    retrofit_capex = model_retrofit_capex()
    retrofit_opex = model_retrofit_opex()
    payback = payback_analysis(legacy, retrofit_capex, retrofit_opex)
    cost_of_inaction(payback, retrofit_capex)
    multi_site_analysis()
    
    print("\n  Generating Retrofit ROI Dashboard...")
    generate_charts(payback, retrofit_capex)
    
    print("\n" + "=" * 70)
    print("  SIMULATION v27.0 COMPLETE")
    print("=" * 70)
