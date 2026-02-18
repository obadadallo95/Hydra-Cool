"""
Hydra-Cool Simulation [CODE] — B02: Hydra-Cool vs Baseline (Net Energy)
=======================================================================
Direct comparison of Hydra-Cool's performance (from Phase A) against
industry baselines.

Goal:
- Show PUE Comparison side-by-side.
- Show "Net Energy Footprint".
- Hydra-Cool PUE ≈ 1.0 (or slightly less if generating).

Data:
- Baseline PUEs from B01.
- Hydra-Cool PUE from A04 (Breakeven or Net Gain).
- Let's assume a conservative operational case where we pump slightly
  more than needed for safety, PUE = 1.02, OR the high-temp case PUE = 0.99.
- We will show the "Range" for Hydra-Cool.

Output:
- Bar chart with "Energy Saved" highlighted.
- Net Annual Energy (GWh) calculation.

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# --- Constants ---
IT_LOAD_MW = 100.0
HOURS_PER_YEAR = 8760
COST_PER_MWH = 80.0 # $80/MWh (Industrial average)

# --- Data ---
systems = ["Air Cooling", "Evap Tower", "Seawater", "Hydra-Cool"]
pues = [1.55, 1.25, 1.11, 1.00] # 1.00 implies neutral or slight gen

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool B02: Running Net Energy Comparison...")
    
    # 1. Power Calc
    cooling_power_mw = [(pue - 1.0)*IT_LOAD_MW for pue in pues]
    
    # Hydra-Cool might be negative (generation)
    # Let's assume A04 optimum: -3.7 kW (negligible) -> 0.0 MW
    # Let's assume High-Temp case (50C delta): Net Gen?
    # Let's stick to the "Honest" base case: Near Zero.
    cooling_power_mw[-1] = 0.05 # 50 kW parasite load (minimal)
    
    # 2. Annual Energy & Cost
    annual_energy_gwh = [p * HOURS_PER_YEAR / 1000 for p in cooling_power_mw]
    annual_cost_m = [e * COST_PER_MWH / 1000 for e in annual_energy_gwh]
    
    # 3. Visualization
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Power Required
    colors = ['#546E7A', '#78909C', '#29B6F6', '#00E676']
    bars = ax1.bar(systems, cooling_power_mw, color=colors)
    ax1.set_ylabel("Cooling Power [MW]")
    ax1.set_title("Cooling Power Required (100MW IT Load)")
    ax1.grid(axis='y', alpha=0.2)
    
    for bar, val in zip(bars, cooling_power_mw):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 1, f"{val:.1f} MW", ha='center', fontweight='bold')
    
    # Plot 2: Annual Cost Savings
    # Baseline = Air Cooling
    baseline_cost = annual_cost_m[0]
    savings_m = [baseline_cost - c for c in annual_cost_m]
    
    # Waterfall for Hydra-Cool
    # Just show cost bars?
    ax2.bar(systems, annual_cost_m, color=colors, alpha=0.8)
    ax2.set_ylabel("Annual Cooling Energy Cost [$ Million]")
    ax2.set_title("Annual Cooling Energy Cost ($0.08/kWh)")
    ax2.grid(axis='y', alpha=0.2)
    
    for bar, cost in zip(ax2.containers[0], annual_cost_m):
        ax2.text(bar.get_x() + bar.get_width()/2, cost + 0.5, f"${cost:.1f}M", ha='center', fontweight='bold')
        
    # Annotate Saving
    hydra_saving = savings_m[-1]
    ax2.annotate(f"Saves ${hydra_saving:.1f}M / year", 
                 xy=(3, 1), xytext=(2, 15),
                 arrowprops=dict(facecolor='white', shrink=0.05),
                 fontsize=12, color='#00E676', fontweight='bold')

    plt.tight_layout()
    output_path = os.path.join(ASSET_DIR, "B02_hydra_vs_baseline.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")
    
    print("-" * 30)
    print(f"Hydra-Cool Cooling Power: {cooling_power_mw[-1]:.2f} MW")
    print(f"Annual Savings vs Air: ${hydra_saving:.2f} Million")
    print("-" * 30)

if __name__ == "__main__":
    run_simulation()
