"""
Hydra-Cool Simulation [CODE] — B01: Baseline Systems Comparison
===============================================================
Establishes the "Competition" to beat.

Data Sources:
- Air Cooling: PUE 1.5 - 1.6 (Traditional)
- Evaporative Cooling (Tower): PUE 1.2 - 1.3 (Modern standard)
- Seawater Cooling (Google Helsinki): PUE ~1.1 (State of the art)

Goal:
- Calculate IT Load vs Cooling Load for these systems.
- 100 MW IT Load needs X MW Cooling Power.

Formula:
- Total Power = IT Load * PUE
- Cooling Power = Total Power - IT Load
- PUE = Total / IT
- Cooling Overhead % = (PUE - 1) * 100

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# --- Constants ---
IT_LOAD_MW = 100.0

# --- Data ---
systems = [
    "Legacy Air (CRAC)",
    "Modern Evaporative",
    "Direct Seawater (Google)",
    "Hydra-Cool (Target)"
]

pue_values = [
    1.55,  # avg of 1.5-1.6
    1.25,  # avg of 1.2-1.3
    1.11,  # Helsinki reported
    1.00   # Theoretical Net Zero (from Phase A)
]

colors = ['#B0BEC5', '#90A4AE', '#4FC3F7', '#00E676']

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool B01: Baseline Systems Comparison...")
    
    cooling_power_mw = [(pue - 1.0) * IT_LOAD_MW for pue in pue_values]
    total_power_mw   = [pue * IT_LOAD_MW for pue in pue_values]
    
    # Correction: Hydra-Cool A04 showed slightly NEGATIVE net power (Generation)
    # So PUE < 1.0 is theoretically possible.
    # Let's set it to 0.99 for visual impact, or 1.0 if we are conservative.
    # Phase A04 found "Breakeven" at dT=53.
    # At dT=40, we had slight consumption (~3kW pump? No, 750kW pump for A02).
    # Wait, A02 showed 750kW pump for 100MW.
    # 750kW = 0.75 MW.
    # PUE = (100 + 0.75) / 100 = 1.0075.
    # So it is effectively ~1.01.
    # Let's use 1.01 for Hydra-Cool Base Case.
    
    pue_values[-1] = 1.008 # 0.8% overhead
    cooling_power_mw[-1] = 0.8
    
    # Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(systems, cooling_power_mw, color=colors, width=0.6)
    
    # Add values on top
    for bar, power, pue in zip(bars, cooling_power_mw, pue_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{power:.1f} MW\n(PUE {pue:.2f})',
                ha='center', va='bottom', color='white', fontweight='bold')

    ax.set_ylabel('Cooling Power Consumption [MW]\n(for 100MW IT Load)', fontsize=12)
    ax.set_title(f"B01: Industry Benchmark - Cooling Power Required", fontsize=14, pad=20)
    ax.grid(axis='y', linestyle='--', alpha=0.2)
    
    # Highlight the savings
    savings = cooling_power_mw[0] - cooling_power_mw[-1]
    ax.annotate(f"Hydra-Cool saves {savings:.1f} MW\nvs Legacy Air",
                xy=(3, 5), xytext=(2, 30),
                arrowprops=dict(facecolor='white', shrink=0.05),
                fontsize=11, color='#00E676')

    output_path = os.path.join(ASSET_DIR, "B01_baseline_comparison.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
