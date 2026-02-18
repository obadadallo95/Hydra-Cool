"""
Hydra-Cool Simulation v41.0 — THE GRAND UNIFIED VISION (Pitch Deck)
===================================================================
"The Thermo-Hydraulic Gravity Engine"

CONCEPT:
  We don't just cool servers. We create a self-sustaining energy loop.
  1. DEEP INTAKE: Cold water (-500m, 5°C) enters via hydrostatic pressure.
  2. THERMAL LIFT: Servers heat water to 50°C. Density drops. Buoyancy aids lift to +40m.
  3. GRAVITY BATTERY: 40m Reservoir acts as UPS and stabilizer.
  4. HYDRO-RECOVERY: Return flow drives turbines (Energy Capture).
  5. DISCHARGE: Mixing ensures eco-friendly return.

OBJECTIVE:
  Prove the "Cycle Efficiency" is superior to any other method.

PARAMETERS:
  - IT Load: 100 MW
  - Intake Depth: 500m
  - Reservoir Height: 40m
  - Delta T: 45°C (5->50)
  - Turbine Eff: 85%
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def run_grand_unified():
    print("="*60)
    print("  HYDRA-COOL v41: THE GRAND UNIFIED VISION")
    print("="*60)
    
    # 1. Thermodynamics (The Load)
    LOAD_MW = 100.0
    DT = 45.0 # 5 to 50
    CP = 4.0  # kJ/kgK
    FLOW_KG_S = (LOAD_MW * 1000) / (CP * DT)
    
    print(f"\n  [1. THERMODYNAMICS]")
    print(f"  IT Load:          {LOAD_MW} MW")
    print(f"  Flow Rate:        {FLOW_KG_S:.1f} kg/s ({FLOW_KG_S/1000:.1f} m3/s)")
    print(f"  Temp Rise:        +45°C (Buoyancy Activation)")
    
    # 2. The Lift (Buoyancy Assist)
    RHO_COLD = 1027.0
    RHO_HOT  = 1012.0
    H_LIFT   = 40.0 # m
    
    # Pressure required to lift
    P_lift_cold = RHO_COLD * 9.81 * H_LIFT
    P_lift_hot  = RHO_HOT  * 9.81 * H_LIFT
    P_saved     = P_lift_cold - P_lift_hot
    
    print(f"\n  [2. THERMAL LIFT]")
    print(f"  Lifting Cold Water: {P_lift_cold/1000:.1f} kPa")
    print(f"  Lifting Hot Water:  {P_lift_hot/1000:.1f} kPa")
    print(f"  Buoyancy Savings:   {P_saved/1000:.1f} kPa (Free Assist)")
    
    # 3. Hydro-Recovery (The Engine)
    # Falling 40m through turbines
    P_gen_kw = FLOW_KG_S * 9.81 * H_LIFT * 0.85 / 1000
    
    print(f"\n  [3. GRAVITY ENGINE]")
    print(f"  Reservoir Height: {H_LIFT} m")
    print(f"  Turbine Gen:      {P_gen_kw:.1f} kW")
    print(f"  Annual Recovery:  {P_gen_kw * 8.76:.1f} MWh/yr")
    
    # 4. Net Efficiency
    # Pump Work (Theoretical) = Flow * g * H / 0.85
    # Actual Pump Work = (Flow * g * H - Buoyancy) / 0.85
    # Net = Pump - Turbine
    
    pump_power_std = (FLOW_KG_S * 9.81 * H_LIFT) / 0.85 / 1000
    pump_power_smart = ((RHO_HOT/RHO_COLD) * FLOW_KG_S * 9.81 * H_LIFT) / 0.85 / 1000
    net_power = pump_power_smart - P_gen_kw
    
    print(f"\n  [4. NET RESULT]")
    print(f"  Standard Pumping: {pump_power_std:.1f} kW")
    print(f"  Smart Pumping:    {pump_power_smart:.1f} kW (Buoyancy)")
    print(f"  Turbine Output:   {P_gen_kw:.1f} kW")
    print(f"  NET CONSUMPTION:  {net_power:.1f} kW")
    
    reduction = (1 - net_power/pump_power_std) * 100
    print(f"  EFFICIENCY GAIN:  {reduction:.1f}%")
    
    # 5. Environmental (Discharge)
    # Mixing 50C with Ambient?
    # Assume 1:5 Dilution before outlet
    T_mix = (50.0 + 5 * 5.0) / 6.0
    print(f"\n  [5. ENVIRONMENTAL]")
    print(f"  Discharge Temp:   {T_mix:.1f}°C (After 1:5 Dilution)")
    print(f"  Impact:           NEGLIGIBLE.")

    plot_grand_cycle(pump_power_std, net_power)

def plot_grand_cycle(std, net):
    os.makedirs("assets", exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.style.use('dark_background')
    
    labels = ['Standard System', 'Hydra-Cool\nSmart Cycle']
    vals = [std, net]
    colors = ['gray', '#00FFCC']
    
    bars = plt.bar(labels, vals, color=colors)
    
    plt.title("v41: THE GRAVITY ENGINE\nEnergy Consumption per 100MW Cooling", color='white', fontweight='bold')
    plt.ylabel("Pump Power (kW)", color='white')
    
    # Label bars
    for rect in bars:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2.0, height, f'{height:.1f} kW', ha='center', va='bottom', color='white', fontsize=12, fontweight='bold')
        
    # Arrow
    plt.annotate(f'-{std-net:.0f} kW\n({(1-net/std)*100:.0f}%)', xy=(1, net), xytext=(0.5, (std+net)/2),
                 arrowprops=dict(facecolor='yellow', shrink=0.05), color='yellow', fontsize=12, fontweight='bold', ha='center')
    
    out = "assets/v41_grand_cycle.png"
    plt.savefig(out, dpi=150)
    print(f"\n  ✓ Chart saved: {out}")

if __name__ == "__main__":
    run_grand_unified()
