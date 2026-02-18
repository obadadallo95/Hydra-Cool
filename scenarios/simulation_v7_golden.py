import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import brentq
import numpy_financial as npf
import warnings
warnings.filterwarnings("ignore")

class NightmarePhysics:
    """
    Simulation v7.0: The Golden Scenario (Nightmare Mode)
    Incorporates Time-Dependent Biofouling, Thermal Pollution, and Pipeline Heat Loss.
    """
    def __init__(self, height, diameter, pump_power_kw):
        # Configuration
        self.H = height
        self.D = diameter
        self.booster_power_w = pump_power_kw * 1000
        
        # System Constants
        self.num_pipes_base = 10 # Baseline, maybe scale with diameter? Let's fix at 10 for simplicity.
        self.g = 9.81
        self.cp_water = 4186
        self.epsilon_base = 0.000045 # Commercial Steel
        self.hx_efficiency_base = 0.90
        self.hx_approach_base = 3.0
        
        # Financial Constants
        self.capex_land = 2_000_000
        self.capex_civil = 1_000_000
        self.capex_titanium_cost = 100 # $/kW
        self.capex_insulation = 50 # $/m
        self.elec_price = 0.12
        self.carbon_credit = 50 # $/ton
        
        # Degradation Factors
        self.biofouling_roughness_rate = 0.10 # +10% per month
        self.biofouling_hx_rate = 0.01 # -1% efficiency per month
        self.maintenance_cost = 50_000 # Clean every 12 months
        
    def get_density(self, temp_c):
        return 1028.17 - 0.0663 * temp_c - 0.0038 * temp_c**2

    def get_viscosity(self, temp_c):
        return 1.88e-3 * ((temp_c + 20)**(-0.6))
        
    def solve_hydraulics_at_month(self, month_idx, t_sea_in):
        """
        Solves system state for a specific month, accounting for degradation.
        """
        months_since_clean = month_idx % 12
        
        # 1. Apply Degradation
        current_roughness = self.epsilon_base * ((1 + self.biofouling_roughness_rate) ** months_since_clean)
        current_hx_eff = self.hx_efficiency_base * ((1 - self.biofouling_hx_rate) ** months_since_clean)
        
        # Degrading HX efficiency increases Approach Temp
        # Eff = (Thi - Tho) / (Thi - Tci)
        # Assuming Thi (Server) = 50C, Tci (Sea) = t_sea_in
        # Q = m * Cp * (Tso - Tsi) ? No, effectiveness model.
        # Let's approximate: Degraded Eff means Tho (Sea Out) is closer to Thi (Sea In).
        # Actually, degraded eff means we transfer LESS heat.
        # But we MUST transfer 50MW. So we need MORE flow or BIGGER LMTD.
        # Or... the Approach Temp increases.
        # Let's model it as an effective Approach Temp increase.
        current_approach = self.hx_approach_base / current_hx_eff 
        # e.g., if eff drops to 0.5, approach doubles to 6C.
        
        t_server_out = 50.0
        t_sea_out = t_server_out - current_approach
        
        if t_sea_out <= t_sea_in: 
            return 0, 0, 0, 0, 0 # Failed to cool
            
        # 2. Pipeline Heat Loss (Reduces Buoyancy)
        # T_hot_avg = T_sea_out - Loss.
        # Q_loss = U * A * dT_ambient. U approx 10 W/m2K (insulated).
        # A = Pi * D * H * N. dT = T_sea_out - T_air (assume 20C).
        # Q_loss_total = 10 * (np.pi * self.D * self.H * 10) * (t_sea_out - 20)
        # T_drop = Q_loss / (m_dot * Cp). Implicit loop!
        # Simplified: Assume 0.5C drop for now to avoid nested solver loop.
        t_sea_hot_riser = t_sea_out - 0.5 
        
        # 3. Hydraulic Solve
        rho_in = self.get_density(t_sea_in)
        rho_out = self.get_density(t_sea_hot_riser) # Use cooler riser temp
        rho_avg = (rho_in + rho_out) / 2
        p_buoyancy = (rho_in - rho_out) * self.g * self.H
        
        # HX Pressure Drop increases with fouling too?
        # Usually dP increases as fouling ^2.
        # current_hx_dp = 50000 * ((1 + 0.05) ** months_since_clean)
        current_hx_dp = 50000 * (1.05 ** months_since_clean)
        
        k_minor_res = 0.5 + 1.0 + (4 * 0.3) + 0.2
        
        def force_balance(v):
             if v <= 1e-4: return p_buoyancy + 1e9 # Driving force large
             
             area_total = 10 * (np.pi * (self.D/2)**2)
             q = v * area_total
             
             p_pump = (self.booster_power_w * 0.85) / q
             
             mu = self.get_viscosity((t_sea_in + t_sea_out)/2)
             Re = (rho_avg * v * self.D) / mu
             
             if Re < 2300: f = 64/Re
             else:
                 rr = current_roughness / self.D
                 term = (rr/3.7)**1.11 + (6.9/Re)
                 f = (-1.8 * np.log10(term))**-2
                 
             hl = (f * self.H / self.D) + k_minor_res
             p_loss_hydro = rho_avg * hl * (v**2 / 2)
             
             return (p_buoyancy + p_pump) - (p_loss_hydro + current_hx_dp)

        try:
             v_sol = brentq(force_balance, 0.01, 15.0)
        except ValueError:
             v_sol = 0.0
             
        area = 10 * (np.pi * (self.D/2)**2)
        q = v_sol * area
        m_dot = q * rho_out
        
        # Check Cooling Capacity
        heat_cap_w = m_dot * self.cp_water * (t_sea_out - t_sea_in)
        cooling_load_w = 50e6
        cooling_met = heat_cap_w >= cooling_load_w
        
        # Power Gen
        p_turbine = 0.80 * m_dot * self.g * self.H
        
        # 4. Thermal Pollution Penalty
        # If T_sea_out > 35, dilute to 34.5
        dilution_power = 0
        if t_sea_out > 35.0:
            # Mixture: (m_sys * T_out) + (m_cold * T_in) = (m_sys + m_cold) * 34.5
            # m_sys(T_out - 34.5) = m_cold(34.5 - T_in)
            # m_cold = m_sys * (T_out - 34.5) / (34.5 - T_in)
            if (34.5 - t_sea_in) > 0:
                m_cold = m_dot * (t_sea_out - 34.5) / (34.5 - t_sea_in)
                # Pumping Power for dilution (Low head 5m)
                dilution_power = (m_cold * self.g * 5) / 0.85
            else:
                dilution_power = 10e6 # Infinite cost if Intake > 34.5 (unlikely 17.5 avg)
                
        return v_sol, p_turbine, dilution_power, cooling_met, t_sea_out

    def run_20y_simulation(self):
        # Time Loop
        months = 240
        data = []
        total_profit = 0
        
        # Setup CapEx
        # Structure Cost
        vol_steel = np.pi * self.D * 0.02 * self.H * 10
        cost_steel = vol_steel * 7850 * 1.5
        cost_struct = 12000 * self.H * (1 + self.H/500)
        cost_hx = 50000 * self.capex_titanium_cost # 50MW * 100/kW
        cost_ins = self.capex_insulation * self.H * 10
        
        capex_total = self.capex_land + self.capex_civil + cost_steel + cost_struct + cost_hx + cost_ins
        
        cash_flow = [-capex_total] # Month 0
        
        cdu_power = 50e6 * 0.025
        
        # Seasonality
        sea_temps = 10 + 15 * np.sin((np.arange(months) % 12) * np.pi / 6) # 10 to 25 Cycle? No, 10 + 15=25? 
        # Base=17.5 +/- 7.5 -> 10 to 25.
        sea_temps = 17.5 + 7.5 * np.sin((np.arange(months) * 2 * np.pi / 12)) 
        
        for m in range(months):
            t_in = sea_temps[m]
            
            # Physics Solve
            v, p_gen, p_dilution, cooling_met, t_out = self.solve_hydraulics_at_month(m, t_in)
            
            # Maintenance Cost
            maint_cost = 0
            if (m + 1) % 12 == 0:
                maint_cost = self.maintenance_cost
            
            # Net Power
            # If cooling not met, assume backup chillers used (Huge Penalty)
            penalty_cooling = 0
            if not cooling_met:
                penalty_cooling = 50e6 / 3.0 # COP 3 chiller cost for unmet load? 
                # Let's just penalize the missing MW
                
            p_net = p_gen - (self.booster_power_w + cdu_power + p_dilution + penalty_cooling)
            
            # Financials
            energy_rev = (p_net / 1000) * 24 * 30 * self.elec_price
            
            # Chemical OpEx (Time dependent?)
            chem_cost = 20000 # Fixed monthly chemical
            
            monthly_net_cash = energy_rev - chem_cost - maint_cost
            
            cash_flow.append(monthly_net_cash)
            data.append({
                "Month": m,
                "Net_Power_MW": p_net/1e6,
                "T_Out": t_out,
                "Cooling_Met": cooling_met
            })
            
        npv = npf.npv(0.08/12, cash_flow) # Monthly discount rate
        
        return npv, pd.DataFrame(data), capex_total

