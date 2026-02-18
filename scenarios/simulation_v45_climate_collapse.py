"""
Hydra-Cool Simulation v45.0 — CLIMATE COLLAPSE 2050 (The Day After Tomorrow)
============================================================================
Scenario: Year 2050. Global Temp +2.5°C. 
Sea Level +1.0m. Ocean Surface Temp +3°C.

IMPACTS:
  1. Intake Temp Rise: Deep water warms slightly (5°C -> 6°C).
  2. Storm Surge: 100-year storm flood level rises.
  3. Biofouling: Algae blooms frequency triples.

OBJECTIVE:
  - Stress test the "Static Head" assumptions with rising sea level.
  - Calculate Biofouling OPEX multiplier.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def run_climate_2050():
    print("="*60)
    print("  HYDRA-COOL v45: CLIMATE COLLAPSE 2050")
    print("="*60)
    
    # 1. Sea Level Rise
    base_sl = 0.0
    rise_2050 = 1.0 # meters
    storm_surge = 3.0 # meters
    
    pump_room_elevation = 2.0 # meters above current SL
    
    flood_height = (base_sl + rise_2050 + storm_surge) - pump_room_elevation
    
    print(f"\n  [FLOOD RISK]")
    print(f"  Pump Room Elev:   +2.0m")
    print(f"  2050 Storm Crest: +4.0m")
    print(f"  Inundation:       {flood_height} meters")
    
    if flood_height > 0:
        print(f"  VERDICT: 💀 PUMP ROOM FLOODED.")
        print(f"  MITIGATION: Build pumps at +5.0m elevation or inside watertight bunkers.")
        
    # 2. Biofouling Multiplier
    # Rate doubles every 10C... but algae blooms depend on surface nutrients/temp.
    # Assume 3x cleaning cost.
    
    base_cleaning_cost = 0.5 # $M/year
    future_cleaning_cost = base_cleaning_cost * 3.0
    
    print(f"\n  [OPEX IMPACT]")
    print(f"  Current Cleaning: ${base_cleaning_cost}M/yr")
    print(f"  2050 Cleaning:    ${future_cleaning_cost}M/yr (Red Tides)")
    
    print("-" * 60)
    print("  SUMMARY: The physics survive, but the infrastructure drowns.")
    print("  SUMMARY: The physics survive, but the infrastructure drowns.")
    print("  DESIGN CHANGE: Raise all critical assets to +5m AMSL.")

    # Plotting
    os.makedirs("assets", exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')
    
    levels = [base_sl, pump_room_elevation, base_sl + rise_2050 + storm_surge]
    labels = ['Current Sea Level (0m)', 'Pump Room Floor (+2m)', '2050 Storm Surge (+4m)']
    colors = ['blue', 'gray', 'red']
    
    for i, (lvl, lbl, col) in enumerate(zip(levels, labels, colors)):
        plt.axhline(lvl, color=col, linewidth=3, linestyle='-' if i != 2 else '--', label=lbl)
        if i == 2:
           plt.fill_between([-1, 1], base_sl, lvl, color='red', alpha=0.3, label='Flood Zone')
    
    plt.xlim(-0.5, 0.5)
    plt.ylim(-1, 6)
    plt.xticks([])
    
    plt.text(0, pump_room_elevation + 0.2, "PUMP ROOM", ha='center', color='white', fontweight='bold', bbox=dict(facecolor='black'))
    plt.text(0, 4.2, f"INUNDATION: {flood_height}m", ha='center', color='red', fontweight='bold', fontsize=14)
    
    plt.title("v45: CLIMATE COLLAPSE 2050 - Flood Risk", color='white', fontweight='bold')
    plt.ylabel("Elevation (m AMSL)", color='white')
    plt.legend(loc='upper right')
    plt.grid(True, axis='y', alpha=0.3)
    
    out = "assets/v45_climate_risk.png"
    plt.savefig(out, dpi=150)
    print(f"\n  ✓ Chart saved: {out}")

if __name__ == "__main__":
    run_climate_2050()
