"""
Hydra-Cool Simulation v35.0 — GALVANIC FAILURE (Corrosion Time Bomb)
====================================================================
The Hidden Killer: Connecting Titanium (Noble) to Carbon Steel (Active)
in an electrolyte (Seawater).

SCENARIO:
  - Isolation gasket fails or is forgotten during retrofit.
  - ICCP (Impressed Current Cathodic Protection) unit loses power.
  - Result: The Steel flange becomes the Anode and dissolves to protect the Titanium.

PHYSICS:
  - Corrosion Rate (mm/year) = 327 * I_corr * MW / (n * rho)
  - For Steel coupled to Ti: Rate is massive (~2-5 mm/year).
  
TIMELINE:
  - Flange thickness: 20mm.
  - Leak threshold: 10mm (structural failure).
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def run_galvanic_failure():
    print("="*60)
    print("  HYDRA-COOL v35: GALVANIC CORROSION FAILURE")
    print("="*60)
    
    initial_thickness = 20.0 # mm
    failure_thickness = 10.0 # mm
    
    # Rates
    rate_protected = 0.1 # mm/year (Normal)
    rate_galvanic  = 4.5 # mm/year (Ti-Steel coupling, violent)
    
    print(f"\n  {'Month':<5} {'Thickness':<10} {'Protection':<15} {'Status':<20}")
    print("-" * 65)
    
    current_thick = initial_thickness
    
    for month in range(1, 37): # 3 Years
        # ICCP Fails at Month 6
        if month < 6:
            protection = "ON (ICCP)"
            loss = rate_protected / 12
        else:
            protection = "OFF (FAILED)"
            loss = rate_galvanic / 12
            
        current_thick -= loss
        
        status = "✅ OK"
        if current_thick < failure_thickness:
            status = "💀 LEAK / BURST"
            
        marker = "⚡" if month == 6 else ""
        print(f"  {month:>2}     {current_thick:>5.2f}mm     {protection:<15} {status} {marker}")
        
        if current_thick < failure_thickness:
            print(f"\n  FAILURE EVENT at Month {month}!")
            print(f"  Cause: Silent failure of ICCP leading to rapid galvanic attack.")
            print(f"  Result: 100MW Cooling Loss. Saltwater floods pump room.")
            break
            
    # Plotting
    os.makedirs("assets", exist_ok=True)
    months = np.arange(1, 37)
    thickness = []
    curr = initial_thickness
    for m in months:
        loss = (rate_protected if m < 6 else rate_galvanic) / 12
        curr -= loss
        thickness.append(curr)
        
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')
    
    plt.plot(months, thickness, 'y-', linewidth=2, label='Pipe Wall Thickness')
    plt.axhline(failure_thickness, color='r', linestyle='--', label='Burst Threshold (10mm)')
    plt.axvline(6, color='w', linestyle=':', label='ICCP Failure')
    plt.axvline(32, color='r', linestyle=':', label='PIPE BURST')
    
    plt.fill_between(months, thickness, failure_thickness, where=[t < failure_thickness for t in thickness], color='red', alpha=0.5)
    
    plt.title("v35: GALVANIC TIME BOMB - Failure Timeline", color='white', fontweight='bold')
    plt.ylabel("Wall Thickness (mm)", color='white')
    plt.xlabel("Month", color='white')
    plt.legend()
    plt.grid(True, alpha=0.2)
    
    plt.savefig("assets/v35_corrosion_timeline.png", dpi=150)
    print("\n  ✓ Chart saved: assets/v35_corrosion_timeline.png")
            
if __name__ == "__main__":
    run_galvanic_failure()