def run_golden_scenario():
    print("Running 3D Optimization for Golden Scenario...")
    
    # Sweep
    heights = np.linspace(50, 200, 5) # 5 points
    diameters = np.linspace(1.5, 3.5, 5) # 5 points
    # Fixed Optimized Pump for now (2MW was good for 50m/2m)
    # Maybe scale pump with H? No, let's keep it fixed to test robustness.
    pump_kw = 2000 
    
    results = []
    
    for h in heights:
        for d in diameters:
            sim = NightmarePhysics(h, d, pump_kw)
            npv, df_time, capex = sim.run_20y_simulation()
            
            results.append({
                "Height": h,
                "Diameter": d,
                "NPV": npv / 1e6, # Millions
                "CapEx": capex / 1e6,
                "Avg_Power_MW": df_time['Net_Power_MW'].mean()
            })
            
    df_res = pd.DataFrame(results)
    
    # Visualization
    os.makedirs("assets", exist_ok=True)
    plt.style.use('dark_background')
    # sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(16, 8))
    
    # Plot 1: 3D Surface
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    
    pivot = df_res.pivot(index="Height", columns="Diameter", values="NPV")
    X, Y = np.meshgrid(pivot.columns, pivot.index)
    Z = pivot.values
    
    surf = ax1.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')
    ax1.set_title("3D Profit Landscape (NPV 20y)")
    ax1.set_xlabel("Diameter (m)")
    ax1.set_ylabel("Height (m)")
    ax1.set_zlabel("NPV ($ Millions)")
    fig.colorbar(surf, ax=ax1, shrink=0.5, aspect=5, label="NPV ($M)")
    
    # Plot 2: Time Series of Golden Config
    # Find best
    best = df_res.loc[df_res['NPV'].idxmax()]
    print("\n" + "#"*60)
    print("SIMULATION v7.0: NIGHTMARE MODE RESULTS")
    print("#"*60)
    print(f"GOLDEN CONFIGURATION:")
    print(f"  Height       : {best['Height']:.0f} m")
    print(f"  Diameter     : {best['Diameter']:.1f} m")
    print(f"  Pump Power   : 2.0 MW")
    print(f"  NPV (20y)    : ${best['NPV']:.1f} Million")
    print(f"  Avg Net Power: {best['Avg_Power_MW']:.2f} MW")
    print("#"*60)
    
    # Re-run best for time plot
    sim_best = NightmarePhysics(best['Height'], best['Diameter'], 2000)
    _, df_best, _ = sim_best.run_20y_simulation()
    
    ax2 = fig.add_subplot(1, 2, 2)
    # Plot only 5 years (60 months) for clarity
    df_plot = df_best.iloc[:60]
    ax2.plot(df_plot['Month'], df_plot['Net_Power_MW'], 'b-', label='Net Power')
    ax2.set_title("Performance Sawtooth: Biofouling vs. Maintenance")
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Net Power (MW)")
    
    # Highlight Maintenance (every 12 months)
    for i in range(12, 60, 12):
        ax2.axvline(i, color='red', linestyle='--', alpha=0.5)
        
    ax2.text(12, df_plot['Net_Power_MW'].min(), ' Maint.', color='red')
    
    plt.tight_layout()
    out = "assets/v7_nightmare_golden.png"
    plt.savefig(out, dpi=150)
    print(f"Chart saved to {out}")

if __name__ == "__main__":
    run_golden_scenario()
