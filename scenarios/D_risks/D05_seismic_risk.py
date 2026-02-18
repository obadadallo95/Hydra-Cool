"""
Hydra-Cool Simulation [CODE] — D05: Seismic Risk Matrix
=======================================================
Assessing the viability of the "Tower" concept in quake zones.

Key Risk:
- Liquefaction of seabed soil (Intake pipe collapse).
- Tower Resonance (Structural failure).

Locations:
- Japan (High Risk).
- California (High Risk).
- Norway (Low Risk).
- Dubai (Low Risk).

Output:
- Risk Matrix (Probability vs Severity).

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool D05: Running Seismic Risk Analysis...")
    
    locations = ['Tokyo', 'Monterey', 'Oslo', 'Dubai']
    
    # Risk Scores (1-10)
    # Probability (P)
    prob = [9, 8, 2, 3] # Japan high, Norway low
    
    # Severity (S) (Assuming mitigation applied)
    # Severity depends on "Robustness".
    sev = [8, 8, 4, 4] 
    
    colors = ['#FF5252', '#FF5252', '#00E676', '#00E676']
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Grid Zones
    ax.axvspan(0, 5, ymin=0, ymax=0.5, color='#00E676', alpha=0.1) # Low/Low
    ax.axvspan(5, 10, ymin=0.5, ymax=1.0, color='#FF5252', alpha=0.1) # High/High
    
    ax.scatter(prob, sev, s=500, c=colors, edgecolors='white', alpha=0.8)
    
    for i, loc in enumerate(locations):
        ax.text(prob[i], sev[i], loc, ha='center', va='center', color='white', fontweight='bold')
        
    ax.set_xlabel("Seismic Probability (1-10)")
    ax.set_ylabel("Impact Severity (1-10)")
    ax.set_title("D05: Seismic Risk Assessment", fontsize=14)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 10.5)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Add annotations
    ax.text(2.5, 2.5, "SAFE ZONE", ha='center', color='#00E676', alpha=0.5, fontsize=20, rotation=45)
    ax.text(7.5, 7.5, "CRITICAL ZONE", ha='center', color='#FF5252', alpha=0.5, fontsize=20, rotation=45)

    output_path = os.path.join(ASSET_DIR, "D05_seismic_risk.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
