"""
Hydra-Cool Simulation [CODE] — D03: Materials Selection
=======================================================
Trade-off analysis for Pipeline Material.

Candidates:
1. Carbon Steel (Cheap, strong, corrodes fast).
2. HDPE (Cheap, flexible, no corrosion, pressure limit).
3. GRP (Glass Reinforced Plastic) (Moderate cost, no corrosion, fragile).
4. Super Duplex Stainless (Very expensive, immortal).

Output:
- Bubble Chart: Cost vs Lifespan.

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool D03: Running Material Selection...")
    
    materials = ['Carbon Steel', 'HDPE (Plastic)', 'GRP/FRP', 'Super Duplex SS']
    
    # X-axis: Lifespan (Years)
    lifespan = [15, 50, 30, 100]
    
    # Y-axis: Cost ($/m for 1.5m dia) relative status
    cost = [1500, 1200, 2000, 8000]
    
    # Size: Pressure Rating (bar)
    pressure = [100, 16, 25, 200]
    
    colors = ['#795548', '#00E676', '#FF9800', '#607D8B']
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(lifespan, cost, s=[p*5 for p in pressure], c=colors, alpha=0.8, edgecolors='white')
    
    # Labels
    for i, txt in enumerate(materials):
        ax.annotate(f"{txt}\n(PN{pressure[i]})", (lifespan[i], cost[i]), 
                    xytext=(0, 25), textcoords='offset points', ha='center', color=colors[i], fontweight='bold')
    
    ax.set_xlabel("Expected Lifespan [Years]")
    ax.set_ylabel("Unit Cost [$/m]")
    ax.set_title("D03: Material Selection Matrix", fontsize=14)
    ax.set_yscale('log')
    ax.grid(True, linestyle= '--', alpha=0.3)
    ax.set_xlim(0, 120)
    ax.set_ylim(500, 10000)
    
    # Ideal Zone
    ax.add_patch(plt.Rectangle((40, 500), 80, 2000, fill=True, color='#00E676', alpha=0.1))
    ax.text(100, 600, "Ideal Zone\n(Low Cost, Long Life)", ha='right', color='#00E676')

    output_path = os.path.join(ASSET_DIR, "D03_material_selection.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
