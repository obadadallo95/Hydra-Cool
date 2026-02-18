"""
Hydra-Cool Simulation [CODE] — A03: Tower Height Optimization
==============================================================
Sweeps the Tower Height parameter to find the optimal configuration
for Net Power Generation (or minimal Power Consumption).

Physics basis:
- Includes "Depth Boost": The density difference over the deep intake leg 
  vs the hypothetical hot column creates a natural pressure head at surface.
  Head_Boost = (ρ_cold - ρ_hot) * g * Depth
- Pump Head = H_tower - Head_Boost + Friction
- Turbine Head = H_tower * Efficiency

Key assumptions:
- Depth: 500m (Max benefit)
- IT Load: 100 MW @ ΔT 40°C
- Pipe Diameter: 1.5 m (Optimized for larger flow/lower friction)
- Friction scales with Height + Depth + 200m horizontal.

Expected output:
- A curve showing Net Power crossing zero (if possible) or the minimum loss point.

Author: Obada Dallo
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# --- Constants ---
G = 9.81
CP_SEAWATER = 3993.0
VISCOSITY = 1.3e-6

# --- Parameters ---
IT_LOAD = 100 * 1e6
DT = 40.0
T_INTAKE = 5.0
T_OUTLET = 45.0
DEPTH = 500.0         # Deep intake
PIPE_DIA = 1.5        # Large diameter
ROUGHNESS = 0.04e-3
ETA_TURBINE = 0.88    # High end
ETA_PUMP = 0.85       # High end
HX_DROP = 30000.0     # 30 kPa (Optimized)

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def get_friction_factor(re, relative_roughness):
    if re < 2300: return 64.0 / re
    return 0.25 / (np.log10( (relative_roughness/3.7) + (5.74/(re**0.9)) ))**2

def seawater_density(temp_c):
    return 1028.17 - 0.0663 * temp_c - 0.0038 * (temp_c ** 2)

def run_simulation():
    print("Hydra-Cool A03: Running Tower Height Optimization...")
    
    # 1. Flow Calculation
    rho_cold = seawater_density(T_INTAKE)
    rho_hot = seawater_density(T_OUTLET)
    delta_rho = rho_cold - rho_hot
    
    q_mass = IT_LOAD / (CP_SEAWATER * DT)
    q_vol_cold = q_mass / rho_cold
    q_vol_hot = q_mass / rho_hot # Volumetric flow increases as it heats
    
    velocity_cold = q_vol_cold / (np.pi * (PIPE_DIA/2)**2)
    velocity_hot = q_vol_hot / (np.pi * (PIPE_DIA/2)**2)
    
    print(f"Flow: {q_mass:.1f} kg/s. Delta_Rho: {delta_rho:.2f} kg/m³")

    # 2. Depth Boost (The "Free" Head)
    # The pressure at the surface from the cold intake is P_atm - losses.
    # But effectively, if we have a hot column balancing it?
    # Let's assume the "Natural Level" of the Hot Water is higher than sea level.
    # Level_Natural = Depth * (rho_cold - rho_hot) / rho_hot
    natural_head_boost = DEPTH * (delta_rho / rho_hot)
    print(f"Natural Buoyancy Head (from {DEPTH}m depth): {natural_head_boost:.2f} m")

    # 3. Sweep Heights
    heights = np.linspace(10, 250, 50)
    p_nets = []
    p_gens = []
    p_cons = []
    
    for h in heights:
        # Total Pipe Length = Depth (Intake) + H (Riser) + H (Downcomer)?
        # Or just H_riser + H_downcomer?
        # Let's assume Intake Pipe is separate.
        # Length = DEPTH (Intake) + H (Riser) + H (Penstock) + 200 (Horizontal)
        l_total = DEPTH + 2*h + 200 
        
        # Friction
        # Cold Leg
        re_cold = (velocity_cold * PIPE_DIA) / VISCOSITY
        f_cold = get_friction_factor(re_cold, ROUGHNESS/PIPE_DIA)
        head_loss_cold = f_cold * (DEPTH/PIPE_DIA) * (velocity_cold**2)/(2*G)
        
        # Hot Leg (Riser + Penstock + Horizontal)
        re_hot = (velocity_hot * PIPE_DIA) / VISCOSITY
        f_hot = get_friction_factor(re_hot, ROUGHNESS/PIPE_DIA)
        head_loss_hot = f_hot * ((2*h + 200)/PIPE_DIA) * (velocity_hot**2)/(2*G)
        
        total_head_loss_m = head_loss_cold + head_loss_hot + (HX_DROP / (rho_cold * G)) + (3.0 * velocity_hot**2/(2*G)) # Minor
        
        # Power Generation
        # Turbine Head = Gross H - Exit Losses?
        # Let's assume Turbine recovers full H (minus penstock friction included above).
        # P_gen = eta * rho * g * Q * H
        power_gen = ETA_TURBINE * rho_hot * G * q_vol_hot * h
        p_gens.append(power_gen/1000) # kW
        
        # Power Consumption (Pump)
        # Pump Lift = Target_H - Natural_Boost + Losses
        # If Target_H < Natural_Boost, we calculate flow limit?
        # Assuming we just pump the difference.
        required_head_m = h - natural_head_boost + total_head_loss_m
        if required_head_m < 0: required_head_m = 0 # Self flowing with throttle
        
        # If head < 0, it means it flows naturally with excess head.
        # We could recover that extra head?
        # For now, P_pump = 0.
        
        power_pump = (rho_hot * G * q_vol_hot * required_head_m) / ETA_PUMP
        p_cons.append(power_pump/1000)
        
        p_nets.append((power_gen - power_pump)/1000)

    # 4. Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(heights, p_nets, color='#00E676', linewidth=3, label='Net Power (Gen - Pump)')
    ax.plot(heights, p_gens, color='#29B6F6', linestyle='--', alpha=0.6, label='Turbine Gen')
    ax.plot(heights, p_cons, color='#FF5252', linestyle='--', alpha=0.6, label='Pump Cons')
    
    ax.axhline(0, color='white', linewidth=1, linestyle='-')
    
    # Find max
    max_p_net = max(p_nets)
    max_h = heights[p_nets.index(max_p_net)]
    
    ax.plot(max_h, max_p_net, 'wo', markersize=8)
    ax.annotate(f"Max Net: {max_p_net:.0f} kW\n@ {max_h:.0f}m", 
                (max_h, max_p_net), xytext=(10, -20), textcoords='offset points')

    ax.set_title(f"A03: Tower Height Optimization (Depth Boost included)\nNatural Head: {natural_head_boost:.1f}m", fontsize=14)
    ax.set_xlabel("Tower Height [m]")
    ax.set_ylabel("Power [kW]")
    ax.legend()
    ax.grid(True, alpha=0.2)
    
    output_path = os.path.join(ASSET_DIR, "A03_height_opt.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")
    print(f"Max Net Power: {max_p_net:.2f} kW at {max_h:.1f} m")

if __name__ == "__main__":
    run_simulation()
