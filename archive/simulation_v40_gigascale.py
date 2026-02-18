"""
Hydra-Cool Simulation v40.0 — THE 1GW SCALING LIMIT (Gigascale)
===============================================================
Scenario: AI Power Demand explodes. Client wants 1 Gigawatt (1000 MW).
Can we scale the "Smart Cycle"?

PHYSICS:
  - Q roughly scales with Power.
  - Pipe Diameter scales with sqrt(Q).
  - Tunnels vs Pipes.

OBJECTIVE:
  - Calculate Flow Rate for 1GW.
  - Sizing the Intake Pipe.
  - Compare "1 Big Pipe" vs "10 Modular Pipes".
"""

import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def run_gigascale():
    print("="*60)
    print("  HYDRA-COOL v40: THE 1GW SCALING CHALLENGE")
    print("="*60)
    
    # 1. Flow Calculation
    # 100MW = 2.0 m3/s (approx from prev sim)
    # 1000MW = 20.0 m3/s
    
    Q_gw = 20.0 # m3/s
    V_max = 2.5 # m/s (Economic Velocity limit)
    
    # Area = Q / V
    Area = Q_gw / V_max
    
    # Diameter = sqrt(4A / pi)
    Dia = math.sqrt(4 * Area / math.pi)
    
    print(f"\n  [REQUIREMENTS FOR 1 GW COOLING]")
    print(f"  Heat Load:        1,000 MW")
    print(f"  Flow Rate:        {Q_gw} m3/s (20 tons/sec)")
    print(f"  Target Velocity:  {V_max} m/s")
    
    print(f"\n  [ENGINEERING SIZING]")
    print(f"  Required Area:    {Area:.2f} m2")
    print(f"  Single Pipe Dia:  {Dia:.2f} METERS")
    
    print("-" * 60)
    
    if Dia > 3.0:
        print("  VERDICT: 🛑 IMPOSSIBLE PIPE SIZE (Standard HDPE maxes at ~2.5m)")
        print("           Solution: TUNNEL BORING MACHINE (TBM) required.")
        print("           Or Modular approach.")
    
    # Modular Comparison
    # Option A: 1x 3.2m Tunnel
    # Option B: 5x 1.4m Pipes (Standard HDPE)
    
    area_1400 = math.pi * (1.4/2)**2
    count = math.ceil(Area / area_1400)
    
    print(f"\n  [MODULAR ALTERNATIVE]")
    print(f"  Using Standard DN1400 Pipes:")
    print(f"  Count Required:   {count} Pipes")
    print(f"  Layout:           5+5 Configuration")
    
    plot_scaling(Dia, count)

def plot_scaling(single_dia, count):
    os.makedirs("assets", exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.style.use('dark_background')
    
    # Visual comparison circle
    circle1 = plt.Circle((0, 0), single_dia/2, color='c', alpha=0.5, label=f'Single Tunnel ({single_dia:.2f}m)')
    ax.add_patch(circle1)
    
    # Modular circles
    # arrange in a ring
    for i in range(count):
        angle = 2 * np.pi * i / count
        r = single_dia * 0.8 # Orbit radius
        x = r * np.cos(angle)
        y = r * np.sin(angle)
        circle = plt.Circle((x, y), 0.7, color='y', alpha=0.5) # 1.4m dia = 0.7 rad
        ax.add_patch(circle)
    
    # Legend trick for modular
    ax.add_patch(plt.Circle((100,100), 0.7, color='y', alpha=0.5, label=f'{count}x DN1400 Pipes'))
    
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    ax.set_title("v40: GIGASCALE INFRASTRUCTURE - Tunnel vs Array", color='white', fontweight='bold')
    ax.axis('off')
    
    out = "assets/v40_scaling_limit.png"
    plt.savefig(out, dpi=150)
    print(f"\n  ✓ Chart saved: {out}")

if __name__ == "__main__":
    run_gigascale()
