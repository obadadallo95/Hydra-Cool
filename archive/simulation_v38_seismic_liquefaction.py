"""
Hydra-Cool Simulation v38.0 — SEISMIC LIQUEFACTION (The Earth Trap)
===================================================================
Scenario: Magnitude 7.0 Earthquake at Coastal Site.
Ground: Saturated Sandy Soil (Standard for reclaimed coastal land).

PHYSICS:
  - Cyclic Stress Ratio (CSR) induced by quake.
  - Cyclic Resistance Ratio (CRR) of soil.
  - Factor of Safety (FoS) = CRR / CSR.
  - If FoS < 1.0, the soil turns to liquid.

IMPACT:
  - The elevated reservoir (Massive Concrete Structure) settles unevenly.
  - Pipe shear failure at connection points.
  - Total loss of "Gravity Battery".

OBJECTIVE:
  - Calculate FoS for a typical coastal site (PGA = 0.3g).
  - Estimate Settlement.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def run_liquefaction():
    print("="*60)
    print("  HYDRA-COOL v38: SEISMIC LIQUEFACTION RISK")
    print("="*60)
    
    # Inputs
    PGA = 0.30       # Peak Ground Acceleration (g) - High Seismicity
    MAGNITUDE = 7.5  # Richter
    DEPTH = 10.0     # Meters (Soil depth of interest)
    GW_TABLE = 1.0   # Meters (Ground water level - Coastal = High)
    
    print(f"\n  [SITE CONDITIONS]")
    print(f"  PGA:              {PGA} g")
    print(f"  Magnitude:        {MAGNITUDE}")
    print(f"  Soil Type:        Loose Coastal Sand (SPT N=10)")
    print(f"  Ground Water:     {GW_TABLE}m (Saturated)")
    
    # Simplified Seed & Idriss Method
    # CSR = 0.65 * (a_max/g) * (sigma_v / sigma_v_prime) * rd
    rd = 1.0 - 0.00765 * DEPTH
    sigma_v = 18.0 * DEPTH # Total stress
    sigma_v_prime = (18.0 * GW_TABLE) + (8.0 * (DEPTH - GW_TABLE)) # Effective stress
    
    CSR = 0.65 * PGA * (sigma_v / sigma_v_prime) * rd
    
    # CRR based on SPT N=10 (Clean Sand) -> Approx 0.11 for Mag 7.5
    CRR_75 = 0.11
    # Magnitude Scaling Factor
    MSF = 10**2.24 / MAGNITUDE**2.56
    CRR = CRR_75 * MSF
    
    FoS = CRR / CSR
    
    print(f"\n  [ANALYSIS]")
    print(f"  Cyclic Stress (Load):   {CSR:.3f}")
    print(f"  Cyclic Resistance:      {CRR:.3f}")
    print(f"  FACTOR OF SAFETY:       {FoS:.3f}")
    
    print("-" * 60)
    if FoS < 1.0:
        print("  VERDICT: 💀 LIQUEFACTION CONFIRMED (FoS < 1)")
        print("  CONSEQUENCE: The reservoir foundation loses 90% bearing capacity.")
        print("               Structure tilts or sinks. Pipes shear.")
        print("  MITIGATION:  Deep Pile Foundations (End-Bearing on Bedrock)")
        print("               or Soil Mixing/Grouting (Expensive).")
    else:
        print("  VERDICT: ✅ STABLE GROUND")

    # Plotting
    os.makedirs("assets", exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')
    
    # Bar Chart: Load (CSR) vs Strength (CRR)
    labels = ['Earthquake Load (CSR)', 'Soil Strength (CRR)']
    values = [CSR, CRR]
    colors = ['red', 'green']
    
    plt.bar(labels, values, color=colors, alpha=0.8)
    plt.axhline(CSR, color='red', linestyle='--', alpha=0.5)
    plt.text(0, CSR + 0.01, f"{CSR:.3f}", ha='center', color='white', fontweight='bold')
    plt.text(1, CRR + 0.01, f"{CRR:.3f}", ha='center', color='white', fontweight='bold')
    
    # Verdict Text
    if FoS < 1.0:
        plt.text(0.5, max(CSR, CRR)*0.5, "⚠️ LIQUEFACTION FAILURE", ha='center', color='yellow', fontsize=14, fontweight='bold', bbox=dict(facecolor='red', alpha=0.5))
        
    plt.title(f"v38: SEISMIC RISK (Mag {MAGNITUDE}) - Factor of Safety {FoS:.2f}", color='white', fontweight='bold')
    plt.ylabel("Cyclic Ratio", color='white')
    
    out = "assets/v38_liquefaction_risk.png"
    plt.savefig(out, dpi=150)
    print(f"\n  ✓ Chart saved: {out}")

if __name__ == "__main__":
    run_liquefaction()
