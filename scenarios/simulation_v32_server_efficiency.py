"""
Hydra-Cool Simulation v32.0 — SILICON EFFICIENCY & RELIABILITY
==============================================================
Professional Scenarios: Investigating the Impact of Cooling on Compute.

OBJECTIVE:
  Compare "Standard Air Cooling" vs "Hydra-Cool Direct-to-Chip" across
  real-world usage patterns. Unbiased analysis of Pros/Cons.

SCENARIOS:
  1. HFT / Overclocking: Frequency matters most. 
     (Air limits clock speed vs Water allows sustained turbo).
  2. AI Training Cluster: 100% Load for weeks. 
     (Air fluctuates causing thermal cycling/cracks vs Water steady state).
  3. Archival Storage (Cold Data): Low power, low heat. 
     (Air is cheap/simple vs Water is overkill/complex).

PHYSICS MODELS:
  - Thermal Throttling: Clock speed drops if Junction Temp > 90°C.
  - Arrhenius Reliability: Expected Lifespan inversely proportional to Temp.
    (Every 10°C rise cuts life in half).
  - Maintenance Penalty: Water cooling takes 3x longer to service.

Author: Obada Dallo
Copyright (c) 2024. All Rights Reserved.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

# ══════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════

# Base Specs (Modern CPU/GPU)
BASE_CLOCK      = 3.0  # GHz
MAX_TURBO       = 5.0  # GHz
THROTTLE_TEMP   = 90.0 # °C (Junction)
SHUTDOWN_TEMP   = 105.0# °C
BASE_LIFESPAN   = 5.0  # Years at 40°C ambient

# Cooling Profiles
# Air: Inlet fluctuates 20-35°C (Day/Night). Heat Resistance (R_th) high (0.2 C/W).
# Water: Inlet constant 20°C. Heat Resistance low (0.05 C/W).
AIR_R_TH   = 0.35 # °C/W (Heatsink & Fan)
WATER_R_TH = 0.08 # °C/W (Microchannel Waterblock)

# Workload Profiles (Watts)
LOAD_HFT = 350    # High (Overclocked single core)
LOAD_AI  = 700    # Extreme (GPU 100%)
LOAD_COLD= 50     # Low (HDD/CPU Idle)

# ══════════════════════════════════════════════════════════════
#  SIMULATION ENGINE
# ══════════════════════════════════════════════════════════════

def simulate_silicon(scenario_name, load_watts, duration_hours=168):
    """
    Simulate 1 week (168 hours) of operation.
    Return: Avg Clock, Avg Temp, Reliability Factor, Service Cost.
    """
    time = np.arange(duration_hours)
    
    # Ambient Temp fluctuation (Air)
    # Day/Night cycle: 25C base +/- 10C swing
    ambient_air = 25 + 10 * np.sin(2 * np.pi * time / 24)
    
    # Water Temp constant (Seawater / Loop)
    water_inlet = np.full(duration_hours, 20.0) # Steady deep water
    
    # --- AIR COOLING SIM ---
    # Junction Temp = Ambient + Load * R_th
    # Fan Ramp: If Temp > 60, Fan speed doubles (R_th drops slightly), but we simplify.
    # Assume adaptive R_th? No, keep fixed for clear physics. Or R_th improves with noise.
    # Let's assume R_th is best case.
    t_j_air = ambient_air + load_watts * AIR_R_TH
    
    # Throttling Air
    clock_air = []
    for t in t_j_air:
        if t < THROTTLE_TEMP:
            # Boost allowed
            # If well below, max turbo.
            # Simple linear boost curve logic
            headroom = THROTTLE_TEMP - t
            boost = min(MAX_TURBO, BASE_CLOCK + headroom * 0.1)
            clock_air.append(boost)
        else:
            # Throttle!
            overshoot = t - THROTTLE_TEMP
            drop = overshoot * 0.2
            clock_air.append(max(1.0, BASE_CLOCK - drop))
    clock_air = np.array(clock_air)
    
    # Reliability Air (Arrhenius)
    # Factor = exp(k * (1/T_ref - 1/T_j)) simplified:
    # Life halves every 10C above 40C.
    ref_temp = 40.0
    degradation_air = 2 ** ((t_j_air - ref_temp) / 10.0)
    avg_life_air = BASE_LIFESPAN / np.mean(degradation_air)

    # --- WATER COOLING SIM ---
    t_j_water = water_inlet + load_watts * WATER_R_TH
    
    # Throttling Water
    clock_water = []
    for t in t_j_water:
         # Water is almost always cool.
         if t < THROTTLE_TEMP:
             headroom = THROTTLE_TEMP - t
             boost = min(MAX_TURBO, BASE_CLOCK + headroom * 0.1)
             clock_water.append(boost)
         else:
             clock_water.append(BASE_CLOCK) # unlikely
    clock_water = np.array(clock_water)
    
    # Reliability Water
    degradation_water = 2 ** ((t_j_water - ref_temp) / 10.0)
    avg_life_water = BASE_LIFESPAN / np.mean(degradation_water)
    
    # Maintenance "Pain Factor"
    # Air: 15 mins to swap fan. Frequency: High.
    # Water: 60 mins to drain/fill loop. Frequency: Low.
    
    results = {
        "scenario": scenario_name,
        "load": load_watts,
        "t_air": np.mean(t_j_air),
        "t_water": np.mean(t_j_water),
        "clock_air": np.mean(clock_air),
        "clock_water": np.mean(clock_water),
        "life_air": avg_life_air,
        "life_water": avg_life_water,
        "throttle_pct_air": np.sum(t_j_air > THROTTLE_TEMP)/duration_hours * 100,
        "throttle_pct_water": np.sum(t_j_water > THROTTLE_TEMP)/duration_hours * 100
    }
    return results, t_j_air, t_j_water, clock_air, clock_water

# ══════════════════════════════════════════════════════════════
#  RUNNER
# ══════════════════════════════════════════════════════════════

def run_scenarios():
    print("="*80)
    print("  HYDRA-COOL v32: SILICON HEALTH & PERFORMANCE (Unbiased)")
    print("="*80)
    
    scenarios = [
        ("A: High Freq Trading (350W)", LOAD_HFT),
        ("B: AI Training Cluster (700W)", LOAD_AI),
        ("C: Cold Storage (50W)", LOAD_COLD)
    ]
    
    for name, load in scenarios:
        res, t_a, t_w, c_a, c_w = simulate_silicon(name, load)
        
        print(f"\n  {name}")
        print("-" * 60)
        
        # Temp
        print(f"    Avg Junction Temp:  Air {res['t_air']:.1f}°C  vs  Water {res['t_water']:.1f}°C")
        
        # Performance
        print(f"    Avg Clock Speed:    Air {res['clock_air']:.2f}GHz vs  Water {res['clock_water']:.2f}GHz")
        if res['throttle_pct_air'] > 0:
            print(f"    ⚠️ THROTTLING ALERT: Air throttled {res['throttle_pct_air']:.1f}% of the time!")
        else:
            print(f"    ✓ No Throttling detected.")
            
        # Lifespan
        print(f"    Expected Lifespan:  Air {res['life_air']:.1f} yrs vs  Water {res['life_water']:.1f} yrs")
        
        # Verdict
        if res['life_water'] > res['life_air'] + 1.0:
            benefit = "MAJOR RELIABILITY GAIN"
        elif res['clock_water'] > res['clock_air'] + 0.2:
            benefit = "PERFORMANCE UNLOCKED"
        elif res['life_water'] < res['life_air']: # Unlikely unless water is hot
             benefit = "WATER RISK (Condensation?)"
        else:
            benefit = "MARGINAL GAIN (Not worth the complexity)"
            
        print(f"    VERDICT: {benefit}")

    print("\n  MAINTENANCE REALITY CHECK:")
    print("  - Air Cooled: Easy to swap. Fan failure is common but trivial (Hot Swap).")
    print("  - Water Cooled: Hard to swap. Leak failure is rare but CATASTROPHIC.")
    print("  - Recommendation: Use Air for Storage. Use Water for AI.")

    # Generate Chart for Scenario B (AI)
    res_ai, t_a, t_w, c_a, c_w = simulate_silicon("AI Training", LOAD_AI)
    plot_silicon_health(t_a, t_w, c_a, c_w)

def plot_silicon_health(t_air, t_water, c_air, c_water):
    os.makedirs("assets", exist_ok=True)
    hours = np.arange(len(t_air))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    plt.style.use('dark_background')
    fig.patch.set_facecolor('#0a0a0a')
    
    # Ax1: Temperature
    ax1.plot(hours, t_air, 'r-', alpha=0.7, label='Air Cooled (Fluctuating)')
    ax1.plot(hours, t_water, 'c-', linewidth=2, label='Hydra-Cool (Stable)')
    ax1.axhline(90, color='yellow', linestyle='--', label='Throttle Limit')
    ax1.set_ylabel("Junction Temp (°C)", color='white')
    ax1.set_title("SCENARIO B: AI TRAINING (700W GPU Load) - 1 Week", color='white', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.2)
    
    # Ax2: Clock Speed
    ax2.plot(hours, c_air, 'r--', alpha=0.7, label='Air Frequency')
    ax2.plot(hours, c_water, 'c-', linewidth=2, label='Water Frequency')
    ax2.set_ylabel("Clock Speed (GHz)", color='white')
    ax2.set_xlabel("Hours of Operation", color='white')
    ax2.legend()
    ax2.grid(True, alpha=0.2)
    
    # Text annotation
    # Calculate integral loss?
    loss = np.sum(c_water - c_air)
    plt.figtext(0.5, 0.02, f"Total Compute Lost by Air Cooling: {loss:.0f} GHz-Hours per week", ha="center", color="#aaa")
    
    out_path = "assets/v32_silicon_performance.png"
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"\n  ✓ Chart saved: {out_path}")

if __name__ == "__main__":
    run_scenarios()
