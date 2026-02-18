"""
Hydra-Cool Simulation [CODE] — C03: TCO 20-Year Analysis
========================================================
Lifecycle cost analysis (20 Years).

Formula:
TCO(y) = CAPEX + Σ(OPEX_n) for n=1 to y

Comparison:
- Air Cooling: Low CAPEX (~$20M), High OPEX ($40M/yr).
- Hydra-Cool: High CAPEX (~$44M), Low OPEX ($2.5M/yr).

Output:
- Crossing curves showing break-even point in time.

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool C03: Running TCO Analysis...")
    
    years = np.arange(0, 21)
    
    # 1. Air Cooling (Baseline)
    capex_air = 20.0
    opex_air = 40.5 # From C02
    
    bg_air = [capex_air + (opex_air * y) for y in years]
    
    # 2. Hydra-Cool (Base)
    capex_hydra = 458.6 # From C01 Base (Updated)
    opex_hydra = 15.5   # From C02 (Updated)
    
    bg_hydra = [capex_hydra + (opex_hydra * y) for y in years]
    
    # 3. Hydra-Cool (Worst Case - High CAPEX/OPEX)
    capex_worst = 60.0
    opex_worst = 5.0
    
    bg_worst = [capex_worst + (opex_worst * y) for y in years]
    
    # Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(years, bg_air, color='#B0BEC5', linestyle='--', linewidth=2, label='Legacy Air Cooling')
    ax.plot(years, bg_hydra, color='#00E676', linewidth=3, label='Hydra-Cool (Base Case)')
    ax.plot(years, bg_worst, color='#FFC107', linestyle=':', linewidth=2, label='Hydra-Cool (Conservative)')
    
    # Axis labels
    ax.set_xlabel("Years of Operation")
    ax.set_ylabel("Cumulative Cost (TCO) [$ Million]")
    ax.set_title("20-Year Total Cost of Ownership (100 MW Facility)", fontsize=14)
    ax.grid(True, alpha=0.2)
    ax.legend()
    
    # Find Crossover
    # Air = Hydra -> 20 + 40.5*t = 44.4 + 2.5*t
    # 38*t = 24.4 -> t = 0.64 years
    
    # Show Crossover point for Base Case
    cross_idx = 0
    for i in range(len(years)):
        if bg_hydra[i] < bg_air[i] and i > 0:
            # Linear interp
            y1_a, y2_a = bg_air[i-1], bg_air[i]
            y1_h, y2_h = bg_hydra[i-1], bg_hydra[i]
            # Simple approx: just mark first year
            break
            
    # Calculate exact crossover t
    # Capex_h + Opex_h * t = Capex_a + Opex_a * t
    # t * (Opex_a - Opex_h) = Capex_h - Capex_a
    # t = Delta_Capex / Delta_Opex
    
    delta_capex = capex_hydra - capex_air
    delta_opex = opex_air - opex_hydra
    t_breakeven = delta_capex / delta_opex
    
    ax.plot(t_breakeven, capex_hydra + opex_hydra*t_breakeven, 'wo', markersize=8)
    ax.annotate(f"Breakeven: {t_breakeven*12:.1f} Months", 
                (t_breakeven, capex_hydra + opex_hydra*t_breakeven),
                xytext=(10, -20), textcoords='offset points', color='white', fontweight='bold')
    
    # Annotate Final Value
    ax.text(20.1, bg_air[-1], f"${bg_air[-1]:.0f}M", va='center', color='#B0BEC5')
    ax.text(20.1, bg_hydra[-1], f"${bg_hydra[-1]:.0f}M", va='center', color='#00E676', fontweight='bold')
    
    # Savings at year 20
    savings_20 = bg_air[-1] - bg_hydra[-1]
    ax.annotate(f"20-Year Savings:\n${savings_20:.0f} Million",
                xy=(20, (bg_air[-1]+bg_hydra[-1])/2), 
                ha='right', color='#00E676', fontsize=12)

    output_path = os.path.join(ASSET_DIR, "C03_tco_20year.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")
    print(f"Breakeven Time: {t_breakeven:.2f} Years")

if __name__ == "__main__":
    run_simulation()
