"""
Hydra-Cool Simulation [CODE] — F02: Scalability & Economies of Scale
====================================================================
"Go big or go home."

Analysis of unit cost ($/MW) as capacity scales from 10MW to 1GW.
- Tunneling costs (Marine pipe) scale sub-linearly (TBM fixed cost + length).
- Civil/Tower scales nicely.
- Larger Diameter = Less Friction = More Efficiency.

Output:
- Cost Curve ($M/MW) vs Capacity (MW).

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool F02: Running Scalability Analysis...")
    
    capacities = np.linspace(10, 1000, 50) # MW
    unit_costs = []
    
    # Base Case: 100 MW -> $44M -> $0.44M/MW
    
    for cap in capacities:
        # Scaling Factors (Exponent < 1 means economies of scale)
        # Marine: 0.7 (Larger pipes are cheaper per unit flow)
        # Civil: 0.8
        # MEP: 0.9 (Equipment is modular, less scaling benefit)
        # Soft: 0.6 (Design once, build big)
        
        # Component Breakdown at 100MW (Updated Base ~458M):
        # Marine: 245, Cathodic: 7, Insurance: 25
        # Civil: 20, HX: 5, MEP: 8
        # Soft: ~43, Contingency: ~105
        
        scale = cap / 100.0
        
        # Marine Group (Pipe + Protection + Insurance) - Strong economies of scale
        c_marine_group = (245.0 + 7.0 + 25.0) * (scale ** 0.6) 
        
        c_civil = 20.0 * (scale ** 0.8)
        c_hx = 5.0 * (scale ** 0.95)
        c_mep = 12.0 * (scale ** 0.9) # Increased due to aux systems for maintenance
        
        c_soft = 43.0 * (scale ** 0.5)
        c_contingency = 105.0 * (scale ** 0.6) # Scales with project complexity
        
        total = c_marine_group + c_civil + c_hx + c_mep + c_soft + c_contingency
        unit_costs.append(total / cap) # $M / MW

    # Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    color = '#00B0FF'
    ax.plot(capacities, unit_costs, color=color, linewidth=3)
    
    # Annotate Points
    for c in [10, 100, 500, 1000]:
        idx = (np.abs(capacities - c)).argmin()
        val = unit_costs[idx]
        ax.plot(c, val, 'wo')
        ax.annotate(f"${val:.2f}M/MW", (c, val), xytext=(10, 10), 
                    textcoords='offset points', color='white', fontweight='bold')
    
    ax.set_xlabel("Facility Capacity [MW]")
    ax.set_ylabel("Unit CAPEX [$ Million / MW]")
    ax.set_title("F02: Economies of Scale (The Gigafactory Effect)", fontsize=14)
    ax.grid(True, alpha=0.2, which='both')
    ax.set_xscale('log')
    
    # Mark 100MW Base
    ax.axvline(100, color='white', linestyle=':', alpha=0.5)
    ax.text(110, 0.8, "Base Case", color='white', rotation=90)

    output_path = os.path.join(ASSET_DIR, "F02_scalability.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
