"""
Hydra-Cool Simulation [CODE] — C01: CAPEX Estimation
====================================================
Establishes the upfront cost of the system.

Methodology:
- Separate costs into:
  1. Marine Works (Intake pipe, laying, protection)
  2. Civil Works (Tower/Tank, Onshore pump station)
  3. MEP (Heat Exchangers, Pumps, Turbine, Piping)
  4. Soft Costs (Permitting, Engineering)

Basis (100 MW System):
- Intake Pipe: 3000m length, 1.5m dia.
  - Cost: $3M - $8M per km (Offshore HDD vs Lay).
- Tower: 20-50m height, concrete.
- HX: Plate heat exchangers ($30/kW).

Output:
- Stacked Bar Chart (Low / Base / High scenarios).

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool C01: Running CAPEX Estimation...")
    
    scenarios = ['Optimistic', 'Base Case', 'Conservative']
    
    # 1. Component Estimations (Millions USD)
    
    # Marine Pipeline (7km length to reach 300m depth)
    # Realistic Cost: $35M/km (Base)
    # Low: $25M/km, Base: $35M/km, High: $50M/km
    pipe_len = 7.0
    cost_per_km = np.array([25.0, 35.0, 50.0])
    cost_marine_pipe = pipe_len * cost_per_km
    
    # New Items
    cost_cathodic = np.array([3.0, 7.0, 12.0])
    cost_insurance = np.array([15.0, 25.0, 40.0])
    
    # Civil - Tower & Intake Station
    # Low: Simple structure, Base: Robust, High: Architecturally complex
    cost_civil = np.array([10.0, 20.0, 40.0]) # Increased slightly for scale
    
    # MEP - Heat Exchangers (100MW)
    # 100,000 kW * $30/kW = $3M (Optimistic)
    # Base: $5M, High: $8M (Titanium plates)
    cost_hx = np.array([3.0, 5.0, 8.0])
    
    # MEP - Pumps & Turbine & internal piping
    cost_mep_other = np.array([5.0, 8.0, 15.0])
    
    # Soft Costs (Permitting, Design) - % of Hard Cost
    hardness = cost_marine_pipe + cost_cathodic + cost_civil + cost_hx + cost_mep_other
    cost_soft = hardness * np.array([0.10, 0.15, 0.20])
    
    subtotal = hardness + cost_soft + cost_insurance
    
    # Contingency (20%, 30%, 40%)
    contingency_pct = np.array([0.20, 0.30, 0.40])
    cost_contingency = subtotal * contingency_pct
    
    # Totals
    total_capex = subtotal + cost_contingency
    
    # 2. Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Stacked Bars
    indices = range(len(scenarios))
    width = 0.5
    
    # Cumulative Bottoms
    b1 = cost_marine_pipe
    b2 = b1 + cost_cathodic
    b3 = b2 + cost_insurance
    b4 = b3 + cost_civil
    b5 = b4 + cost_hx
    b6 = b5 + cost_mep_other
    b7 = b6 + cost_soft
    
    p1 = ax.bar(scenarios, cost_marine_pipe, width, label='Marine Pipe (7km)', color='#0288D1')
    p2 = ax.bar(scenarios, cost_cathodic, width, bottom=b1, label='Cathodic Prot.', color='#00BCD4')
    p3 = ax.bar(scenarios, cost_insurance, width, bottom=b2, label='Insurance (10y)', color='#009688')
    p4 = ax.bar(scenarios, cost_civil, width, bottom=b3, label='Civil Works', color='#795548')
    p5 = ax.bar(scenarios, cost_hx, width, bottom=b4, label='Heat Exchangers', color='#FF5722')
    p6 = ax.bar(scenarios, cost_mep_other, width, bottom=b5, label='Other MEP', color='#FF9800')
    p7 = ax.bar(scenarios, cost_soft, width, bottom=b6, label='Soft Costs', color='#9E9E9E')
    p8 = ax.bar(scenarios, cost_contingency, width, bottom=b7, label='Contingency', color='#607D8B', hatch='//')

    
    ax.set_ylabel("CAPEX [USD Million]")
    ax.set_title(f"C01: CAPEX Estimation (100 MW System)", fontsize=14)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Annotate Totals
    for i, v in enumerate(total_capex):
        ax.text(i, v + 2, f"${v:.1f}M", ha='center', fontweight='bold', color='white', fontsize=12)
        ax.text(i, v/2, f"Target: ${v/100:.2f}M/MW", ha='center', color='black', alpha=0.0) # Hidden

    # Comparisons
    # Traditional Cooling Tower CAPEX ~ $0.4M/MW -> $40M
    # Air Cooling CAPEX ~ $0.2M/MW -> $20M
    # Hydra-Cool Base is ~$44M. So slightly higher CAPEX.
    
    # Add Benchmark line
    ax.axhline(40, color='#B0BEC5', linestyle='--', linewidth=1)
    ax.text(0, 41, "Approx. Cooling Tower CAPEX ($40M)", color='#B0BEC5', fontsize=9)

    plt.tight_layout()
    output_path = os.path.join(ASSET_DIR, "C01_capex_estimation.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")
    
    print("-" * 30)
    print(f"Base Case CAPEX: ${total_capex[1]:.1f} Million")
    print(f"Cost per MW: ${total_capex[1]/100:.2f} Million/MW")
    print("-" * 30)

if __name__ == "__main__":
    run_simulation()
