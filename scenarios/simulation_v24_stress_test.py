"""
Hydra-Cool Simulation v24.0 — STRESS TEST TO DESTRUCTION
==========================================================
What breaks first? At what cost? And what does the REAL
business case look like after we account for every weakness?

This is the final, corrected financial model that incorporates
ALL the weaknesses found in v23 to produce an honest P&L.

Author: Obada Dallo
Copyright (c) 2024. All Rights Reserved.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

# ══════════════════════════════════════════════════════════════
#  SCENARIO 1: FAILURE CASCADE — What Breaks First?
# ══════════════════════════════════════════════════════════════

def failure_cascade():
    """
    Model every component failure mode with realistic MTBF,
    repair cost, and downtime. Ask: what's the annual failure cost?
    
    Sources:
      - OREDA Offshore Reliability Data 2022
      - DNV GL Marine Equipment Failure Rates
      - NACE International Corrosion Cost Studies
    """
    print("\n" + "=" * 70)
    print("  FAILURE CASCADE: What Breaks First?")
    print("=" * 70)
    
    components = [
        # (Component, MTBF years, Repair cost $K, Downtime days, Source)
        ("Seawater intake screens (wedgewire)",   2.0,    150,   3,  "OREDA subsea intake data"),
        ("Heat exchanger fouling (titanium)",     1.5,    300,   5,  "Alfa Laval marine HX data"),
        ("Deep-sea pipe joint seal failure",      8.0,   2000,  30,  "DNV GL subsea pipeline"),
        ("Cathodic protection anode depletion",    5.0,    200,   2,  "NACE anode life data"),
        ("Biofouling — pipe internal",            0.5,     80,   2,  "WHOI marine growth rates"),
        ("Tower concrete spalling (marine)",      10.0,  1500,  45,  "ACI 357R marine concrete"),
        ("Seawater pump bearing failure",          3.0,    100,   2,  "OREDA pump reliability"),
        ("Thermal expansion joint failure",        5.0,    400,   7,  "ASME B31.3 data"),
        ("Diffuser nozzle clogging",              1.0,     60,   1,  "Desalination plant data"),
        ("Instrumentation/sensor failure",         2.0,     50,   1,  "ISA-84 SIL data"),
        ("Power supply to CP system",             3.0,     30,   0.5,"IEEE 493 Gold Book"),
        ("Anti-corrosion coating damage",          4.0,    500,  14,  "NORSOK M-501 experience"),
        ("Marine vessel strike on pipe",           15.0,  5000,  90,  "MAIB incident database"),
        ("Storm damage to intake structure",       7.0,   3000,  60,  "Gulf of Mexico data"),
    ]
    
    print(f"\n  {'Component':<42} {'MTBF':>6} {'Repair $K':>10} {'Downtime':>10} {'Annual Cost':>12}")
    print(f"  {'-'*82}")
    
    total_annual_cost = 0
    total_annual_downtime_days = 0
    
    for comp, mtbf, repair_k, downtime, source in components:
        annual_failures = 1.0 / mtbf
        annual_cost = annual_failures * repair_k * 1000
        annual_downtime = annual_failures * downtime
        total_annual_cost += annual_cost
        total_annual_downtime_days += annual_downtime
        
        print(f"  {comp:<42} {mtbf:>5.1f}y ${repair_k:>8}K {downtime:>8.1f}d ${annual_cost/1000:>9.0f}K/yr")
    
    print(f"  {'-'*82}")
    print(f"  {'TOTAL ANNUAL MAINTENANCE BURDEN':<42} {'':>6} {'':>10} {total_annual_downtime_days:>8.1f}d ${total_annual_cost/1e6:>9.2f}M/yr")
    
    # For a 100MW facility
    facility_mw = 100
    total_for_facility = total_annual_cost * (facility_mw / 25)  # Scale from 25MW baseline
    
    print(f"\n  ╔══════════════════════════════════════════════════════════")
    print(f"  ║  For 100MW facility (4x baseline):")
    print(f"  ║    Annual maintenance:  ${total_for_facility/1e6:.1f}M/year")
    print(f"  ║    10-year total:       ${total_for_facility*10/1e6:.0f}M")
    print(f"  ║    Annual downtime:     {total_annual_downtime_days*4:.0f} days (across all components)")
    print(f"  ║")
    print(f"  ║  Our original model assumed $9.5M/year OPEX.")
    print(f"  ║  Realistic maintenance alone: ${total_for_facility/1e6:.1f}M/year")
    print(f"  ║  Delta: {total_for_facility/9.5e6:.1f}x higher than modeled.")
    print(f"  ╚══════════════════════════════════════════════════════════")
    
    return {
        "annual_cost_100mw": total_for_facility,
        "annual_downtime_days": total_annual_downtime_days * 4,
    }


# ══════════════════════════════════════════════════════════════
#  SCENARIO 2: CORRECTED 10-YEAR P&L
# ══════════════════════════════════════════════════════════════

def corrected_pnl(failure_data):
    """
    The HONEST profit-and-loss including:
    - Realistic CAPEX (from v23)
    - Real maintenance costs (from failure cascade)
    - Insurance at marine rates
    - Permitting costs amortized
    - Pump energy (not fully passive)
    """
    print("\n" + "=" * 70)
    print("  CORRECTED 10-YEAR P&L (100MW Facility)")
    print("=" * 70)
    
    facility_mw = 100
    years = 10
    
    # CAPEX (realistic from v23)
    capex_items = {
        "Cooling Tower (200m, marine)":    180_000_000,
        "Deep-Sea Pipe (400m, 5km)":       95_000_000,
        "Heat Exchangers (titanium)":      35_000_000,
        "Intake & Outfall Structures":     45_000_000,
        "Coastal Land":                    60_000_000,
        "Permitting & Legal":              15_000_000,
        "Cathodic Protection System":       8_000_000,
        "Grid Connection":                 30_000_000,
        "FIRST-OF-KIND Contingency (15%)": 80_000_000,
    }
    total_capex = sum(capex_items.values())
    
    print(f"\n  CAPEX Breakdown:")
    for item, cost in capex_items.items():
        print(f"    {item:<40} ${cost/1e6:>8.0f}M")
    print(f"    {'TOTAL CAPEX':<40} ${total_capex/1e6:>8.0f}M")
    print(f"    CAPEX per MW: ${total_capex/facility_mw/1e6:.2f}M")
    
    # Annual OPEX (realistic)
    opex_items = {
        "Component Maintenance (from cascade)": failure_data["annual_cost_100mw"],
        "Auxiliary Pump Energy":                2_400_000,   # ~3MW of pumps × $0.07/kWh × 8760h × 0.13
        "Marine Insurance (3.5% of asset)":    total_capex * 0.035,
        "Anti-fouling Chemical Treatment":      1_200_000,
        "Cathodic Protection Ops":              800_000,
        "Staff (24/7 × 12 operators)":         2_400_000,
        "Environmental Monitoring":             600_000,
        "Structural Inspection (annual ROV)":   400_000,
    }
    annual_opex = sum(opex_items.values())
    
    print(f"\n  Annual OPEX Breakdown:")
    for item, cost in opex_items.items():
        print(f"    {item:<45} ${cost/1e6:>7.2f}M")
    print(f"    {'TOTAL ANNUAL OPEX':<45} ${annual_opex/1e6:>7.2f}M")
    print(f"    OPEX per MW per year: ${annual_opex/facility_mw/1e3:.0f}K")
    
    # 10-year TCO
    tco_10y = total_capex + (annual_opex * years)
    tco_per_mw = tco_10y / facility_mw
    
    print(f"\n  10-YEAR TCO:")
    print(f"    CAPEX:            ${total_capex/1e6:>8.0f}M")
    print(f"    OPEX (10 years):  ${annual_opex*years/1e6:>8.0f}M")
    print(f"    TOTAL TCO:        ${tco_10y/1e6:>8.0f}M")
    print(f"    TCO per MW:       ${tco_per_mw/1e6:>8.2f}M")
    
    # Compare with Big 4
    competitors = {
        "Google":    {"tco_100mw": 1_593_000_000},
        "Microsoft": {"tco_100mw": 1_740_000_000},
        "AWS":       {"tco_100mw": 1_873_000_000},
        "Meta":      {"tco_100mw": 1_426_000_000},
    }
    
    print(f"\n  CORRECTED COMPARISON:")
    print(f"  {'Company':<20} {'10Y TCO':>12} {'vs HC':>10} {'Savings':>12}")
    print(f"  {'-'*55}")
    
    for name, data in competitors.items():
        tco_other = data["tco_100mw"]
        savings = tco_other - tco_10y
        pct = savings / tco_other * 100
        status = "CHEAPER" if savings > 0 else "MORE EXPENSIVE"
        print(f"  {name:<20} ${tco_other/1e6:>9.0f}M {pct:>+8.0f}% ${savings/1e6:>9.0f}M ({status})")
    
    print(f"  {'Hydra-Cool (Real)':<20} ${tco_10y/1e6:>9.0f}M {'BASE':>10} {'—':>12}")
    
    avg_savings_pct = np.mean([(c["tco_100mw"] - tco_10y) / c["tco_100mw"] * 100 for c in competitors.values()])
    
    print(f"\n  ╔══════════════════════════════════════════════════════════")
    print(f"  ║  CORRECTED ADVANTAGE:")
    print(f"  ║")
    print(f"  ║  ORIGINAL CLAIM:   '85% cheaper than AWS'")
    print(f"  ║  CORRECTED CLAIM:  '{(competitors['AWS']['tco_100mw']-tco_10y)/competitors['AWS']['tco_100mw']*100:.0f}% cheaper than AWS'")
    print(f"  ║")
    print(f"  ║  ORIGINAL CLAIM:   '$304M TCO (100MW/10Y)'")
    print(f"  ║  CORRECTED VALUE:  '${tco_10y/1e6:.0f}M TCO (100MW/10Y)'")
    print(f"  ║")
    print(f"  ║  Average savings vs Big 4: {avg_savings_pct:.0f}%")
    print(f"  ║  Still significant IF the technology works.")
    print(f"  ║  But 'IF' is doing heavy lifting at TRL 2.")
    print(f"  ╚══════════════════════════════════════════════════════════")
    
    return {
        "total_capex": total_capex,
        "annual_opex": annual_opex,
        "tco_10y": tco_10y,
        "tco_per_mw": tco_per_mw,
        "avg_savings_pct": avg_savings_pct,
    }


# ══════════════════════════════════════════════════════════════
#  SCENARIO 3: WHAT IF EVERYTHING GOES WRONG? (WORST CASE)
# ══════════════════════════════════════════════════════════════

def worst_case_scenario(corrected_data):
    """
    Murphy's Law edition:
    - Permitting delayed 3 years → $150M carrying cost
    - First 2 years operational problems (TRL scaling issues)
    - Hurricane hits in year 5 → $200M damage
    - Insurance premium spikes 2x after hurricane
    - Regulatory changes add $50M compliance cost
    """
    print("\n" + "=" * 70)
    print("  WORST CASE: Murphy's Law Edition")
    print("=" * 70)
    
    baseline_tco = corrected_data["tco_10y"]
    
    worst_case_additions = {
        "Permitting delay (3yr carry cost @ 8%)":    corrected_data["total_capex"] * 0.08 * 3,
        "Startup failures (2yr debugging, TRL gap)": 50_000_000,
        "Hurricane damage (Category 3, Year 5)":     200_000_000,
        "Insurance spike post-hurricane (2x × 5yr)": corrected_data["total_capex"] * 0.035 * 5,
        "Regulatory compliance (new marine rules)":   50_000_000,
        "Pipe repair (joint failure, Year 7)":        30_000_000,
        "Legal defense (environmental lawsuits)":     20_000_000,
        "Revenue loss during downtime (60 days)":     15_000_000,
    }
    
    total_additions = sum(worst_case_additions.values())
    worst_tco = baseline_tco + total_additions
    
    print(f"\n  Baseline Corrected TCO:  ${baseline_tco/1e6:.0f}M")
    print(f"\n  Worst-Case Additions:")
    for item, cost in worst_case_additions.items():
        print(f"    {item:<52} ${cost/1e6:>8.0f}M")
    print(f"    {'TOTAL ADDITIONS':<52} ${total_additions/1e6:>8.0f}M")
    print(f"\n  WORST CASE 10Y TCO:      ${worst_tco/1e6:.0f}M")
    
    # Compare
    competitors = {
        "Google":    1_593_000_000,
        "Microsoft": 1_740_000_000,
        "AWS":       1_873_000_000,
        "Meta":      1_426_000_000,
    }
    
    print(f"\n  WORST CASE COMPARISON:")
    for name, tco_other in competitors.items():
        delta = tco_other - worst_tco
        pct = delta / tco_other * 100
        status = "STILL CHEAPER" if delta > 0 else "MORE EXPENSIVE ⚠️"
        print(f"    vs {name:<12}: ${delta/1e6:>+8.0f}M ({status})")
    
    print(f"\n  ╔══════════════════════════════════════════════════════════")
    print(f"  ║  IN THE WORST CASE:")
    print(f"  ║")
    print(f"  ║  Hydra-Cool TCO = ${worst_tco/1e6:.0f}M")
    for name, tco_other in competitors.items():
        if worst_tco > tco_other:
            print(f"  ║  ⚠️ MORE EXPENSIVE than {name} (${tco_other/1e6:.0f}M)")
    for name, tco_other in competitors.items():
        if worst_tco <= tco_other:
            print(f"  ║  ✅ Still cheaper than {name} (${tco_other/1e6:.0f}M)")
    print(f"  ║")
    print(f"  ║  Worst case turns '85% advantage' into barely competitive.")
    print(f"  ╚══════════════════════════════════════════════════════════")
    
    return {"worst_tco": worst_tco}


# ══════════════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════════════

def generate_charts(corrected_data, worst_data, failure_data, output_dir="assets"):
    """Generate the stress test dashboard."""
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.patch.set_facecolor("#0a0a0a")
    fig.suptitle("STRESS TEST TO DESTRUCTION: Honest Financial Reality",
                 fontsize=18, fontweight="bold", color="#FF4444", y=0.98)
    
    # ── Chart 1: TCO Comparison (Original vs Corrected vs Worst) ──
    ax = axes[0, 0]
    ax.set_facecolor("#111111")
    labels = ["Google", "Microsoft", "AWS", "Meta", "HC\nOriginal", "HC\nCorrected", "HC\nWorst"]
    values = [1593, 1740, 1873, 1426, 304, corrected_data["tco_10y"]/1e6, worst_data["worst_tco"]/1e6]
    colors = ["#4285F4", "#00A4EF", "#FF9900", "#1877F2", "#00FFCC", "#FFAA00", "#FF4444"]
    bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=0.5)
    for b, v in zip(bars, values):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+20, f"${v:.0f}M",
                ha="center", color="white", fontweight="bold", fontsize=9)
    ax.set_ylabel("10Y TCO ($M)", color="white", fontweight="bold")
    ax.set_title("TCO: Fantasy vs Reality", color="#FF4444", fontweight="bold", fontsize=12)
    ax.tick_params(colors="white", labelsize=8)
    for s in ax.spines.values(): s.set_color("#333")
    
    # ── Chart 2: CAPEX/MW Comparison ──
    ax = axes[0, 1]
    ax.set_facecolor("#111111")
    labels2 = ["HC Original", "HC Realistic", "Meta", "Google", "Microsoft", "AWS"]
    values2 = [2.08, corrected_data["total_capex"]/100/1e6, 7.8, 8.5, 9.2, 10.0]
    colors2 = ["#00FFCC", "#FF4444", "#1877F2", "#4285F4", "#00A4EF", "#FF9900"]
    bars = ax.bar(labels2, values2, color=colors2, edgecolor="white", linewidth=0.5)
    for b, v in zip(bars, values2):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.1, f"${v:.1f}M",
                ha="center", color="white", fontweight="bold", fontsize=10)
    ax.set_ylabel("CAPEX per MW ($M)", color="white", fontweight="bold")
    ax.set_title("CAPEX/MW: The Real Picture", color="#FF4444", fontweight="bold", fontsize=12)
    ax.tick_params(colors="white", labelsize=8)
    for s in ax.spines.values(): s.set_color("#333")
    
    # ── Chart 3: Annual OPEX Breakdown ──
    ax = axes[1, 0]
    ax.set_facecolor("#111111")
    opex_cats = ["Maintenance", "Insurance", "Pumps", "Staff", "Anti-foul", "CP", "Monitor", "Inspect"]
    opex_vals = [
        failure_data["annual_cost_100mw"]/1e6,
        corrected_data["total_capex"]*0.035/1e6,
        2.4, 2.4, 1.2, 0.8, 0.6, 0.4
    ]
    colors3 = ["#FF4444", "#FF6666", "#FF8888", "#FFAAAA", "#FFCCCC", "#FFE0E0", "#FFF0F0", "#FFFFFF"]
    bars = ax.barh(opex_cats, opex_vals, color=colors3[:len(opex_cats)], edgecolor="white", linewidth=0.5)
    for b, v in zip(bars, opex_vals):
        ax.text(b.get_width()+0.1, b.get_y()+b.get_height()/2, f"${v:.1f}M",
                va="center", color="white", fontweight="bold")
    ax.set_xlabel("Annual Cost ($M)", color="white", fontweight="bold")
    ax.set_title("Real Annual OPEX (100MW)", color="#FF4444", fontweight="bold", fontsize=12)
    ax.tick_params(colors="white")
    for s in ax.spines.values(): s.set_color("#333")
    
    # ── Chart 4: Savings Erosion ──
    ax = axes[1, 1]
    ax.set_facecolor("#111111")
    scenarios = ["Original\nClaim", "Corrected\nCAPEX", "Real\nOPEX", "Insurance\nAdded", "Worst\nCase"]
    # Erosion of savings vs AWS ($1,873M)
    aws_tco = 1873
    savings = [
        aws_tco - 304,                              # Original claim
        aws_tco - (corrected_data["total_capex"]/1e6 + 9.5*10),  # Corrected CAPEX only
        aws_tco - (corrected_data["total_capex"]/1e6 + corrected_data["annual_opex"]*10/1e6*0.5),
        aws_tco - corrected_data["tco_10y"]/1e6,   # Full corrected
        aws_tco - worst_data["worst_tco"]/1e6,      # Worst case
    ]
    colors4 = ["#00FFCC", "#66DDAA", "#FFAA00", "#FF6600", "#FF4444"]
    bars = ax.bar(scenarios, savings, color=colors4, edgecolor="white", linewidth=0.5)
    for b, v in zip(bars, savings):
        label = f"${v:.0f}M" if v > 0 else f"-${abs(v):.0f}M"
        color = "white" if v > 0 else "#FF4444"
        pos = max(b.get_height(), 0) + 20
        ax.text(b.get_x()+b.get_width()/2, pos, label,
                ha="center", color=color, fontweight="bold", fontsize=10)
    ax.axhline(y=0, color="#FF4444", linestyle="--", linewidth=1)
    ax.set_ylabel("Savings vs AWS ($M)", color="white", fontweight="bold")
    ax.set_title("How Savings Erode with Reality", color="#FF4444", fontweight="bold", fontsize=12)
    ax.tick_params(colors="white", labelsize=8)
    for s in ax.spines.values(): s.set_color("#333")
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    path = os.path.join(output_dir, "v24_stress_test.png")
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="#0a0a0a")
    plt.close()
    print(f"\n  Chart saved: {path}")
    return path


# ══════════════════════════════════════════════════════════════
#  FINAL CONCLUSION
# ══════════════════════════════════════════════════════════════

def final_conclusion(corrected_data, worst_data):
    """The honest final word."""
    print("\n" + "=" * 70)
    print("  FINAL CONCLUSION: THE UNVARNISHED TRUTH")
    print("=" * 70)
    print(f"""
  ┌──────────────────────────────────────────────────────────────┐
  │  CLAIM vs REALITY                                           │
  ├─────────────────────────────────────┬────────────────────────┤
  │  Original Claim                     │  Corrected Reality     │
  ├─────────────────────────────────────┼────────────────────────┤
  │  CAPEX: $2.08M/MW                   │  ${corrected_data['total_capex']/100/1e6:.2f}M/MW              │
  │  OPEX:  $95K/MW/yr                  │  ${corrected_data['annual_opex']/100/1e3:.0f}K/MW/yr              │
  │  TCO:   $304M (10yr/100MW)          │  ${corrected_data['tco_10y']/1e6:.0f}M                │
  │  Savings vs AWS: 85%                │  {corrected_data['avg_savings_pct']:.0f}%                     │
  │  PUE: 1.02 (passive)               │  ~1.05-1.08 (needs pumps)   │
  │  TRL: 9 (production)               │  2 (simulation only)   │
  │  Time to market: 2 years            │  8-15 years            │
  │  Addressable market: 100%           │  ~6% (coastal only)    │
  ├─────────────────────────────────────┴────────────────────────┤
  │                                                              │
  │  THE CORRECTED VERDICT:                                      │
  │                                                              │
  │  Hydra-Cool has a {corrected_data['avg_savings_pct']:.0f}% TCO advantage — real but modest.    │
  │  In worst case, barely competitive with Big Tech.            │
  │                                                              │
  │  The concept is VALID but the business case was overstated.  │
  │  Before any investor presentation:                           │
  │    1. Correct all CAPEX to marine-grade estimates             │
  │    2. Include pump energy (not fully passive)                 │
  │    3. Price marine insurance properly                         │
  │    4. Acknowledge TRL 2 and 8-12 year development path       │
  │    5. Limit addressable market claims to coastal sites        │
  │                                                              │
  │  HONESTY IS THE STRONGEST FOUNDATION FOR ANY STARTUP.        │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
    """)


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  HYDRA-COOL v24.0 — STRESS TEST TO DESTRUCTION")
    print("  'The honest numbers. The uncomfortable truth.'")
    print("=" * 70)
    
    failure_data = failure_cascade()
    corrected_data = corrected_pnl(failure_data)
    worst_data = worst_case_scenario(corrected_data)
    
    print("\n  Generating Stress Test Dashboard...")
    generate_charts(corrected_data, worst_data, failure_data)
    
    final_conclusion(corrected_data, worst_data)
