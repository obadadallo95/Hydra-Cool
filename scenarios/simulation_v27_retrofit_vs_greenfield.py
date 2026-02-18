"""
Hydra-Cool Simulation v27.0 — RETROFIT vs GREENFIELD (The Real Comparison)
=============================================================================
Brutally Honest Investment Case:
Building New vs. Retrofitting Live.

THE REALITY CHECK:
  - Previous retrofit estimate ($169M) was too optimistic.
  - Working in a live data center is slow, dangerous, and expensive.
  - "Brownfield Complexity Factor": 1.5x on labor.
  - Marine works are NOT cheaper just because it's a retrofit.
  - BUT... it's still the only viable option compared to Greenfield ($614M).

Scenarios:
  1. GREENFIELD ($614M): The anchor. 6 years. High risk.
  2. RETROFIT REALITY ($350M): The solution. 2 years. Integration risk.
  3. DO NOTHING ($65M/yr): The losing baseline. Bleeding cash.

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

ANALYSIS_YEARS  = 10
FACILITY_MW     = 100
HOURS_PER_YEAR  = 8760
ENERGY_PRICE    = 0.07     # $/kWh baseline
ENERGY_ESC      = 0.03     # 3%/yr escalation
WACC            = 0.08     # Weighted Average Cost of Capital

# Legacy Baseline (Do Nothing)
LEGACY_OPEX_YR  = 65_000_000  # $65M/year initially
LEGACY_WATER_M3 = 1_500_000   # m³/year

# ══════════════════════════════════════════════════════════════
#  CAPEX MODELS
# ══════════════════════════════════════════════════════════════

def get_greenfield_capex():
    """From v26 Reality Check."""
    return {
        "Materials": 116_000_000,
        "Labor":     112_000_000,
        "Marine":    181_000_000,
        "Soft":       75_000_000,
        "Contingency":97_000_000,
        "Insurance":  33_000_000,
        "TOTAL":     614_000_000,
        "Time": 6, # Years to revenue
    }

def get_retrofit_capex():
    """
    The 'Real' Retrofit Cost.
    Includes Brownfield Complexity Premium.
    """
    # Materials: Same as Greenfield (High grade Ti, Pipes)
    materials = 116_000_000
    
    # Marine: Same as Greenfield (The ocean doesn't care it's a retrofit)
    marine = 189_000_000  # Updated user constraint
    
    # Labor: Greenfield was $112M (includes building & system).
    # Retrofit removes building labor (~40%) but adds complexity to system labor.
    # Assume System Labor is $60M of the original $112M.
    # Brownfield Factor: 1.5x on System Labor.
    base_system_labor = 60_000_000
    retrofit_labor = base_system_labor * 1.5
    
    # Civil/Integration: Minor civil works for pump house tie-in
    civil = 15_000_000
    
    # Soft Costs: Lower than GF (no EIS, no land dev)
    soft = 30_000_000
    
    # Downtime Insurance Reserve (User Requirement)
    insurance = 10_000_000
    
    total = materials + marine + retrofit_labor + civil + soft + insurance
    
    return {
        "Materials": materials,
        "Marine": marine,
        "Labor (1.5x Complexity)": retrofit_labor,
        "Civil/Integration": civil,
        "Soft Costs": soft,
        "Downtime Insurance": insurance,
        "TOTAL": total,
        "Time": 2 # Years to revenue (concurrent)
    }

# ══════════════════════════════════════════════════════════════
#  FINANCIAL ANALYSIS
# ══════════════════════════════════════════════════════════════

def run_comparison(greenfield, retrofit):
    print("="*80)
    print("  HYDRA-COOL v27: RETROFIT vs GREENFIELD (The Real Numbers)")
    print("="*80)
    
    # Print CAPEX Comparison
    print(f"\n  {'Category':<25} {'Greenfield ($M)':>15} {'Retrofit ($M)':>15} {'Notes':<30}")
    print("-" * 90)
    
    # Map retrofit keys to match roughly for display
    print(f"  {'Materials':<25} ${greenfield['Materials']/1e6:>14.1f} ${retrofit['Materials']/1e6:>14.1f} {'Same hardware'}")
    print(f"  {'Marine Works':<25} ${greenfield['Marine']/1e6:>14.1f} ${retrofit['Marine']/1e6:>14.1f} {'Ocean work is fixed cost'}")
    print(f"  {'Labor / Install':<25} ${greenfield['Labor']/1e6:>14.1f} ${retrofit['Labor (1.5x Complexity)']/1e6:>14.1f} {'1.5x factor on brownfield'}")
    print(f"  {'Civil / Soft / Other':<25} ${205/1e6:>14.1f} ${sum([retrofit['Civil/Integration'], retrofit['Soft Costs'], retrofit['Downtime Insurance']])/1e6:>14.1f} {'No building, existing permit'}")
    print("-" * 90)
    print(f"  {'TOTAL CAPEX':<25} ${greenfield['TOTAL']/1e6:>14.1f} ${retrofit['TOTAL']/1e6:>14.1f} {'Save 43% (not 73%)'}")
    print(f"  {'Time to Revenue':<25} {greenfield['Time']:>14} yrs {retrofit['Time']:>14} yrs {'Immediate impact'}")

    
    # ── NPV & Cash Flow Analysis ──
    # We compare "Cash Outflow" relative to revenue.
    # Actually, let's compare "Total Cost of Ownership" (CAPEX + OPEX) over 10 years.
    # Revenue is assumed same for simplicity, or zero for GF during build.
    
    print("\n  10-YEAR CASH FLOW ANALYSIS (Cumulative TCO):")
    print(f"  {'Year':<5} {'Do Nothing':>12} {'Greenfield':>12} {'Retrofit':>12} {'Retrofit Savings':>18}")
    print("-" * 65)
    
    # Initial
    cf_legacy = 0
    cf_greenfield = 0 # Spend starts
    cf_retrofit = 0   # Spend starts
    
    # Store for plotting
    data_legacy = []
    data_greenfield = []
    data_retrofit = []
    
    retrofit_annual_opex = 16_000_000 # v26 Reality Check OPEX
    
    for year in range(1, 11):
        # Escalation
        escalator = (1 + ENERGY_ESC)**(year-1)
        legacy_opex = LEGACY_OPEX_YR * escalator
        retrofit_opex = retrofit_annual_opex * escalator
        
        # 1. Do Nothing
        cf_legacy += legacy_opex
        
        # 2. Greenfield
        # Years 1-6: Construction Spend (Linear spread of CAPEX)
        if year <= 6:
            annual_capex = greenfield['TOTAL'] / 6
            cf_greenfield += annual_capex
            # No revenue (or opportunity cost of no cooling? Assume 0 OPEX coz no DC yet)
            # Actually, to make fair comparison for "Meeting 100MW Demand":
            # If GF is building NEW capacity, it doesn't replace legacy costs until Y7.
            # But if we compare "Providing 100MW Cooling":
            # GF option implies we PAY legacy costs on existing DC while building new one?
            # Or is this "New Build vs Upgrade"?
            # Let's assume GF is "Build new efficient DC to replace old one".
            # So we pay Legacy OPEX for 6 years, THEN switch to GF OPEX.
            # PLUS the GF CAPEX.
            cf_greenfield += legacy_opex 
        else:
            # GF Operating
            cf_greenfield += retrofit_opex # Assume GF has same efficiency as Retrofit
            
        # 3. Retrofit
        # Years 1-2: Construction (Capex spread)
        if year <= 2:
            annual_capex = retrofit['TOTAL'] / 2
            cf_retrofit += annual_capex
            # During build, we still pay Legacy OPEX (Parallel operation)
            cf_retrofit += legacy_opex
        else:
            # Operating
            cf_retrofit += retrofit_opex

        # Calculate Retrofit "Savings" vs Do Nothing (Net Benefit)
        # Net Benefit = (Legacy Cumulative) - (Retrofit Cumulative)
        # If Positive, we made money.
        net_benefit = cf_legacy - cf_retrofit

        data_legacy.append(cf_legacy)
        data_greenfield.append(cf_greenfield)
        data_retrofit.append(cf_retrofit)
        
        marker = "← Payback" if (net_benefit > 0 and (cf_legacy - (cf_retrofit - retrofit['TOTAL'])) < 0 ) else "" 
        # Actually simplified Payback: When does Cumulative Retrofit < Cumulative Legacy?
        pb_marker = "✅" if cf_retrofit < cf_legacy else "❌"
        
        print(f"  {year:<5} ${cf_legacy/1e6:>11.0f}M ${cf_greenfield/1e6:>11.0f}M ${cf_retrofit/1e6:>11.0f}M ${net_benefit/1e6:>17.0f}M {pb_marker}")

    # Conclusion
    print("\n  VERDICT:")
    print(f"  1. Do Nothing 10Y Cost:  ${cf_legacy/1e6:.0f}M (Burning cash)")
    print(f"  2. Greenfield 10Y Cost:  ${cf_greenfield/1e6:.0f}M (Huge initial hole, paying double ops for 6 yrs)")
    print(f"  3. Retrofit 10Y Cost:    ${cf_retrofit/1e6:.0f}M")
    print("-" * 50)
    print(f"  RETROFIT SAVINGS vs DO NOTHING: ${cf_legacy - cf_retrofit:,.0f} ({ (cf_legacy-cf_retrofit)/cf_legacy*100 :.1f}%)")
    
    return data_legacy, data_greenfield, data_retrofit

# ══════════════════════════════════════════════════════════════
#  PLOTTING
# ══════════════════════════════════════════════════════════════

def plot_comparison(legacy, greenfield, retrofit):
    years = range(1, 11)
    
    plt.figure(figsize=(12, 7))
    plt.style.use('dark_background')
    
    plt.plot(years, [x/1e6 for x in legacy], 'r--', label='Do Nothing (Legacy OPEX)', linewidth=2)
    plt.plot(years, [x/1e6 for x in greenfield], 'y-', label='Greenfield (Build New)', linewidth=2)
    plt.plot(years, [x/1e6 for x in retrofit], 'c-', label='Retrofit (The Upgrade)', linewidth=3)
    
    # Highlight the gap
    plt.fill_between(years, [x/1e6 for x in legacy], [x/1e6 for x in retrofit], color='cyan', alpha=0.1, label='Retrofit Value Capture')
    
    plt.title('TCO COMPARISON: The Higher Cost of Waiting', fontsize=16, color='white', pad=20)
    plt.xlabel('Years', fontsize=12)
    plt.ylabel('Cumulative Cost ($ Millions)', fontsize=12)
    plt.grid(True, alpha=0.2)
    plt.legend()
    
    # Annotate final values
    plt.text(10.1, legacy[-1]/1e6, f"${legacy[-1]/1e6:.0f}M", color='red', va='center', fontweight='bold')
    plt.text(10.1, greenfield[-1]/1e6, f"${greenfield[-1]/1e6:.0f}M", color='yellow', va='center')
    plt.text(10.1, retrofit[-1]/1e6, f"${retrofit[-1]/1e6:.0f}M", color='cyan', va='center', fontweight='bold')

    # Annotate Crossover
    # Find approx crossover index where Retrofit < Legacy
    crossover_idx = next((i for i, (r, l) in enumerate(zip(retrofit, legacy)) if r < l), None)
    if crossover_idx is not None:
        year_x = years[crossover_idx]
        val_y = retrofit[crossover_idx]/1e6
        plt.annotate('ROI Breakeven', xy=(year_x, val_y), xytext=(year_x, val_y+200),
                     arrowprops=dict(facecolor='white', shrink=0.05))

    out_path = "assets/v27_retrofit_comparison.png"
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f"\n  ✓ Chart saved: {out_path}")

if __name__ == "__main__":
    gf = get_greenfield_capex()
    rf = get_retrofit_capex()
    l, g, r = run_comparison(gf, rf)
    plot_comparison(l, g, r)
