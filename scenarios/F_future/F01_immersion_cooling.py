"""
Hydra-Cool Simulation [CODE] — F01: Immersion Cooling Integration
=================================================================
"The future is hotter."

Immersion Cooling allows chips to run hotter (T_out = 65°C+).
This means Higher ΔT -> Lower Flow -> Lower Friction -> Higher Net Power.

Scenario:
- Sweep T_out from 50°C (Standard) to 70°C (Immersion).
- Calculate Net Power.
- Show the "Sweet Spot" for next-gen data centers.

Output:
- Performance Curve (Net Power vs Delta T).

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def seawater_density(temp_c):
    return 1028.17 - 0.0663 * temp_c - 0.0038 * (temp_c ** 2)

def run_simulation():
    print("Hydra-Cool F01: Running Immersion Cooling Analysis...")
    
    t_intake = 5.0
    t_out_range = np.linspace(45, 75, 50)
    
    net_powers = []
    
    # Constants (From A04)
    IT_LOAD = 100e6
    CP = 3993.0
    G = 9.81
    DEPTH = 500.0
    TOWER = 20.0
    PIPE_DIA = 1.5
    ROUGHNESS = 0.04e-3
    VISC = 1.3e-6
    ETA_T = 0.88
    ETA_P = 0.85
    
    for t_out in t_out_range:
        dt = t_out - t_intake
        rho_out = seawater_density(t_out)
        rho_in = seawater_density(t_intake)
        delta_rho = rho_in - rho_out
        
        # Flow
        q_mass = IT_LOAD / (CP * dt)
        q_vol = q_mass / rho_out
        v = q_vol / (np.pi * (PIPE_DIA/2)**2)
        
        # Boost
        h_boost = DEPTH * (delta_rho / rho_out)
        
        # Friction
        re = (v * PIPE_DIA) / VISC
        # approx f
        f = 0.015 # Simplified for speed/stability in this loop
        l_total = DEPTH + 2*TOWER + 200
        h_loss = f * (l_total/PIPE_DIA) * (v**2)/(2*G) + 3.0*(v**2)/(2*G) + 30000/(rho_in*G)
        
        # Power
        h_pump = TOWER - h_boost + h_loss
        if h_pump < 0: h_pump = 0
        
        p_cons = (rho_out * G * q_vol * h_pump) / ETA_P
        p_gen = ETA_T * rho_out * G * q_vol * TOWER
        
        net_powers.append((p_gen - p_cons)/1000) # kW

    # Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    color = '#D500F9'
    ax.plot(t_out_range, net_powers, color=color, linewidth=3)
    
    ax.set_xlabel("Outlet Temperature [°C]")
    ax.set_ylabel("Net Power Generation [kW]")
    ax.set_title("F01: Immersion Cooling Synergy\n(Higher Temp = Higher Efficiency)", fontsize=14)
    ax.grid(True, alpha=0.2)
    
    # Zones
    ax.axvspan(45, 55, color='#90A4AE', alpha=0.1, label='Standard Air/Water')
    ax.axvspan(55, 75, color='#D500F9', alpha=0.1, label='Immersion Cooling Zone')
    
    ax.axhline(0, color='white', linestyle='--')
    ax.text(60, 5, "Net Positive Power Generation", color=color, fontweight='bold')
    
    ax.legend(loc='upper left')

    output_path = os.path.join(ASSET_DIR, "F01_immersion_cooling.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
