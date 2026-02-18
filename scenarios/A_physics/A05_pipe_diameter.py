"""
Hydra-Cool Simulation [CODE] — A05: Flow Rate vs Pipe Diameter
==============================================================
Analyzes the trade-off between Pipe Diameter and Friction Loss.

Physics basis:
- Friction Head Loss ∝ 1/D^5 (Darcy-Weisbach with constant Q)
- Larger pipe = Massive reduction in pump power.

Key assumptions:
- IT Load: 100 MW
- ΔT: 40°C (Fixed)
- Length: 1000m (Representative loop length)
- Depth Boost included (Fixed at 500m depth value)

Expected output:
- Curve showing Friction Loss vs Diameter.
- Curve showing Net Power vs Diameter.

Author: Obada Dallo
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# --- Constants ---
G = 9.81
CP_SEAWATER = 3993.0
VISCOSITY = 1.3e-6
IT_LOAD = 100e6
DT = 40.0
LENGTH = 1000.0
DEPTH = 500.0

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def get_friction_factor(re, relative_roughness):
    if re < 2300: return 64.0 / re
    return 0.25 / (np.log10( (relative_roughness/3.7) + (5.74/(re**0.9)) ))**2

def seawater_density(temp_c):
    return 1028.17 - 0.0663 * temp_c - 0.0038 * (temp_c ** 2)

def run_simulation():
    print("Hydra-Cool A05: Running Pipe Diameter Analysis...")
    
    # Fixed Flow
    rho = seawater_density(5 + DT)
    q_mass = IT_LOAD / (CP_SEAWATER * DT)
    q_vol = q_mass / rho
    
    diameters = np.linspace(0.5, 3.0, 50)
    head_losses = []
    velocities = []
    
    for d in diameters:
        v = q_vol / (np.pi * (d/2)**2)
        velocities.append(v)
        
        re = (v * d) / VISCOSITY
        f = get_friction_factor(re, 0.04e-3/d)
        
        h_loss = f * (LENGTH/d) * (v**2)/(2*G)
        head_losses.append(h_loss)

    # Visualization
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color = '#FFC107'
    ax1.set_xlabel('Pipe Diameter [m]', fontsize=12)
    ax1.set_ylabel('Friction Head Loss [m/km]', color=color, fontsize=12)
    ax1.plot(diameters, head_losses, color=color, linewidth=3)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim(0, 10) # Log scale might be better but linear shows the "Wall"
    
    ax2 = ax1.twinx()
    color2 = '#B0BEC5'
    ax2.set_ylabel('Flow Velocity [m/s]', color=color2, fontsize=12)
    ax2.plot(diameters, velocities, color=color2, linestyle='--', linewidth=2)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Thresholds
    ax1.axhline(1.0, color='white', linestyle=':', alpha=0.5)
    ax1.text(0.6, 1.2, "Low Loss Zone (<1m)", color='white', fontsize=9)
    
    plt.title(f"A05: Pipe Sizing Trade-off\n(Flow: {q_vol:.2f} m³/s)", fontsize=14)
    ax1.grid(True, alpha=0.2)
    
    output_path = os.path.join(ASSET_DIR, "A05_pipe_diameter.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
