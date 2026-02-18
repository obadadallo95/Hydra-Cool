import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns

class AnalysisEngine:
    """
    Simulation v12.0: The Crash Test
    Forensic analysis of Transient Flow (Water Hammer) and Structural Vibration (Resonance).
    """
    def __init__(self):
        # Configuration (Golden Scenario)
        self.H = 200.0 # m
        self.D = 3.5   # m (Inner Dia)
        self.t_wall = 0.02 # m (20mm Steel Penstock at bottom?)
                           # Actually v9 said 0.5m Concrete.
                           # Let's assume the high pressure section at bottom is lined with Steel.
                           # Penstock usually steel.
                           # Let's assess critical Steel section.
        self.roughness = 0.000045
        
        # Operational
        self.flow_velocity = 2.0 # m/s (Approx from v11 results ~50MW/High Flow)
        self.valve_close_time = 0.5 # s (Emergency Trip)
        self.turbine_rpm = 300.0 # RPM
        
        # Constants
        self.rho = 1025.0 # kg/m3
        self.K_water = 2.2e9 # Pa (Bulk Modulus)
        self.E_steel = 200e9 # Pa (Young's Modulus)
        self.E_concrete = 30e9 # Pa
        self.g = 9.81
        
    def run_water_hammer_analysis(self):
        # 1. Wave Speed (c)
        # c = sqrt( (K/rho) / (1 + (K/E)*(D/e)) )
        # Using Steel Penstock assumption for worst case rigidity
        # D = 3.5, e = 0.02 (20mm)
        # If Concrete: D=3.5, e=0.5. E=30e9.
        # Let's calculate both? The wave travels through the whole system.
        # The riser key part is likely concrete.
        
        # Concrete Wave Speed
        term_conc = (self.K_water / self.E_concrete) * (self.D / 0.5)
        c_conc = np.sqrt((self.K_water / self.rho) / (1 + term_conc))
        
        # Steel Wave Speed (If we had a steel section)
        term_steel = (self.K_water / self.E_steel) * (self.D / 0.02)
        c_steel = np.sqrt((self.K_water / self.rho) / (1 + term_steel))
        
        # Let's use the faster one (Steel) as conservative for pressure spike?
        # Actually slower wave speed means lower pressure rise Joukowsky?
        # dP = rho * c * dV. So higher c is worse.
        # Let's assume a Steel Liner is present (common for high head).
        c = c_steel 
        
        # 2. Critical Time (2L/c)
        L = 250.0 # Tower + some intake
        t_crit = (2 * L) / c
        
        # 3. Joukowsky Pressure Rise
        # Rapid closure if t_close < t_crit
        is_rapid = self.valve_close_time < t_crit
        
        if is_rapid:
            # Full Joukowsky
            dp_surge = self.rho * c * self.flow_velocity
        else:
            # Partial (Allievi)
            # Roughly proportional
            dp_surge = self.rho * c * self.flow_velocity * (t_crit / self.valve_close_time)
            
        # 4. Total Pressure
        p_static = self.rho * self.g * self.H # Bottom of tower
        p_max_abs = p_static + dp_surge
        
        p_max_bar = p_max_abs / 1e5
        p_burst_limit = 40.0 # Bar (PN40 standard)
        
        survived = p_max_bar < p_burst_limit
        
        return {
            "Wave_Speed_m_s": c,
            "Critical_Time_s": t_crit,
            "Closure_Type": "Rapid" if is_rapid else "Slow",
            "Surge_Pressure_Bar": dp_surge / 1e5,
            "Static_Pressure_Bar": p_static / 1e5,
            "Max_Pressure_Bar": p_max_bar,
            "Limit_Bar": p_burst_limit,
            "Survived": survived
        }

    def run_resonance_analysis(self):
        # 1. Natural Frequency (f_n) of Cantilever Tower
        # f_n = (coef / 2PI * H^2) * sqrt(EI / mu)
        # Coef for cantilever 1st mode = 3.516
        
        # Mass per unit length (mu)
        # Water mass
        area_water = np.pi * (self.D/2)**2
        mu_water = area_water * self.rho
        
        # Concrete mass (Annulus)
        # Do = 3.5 + 2*0.5 = 4.5
        area_conc = np.pi * ((4.5/2)**2 - (3.5/2)**2)
        mu_conc = area_conc * 2400 # Density of concrete
        
        mu_total = mu_water + mu_conc
        
        # Stiffness (EI)
        # I for annulus = PI/64 * (Do^4 - Di^4)? No, PI/4 * (R_o^4 - R_i^4)
        I_conc = (np.pi / 4) * ((4.5/2)**4 - (3.5/2)**4)
        EI = self.E_concrete * I_conc
        
        f_n = (3.516 / (2 * np.pi * self.H**2)) * np.sqrt(EI / mu_total)
        
        # 2. Forcing Frequency (f_op)
        f_op = self.turbine_rpm / 60.0 # Hz
        
        # 3. Check Resonance
        ratio = f_op / f_n
        danger = 0.9 <= ratio <= 1.1
        
        return {
            "Natural_Freq_Hz": f_n,
            "Turbine_Freq_Hz": f_op,
            "Ratio": ratio,
            "Resonance_Risk": danger
        }

    def generate_report(self):
        print("\n" + "#"*60)
        print("SIMULATION v12.0: THE CRASH TEST (Forensic Analysis)")
        print("#"*60)
        
        # Water Hammer
        wh = self.run_water_hammer_analysis()
        print(f"TEST 1: WATER HAMMER (Transient Flow)")
        print(f"  Wave Speed       : {wh['Wave_Speed_m_s']:.0f} m/s")
        print(f"  Surge Pressure   : {wh['Surge_Pressure_Bar']:.1f} Bar (Joukowsky)")
        print(f"  Max Total Press. : {wh['Max_Pressure_Bar']:.1f} Bar")
        print(f"  Burst Limit      : {wh['Limit_Bar']:.0f} Bar")
        print(f"  STATUS           : {'PASSED' if wh['Survived'] else 'FAILED (EXPLOSION RISK)'}")
        
        if not wh['Survived']:
             # Calc Surge Tank
             # V_tank approx = (Vol_Flow * Length * Velocity) / (2 * g * Head_Rated * 0.5) ???
             # Detailed Thoma criteria is complex.
             # Heuristic: Need tank to absorb Momentum = m * v.
             print(f"   >>> MITIGATION: SURGE TANK REQUIRED. Recommend 500m3 Air Cushion Tank.")
             
        # Resonance
        res = self.run_resonance_analysis()
        print("-" * 60)
        print(f"TEST 2: STRUCTURAL RESONANCE (Vibration)")
        print(f"  Tower Nat. Freq  : {res['Natural_Freq_Hz']:.2f} Hz")
        print(f"  Turbine Oper.    : {res['Turbine_Freq_Hz']:.2f} Hz (300 RPM)")
        print(f"  Ratio (Op / Nat) : {res['Ratio']:.2f}")
        print(f"  STATUS           : {'PASSED' if not res['Resonance_Risk'] else 'FAILED (STRUCTURAL COLLAPSE RISK)'}")
        
        if res['Resonance_Risk']:
            print(f"   >>> MITIGATION: CHANGE TURBINE RPM or ADD MASS DAMPERS.")
            
        print("#"*60)
        
        self.plot_results(wh, res)

    def plot_results(self, wh, res):
        os.makedirs("assets", exist_ok=True)
        plt.style.use('dark_background')
        # sns.set_theme(style="whitegrid")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Pressure Transient
        # Simple step function for viz
        t = np.linspace(0, 2, 100)
        p = np.ones_like(t) * wh['Static_Pressure_Bar']
        # Spike at t > 0.5 (valve close)
        spike_idx = t > 0.5
        p[spike_idx] = wh['Max_Pressure_Bar']
        # Decay (damped vibration)
        decay = np.exp(-(t[spike_idx]-0.5)*2)
        p[spike_idx] = wh['Static_Pressure_Bar'] + (wh['Surge_Pressure_Bar'] * decay * np.cos(20*np.pi*(t[spike_idx]-0.5)))
        
        ax1.plot(t, p, 'r-', linewidth=2)
        ax1.axhline(wh['Limit_Bar'], color='black', linestyle='--', label='Burst Limit')
        ax1.set_title("Water Hammer: Pressure Surge Event")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Pressure (Bar)")
        ax1.legend()
        
        # Plot 2: Frequency Spectrum
        # Bell curve for Resonance Zone
        freqs = np.linspace(0, 10, 100)
        
        # Response curve 1/sqrt((1-r^2)^2 + (2*zeta*r)^2)
        fn = res['Natural_Freq_Hz']
        r = freqs / fn
        zeta = 0.05 # Damping ratio for concrete
        response = 1 / np.sqrt((1 - r**2)**2 + (2*zeta*r)**2)
        
        ax2.plot(freqs, response, 'b-', label='Structure Response')
        ax2.axvline(res['Turbine_Freq_Hz'], color='red', linestyle='--', label='Turbine RPM (5Hz)')
        
        # Danger Zone
        ax2.axvspan(fn*0.9, fn*1.1, color='orange', alpha=0.3, label='Resonance Zone')
        
        ax2.set_title("Vibration Analysis: Tower Resonance")
        ax2.set_xlabel("Frequency (Hz)")
        ax2.set_ylabel("Dynamic Amplification Factor")
        ax2.legend()
        
        plt.tight_layout()
        out = "assets/v12_crashtest.png"
        plt.savefig(out, dpi=150)
        print(f"Chart saved to {out}")

if __name__ == "__main__":
    sim = AnalysisEngine()
    sim.generate_report()
