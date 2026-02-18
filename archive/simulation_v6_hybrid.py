import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns
from scipy.optimize import brentq

class HybridSystem:
    """
    Simulation v6.0: The Hybrid System
    Combines Thermosiphon + Booster Pump to overcome HX resistance.
    """
    def __init__(self, pump_power_kw):
        # --- Physical Parameters ---
        self.height = 50.0  # m
        self.diameter = 2.0  # m
        self.num_pipes = 10 
        self.roughness = 0.000045 
        self.g = 9.81
        
        # Heat Exchanger
        self.hx_pressure_drop_pa = 50000.0 # 50 kPa Fixed
        self.hx_approach_temp = 3.0 # deg C
        
        # System Load
        self.it_load_mw = 50.0 
        self.cdu_parasitic_pct = 0.025 # 2.5%
        
        # Efficiencies
        self.pump_eff = 0.85
        self.turbine_eff = 0.80
        
        # Variable Control Input
        self.booster_power_w = pump_power_kw * 1000
        
    def get_density(self, temp_c):
        return 1028.17 - 0.0663 * temp_c - 0.0038 * temp_c**2

    def get_viscosity(self, temp_c):
        return 1.88e-3 * ((temp_c + 20)**(-0.6))

    def solve_hydraulics(self, t_sea_in=17.5):
        """
        Solves flow rate given Thermosiphon Drive + Booster Pump Drive.
        """
        t_server_out = 50.0
        t_sea_out = t_server_out - self.hx_approach_temp # 47.0 C
        
        if t_sea_out <= t_sea_in: return 0, 0, 0, 0
        
        # 1. Driving Forces
        # A. Thermosiphon (Buoyancy)
        rho_in = self.get_density(t_sea_in)
        rho_out = self.get_density(t_sea_out)
        rho_avg = (rho_in + rho_out) / 2
        delta_rho = rho_in - rho_out
        p_buoyancy = delta_rho * self.g * self.height
        
        # B. Booster Pump Pressure
        # P_pump = (Power * Eff) / Q
        # This makes the equation implicit on Q (or v).
        
        # Loss Coeffs
        k_minor_standard = 0.5 + 1.0 + (4 * 0.3) + 0.2
        
        def force_balance(v):
            if v <= 1e-4: return p_buoyancy + (self.booster_power_w * self.pump_eff / 1e-6) # Singularity
            
            # Flow Q
            area_total = self.num_pipes * (np.pi * (self.diameter/2)**2)
            q = v * area_total
            
            # Pump Pressure Head
            p_pump = (self.booster_power_w * self.pump_eff) / q
            
            # Friction Loss
            mu_avg = self.get_viscosity((t_sea_in + t_sea_out)/2)
            Re = (rho_avg * v * self.diameter) / mu_avg
            
            if Re < 2300: f = 64/Re
            else:
                rel_rough = self.roughness / self.diameter
                term = (rel_rough/3.7)**1.11 + (6.9/Re)
                f = (-1.8 * np.log10(term))**-2
                
            head_loss_coeff = (f * self.height / self.diameter) + k_minor_standard
            p_loss_hydro = rho_avg * head_loss_coeff * (v**2 / 2)
            
            # HX Loss
            p_loss_hx = self.hx_pressure_drop_pa
            
            # Balance: (Drive + Pump) - (Friction + HX) = 0
            return (p_buoyancy + p_pump) - (p_loss_hydro + p_loss_hx)

        try:
            v_sol = brentq(force_balance, 0.01, 10.0)
        except ValueError:
            v_sol = 0.0
            
        area_total = self.num_pipes * (np.pi * (self.diameter/2)**2)
        q_sol = v_sol * area_total
        m_dot = q_sol * rho_out
        
        # Turbine Generation
        p_gen = self.turbine_eff * m_dot * self.g * self.height
        
        return m_dot, v_sol, p_gen, p_buoyancy

    def run_analysis(self):
        m_dot, v, p_turbine, p_buoyancy = self.solve_hydraulics()
        
        p_cdu = self.it_load_mw * 1e6 * self.cdu_parasitic_pct
        p_booster = self.booster_power_w
        
        # Net Power = Generated - (Booster + CDU)
        p_net = p_turbine - (p_booster + p_cdu)
        
        # Cooling Check
        heat_capacity_w = m_dot * 4186 * (47.0 - 17.5)
        cooling_met = heat_capacity_w >= (self.it_load_mw * 1e6)
        
        # Comparative Baseline (Google Class A)
        # They pump same mass low, but NO Thermosiphon lift assistance.
        # They pay for full friction + HX loss.
        # Power_Google = (flow * pressure_drop_total) / pump_eff
        # Pressure Drop Total is roughly equal to Driving Forces in equilibrium
        # P_drop_total = P_buoyancy + P_booster
        # So Google Power = (P_buoyancy * Q + P_booster * Q) / eff? No.
        # Google Power = (Total Head Loss * Q) / eff
        # And Total Head Loss = P_buoyancy + P_booster_pressure
        # So yes, they pay for the lift we got for free + the boost we added.
        p_google_pump = ((p_buoyancy + (p_booster * self.pump_eff / (m_dot/1000 if m_dot>0 else 1))) * (m_dot/1000 if m_dot>0 else 0)) / self.pump_eff
        # Wait, strictly: Power = Q * DeltaP / eff
        # DeltaP_req = P_loss_hydro + P_loss_hx
        # In our equilibrium, DeltaP_req = P_buoyancy + P_pump_pressure
        # So Google pays for (P_buoyancy + P_pump_pressure) * Q / eff
        
        if m_dot > 0:
            area_total = self.num_pipes * (np.pi * (self.diameter/2)**2)
            q = v * area_total
            total_pressure_loss = p_buoyancy + (p_booster * self.pump_eff / q)
            p_google_cooling = (q * total_pressure_loss) / self.pump_eff
        else:
            p_google_cooling = 0
            
        p_google_total_drain = p_google_cooling + p_cdu # They also have CDU
        
        return {
            "booster_kw": self.booster_power_w / 1000,
            "flow_v": v,
            "p_gen_mw": p_turbine / 1e6,
            "p_cons_mw": (p_booster + p_cdu) / 1e6,
            "p_net_mw": p_net / 1e6,
            "cooling_met": cooling_met,
            "google_drain_mw": p_google_total_drain / 1e6,
            "hybrid_advantage_mw": (p_net - (-p_google_total_drain)) / 1e6 # Net - (-Drain) = Net + Drain? 
            # No. Net is (Gen - Cons). Google is (-Cons). Advantage is Net - Google?
            # Example: We are -1MW (consumption). Google is -5MW. Advantage is 4MW.
            # Example: We are +1MW. Google is -5MW. Advantage is 6MW.
        }

