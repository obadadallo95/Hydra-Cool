"""
Hydra-Cool Simulation [CODE] — D04: Thermal Plume Dispersion
=============================================================
Environmental Impact Analysis.

Physics:
- Discharge of warm water (T_out ~ 45-50°C) into surface water (20°C).
- Turbulent mixing reduces temperature with distance.
- Regulatory Limit: usually < 3°C rise at 100m mixing zone boundary.

Model:
- Simple Gaussian Plume spreading or Jet Dilution.
- T(x) = T_ambient + (T_discharge - T_ambient) / Dilution(x).

Output:
- Heatmap of ΔT vs Distance (Plan View).

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool D04: Running Thermal Plume Analysis...")
    
    # Grid (meters)
    x = np.linspace(0, 200, 100) # Distance from outlet
    y = np.linspace(-50, 50, 100) # Width
    X, Y = np.meshgrid(x, y)
    
    # Parameters
    T_discharge = 50.0
    T_ambient = 20.0
    DT_initial = T_discharge - T_ambient # 30 deg rise
    
    # Plume Model (Simplified Gaussian Jet)
    # Centerline decay: DT(x) = DT0 * (D/x) (for simple jet)
    # Width spread: sigma(x) = 0.1 * x
    
    D_pipe = 1.5
    
    # Decay function (approximate for submerged jet)
    # Avoid division by zero at x=0
    decay = np.zeros_like(X)
    sigmas = np.zeros_like(X)
    
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            dist = X[i,j]
            width = Y[i,j]
            
            if dist < 1:
                decay[i,j] = 1.0 # Core
            else:
                # Centerline dilution
                dilution = 1 + 0.15 * (dist / D_pipe)
                center_T = DT_initial / dilution
                
                # Gaussian spread
                sigma = 0.1 * dist + D_pipe/2
                decay[i,j] = (center_T / DT_initial) * np.exp(-(width**2)/(2*sigma**2))
    
    DT_field = decay * DT_initial
    
    # Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Contour Plot
    levels = np.linspace(0, 30, 16) # 2 deg steps
    cp = ax.contourf(X, Y, DT_field, levels=levels, cmap='inferno')
    cbar = fig.colorbar(cp)
    cbar.set_label('Temperature Rise [°C]')
    
    # Compliance Line (3°C Limit)
    ax.contour(X, Y, DT_field, levels=[3.0], colors='white', linewidths=2, linestyles='--')
    
    # Find Distance to <3°C
    # Centerline check
    centerline_DT = DT_field[50, :] # Middle row (y=0)
    safe_dist = 0
    for d, t in zip(x, centerline_DT):
        if t < 3.0:
            safe_dist = d
            break
            
    ax.annotate(f"Mixing Zone Boundary\n(< 3°C rise @ {safe_dist:.0f}m)", 
                (safe_dist, 0), xytext=(safe_dist, 25), 
                arrowprops=dict(facecolor='white', arrowstyle='->'),
                ha='center', color='white', fontweight='bold')
    
    ax.set_xlabel("Distance from Discharge [m]")
    ax.set_ylabel("Lateral Distance [m]")
    ax.set_title(f"D04: Thermal Plume Dispersion (Outlet T={T_discharge}°C)", fontsize=14)
    
    output_path = os.path.join(ASSET_DIR, "D04_thermal_plume.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")
    print(f"Mixing Zone Radius (<3°C): {safe_dist:.1f} m")

if __name__ == "__main__":
    run_simulation()
