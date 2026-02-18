"""
Hydra-Cool Simulation [CODE] — B04: Geographic Suitability
==========================================================
Identifies prime locations.

Criteria:
1. Deep Water (>400m) within 10-20km of shore.
2. Existing Data Center Hubs or reliable power.
3. Stable political/geological environment (checked in D-Risk).

Candidates:
- Helsinki, Finland (Baltic is shallow? No, uses shallow seawater cooling. Hydra-Cool needs DEEP.)
- Oslo, Norway (Fjords are very deep close to shore).
- Tokyo/Chiba (Pacific drop-off).
- Monterey, CA (Submarine canyon).
- Hawaii (Deep immediately).
- Dubai (Persian Gulf is shallow ~80m avg. Might NOT work for pure deep cold intake. Needs analysis).

Output:
- Bar chart of "Distance to Deep Water" for major hubs.
- Suitability Score.

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool B04: Geographic Suitability Analysis...")
    
    locations = [
        "Oslo (Norway)",  # Deep fjords
        "Monterey (USA)", # Deep canyon
        "Tokyo (Japan)",  # Moderate shelf
        "Helsinki (Fin)", # Shallow (Need very long pipe)
        "Dubai (UAE)",    # Very Shallow (Gulf avg 50m)
        "Singapore"       # Shallow shelf, deep water far
    ]
    
    # Distance to -400m depth (Estimated km)
    dist_to_depth_km = [
        2.0,   # Oslo: Immediate deep water
        5.0,   # Monterey: Canyon close to shore
        25.0,  # Tokyo: Shelf
        100.0, # Helsinki: Baltic is shallow
        250.0, # Dubai: Gulf is a shallow basin
        300.0  # Singapore: Sunda shelf is shallow
    ]
    
    # Ideal is < 20 km.
    
    # Suitability Score (0-100)
    # Score = 100 - (Distance * Factor)
    scores = []
    for d in dist_to_depth_km:
        s = 100 - (d * 2) 
        if s < 0: s = 0
        scores.append(s)
        
    # Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color map based on score
    colors = ['#00E676' if s > 80 else '#FFC107' if s > 40 else '#FF5252' for s in scores]
    
    bars = ax.barh(locations, dist_to_depth_km, color=colors)
    ax.set_xlabel("Distance to 400m Depth [km]")
    ax.set_title("Geographic constraints: Distance to Cold Water")
    
    # Add Threshold Line
    ax.axvline(20, color='white', linestyle='--', alpha=0.5)
    ax.text(22, len(locations)-1, "Economic Limit (~20km)", color='white', fontsize=10)
    
    for i, (bar, d) in enumerate(zip(bars, dist_to_depth_km)):
        ax.text(d + 2, i, f"{d} km", va='center', fontweight='bold', color=colors[i])
        
    plt.tight_layout()
    output_path = os.path.join(ASSET_DIR, "B04_geographic_suitability.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")
    
    print("Suitability Analysis:")
    for loc, score in zip(locations, scores):
        status = "PRIME" if score > 80 else "FEASIBLE" if score > 40 else "UNVIABLE"
        print(f" - {loc}: {status} (Dist: {dist_to_depth_km[locations.index(loc)]}km)")

if __name__ == "__main__":
    run_simulation()
