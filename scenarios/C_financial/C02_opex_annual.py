"""
Hydra-Cool Simulation [CODE] — C02: OPEX Annual Analysis
========================================================
Establishes the annual running cost.

Components:
- Maintenance (1-2% of CAPEX).
- Bio-fouling control (Chlorination/Pigging).
- Monitoring & Inspection (ROV).
- Auxiliary Power (Lighting, Controls).

Comparison:
- Air Cooling: High PUE -> High Electricity Cost.
- Hydra-Cool: Near Zero Electricity, but higher Maintenance.

Output:
- Waterfall Chart of OPEX components.

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool C02: Running OPEX Analysis...")
    
    # Baseline: Air Cooling 100MW
    pue_air = 1.55
    energy_cost_air = (pue_air - 1.0) * 100.0 * 8760 * 80 / 1e6 # $Mil: 55 * 8760 * 80 -> ~$38.5M
    # Maintenance of Chillers (approx 5% of energy cost?)
    maint_air = 2.0
    
    total_opex_air = energy_cost_air + maint_air
    
    # Hydra-Cool (Base Case)
    # Energy: 0.05 MW (Parasitic) -> negligible
    energy_cost_hydra = 0.05 * 8760 * 80 / 1e6 # ~$0.035M
    
    # Maintenance items (Revised Realistic Dictionary)
    hydra_opex_components = {
        'Marine Maintenance': 6.0,
        'Biofouling Treatment': 1.5,
        'Cathodic Protection': 0.8,
        'Marine Staff': 3.0,
        'Insurance Annual': 3.0,
        'Auxiliary Energy': 1.2,
    }
    maint_hydra_total = sum(hydra_opex_components.values()) # 15.5M
    maint_hydra_items = np.array(list(hydra_opex_components.values()))
    
    total_opex_hydra = energy_cost_hydra + maint_hydra_total
    
    # Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Comparison Bar
    systems = ['Legacy Air (PUE 1.55)', 'Hydra-Cool (Realistic)']
    totals = [total_opex_air, total_opex_hydra]
    
    bars = ax.bar(systems, totals, color=['#B0BEC5', '#00E676'], width=0.5)
    
    ax.set_ylabel("Annual OPEX [$ Million]")
    ax.set_title("Annual OPEX Comparison (100 MW) - Realistic", fontsize=14)
    ax.grid(axis='y', alpha=0.2)
    
    # Annotate Air
    ax.text(0, totals[0]/2, f"Energy: ${energy_cost_air:.1f}M", ha='center', color='#37474F')
    ax.text(0, totals[0] + 0.5, f"${totals[0]:.1f}M", ha='center', color='white', fontweight='bold')
    
    # Annotate Hydra
    ax.text(1, totals[1] + 0.5, f"${totals[1]:.1f}M", ha='center', color='white', fontweight='bold')
    
    # Show saving
    saving = total_opex_air - total_opex_hydra
    ax.annotate(f"Operational Saving:\n${saving:.1f}M / year", 
                xy=(1, totals[1]), xytext=(0.5, totals[0]*0.8),
                arrowprops=dict(facecolor='white', arrowstyle='->'),
                fontsize=12, color='#00E676', fontweight='bold')
                
    # Insert mini-pie for Hydra Breakdown
    left, bottom, width, height = [0.65, 0.45, 0.25, 0.35]
    ax2 = fig.add_axes([left, bottom, width, height])
    ax2.pie(maint_hydra_items, labels=list(hydra_opex_components.keys()), 
            autopct='%1.0f%%', startangle=90, 
            colors=['#00BCD4', '#8BC34A', '#CDDC39', '#FF9800', '#9C27B0', '#607D8B'],
            textprops={'fontsize': 8})
    ax2.set_title("Hydra OPEX Breakdown", fontsize=9)
    
    output_path = os.path.join(ASSET_DIR, "C02_opex_annual.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")
    
    print("-" * 30)
    print(f"Air OPEX: ${total_opex_air:.1f}M")
    print(f"Hydra OPEX: ${total_opex_hydra:.1f}M")
    print(f"Annual Savings: ${saving:.1f}M")
    print("-" * 30)

if __name__ == "__main__":
    run_simulation()
