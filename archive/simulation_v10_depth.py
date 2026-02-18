import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns
from scipy.optimize import brentq

class DeepSeaPhysics:
    """
    Simulation v10.0: Intake Depth Optimization
    Balancing Thermal Gain vs Friction Loss.
    """
    def __init__(self):
        # Configuration
        self.H_tower = 200.0 # From Golden Scenario
        self.D_pipe = 3.5    # From Golden Scenario
        self.g = 9.81
        self.slope_deg = 10.0 # Seabed slope
        self.roughness = 0.000045
        
        # Pump Specs
        self.pump_eff = 0.85
        self.turbine_eff = 0.80
        
        # Base Booster needed for tower itself (from v7)
        self.base_booster_kw = 2000.0 
        
    def get_seawater_temp(self, depth):
        """
        Thermocline Model for Dubai.
        Surface: 35C. Deep: 5C.
        """
        t_surface = 35.0
        t_deep = 5.0
        k = 0.01 # Decay constant
        # Simple exponential decay
        return t_deep + (t_surface - t_deep) * np.exp(-k * depth)

    def get_density(self, t):
         return 1028.17 - 0.0663 * t - 0.0038 * t**2
         
    def get_viscosity(self, t):
        return 1.88e-3 * ((t + 20)**(-0.6))

    def solve_system(self, depth):
        t_in = self.get_seawater_temp(depth)
        
        # 1. Intake Pipe Physics
        if depth > 0:
            length_intake = depth / np.sin(np.radians(self.slope_deg))
        else:
            length_intake = 0
            
        # 2. Thermosiphon Drive
        # T_out depends on Q. 
        # Let's iterate Q or Velocity.
        
        t_hot_guess = t_in + 30.0 # Initial guess for dT
        
        def system_balance(v):
            if v <= 1e-4: return 1e9
            
            # A. Buoyancy Drive
            rho_in = self.get_density(t_in)
            # T_out calculation based on 50MW load
            # Q = v * Area
            area = 10 * (np.pi * (self.D_pipe/2)**2) # 10 pipes
            q = v * area
            m_dot = q * rho_in
            
            # Heat Balance: 50MW = m * Cp * dT
            # dT = 50e6 / (m * 4186)
            d_t = 50e6 / (m_dot * 4186)
            t_out = t_in + d_t
            
            # Check T_out limits (boiling?) - unlikely with high flow
            
            rho_out = self.get_density(t_out)
            rho_avg = (rho_in + rho_out)/2
            
            p_buoyancy = (rho_in - rho_out) * self.g * self.H_tower
            
            # B. Friction Loss (Tower + Intake)
            # Tower Length = 200m vertical. Total loop length? 
            # Let's assume Tower Down + Tower Up = 400m + connections roughly.
            # Plus Intake Length.
            l_total = 400.0 + length_intake
            
            mu = self.get_viscosity((t_in + t_out)/2)
            Re = (rho_avg * v * self.D_pipe) / mu
            
            if Re < 2300: f = 64/Re
            else:
                rel_rough = self.roughness / self.D_pipe
                term = (rel_rough/3.7)**1.11 + (6.9/Re)
                f = (-1.8 * np.log10(term))**-2
            
            k_minor = 2.5 # Entrances, bends, HX interaction
            
            head_loss = (f * l_total / self.D_pipe) + k_minor
            p_friction = rho_avg * head_loss * (v**2 / 2)
            
            # C. HX Pressure Drop (Fixed 50kPa)
            p_hx = 50000 
            
            # D. Pump Support
            # We fix Pump Power to Base (2MW)? Or do we optimize pump for depth?
            # Goal is to see Net Power. Let's fix 2MW Booster capability.
            # But deep intake might need MORE pumping to maintain flow.
            # If we fix pump power, flow will drop with depth due to friction.
            # If flow drops too much, T_out spikes -> Thermal Pollution.
            
            p_pump_pressure = (self.base_booster_kw * 1000 * self.pump_eff) / q
            
            # Balance: Drive + Pump = Friction + HX
            return (p_buoyancy + p_pump_pressure) - (p_friction + p_hx)

        try:
            v_sol = brentq(system_balance, 0.1, 10.0)
        except ValueError:
            v_sol = 0.0
            
        # Calculate Outputs
        if v_sol > 0:
            area = 10 * (np.pi * (self.D_pipe/2)**2)
            q = v_sol * area
            rho_in = self.get_density(t_in)
            m_dot = q * rho_in
            d_t = 50e6 / (m_dot * 4186)
            t_out = t_in + d_t
            
            # Power
            p_gen = self.turbine_eff * m_dot * self.g * self.H_tower
            p_cons = self.base_booster_kw * 1000 + (50e6 * 0.025) # Booster + CDU
            
            # Dilution Penalty
            p_dilution = 0
            if t_out > 35.0:
               if t_in < 35.0:
                   m_dil = m_dot * (t_out - 35.0) / (35.0 - t_in)
                   # Dilution Pump Head conservative 5m
                   p_dilution = (m_dil * 9.81 * 5) / 0.85
               else:
                   p_dilution = 100e6 # Infinite penalty
                   
            p_net = p_gen - p_cons - p_dilution
            
        else:
            p_net = -10e6 # Fail
            t_out = 100
            length_intake = 0
            
        return {
            "Depth": depth,
            "Temp_In": t_in,
            "Temp_Out": t_out,
            "Pipe_Length": length_intake,
            "Net_Power_MW": p_net / 1e6
        }

    def run_sweep(self):
        depths = np.linspace(0, 1000, 50)
        results = []
        
        print("Running Depth Optimization Sweep...")
        for d in depths:
            res = self.solve_system(d)
            results.append(res)
            
        df = pd.DataFrame(results)
        return df

    def generate_report(self):
        df = self.run_sweep()
        
        # Find Sweet Spot
        k = df.loc[df['Net_Power_MW'].idxmax()]
        
        print("\n" + "#"*60)
        print("SIMULATION v10.0: INTAKE DEPTH OPTIMIZATION (Dubai)")
        print("#"*60)
        print(f"OPTIMAL DEPTH FOUND: {k['Depth']:.1f} meters")
        print(f"  Intake Temp      : {k['Temp_In']:.1f}°C")
        print(f"  Intake Pipe Len  : {k['Pipe_Length']:.0f} meters")
        print(f"  Max Net Power    : {k['Net_Power_MW']:.2f} MW")
        print("-" * 60)
        
        # Compare 3 Points
        # Surface
        surf = df.iloc[0]
        # 50m
        mid_idx = (np.abs(df['Depth'] - 50)).argmin()
        mid = df.iloc[mid_idx]
        # Deep (Optimal)
        
        print(f"{'Strategy':<15} | {'Depth':<6} | {'Tin':<5} | {'Pipe Len':<8} | {'Net MW':<8}")
        print("-" * 60)
        print(f"{'Surface':<15} | {surf['Depth']:<6.0f} | {surf['Temp_In']:<5.1f} | {surf['Pipe_Length']:<8.0f} | {surf['Net_Power_MW']:<8.2f}")
        print(f"{'Mid-Range':<15} | {mid['Depth']:<6.0f} | {mid['Temp_In']:<5.1f} | {mid['Pipe_Length']:<8.0f} | {mid['Net_Power_MW']:<8.2f}")
        print(f"{'Deep (Opt)':<15} | {k['Depth']:<6.0f} | {k['Temp_In']:<5.1f} | {k['Pipe_Length']:<8.0f} | {k['Net_Power_MW']:<8.2f}")
        print("#"*60)
        
        self.plot_results(df, k)

    def plot_results(self, df, optimal):
        os.makedirs("assets", exist_ok=True)
        plt.style.use('dark_background')
        # sns.set_theme(style="whitegrid")
        fig, ax1 = plt.subplots(figsize=(12, 7))
        
        # Plot Temp (Left Axis)
        color = 'tab:blue'
        ax1.set_xlabel('Intake Depth (m)')
        ax1.set_ylabel('Seawater Temp (°C)', color=color)
        ax1.plot(df['Depth'], df['Temp_In'], color=color, linewidth=2, label='Intake Temp')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.invert_yaxis() # Depth style physics usually flip Y? No, Temp drops.
        # Actually normal axis is fine.
        
        # Plot Net Power (Right Axis)
        ax2 = ax1.twinx()
        color = 'tab:green'
        ax2.set_ylabel('Net System Power (MW)', color=color)
        ax2.plot(df['Depth'], df['Net_Power_MW'], color=color, linewidth=3, label='Net Power')
        ax2.tick_params(axis='y', labelcolor=color)
        
        # Highlight Optimal
        ax2.axvline(optimal['Depth'], color='red', linestyle='--', label=f"Sweet Spot: {optimal['Depth']:.0f}m")
        bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="red", lw=1)
        ax2.text(optimal['Depth'], optimal['Net_Power_MW'], f" Peak: {optimal['Net_Power_MW']:.1f} MW", 
                 ha="left", va="bottom", bbox=bbox_props)
        
        plt.title("The Depth Trade-Off: Gain (Cold Water) vs Loss (Pipe Friction)")
        
        fig.tight_layout()
        out = "assets/v10_depth_optimization.png"
        plt.savefig(out, dpi=150)
        print(f"Chart saved to {out}")

if __name__ == "__main__":
    sim = DeepSeaPhysics()
    sim.generate_report()
