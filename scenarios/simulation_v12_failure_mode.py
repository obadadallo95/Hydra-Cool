import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns

class FailureEngine:
    """
    Simulation v12.0: The Brutal Safety Audit
    Forces the system to fail by finding critical Water Hammer and Resonance limits.
    """
    def __init__(self):
        # Configuration
        self.H = 200.0 # m
        self.D = 3.5   # m
        self.flow_velocity = 2.0 # m/s (Standard Op)
        
        # Constants
        self.rho = 1025.0 # kg/m3
        self.K_water = 2.2e9 # Pa
        self.E_steel = 200e9 # Pa
        self.g = 9.81
        
        # Burst Limit (Grade B Steel Pipe)
        self.burst_limit_bar = 40.0 # PN40
        
        # Calculate Wave Speed (Fixed)
        term_steel = (self.K_water / self.E_steel) * (self.D / 0.02)
        self.a = np.sqrt((self.K_water / self.rho) / (1 + term_steel)) # ~857 m/s
        
        # Critical Time
        self.L_pipe = 250.0 # m
        self.t_crit = (2 * self.L_pipe) / self.a # ~0.58s
        
        # Structural Limit
        # Natural Frequency
        # Using previous calc result: 0.05 Hz
        self.f_n = 0.05 # Hz

    def run_water_hammer_sweep(self):
        # Sweep Valve Closure Time from 0.01s (Instant) to 5.0s (Slow)
        times = np.linspace(0.01, 5.0, 500)
        pressures = []
        failure_t = None
        
        print(f"DEBUG: Wave Speed a = {self.a:.1f} m/s")
        print(f"DEBUG: Critical Time T_crit = {self.t_crit:.3f} s")
        
        static_p_bar = (self.rho * self.g * self.H) / 1e5 # ~20 Bar
        
        for t in times:
            if t < self.t_crit:
                # Rapid Closure (Full Joukowsky)
                dp_surge = self.rho * self.a * self.flow_velocity
            else:
                # Slow Closure (Allievi approx)
                dp_surge = self.rho * self.a * self.flow_velocity * (self.t_crit / t)
            
            p_total_bar = static_p_bar + (dp_surge / 1e5)
            pressures.append(p_total_bar)
            
            if p_total_bar > self.burst_limit_bar:
                if failure_t is None: failure_t = t # First failure point
        
        return times, pressures, failure_t

    def run_resonance_sweep(self):
        # Sweep RPM from 0 to 5000
        rpms = np.linspace(0, 5000, 5000)
        amplitudes = []
        failure_rpm = None
        
        # Damping Ratio (Concrete)
        zeta = 0.05 
        
        for r in rpms:
            f_op = r / 60.0 # Hz
            ratio = f_op / self.f_n
            
            # response = 1 / sqrt( (1-r^2)^2 + (2*zeta*r)^2 )
            # Limit at resonance approaches 1/(2*zeta) = 10x dynamic amp
            
            try:
                resp = 1 / np.sqrt((1 - ratio**2)**2 + (2*zeta*ratio)**2)
            except ZeroDivisionError:
                resp = 100.0 # Infinite
            
            # Failure Condition: Infinite Spike?
            # Let's say Amp > 8.0 is destruction.
            if resp > 8.0:
                if failure_rpm is None: failure_rpm = r
                
            amplitudes.append(resp)
            
        return rpms, amplitudes, failure_rpm

    def generate_report(self):
        print("\n" + "#"*60)
        print("SIMULATION v12.0: BRUTAL SAFETY AUDIT (Failure Mode Analysis)")
        print("#"*60)
        
        # 1. Water Hammer
        t, p, fail_t = self.run_water_hammer_sweep()
        print(f"TEST 1: WATER HAMMER (Valve Closure Sweep)")
        if fail_t:
             print(f"  CRITICAL FAILURE DETECTED!")
             print(f"  Condition: Valve Closure < {fail_t:.3f} seconds")
             print(f"  Result   : PIPE EXPLOSION (Pressure > 40 Bar)")
        else:
             print(f"  STATUS: SYSTEM ROBUST (No failure detected even at 0.01s??)")
             
        # 2. Resonance
        r, amp, fail_r = self.run_resonance_sweep()
        print("-" * 60)
        print(f"TEST 2: RESONANCE (RPM Sweep 0-5000)")
        if fail_r:
             print(f"  CRITICAL FAILURE DETECTED!")
             print(f"  Condition: Turbine RPM = {fail_r:.0f} RPM")
             print(f"  Result   : STRUCTURAL COLLAPSE (Resonance Spike)")
             print(f"  Nat Freq : {self.f_n:.2f} Hz ({self.f_n*60:.1f} RPM)")
        else:
             print(f"  STATUS: NO RESONANCE FOUND IN RANGE")
             
        print("#"*60)
        
        self.plot_results(t, p, fail_t, r, amp, fail_r)

    def plot_results(self, t, p, fail_t, r, amp, fail_r):
        os.makedirs("assets", exist_ok=True)
        plt.style.use('dark_background')
        # sns.set_theme(style="whitegrid")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Pressure vs Time
        ax1.plot(t, p, 'r-', linewidth=2)
        ax1.axhline(self.burst_limit_bar, color='black', linestyle='--', label='Burst Limit (40 Bar)')
        
        # Mark Failure Zone
        if fail_t:
            ax1.axvspan(0, fail_t, color='red', alpha=0.3, label='EXPLOSION ZONE')
            ax1.text(fail_t, 45, f' Critical: < {fail_t:.2f}s', color='red', fontweight='bold')
            
        ax1.set_title("Water Hammer Vulnerability")
        ax1.set_xlabel("Valve Closure Time (s)")
        ax1.set_ylabel("Max Surge Pressure (Bar)")
        ax1.legend()
        ax1.set_ylim(0, 50)
        
        # Plot 2: Vibration vs RPM
        ax2.plot(r, amp, 'b-', linewidth=1)
        
        # Mark Failure
        if fail_r:
             # Zoom in on first resonance usually low RPM
             ax2.axvline(fail_r, color='red', linestyle='--', label=f'Collapse RPM: {fail_r:.0f}')
             ax2.text(fail_r + 100, 5, ' RESONANCE', color='red', fontweight='bold')
        
        ax2.set_title("Resonance Vulnerability")
        ax2.set_xlabel("Turbine RPM")
        ax2.set_ylabel("Vibration Amplitude Factor")
        
        # Use log scale x if needed? No, linear 0-5000 is fine if peaks are distinct.
        # Given f_n = 0.05 Hz -> 3 RPM. This is tiny!
        # Let's check logic.
        # f_n approx 3.516/2piH^2... with H=200m it's very low. Large flexible structure.
        # So Resonance is at 3 RPM.
        # We operate at 300 RPM (5 Hz).
        # We pass through resonance during startup?
        
        ax2.set_xlim(0, 500) # Zoom to low RPM for visibility
        if fail_r and fail_r < 500:
             pass
        elif fail_r:
             ax2.set_xlim(0, fail_r * 1.5)
             
        ax2.legend()
        
        plt.tight_layout()
        out = "assets/v12_failure_mode.png"
        plt.savefig(out, dpi=150)
        print(f"Chart saved to {out}")

if __name__ == "__main__":
    sim = FailureEngine()
    sim.generate_report()
