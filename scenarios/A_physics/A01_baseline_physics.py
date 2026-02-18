"""
Hydra-Cool Simulation [CODE] — A01: Baseline Physics
====================================================
Establishes the fundamental driving force of the Hydra-Cool system: Buoyancy.

Physics basis:
- Density of seawater as a function of temperature: ρ(T)
- Hydrostatic pressure differential: ΔP = (ρ_cold - ρ_hot) * g * H

Key assumptions:
- Deep sea intake temperature: 5°C
- Data center outlet temperature: 50°C (ΔT = 45°C)
- Salinity: 35 ppt (constant)
- No friction losses considered yet (pure static potential)

Expected output:
- A clear relationship showing how much pressure can be generated purely by
  the density difference height column.

Author: Obada Dallo
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# --- Constants & Parameters ---
G = 9.81  # m/s^2
T_INTAKE = 5.0   # °C
T_OUTLET = 50.0  # °C

# Output directory
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")
os.makedirs(ASSET_DIR, exist_ok=True)

# --- Components ---

def seawater_density(temp_c):
    """
    Calculates seawater density at 35 ppt salinity.
    Approximation valid for 0-80°C.
    Formula: ρ(T) = 1028.17 - 0.0663*T - 0.0038*T^2
    """
    return 1028.17 - 0.0663 * temp_c - 0.0038 * (temp_c ** 2)

# --- Simulation ---

def run_simulation():
    print("Hydra-Cool A01: Running Baseline Physics Simulation...")
    
    # 1. Calculate Densities
    rho_cold = seawater_density(T_INTAKE)
    rho_hot = seawater_density(T_OUTLET)
    delta_rho = rho_cold - rho_hot
    
    print(f"[-] Intake Temp: {T_INTAKE}°C -> Density: {rho_cold:.2f} kg/m³")
    print(f"[-] Outlet Temp: {T_OUTLET}°C -> Density: {rho_hot:.2f} kg/m³")
    print(f"[-] Density Delta (Δρ): {delta_rho:.2f} kg/m³")

    # 2. Sweep Tower Height
    # From 10m to 200m
    heights = np.linspace(10, 200, 50)
    
    # 3. Calculate Buoyancy Pressure (Static Head)
    # ΔP = Δρ * g * H
    # Convert to kPa for readability (1 kPa = 1000 Pa)
    pressures_pa = delta_rho * G * heights
    pressures_kpa = pressures_pa / 1000.0
    
    # 4. Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(heights, pressures_kpa, color='#00BCD4', linewidth=2.5, label='Buoyancy Pressure')
    
    # Fill area under curve
    ax.fill_between(heights, pressures_kpa, color='#00BCD4', alpha=0.2)
    
    # Annotate specific points
    for h_target in [50, 100, 200]:
        p_target = delta_rho * G * h_target / 1000.0
        ax.plot(h_target, p_target, 'wo', markersize=6)
        ax.annotate(f"{p_target:.1f} kPa @ {h_target}m", 
                    (h_target, p_target), 
                    xytext=(10, -10), 
                    textcoords='offset points', 
                    color='white', 
                    fontsize=9)

    ax.set_title(f"A01: Buoyancy Pressure vs Tower Height\n(ΔT = {T_OUTLET - T_INTAKE}°C, Δρ = {delta_rho:.2f} kg/m³)", fontsize=14, pad=15)
    ax.set_xlabel("Tower Height [m]", fontsize=12)
    ax.set_ylabel("Available Buoyancy Pressure [kPa]", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend()
    
    # Save output
    output_path = os.path.join(ASSET_DIR, "A01_buoyancy_physics.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"[+] Saved visualization to: {output_path}")
    
    # Summary
    print("-" * 40)
    print("SIMULATION RESULTS:")
    print(f"At 50m tower:  {(delta_rho * G * 50 / 1000):.2f} kPa")
    print(f"At 100m tower: {(delta_rho * G * 100 / 1000):.2f} kPa")
    print(f"At 200m tower: {(delta_rho * G * 200 / 1000):.2f} kPa")
    print("-" * 40)

if __name__ == "__main__":
    run_simulation()
