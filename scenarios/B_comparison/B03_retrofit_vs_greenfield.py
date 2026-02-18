"""
Hydra-Cool Simulation [CODE] — B03: Retrofit vs Greenfield
==========================================================
Analyzes the implementation feasibility.

Scenarios:
1. Greenfield: Building a new DC optimized for Hydra-Cool.
   - High CAPEX (New Building), but optimized plumbing.
   - Time: 3-5 Years.
2. Retrofit: Adding Hydra-Cool to existing coastal DC.
   - Lower CAPEX (Building exists), but higher complexity piping.
   - Time: 1.5 - 2 Years.

Goal:
- Visualize the "Payback Timeline" conceptually.
- Breakdown of CAPEX intensity.

Output:
- Stacked Bar Chart of Cost Components (Normalized).
- Timeline Gantt Chart.

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool B03: Retrofit vs Greenfield Analysis...")
    
    # 1. Cost Breakdown (Normalized to 100 units of standard DC cost)
    # Standard DC: M&E (Mechanical & Electrical) is huge.
    # Hydra-Cool reduces Mechanical (Chillers) but adds Civil (Tower/Intake).
    
    scenarios = ['Standard DC', 'Hydra Greenfield', 'Hydra Retrofit']
    
    # Costs ($M per MW?) - Let's use relative units
    # Standard: Building 30, Power 40, Cooling 30
    # Hydra Green: Building 30, Power 40, Cooling 10, Civil/Marine 15 -> Total 95?
    # Hydra Retro: Building 0 (Sunk), Power 5 (Upgrade?), Cooling 10, Civil/Marine 20 -> Total 35 (Incremental)
    
    # Let's show "Capital Intensity per MW of IT"
    # Standard: $8M / MW (Average)
    # Hydra Green: $8.5M / MW ? (Marine works are expensive)
    # Hydra Retro: $2.5M / MW (Incremental investment)
    
    # Components
    labels = ['Building/Core', 'Power Infra', 'Cooling System', 'Marine/Tower']
    
    data_std = np.array([3.0, 3.5, 2.5, 0.0]) # Standard
    data_grn = np.array([3.0, 3.5, 0.8, 1.8]) # Hydra Green (Cooling cheaper, added Marine)
    data_ret = np.array([0.0, 0.5, 0.8, 2.2]) # Hydra Retro (Just the delta)
    
    data = np.vstack([data_std, data_grn, data_ret])
    
    # 2. Visualization
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Stacked Bar (CAPEX)
    colors = ['#795548', '#FFC107', '#03A9F4', '#E91E63']
    bottoms = np.zeros(3)
    
    for i in range(4):
        ax1.bar(scenarios, data[:, i], bottom=bottoms, label=labels[i], color=colors[i], width=0.5)
        bottoms += data[:, i]
        
    ax1.set_ylabel("CAPEX Intensity [$M / MW]")
    ax1.set_title("CAPEX Comparison: Traditional vs Hydra-Cool")
    ax1.legend()
    # Annotate Totals
    for i, total in enumerate(bottoms):
        ax1.text(i, total + 0.1, f"${total:.1f}M", ha='center', fontweight='bold')
        
    # Gantt Chart (Timeline)
    # Tasks: Permitting, Civil, MEP Install, Commissioning
    projects = ['Retrofit', 'Greenfield']
    start_dates = [0, 0]
    durations = [18, 42] # Months
    
    # Broken down
    # Retrofit: Permit (6), Marine (8), Tie-in (4)
    # Greenfield: Permit (12), Building (18), Marine (8), Comm (4)
    
    # Simple Horizontal Bar for total time
    y_pos = np.arange(len(projects))
    ax2.barh(y_pos, durations, color=['#00E676', '#AB47BC'], alpha=0.8, height=0.5)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(projects)
    ax2.set_xlabel("Project Duration [Months]")
    ax2.set_title("Time-to-Market Comparison")
    
    for i, v in enumerate(durations):
        ax2.text(v + 1, i, f"{v} Months", va='center', fontweight='bold')
        
    output_path = os.path.join(ASSET_DIR, "B03_retrofit_vs_greenfield.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
