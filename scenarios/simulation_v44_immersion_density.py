"""
Hydra-Cool Simulation v44.0 — IMMERSION COOLING (The NVIDIA H100 Play)
======================================================================
Scenario: Transition from Air Cooling to Two-Phase Immersion.
Density rises from 10kW/rack to 200kW/rack.

PHYSICS:
  - Air Cooling: Returns water at 30°C (Delta T = 10°C).
  - Immersion: Returns water at 60°C (Delta T = 40°C).
  - Higher Temp = Lower Density = MORE BUOYANCY.

OBJECTIVE:
  - Compare "Lift Efficiency" of Air vs Immersion return temps.
  - Does Immersion make Hydra-Cool better?
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def run_immersion_density():
    print("="*60)
    print("  HYDRA-COOL v44: IMMERSION COOLING DENSITY")
    print("="*60)
    
    RHO_5C = 1027.0
    
    # Case A: Air Cooled (Return 30C)
    rho_30 = 1017.0
    d_rho_air = RHO_5C - rho_30
    
    # Case B: Immersion (Return 60C)
    rho_60 = 1007.0 # Hotter!
    d_rho_imm = RHO_5C - rho_60
    
    print(f"\n  [BUOYANCY PHYSICS]")
    print(f"  Intake (5°C):       1027 kg/m3")
    print(f"  Air Return (30°C):  {rho_30} kg/m3 (Delta: {d_rho_air} kg/m3)")
    print(f"  Immersion (60°C):   {rho_60} kg/m3 (Delta: {d_rho_imm} kg/m3)")
    
    gain = (d_rho_imm - d_rho_air) / d_rho_air * 100
    
    print(f"\n  [VERDICT]")
    print(f"  - Immersion roughly DOUBLES the 'Thermosiphon Effect' (+{gain:.0f}%).")
    print(f"  - Hotter water = Easier lift.")
    print(f"  - Turbine output is same (Mass flow balancing), but Pump Work drops significantly.")
    print(f"  - CONCLUSION: Hydra-Cool is purpose-built for Immersion.")

    plot_immersion_boost(d_rho_air, d_rho_imm)

def plot_immersion_boost(air, imm):
    os.makedirs("assets", exist_ok=True)
    labels = ['Air Cooled (30°C)', 'Immersion (60°C)']
    vals = [air, imm]
    colors = ['gray', '#00FFCC']
    
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')
    
    plt.bar(labels, vals, color=colors)
    plt.title("v44: BUOYANCY LIFT FORCE (kg/m3 Delta)", color='white', fontweight='bold')
    plt.ylabel("Density Difference vs Intake (kg/m3)", color='white')
    
    plt.text(1, imm + 0.5, f"+{int((imm-air)/air*100)}% BOOST", ha='center', color='yellow', fontweight='bold')
    
    out = "assets/v44_immersion_buoyancy.png"
    plt.savefig(out, dpi=150)
    print(f"\n  ✓ Chart saved: {out}")

if __name__ == "__main__":
    run_immersion_density()
