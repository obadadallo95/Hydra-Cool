"""
Hydra-Cool Simulation v31.0 — COMPETITOR SHOWDOWN (Unbiased Reality)
=====================================================================
Head-to-head comparison against real-world tech giants.
No marketing fluff. Just physics and dollars.

COMPETITORS:
  1. Google Hamina (Finland): Seawater Cooling. No Recovery. PUE 1.11.
  2. Meta Lulea (Sweden): Arctic Air. Fans only. PUE 1.07.
  3. Microsoft Dublin (Ireland): Adiabatic (Gen 4). PUE 1.25.
  4. AWS Virginia (USA): Evaporative Cooling. Water Stressed. PUE 1.20.

HYDRA-COOL PERFORMANCE:
  - Net PUE: 1.02 (After Hydro-Recovery credit)
  - Water Use: 0.0 L/kWh

OBJECTIVE:
  Calculate Annual OPEX Savings (Energy + Water) vs each competitor.
  Identifiy where Hydra-Cool WINS and where it LOSES.

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

IT_LOAD_MW      = 100.0
HOURS_YR        = 8760
ENERGY_COST     = 0.12     # $/kWh (Global average industrial)
WATER_COST      = 3.00     # $/m3 (High due to treatment/scarcity)

# ══════════════════════════════════════════════════════════════
#  COMPETITOR PROFILES
# ══════════════════════════════════════════════════════════════

class Competitor:
    def __init__(self, name, location, pue, wue, notes):
        self.name = name
        self.location = location
        self.pue = pue
        self.wue = wue  # L/kWh
        self.notes = notes

def get_competitors():
    return [
        Competitor("Google (Hamina)", "Finland", 1.11, 0.0, "Sea Pumped (No Recovery)"),
        Competitor("Meta (Lulea)", "Sweden", 1.07, 0.0, "Arctic Air (Fans)"),
        Competitor("Microsoft (Dublin)", "Ireland", 1.25, 0.5, "Adiabatic (Gen 4)"),
        Competitor("AWS (Virginia)", "USA", 1.20, 1.8, "Evaporative (Water Hog)")
    ]

# ══════════════════════════════════════════════════════════════
#  ANALYSIS ENGINE
# ══════════════════════════════════════════════════════════════

def run_showdown():
    print("="*80)
    print("  HYDRA-COOL v31: COMPETITOR SHOWDOWN (Unbiased Analysis)")
    print("="*80)
    
    hydra_pue = 1.02
    hydra_wue = 0.0
    
    competitors = get_competitors()
    results = []
    
    # Calculate Base Energy (IT Load Only)
    energy_it_mwh = IT_LOAD_MW * HOURS_YR
    
    print(f"\n  {'Competitor':<25} {'PUE':<6} {'WUE':<6} {'Energy $_Cost/yr':>16} {'Water $_Cost/yr':>16} {'Total OPEX':>16}")
    print("-" * 100)
    
    # 1. Hydra-Cool Baseline
    hydra_energy_cost = energy_it_mwh * (hydra_pue - 1.0) * 1000 * ENERGY_COST 
    # Note: PUE cost is only the "Cooling Overhead". IT load is constant for all.
    # Cost = (Total Energy - IT Energy) * Rate
    # Total Energy = IT * PUE
    # Cooling Energy = IT * (PUE - 1)
    
    print(f"  {'Hydra-Cool (Target)':<25} {hydra_pue:<6.2f} {hydra_wue:<6.1f} ${hydra_energy_cost/1e6:>15.1f}M ${0.0:>15.1f}M ${hydra_energy_cost/1e6:>15.1f}M")
    print("-" * 100)
    
    # 2. Competitors
    for c in competitors:
        # Energy Cost (Cooling Overhead)
        cooling_energy_mwh = energy_it_mwh * (c.pue - 1.0)
        cost_energy = cooling_energy_mwh * 1000 * ENERGY_COST
        
        # Water Cost
        # WUE is L/kWh of IT Energy usually. Or Total Energy? Usually IT.
        total_water_liters = c.wue * (energy_it_mwh * 1000)
        total_water_m3 = total_water_liters / 1000
        cost_water = total_water_m3 * WATER_COST
        
        total_opex = cost_energy + cost_water
        
        # Savings
        saving = total_opex - hydra_energy_cost
        
        results.append({
            "name": c.name,
            "saving": saving,
            "cost_energy": cost_energy,
            "cost_water": cost_water,
            "total": total_opex
        })
        
        # Verdict Marker
        verdict = "✅ WIN" if saving > 0 else "❌ LOSS"
        
        print(f"  {c.name:<25} {c.pue:<6.2f} {c.wue:<6.1f} ${cost_energy/1e6:>15.1f}M ${cost_water/1e6:>15.1f}M ${total_opex/1e6:>15.1f}M {verdict}")

    return results

# ══════════════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════════════

def plot_competitor_showdown(results):
    os.makedirs("assets", exist_ok=True)
    
    names = [r['name'] for r in results]
    savings = [r['saving']/1e6 for r in results]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.style.use('dark_background')
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#111')
    
    # Colors: Green for savings, Red for loss (neg savings)
    colors = ['#00FFCC' if s > 0 else '#FF4444' for s in savings]
    
    bars = ax.bar(names, savings, color=colors, edgecolor='white', alpha=0.9)
    
    ax.axhline(0, color='white', linewidth=1)
    
    # Labels
    for bar, val in zip(bars, savings):
        height = bar.get_height()
        if val >= 0:
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.5, f"+${val:.1f}M", ha='center', color='#00FFCC', fontweight='bold')
        else:
             ax.text(bar.get_x() + bar.get_width()/2, height - 1.5, f"-${abs(val):.1f}M", ha='center', color='#FF4444', fontweight='bold')
             
    ax.set_title("ANNUAL OPEX SAVINGS: Hydra-Cool vs Big Tech", fontsize=16, color='white', pad=20)
    ax.set_ylabel("Annual Savings ($ Millions)", fontsize=12, color='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#333')
    ax.spines['left'].set_color('#333')
    
    # Add explanation text
    plt.figtext(0.5, 0.02, "Note: Comparison includes Energy Cost ($0.12/kWh) and Water Cost ($3.00/m³).", ha="center", fontsize=9, color="#aaa")
    
    out_path = "assets/v31_competitor_savings.png"
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"\n  ✓ Chart saved: {out_path}")
    
    print("\n  VERDICT ANALYSIS:")
    for r in results:
        if r['saving'] > 0:
            print(f"  - {r['name']}: Hydra-Cool is CHEAPER. Save ${r['saving']/1e6:.1f}M/year.")
        else:
            print(f"  - {r['name']}: Hydra-Cool is MORE EXPENSIVE. Lose ${abs(r['saving']/1e6):.1f}M/year.")

if __name__ == "__main__":
    res = run_showdown()
    plot_competitor_showdown(res)
