"""
Hydra-Cool Simulation v34.0 — THERMAL RECIRCULATION (Short Circuit)
===================================================================
The "Loop of Death": Ocean currents reverse, pushing hot discharge
water back into the intake pipe.

SCENARIO:
  - Normal Intake: 5°C
  - Plume: 30°C
  - Short Circuit Event: Intake rises to 15°C (Mix).

IMPACT ASSESSMENT:
  - Can we still cool 100MW?
  - Do we violate ASHRAE Server Intake Limits (27°C)?
  - Does PUE explode?

Physics:
  Q = Load / (Cp * Delta T)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def run_thermal_short_circuit():
    print("="*60)
    print("  HYDRA-COOL v34: THERMAL SHORT CIRCUIT")
    print("="*60)
    
    LOAD_MW = 100.0
    CP_SW   = 3.993 # kJ/kg.K
    OFFSET_HX = 3.0 # Main HX Approach Temperature (LMTD approx)
    OFFSET_LOOP = 2.0 # Secondary Loop Approach
    
    # 1. Normal Operation
    t_sea_normal = 5.0
    t_supply_water = t_sea_normal + OFFSET_HX # 8C
    t_server_air_in = t_supply_water + OFFSET_LOOP # 10C
    
    print(f"\n  [NORMAL STATE] Sea: {t_sea_normal}°C")
    print(f"    -> Supply Water: {t_supply_water}°C")
    print(f"    -> Server Air Inlet: {t_server_air_in}°C (Target < 27°C)")
    print(f"    STATUS: ✅ PERFECT COOLING")
    
    # 2. Event: Recirculation
    print("-" * 60)
    print("  ⚠️ EVENT: CURRENT REVERSAL. DISCHARGE PLUME HITS INTAKE.")
    t_sea_event = 15.0 # Mixed (50% fresh, 50% plume)
    
    # Physics Propagation
    t_supply_event = t_sea_event + OFFSET_HX # 18C
    t_server_air_event = t_supply_event + OFFSET_LOOP # 20C
    
    print(f"\n  [EVENT STATE] Sea: {t_sea_event}°C")
    print(f"    -> Supply Water: {t_supply_event}°C")
    print(f"    -> Server Air Inlet: {t_server_air_event}°C")
    
    # Check Limits
    limit_ashrae = 27.0
    margin = limit_ashrae - t_server_air_event
    
    if margin > 0:
        print(f"    STATUS: ✅ SAFE (Margin {margin}°C)")
        print("    PHYISCS WIN: Because we started ultra-cold (5C), even a +10C")
        print("    impurity doesn't break the facility.")
    else:
        print(f"    STATUS: ❌ THROTTLING REQUIRED")

    # Plotting
    os.makedirs("assets", exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')
    
    stages = ['Deep Sea', 'Mixed Event', 'Supply Water', 'Server Air Inlet', 'ASHRAE Limit']
    temps = [5, 15, 18, 20, 27]
    colors = ['blue', 'cyan', 'green', 'yellow', 'red']
    
    plt.bar(stages, temps, color=colors, alpha=0.8)
    plt.title("v34: THERMAL SHORT CIRCUIT - Temperature Margin", color='white', fontweight='bold')
    plt.ylabel("Temperature (°C)", color='white')
    plt.axhline(27, color='red', linestyle='--', label='ASHRAE Limit (27°C)')
    
    for i, t in enumerate(temps):
        plt.text(i, t + 0.5, f"{t}°C", ha='center', color='white', fontweight='bold')
        
    plt.savefig("assets/v34_thermal_profile.png", dpi=150)
    print("\n  ✓ Chart saved: assets/v34_thermal_profile.png")

    # 3. Efficiency Hit
    # Flow rate must increase?
    # Delta T across server is fixed by airflow (say 15C rise).
    # If Inlet rises from 10C to 20C, Outlet rises from 25C to 35C.
    # CPU Temp rises by 10C.
    # PUE Impact? Constant Pumping (unless VSD ramps up flow to lower approach temp)
    # Actually, pumps might run HARDER to try to lower water temp? No, can't lower below sea temp.
    # Pumps run same speed. 
    # Result: Servers run 10C hotter. 
    # Reliability impact (Arrhenius) kicks in, but immediate failure avoided.

if __name__ == "__main__":
    run_thermal_short_circuit()
