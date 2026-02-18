"""
Hydra-Cool Simulation v37.0 — CHAOS THEORY: WATER HAMMER (The "Pipe Killer")
============================================================================
Simulation of Hydraulic Transients (Surge & Vacuum).

SCENARIO:
  - System running at full load (Flow Velocity = 2.5 m/s).
  - Emergency Shutdown (ESD) triggers.
  - "Fail-Safe" Valve closes in 1.0 second (Too fast!).

PHYSICS (Joukowsky Equation):
  - Pressure Rise: dP = rho * c * dV
  - Wave Speed c: ~1000-1200 m/s (Steel Pipe with Water).
  - Density rho: ~1000 kg/m3.
  - Velocity Change dV: 2.5 m/s.

RISK:
  1. POSITIVE SURGE (Upstream of Valve): Tube Burst?
  2. NEGATIVE SURGE (Downstream of Valve): Vacuum Collapse? (Buckling).

OBJECTIVE:
  - Calculate Peak Pressure.
  - Check against Pipe Rating (PN16 = 16 Bar).
  - Recommend Mitigation (Surge Tank / Air Valve).
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def run_water_hammer():
    print("="*60)
    print("  HYDRA-COOL v37: WATER HAMMER & VACUUM COLLAPSE")
    print("="*60)
    
    # Constants
    RHO = 1000.0   # kg/m3
    C_WAVE = 1200.0 # m/s (Steel Pipe)
    V_FLOW = 2.5   # m/s
    PIPE_RATING_BAR = 16.0 # PN16 Standard
    BUCKLING_LIMIT = -0.5  # Bar (Thin wall pipe collapses at -0.5 bar vacuum)
    
    # 1. Joukowsky Calculation
    surge_pa = RHO * C_WAVE * V_FLOW
    surge_bar = surge_pa / 1e5
    
    static_bar = 4.0 # 40m head
    
    peak_pressure = static_bar + surge_bar
    min_pressure  = static_bar - surge_bar
    
    print(f"\n  [PHYSICS INPUTS]")
    print(f"  Flow Velocity:    {V_FLOW} m/s")
    print(f"  Wave Speed:       {C_WAVE} m/s")
    print(f"  Static Head:      {static_bar} Bar")
    
    print(f"\n  [TRANSIENT RESULTS]")
    print(f"  Joukowsky Surge:  +/- {surge_bar:.1f} Bar")
    print(f"  Peak Pressure:    {peak_pressure:.1f} Bar")
    print(f"  Min Pressure:     {min_pressure:.1f} Bar (Theoretical)")
    
    # Clamping Vacuum to -1.0 Bar (Vapor Pressure)
    if min_pressure < -1.0:
        min_real = -1.0
        print(f"  Real Min Press:   -1.0 Bar (Vapor Cavity Formation)")
    else:
        min_real = min_pressure

    print("-" * 60)
    
    # Verdicts
    verdict1 = "✅ OK"
    if peak_pressure > PIPE_RATING_BAR:
        verdict1 = f"💀 BURST (Exceeds PN{int(PIPE_RATING_BAR)})"
        
    verdict2 = "✅ OK"
    if min_real < BUCKLING_LIMIT:
        verdict2 = f"💀 COLLAPSE/BUCKLING ( Vacuum < {BUCKLING_LIMIT} Bar )"
        
    print(f"  RISK 1 (Burst):   {verdict1}")
    print(f"  RISK 2 (Vacuum):  {verdict2}")
    
    print("-" * 60)
    print("  ROOT CAUSE: Valve closure time (1s) < Critical Time (2L/c).")
    print("  MITIGATION: Surge Tanks + Air Vacuum Breakers + Slow Closing (60s).")

    # Plotting
    plot_transient(static_bar, surge_bar, PIPE_RATING_BAR, BUCKLING_LIMIT)

def plot_transient(static, surge, rating, buckling):
    os.makedirs("assets", exist_ok=True)
    t = np.linspace(0, 2, 100)
    
    # Simulation of pressure wave dampening
    pressure = static + surge * np.exp(-t*2) * np.sin(2 * np.pi * 5 * t)
    
    # Clip for vacuum
    pressure = np.maximum(pressure, -1.0)
    
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')
    
    plt.plot(t, pressure, 'r-', linewidth=2, label='Transient Pressure')
    plt.axhline(rating, color='y', linestyle='--', label=f'Pipe Rating ({int(rating)} Bar)')
    plt.axhline(buckling, color='c', linestyle='--', label='Buckling Limit (-0.5 Bar)')
    plt.axhline(static, color='w', linestyle=':', label='Static Head')
    
    plt.fill_between(t, pressure, rating, where=[p > rating for p in pressure], color='red', alpha=0.5, label='Execeds Rating')
    plt.fill_between(t, pressure, buckling, where=[p < buckling for p in pressure], color='cyan', alpha=0.5, label='Vacancy Risk')
    
    plt.title("v37: WATER HAMMER - The Pipe Killer", color='white', fontweight='bold')
    plt.ylabel("Pressure (Bar)", color='white')
    plt.xlabel("Time (seconds)", color='white')
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.2)
    
    out = "assets/v37_pressure_transient.png"
    plt.savefig(out, dpi=150)
    print(f"\n  ✓ Chart saved: {out}")

if __name__ == "__main__":
    run_water_hammer()
