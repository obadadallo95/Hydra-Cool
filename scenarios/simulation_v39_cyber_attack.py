"""
Hydra-Cool Simulation v39.0 — CYBER-PHYSICAL ATTACK (Resonance)
===============================================================
Scenario: "Stuxnet 2.0" - Hacker controls the VSD or Valve Actuator.
Attack: Oscillate flow/valve at the system's Natural Frequency.

PHYSICS (Acoustic Resonance):
  - Fundamental Freq f_n = c / (4 * L)  (Open-Closed pipe)
  - c = 1200 m/s
  - L = 500m (Intake Pipe)
  - Impulse: Periodic pressure pulses.

IMPACT:
  - Pressure waves amplify with each cycle (Standing Wave).
  - Peak pressures exceed pipe rating rapidly.
  - Fatigue failure of welds.

OBJECTIVE:
  - Find the "Kill Frequency".
  - Simulate pressure amplification over time.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def run_cyber_attack():
    print("="*60)
    print("  HYDRA-COOL v39: CYBER-PHYSICAL RESONANCE ATTACK")
    print("="*60)
    
    C_WAVE = 1200.0 # m/s
    L_PIPE = 500.0  # m
    
    # 1. Calculate Kill Frequencies
    # Mode 1, 3, 5... for Open-Closed
    # f = n * c / (4L) for n=1,3,5
    
    modes = []
    print(f"\n  [VULNERABILITY SCAN]")
    print(f"  Pipe Length: {L_PIPE}m")
    print(f"  Wave Speed:  {C_WAVE}m/s")
    print(f"  Critical Frequencies (Harmonics):")
    
    for n in [1, 3, 5, 7]:
        f = n * C_WAVE / (4 * L_PIPE)
        period = 1/f
        modes.append(f)
        print(f"    Mode {n}: {f:.2f} Hz (Period: {period:.2f}s)")
        
    kill_freq = modes[0] # 0.6 Hz
    print(f"\n  ATTACK VECTOR SELECTED: oscillate valve at {kill_freq:.2f} Hz.")
    
    # 2. Simulate Amplification (Simplified Damped Driven Oscillator)
    # P(t+1) = P(t) + DrivingForce - Damping
    # At resonance, Damping limits infinity, but amplitude gets HUGE.
    
    time = np.linspace(0, 30, 1000) # 30 seconds
    drive = np.sin(2 * np.pi * kill_freq * time)
    
    # Response grows linearly then saturates?
    # Envelope growth: A * (1 - exp(-t/tau))
    # Unchecked, it grows until burst.
    
    # Let's model pressure envelope
    base_pressure = 4.0 # Bar
    burst_limit = 16.0  # Bar
    
    # Growth factor Q (Quality factor of pipe ~ 20)
    # Amplitude grows to Q * DrivingAmplitude.
    # Say Driving is 2 Bar (Valve stutter). Max = 40 Bar.
    
    envelope = 4.0 + 2.0 * 20 * (1 - np.exp(-time/5.0)) # 5s time constant
    
    # Modulate
    signal = base_pressure + (envelope - base_pressure) * np.sin(2 * np.pi * kill_freq * time)
    
    print("\n  [ATTACK SIMULATION]")
    print(f"  Time 0s:  Pressure +/- 4 Bar (Normal)")
    print(f"  Time 10s: Pressure +/- {envelope[333]:.1f} Bar (Building)")
    print(f"  Time 20s: Pressure +/- {envelope[666]:.1f} Bar (CRITICAL)")
    
    burst_time = next((t for t, p in zip(time, envelope) if p > burst_limit), None)
    
    if burst_time:
        print(f"\n  💀 BURST DETECTED AT t = {burst_time:.1f} SECONDS")
        print(f"  The resonance tore the pipe apart.")
    else:
        print(f"\n  ⚠️ SYSTEM SURVIVED (But highly stressed)")

    # Plot
    plot_resonance(time, signal, burst_limit)

def plot_resonance(t, p, limit):
    os.makedirs("assets", exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')
    
    plt.plot(t, p, 'r-', linewidth=1, label='Internal Pressure')
    plt.axhline(limit, color='y', linestyle='--', label='Burst Pressure (16 Bar)')
    plt.axhline(-1, color='c', linestyle=':', label='Vacuum Limit')
    
    plt.title(f"v39: STUXNET 2.0 - Resonance Attack (0.6 Hz)", color='white', fontweight='bold')
    plt.ylabel("Pressure (Bar)", color='white')
    plt.xlabel("Time (seconds)", color='white')
    plt.grid(True, alpha=0.2)
    plt.legend()
    
    out = "assets/v39_resonance_attack.png"
    plt.savefig(out, dpi=150)
    print(f"\n  ✓ Chart saved: {out}")

if __name__ == "__main__":
    run_cyber_attack()
