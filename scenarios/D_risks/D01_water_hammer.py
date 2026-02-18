"""
Hydra-Cool Simulation [CODE] — D01: Water Hammer Analysis
=========================================================
Safety Critical: Analysis of hydraulic shock.

Physics:
- Joukowsky Equation: ΔP = ρ * a * Δv
- Wave Speed (a) in water/pipe combo.

Scenario:
- Emergency shutdown (Valve closes in T seconds).
- Comparison of Fast Close (Dangerous) vs Slow Close (Safe).

Goal:
- Determine if a Surge Tank is needed.
- Determine minimum valve closure time.

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool D01: Running Water Hammer Analysis...")
    
    # Parameters
    L = 3000.0   # Pipe Length (m)
    v0 = 0.6     # Initial Velocity (m/s) (From A02)
    rho = 1025.0
    
    # Wave speed (a)
    # Steel pipe: ~1000-1200 m/s
    # HDPE pipe: ~300-400 m/s (more flexible, absorbs shock better)
    # Let's assume HDPE for the sea line to be safe? Or Steel?
    # Let's simulate Steel for worst case.
    a = 1000.0 
    
    # Critical Time Tc = 2L / a
    Tc = 2 * L / a # 6 seconds
    
    # Joukowsky Pressure Rise (Instant closure)
    dP_max = rho * a * v0 # Pa
    dP_max_bar = dP_max / 1e5
    
    print(f"Critical Closure Time: {Tc:.1f} s")
    print(f"Max Surge Head (Instant): {dP_max_bar:.1f} bar")
    
    # Simulation: Valve Closure Time
    closure_times = np.linspace(1, 60, 60)
    surge_pressures = []
    
    for t in closure_times:
        if t < Tc:
            # Fast closure: Full Joukowsky
            surge = dP_max_bar
        else:
            # Slow closure: Dampened
            # Approx formula: dP = dP_max * (Tc / t)
            surge = dP_max_bar * (Tc / t)
        surge_pressures.append(surge)
        
    # Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(closure_times, surge_pressures, color='#FF5252', linewidth=3)
    
    # Zones
    ax.axvspan(0, Tc, color='#FF5252', alpha=0.3, label='Dangerous Zone (Fast Close)')
    ax.axvspan(Tc, 60, color='#69F0AE', alpha=0.1, label='Safe Zone (Slow Close)')
    
    ax.axvline(Tc, color='white', linestyle='--', linewidth=1)
    ax.text(Tc + 1, dP_max_bar/2, f"Critical Time: {Tc:.1f}s", color='white')
    
    ax.set_xlabel("Valve Closure Time [s]")
    ax.set_ylabel("Pressure Surge [bar]")
    ax.set_title(f"D01: Water Hammer - Surge Pressure vs Closure Time\n(Pipe L={L}m, v={v0}m/s)", fontsize=14)
    ax.grid(True, alpha=0.2)
    ax.legend()
    
    # Design Limit Line (PN10 or PN16 pipe)
    ax.axhline(10, color='#FFC107', linestyle=':')
    ax.text(40, 10.5, "PN10 Pipe Limit (10 bar)", color='#FFC107')
    
    output_path = os.path.join(ASSET_DIR, "D01_water_hammer.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