def run_optimization():
    print("Running Hybrid Optimization...")
    
    # Sweep Pump Power from 0 to 500 kW (0.5 MW)
    # Note: 50kW might be too small for 10 pipes * 2m dia? Net volume is huge.
    # Let's try 0 to 2000 kW (2 MW) just to be safe and find peak.
    powers = np.linspace(0, 2000, 50) 
    results = []
    
    for p in powers:
        sys = HybridSystem(p) # p in kW
        results.append(sys.run_analysis())
        
    df = pd.DataFrame(results)
    
    # Find Optimal Point
    # Where Cooling is Met AND p_net_mw is maximized
    valid = df[df['cooling_met'] == True]
    
    if valid.empty:
        print("CRITICAL: Even with 2MW pump, cooling is not met? (Unlikely)")
        best = df.iloc[df['p_net_mw'].argmax()]
    else:
        best = valid.loc[valid['p_net_mw'].idxmax()]
        
    print("\n" + "="*60)
    print("SIMULATION v6.0: HYBRID SYSTEM RESULTS")
    print("="*60)
    print(f"OPTIMAL BOOSTER CONFIGURATION:")
    print(f"  Booster Pump Power   : {best['booster_kw']:.1f} kW")
    print(f"  Flow Velocity        : {best['flow_v']:.2f} m/s")
    print("-" * 60)
    print(f"ENERGY BALANCE (50MW Load):")
    print(f"  1. Turbine Generation: {best['p_gen_mw']:.2f} MW")
    print(f"  2. Hybrid Consumption: {best['p_cons_mw']:.2f} MW (Booster + CDU)")
    print(f"  3. NET SYSTEM POWER  : {best['p_net_mw']:.2f} MW")
    print("-" * 60)
    print(f"COMPARISON vs GOOGLE (Traditional):")
    print(f"  Google Consumption   : {best['google_drain_mw']:.2f} MW")
    print(f"  Hybrid Advantage     : {best['p_net_mw'] - (-best['google_drain_mw']):.2f} MW (Shift)")
    print("="*60)
    
    # Visualization
    os.makedirs("assets", exist_ok=True)
    plt.style.use('dark_background')
    # sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(14, 6))
    
    # Plot 1: Optimization Curve
    ax1 = plt.subplot(1, 2, 1)
    # Plot Net Power vs Booster Power
    sns.lineplot(data=df, x='booster_kw', y='p_net_mw', ax=ax1, color='green', label='Net System Power')
    # Plot Cooling Threshold line (vertical?) or region.
    # Just verify valid region
    valid_min = valid['booster_kw'].min() if not valid.empty else 0
    ax1.axvline(best['booster_kw'], color='blue', linestyle='--', label=f'Optimal: {best["booster_kw"]:.0f}kW')
    ax1.axhline(0, color='red', linestyle='--', label='Break Even')
    
    ax1.set_title("Hybrid Optimization: Finding the Sweet Spot")
    ax1.set_xlabel("Booster Pump Power (kW)")
    ax1.set_ylabel("Net Power Output (MW)")
    ax1.legend()
    
    # Plot 2: Bar Comparison
    ax2 = plt.subplot(1, 2, 2)
    categories = ['Google (Traditional)', 'Hybrid (Booster+Gravity)']
    # Values: Energy Consumption (Drain). For Hybrid, if Net is Positive, drain is "Negative Consumption"
    
    google_val = -best['google_drain_mw'] # Consumption as negative
    hybrid_val = best['p_net_mw']
    
    colors = ['#EA4335', '#2ecc71']
    bars = ax2.bar(categories, [google_val, hybrid_val], color=colors)
    ax2.axhline(0, color='black', linewidth=1)
    
    ax2.set_title(f"Energy Performance Comparison\n(Impact: {best['p_net_mw'] - google_val:.2f} MW Shift)")
    ax2.set_ylabel("Net Power (MW) [+ is Gen, - is Cons]")
    
    # Label bars
    for bar in bars:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h, f'{h:.2f} MW', ha='center', va='bottom' if h<0 else 'bottom')

    plt.tight_layout()
    out = "assets/v6_hybrid_opt.png"
    plt.savefig(out, dpi=150)
    print(f"Chart saved to {out}")

if __name__ == "__main__":
    run_optimization()
