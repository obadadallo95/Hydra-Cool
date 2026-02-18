"""
Hydra-Cool Simulation [CODE] — A04: Temperature Delta Sensitivity
===================================================================
Sweeps the ΔT parameter to see how it affects the system balance.

Physics relations:
- Higher ΔT -> Lower Mass Flow Needed (Linear) -> Much Lower Friction (Squared)
- Higher ΔT -> Higher Buoyancy (Density difference increases)

Hypothesis:
- Increasing ΔT is the most effective way to improve system performance.

Key assumptions:
- IT Load: 100 MW
- Depth: 500m
- Pipe Dia: 1.5m
- Tower Height: Fixed at 20m (Near optimal from A03)

Expected output:
- Heatmap or Multi-line chart showing Net Power vs ΔT.

Author: Obada Dallo
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# --- Constants ---
G = 9.81
CP_SEAWATER = 3993.0
VISCOSITY = 1.3e-6
DEPTH = 500.0
HUMAN_HEIGHT_TOWER = 20.0
PIPE_DIA = 1.5
ROUGHNESS = 0.04e-3
IT_LOAD = 100e6

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def get_friction_factor(re, relative_roughness):
    if re < 2300: return 64.0 / re
    return 0.25 / (np.log10( (relative_roughness/3.7) + (5.74/(re**0.9)) ))**2

def seawater_density(temp_c):
    return 1028.17 - 0.0663 * temp_c - 0.0038 * (temp_c ** 2)

def run_simulation():
    print("Hydra-Cool A04: Running Temperature Sensitivity...")
    
    delta_ts = np.linspace(10, 60, 51)
    net_powers = []
    flow_rates = []
    buoy_heads = []
    
    fixed_len = DEPTH + 2*HUMAN_HEIGHT_TOWER + 200
    
    for dt in delta_ts:
        t_in = 5.0
        t_out = 5.0 + dt
        
        rho_in = seawater_density(t_in)
        rho_out = seawater_density(t_out)
        delta_rho = rho_in - rho_out
        
        # Flow
        q_mass = IT_LOAD / (CP_SEAWATER * dt)
        q_vol = q_mass / rho_out
        v = q_vol / (np.pi * (PIPE_DIA/2)**2)
        flow_rates.append(q_mass)
        
        # Buoyancy Head (Natural Boost from Depth)
        # Head = Depth * (d_rho / rho_out)
        h_boost = DEPTH * (delta_rho / rho_out)
        buoy_heads.append(h_boost)
        
        # Friction
        re = (v * PIPE_DIA) / VISCOSITY
        f = get_friction_factor(re, ROUGHNESS/PIPE_DIA)
        h_loss_fric = f * (fixed_len/PIPE_DIA) * (v**2)/(2*G)
        h_loss_hx = 30000 / (rho_in * G) # 30 kPa
        h_loss_tot = h_loss_fric + h_loss_hx + (2.0 * v**2/(2*G))
        
        # Balance
        # Pump Head = Tower - Boost + Losses
        h_pump = HUMAN_HEIGHT_TOWER - h_boost + h_loss_tot
        if h_pump < 0: h_pump = 0 # Throttled
        
        # Turbine Head = Tower
        h_turb = HUMAN_HEIGHT_TOWER
        
        p_gen = 0.88 * rho_out * G * q_vol * h_turb
        p_cons = (rho_out * G * q_vol * h_pump) / 0.85
        
        net_powers.append((p_gen - p_cons)/1000)

    # Visualization
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color = '#FF4081'
    ax1.set_xlabel('Temperature Difference ΔT [°C]', fontsize=12)
    ax1.set_ylabel('Net Power [kW]', color=color, fontsize=12)
    ax1.plot(delta_ts, net_powers, color=color, linewidth=3)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axhline(0, color='white', linestyle='--', alpha=0.5)
    
    ax2 = ax1.twinx()  
    color2 = '#00E5FF'
    ax2.set_ylabel('Required Flow Rate [kg/s]', color=color2, fontsize=12)
    ax2.plot(delta_ts, flow_rates, color=color2, linestyle='--', linewidth=2)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    plt.title(f"A04: Impact of ΔT on Performance\n(Fixed Tower={HUMAN_HEIGHT_TOWER}m, Depth={DEPTH}m)", fontsize=14)
    ax1.grid(True, alpha=0.2)
    
    # Annotate Zero Crossing
    # interpolated
    for i in range(len(net_powers)-1):
        if net_powers[i] < 0 and net_powers[i+1] > 0:
            # Linear interp
            y1, y2 = net_powers[i], net_powers[i+1]
            x1, x2 = delta_ts[i], delta_ts[i+1]
            x_cross = x1 + (0 - y1)*(x2-x1)/(y2-y1)
            ax1.plot(x_cross, 0, 'wo', markersize=8)
            ax1.annotate(f"Breakeven\nΔT ~ {x_cross:.1f}°C", (x_cross, 0), xytext=(10, 20), textcoords='offset points')
            print(f"Breakeven at ΔT = {x_cross:.2f}°C")
            break
            
    output_path = os.path.join(ASSET_DIR, "A04_temp_sensitivity.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
