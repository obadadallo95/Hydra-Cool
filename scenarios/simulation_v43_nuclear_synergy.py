"""
Hydra-Cool Simulation v43.0 — NUCLEAR SMR SYNERGY (The Microsoft Play)
======================================================================
Scenario: Pairing a 300MWe Small Modular Reactor (SMR) with the Data Center.

PHYSICS:
  - SMR Efficiency: ~33%.
  - Electrical Output: 300 MW (Powers the DC).
  - Waste Heat Rejection: ~600 MW.
  - IT Load: 300 MW (Matches SMR output).
  - Total Cooling Load: 300 (IT) + 600 (SMR) = 900 MW.

CHALLENGE:
  - Can Hydra-Cool handle 900MW?
  - Do we dump the SMR heat into the same loop?
  - Opportunity: Desalination?

OBJECTIVE:
  - Calculate Flow Rate for 900MW.
  - Assess if "Waste Heat" can drive stronger Buoyancy/Turbine.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def run_nuclear_synergy():
    print("="*60)
    print("  HYDRA-COOL v43: THE NUCLEAR OPTION")
    print("="*60)
    
    P_ELEC = 300.0 # MW (SMR Output)
    P_HEAT_SMR = 600.0 # MW (SMR Waste Heat)
    P_HEAT_IT  = 300.0 # MW (IT Load)
    
    TOTAL_mw = P_HEAT_SMR + P_HEAT_IT
    
    print(f"\n  [ENERGY BALANCE]")
    print(f"  SMR Electric Output: {P_ELEC} MW (Powers the Servers)")
    print(f"  SMR Waste Heat:      {P_HEAT_SMR} MW")
    print(f"  IT Waste Heat:       {P_HEAT_IT} MW")
    print(f"  --------------------------------")
    print(f"  TOTAL COOLING LOAD:  {TOTAL_mw} MW (Gigantic)")
    
    # Flow Calculation
    # Keep Delta T high (e.g. 50C rise) to maximize buoyancy/turbine
    dt = 50.0
    cp = 4.0
    flow_kg_s = (TOTAL_mw * 1000) / (cp * dt) # 4500 kg/s
    
    # Turbine Recovery on 4500 kg/s dropping 40m
    # P = rho * g * Q * H * eff
    recovery_mw = (flow_kg_s * 9.81 * 40.0 * 0.85) / 1e6
    
    print(f"\n  [HYDRAULIC IMPACT]")
    print(f"  Required Flow:       {flow_kg_s/1000:.1f} m3/s")
    print(f"  Turbine Recovery:    {recovery_mw:.1f} MW")
    
    print(f"\n  [VERDICT]")
    print(f"  - We recover ~1.5 MW from the Gravity Engine.")
    print(f"  - But we are managing 900 MW of heat.")
    print(f"  - SYNERGY: YES. The heavy flow makes the Turbine efficient.")
    print(f"  - RISK: Thermal Plume is massive. 900MW scale requires offshore discharge.")
    
    # Advanced: Desalination Co-Gen?
    # Use SMR heat for Flash Distillation?
    print(f"  - BONUS: 600MW SMR heat is high grade (300C steam).")
    print(f"    Don't dump it in Hydra-Cool.")
    print(f"    Use it for District Heating or Desalination.")
    print(f"    Use it for District Heating or Desalination.")
    print(f"    Hydra-Cool only handles the 300MW IT Load.")

    # Plotting
    os.makedirs("assets", exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')
    
    labels = ['IT Load (300 MW)', 'SMR Output (300 MW)', 'SMR Waste Heat (600 MW)']
    values = [P_HEAT_IT, P_ELEC, P_HEAT_SMR]
    colors = ['#00FFCC', 'purple', 'red']
    
    plt.bar(labels, values, color=colors, alpha=0.8)
    
    # Total Line
    plt.axhline(TOTAL_mw, color='orange', linestyle='--', label=f'Total Cooling Requirement ({TOTAL_mw} MW)')
    plt.text(1, TOTAL_mw + 20, "900 MW THERMAL LOAD!", ha='center', color='orange', fontweight='bold')
    
    plt.title("v43: THE NUCLEAR HEAT BEHEMOTH", color='white', fontweight='bold')
    plt.ylabel("Power (MW)", color='white')
    plt.legend()
    
    out = "assets/v43_nuclear_load.png"
    plt.savefig(out, dpi=150)
    print(f"\n  ✓ Chart saved: {out}")

if __name__ == "__main__":
    run_nuclear_synergy()
