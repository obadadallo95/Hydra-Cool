"""
Hydra-Cool Simulation [CODE] — D02: Biofouling Impact
=====================================================
Models the degradation of performance due to marine growth.

Physics:
- Biofouling increases Roughness (ε).
- Friction Factor (f) increases.
- Pressure Drop increases -> Pump Power increases.

Scenario:
- 5 Year period.
- Cleaning (Pigging) every 1 year.
- Shows typical "Sawtooth" performance curve.

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool D02: Running Biofouling Analysis...")
    
    months = np.arange(0, 60)
    
    # Base Roughness
    eps_base = 0.05e-3
    eps_fouled_max = 2.0e-3 # 2mm growth (significant)
    
    roughness = []
    accum = eps_base
    
    # Growth Model
    for m in months:
        if m % 12 == 0 and m > 0:
            accum = eps_base # Cleaned
        else:
            accum += (eps_fouled_max - eps_base) / 12 * 0.5 # Growth rate
            
        roughness.append(accum * 1000) # mm
    
    # Power Penalty Proxy (proportional to Roughness^0.25 roughly? No, use f)
    # Simplified: Power penalty %
    power_penalty = [(r / (eps_base*1000)) * 5 for r in roughness] # Scaling factor for visualization
    # Realistically, f doubles -> Head doubles -> Power doubles?
    # f changes from 0.015 to 0.030 approx. So yes, power doubles.
    
    # Visualization
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color = '#B2FF59'
    ax1.set_xlabel('Time [Months]')
    ax1.set_ylabel('Effective Pipe Roughness [mm]', color=color)
    ax1.plot(months, roughness, color=color, linewidth=2, label='Biofouling Growth')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.2)
    
    ax2 = ax1.twinx()
    color2 = '#FF5252'
    ax2.set_ylabel('Pump Power Penalty [% increase]', color=color2)
    # Crude approx for viz
    penalty_curve = [r*20 for r in roughness] 
    ax2.plot(months, penalty_curve, color=color2, linestyle='--', label='Power Cost')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Maintenance markers
    for m in range(12, 60, 12):
        ax1.axvline(m, color='white', linestyle=':', alpha=0.5)
        if m == 24:
            ax1.text(m, 1.5, "Annual Cleaning\n(Pigging)", ha='center', color='white', fontsize=10)
            
    plt.title("D02: Biofouling Accumulation & Maintenance Cycles", fontsize=14)
    
    output_path = os.path.join(ASSET_DIR, "D02_biofouling_impact.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
