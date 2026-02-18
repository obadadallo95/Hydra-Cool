import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns
from scipy.optimize import brentq
import numpy_financial as npf

class DigitalTwinSystem:
    """
    Simulation v5.0: The Digital Twin
    Rigorous engineering model with Two-Loop architecture and internal losses.
    """
    def __init__(self, hx_pressure_drop_kpa=50):
        # --- Physical Parameters ---
        self.height = 50.0  # m
        self.diameter = 2.0  # m
        self.num_pipes = 10 
        self.roughness = 0.000045 # Commercial steel
        self.g = 9.81
        
        # Heat Exchanger (HX) Parameters
        self.hx_approach_temp = 3.0 # deg C
        self.hx_effectiveness = 0.90
        self.hx_pressure_drop_pa = hx_pressure_drop_kpa * 1000 # Convert kPa to Pa
        
        # System Load
        self.it_load_mw = 50.0 # 50 MW Data Center
        self.cdu_parasitic_pct = 0.025 # 2.5% of Total Heat Load
        
        # Financial Parameters
        self.capex_titanium_hx_per_kw = 100.0 # $/kW cooling
        self.capex_civil_fixed = 2_000_000 # $2M
        self.capex_base_structure_per_m = 12000 # from v3
        self.steel_price = 1.5 # $/kg
        self.elec_price = 0.12 # $/kWh
        
        # Constants
        self.cp_water = 4186 # J/kg.K
        
    def get_density(self, temp_c):
        """Seawater density (kg/m^3)."""
        return 1028.17 - 0.0663 * temp_c - 0.0038 * temp_c**2

    def get_viscosity(self, temp_c):
        """Seawater viscosity (Pa.s)."""
        return 1.88e-3 * ((temp_c + 20)**(-0.6))

    def solve_loop_b_hydraulics(self, t_sea_in):
        """
        Solves the External Seawater Loop (Thermosiphon).
        Returns: mass_flow (kg/s), velocity (m/s), turbine_power (W)
        """
        # 1. Determine Loop B Temperatures
        # Loop A (Internal) is roughly constant T_hot_in (e.g., 50C)
        t_server_out = 50.0
        
        # Loop B (External) T_out depends on HX Approach
        # T_sea_out = T_server_out - Approach
        t_sea_out = t_server_out - self.hx_approach_temp
        
        # Check if T_sea_out > T_in (Thermodynamics check)
        if t_sea_out <= t_sea_in:
            return 0.0, 0.0, 0.0 # No driving force
            
        # 2. Solve Thermosiphon Velocity
        # Driving Pressure = (rho_in - rho_out) * g * H
        rho_in = self.get_density(t_sea_in)
        rho_out = self.get_density(t_sea_out)
        rho_avg = (rho_in + rho_out) / 2
        
        delta_rho = rho_in - rho_out
        p_drive = delta_rho * self.g * self.height
        
        # Loss Coefficients
        # Standard minor losses (Entrance, Exit, Bends)
        k_minor_standard = 0.5 + 1.0 + (4 * 0.3) + 0.2
        
        def pressure_balance(v):
            if v <= 0: return p_drive
            
            # Reynolds
            mu_avg = self.get_viscosity((t_sea_in + t_sea_out)/2)
            Re = (rho_avg * v * self.diameter) / mu_avg
            
            # Friction Factor (Haaland)
            if Re < 2300: f = 64/Re
            else:
                rel_rough = self.roughness / self.diameter
                term = (rel_rough/3.7)**1.11 + (6.9/Re)
                f = (-1.8 * np.log10(term))**-2
                
            # Head Loss (Pipe Friction + Dist)
            # h_L = (f*L/D + K_std) * v^2/2g
            head_loss_coeff = (f * self.height / self.diameter) + k_minor_standard
            p_loss_hydro = rho_avg * head_loss_coeff * (v**2 / 2)
            
            # ADD HX PRESSURE DROP (Fixed Value)
            # This is a major penalty!
            p_loss_total = p_loss_hydro + self.hx_pressure_drop_pa
            
            return p_drive - p_loss_total

        try:
            v_sol = brentq(pressure_balance, 0.001, 20.0)
        except ValueError:
            v_sol = 0.0 # Stalled
            
        # 3. Calculate Power
        area_total = self.num_pipes * (np.pi * (self.diameter/2)**2)
        q_total = v_sol * area_total # m3/s
        m_dot = q_total * rho_out # kg/s
        
        turbine_eff = 0.80
        p_gen = turbine_eff * m_dot * self.g * self.height
        
        return m_dot, v_sol, p_gen

    def run_simulation(self):
        # 1. Parasitic Load (CDU Pumps)
        # Power = 2.5% of 50MW
        p_cdu = self.it_load_mw * 1e6 * self.cdu_parasitic_pct # Watts
        
        # 2. Turbine Generation
        # Assume annual avg sea temp 17.5C
        t_sea_avg = 17.5
        m_dot, v, p_turbine = self.solve_loop_b_hydraulics(t_sea_avg)
        
        # 3. Net Power Analysis
        p_net = p_turbine - p_cdu
        
        # 4. Thermal Capacity Check
        # Does the Loop B mass flow have enough capacity to cool 50MW?
        # Q_capacity = m_dot * Cp * delta_T
        # T_in = 17.5, T_out = 47.0 -> dT = 29.5
        heat_capacity_w = m_dot * self.cp_water * (47.0 - 17.5)
        
        cooling_deficit = (self.it_load_mw * 1e6) - heat_capacity_w
        cooling_met = heat_capacity_w >= (self.it_load_mw * 1e6)
        
        # 5. Financials
        # CapEx
        # Titanium HX Cost
        capex_hx = (self.it_load_mw * 1000) * self.capex_titanium_hx_per_kw # $ per kW * kW
        # Civil
        capex_civil = self.capex_civil_fixed
        # Structure + Pipes (Scaled from v3)
        pipe_vol = np.pi * self.diameter * 0.02 * self.height * self.num_pipes
        pipe_cost = pipe_vol * 7850 * self.steel_price
        struct_cost = self.capex_base_structure_per_m * self.height * (1 + self.height/500)
        capex_infra = pipe_cost + struct_cost
        
        total_capex = capex_hx + capex_civil + capex_infra
        
        # OpEx & Revenue
        # Revenue = Value of Generated Power + Value of Saved Pumping Power (External Loop)
        # We compare against a standard system that would pump this seawater.
        # Avoided Pump Power: (m * g * H) / pump_eff
        p_avoided = (m_dot * self.g * self.height) / 0.85
        
        # Total Value Created (vs Baseline)
        total_power_value_w = p_turbine + p_avoided - p_cdu
        # If negative, we are losing money compared to just... doing nothing? 
        # Actually value is calculated based on what we SAVE vs Class A.
        # Class A pays for Seawater Pump + CDU Pump.
        # We pay for CDU Pump but GAIN Turbine Power.
        # Differential = (Their_Seawater_Pump + Their_CDU) - (Our_CDU - Turbine)
        #              = Their_Seawater_Pump + Turbine
        # So "Value" is Turbine + Avoided Pumping. CDU cancels out roughly (standard vs ours).
        
        annual_revenue = (p_turbine + p_avoided) / 1000 * 24 * 365 * self.elec_price
        
        opex_annual = total_capex * 0.03 # 3% Maint
        
        net_profit = annual_revenue - opex_annual
        
        payback_years = total_capex / net_profit if net_profit > 0 else 999
        roi = ((net_profit * 10) - total_capex) / total_capex * 100
        
        return {
            "v_flow": v,
            "m_dot": m_dot,
            "p_turbine_mw": p_turbine / 1e6,
            "p_cdu_mw": p_cdu / 1e6,
            "p_net_mw": p_net / 1e6,
            "heat_capacity_mw": heat_capacity_w / 1e6,
            "cooling_met": cooling_met,
            "capex": total_capex,
            "annual_net_profit": net_profit,
            "payback": payback_years,
            "roi_10y": roi,
            "hx_pressure_drop": self.hx_pressure_drop_pa / 1000 # kPa
        }

def run_digital_twin_study():
    # 1. Run Parametric Sweep on HX Pressure Drop
    # Tradeoff: Lower dP = Bigger/Better HX = More Flow = More Power
    # But does it affect cost? In this simplified model, dP is an input parameter.
    # Let's see how sensitive the Net Power is to this restriction.
    
    drops = np.linspace(10, 100, 20) # 10 kPa to 100 kPa
    results = []
    
    for dP in drops:
        dt = DigitalTwinSystem(hx_pressure_drop_kpa=dP)
        res = dt.run_simulation()
        results.append(res)
        
    df = pd.DataFrame(results)
    
    # 2. Executive Report (Base Case 50 kPa)
    base_res = [r for r in results if abs(r['hx_pressure_drop'] - 50) < 2]
    if base_res:
        res = base_res[0]
    else:
        res = results[len(results)//2] # Fallback
        
    print("\n" + "#"*60)
    print("SIMULATION v5.0: DIGITAL TWIN - REALITY CHECK")
    print("#"*60)
    print(f"System Load        : 50.0 MW")
    print(f"Parasitic CDU Load : {res['p_cdu_mw']:.2f} MW (To be covered)")
    print("-" * 60)
    print(f"PHYSICS STATUS:")
    print(f"  Driving Force Reduced by HX Approach Temp (3°C)")
    print(f"  Flow Restriction : {res['hx_pressure_drop']:.1f} kPa (Heat Exchanger)")
    print(f"  Resulting V      : {res['v_flow']:.2f} m/s")
    print(f"  Turbine Gen      : {res['p_turbine_mw']:.2f} MW")
    print(f"  Net System Power : {res['p_net_mw']:.2f} MW")
    
    if res['p_net_mw'] < 0:
        print("\n>>> CRITICAL FAILURE: SYSTEM CONSUMES MORE POWER THAN IT GENERATES <<<")
        print(f"    Deficit: {abs(res['p_net_mw']):.2f} MW")
    else:
        print("\n>>> SUCCESS: SYSTEM IS ENERGY POSITIVE <<<")
        print(f"    Surplus: {res['p_net_mw']:.2f} MW")
        
    if not res['cooling_met']:
        print(">>> WARNING: INSUFFICIENT FLOW TO COOL 50MW! <<<")
        print(f"    Capacity: {res['heat_capacity_mw']:.1f} MW")
    
    print("-" * 60)
    print("FINANCIAL REALITY:")
    print(f"  Titanium HX Cost : ${50000 * 100:,.0f} (Significant CapEx Spike)")
    print(f"  Total CapEx      : ${res['capex']:,.2f}")
    print(f"  True Payback     : {res['payback']:.2f} Years")
    print(f"  True ROI (10y)   : {res['roi_10y']:.1f}%")
    print("#"*60)
    
    # 3. Visualization
    os.makedirs("assets", exist_ok=True)
    plt.style.use('dark_background')
    # sns.set_theme(style="darkgrid")
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color = 'tab:blue'
    ax1.set_xlabel('HX Pressure Drop (kPa)')
    ax1.set_ylabel('Net Power Output (MW)', color=color)
    ax1.plot(df['hx_pressure_drop'], df['p_net_mw'], color=color, linewidth=2, marker='o')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axhline(0, color='red', linestyle='--', label="Break Even Power")
    
    # Add CDU Load Line
    # No, Net Power already subtracts CDU. 0 is the threshold.
    
    # Secondary Axis: Payback Period
    ax2 = ax1.twinx()  
    color = 'tab:green'
    ax2.set_ylabel('Payback Period (Years)', color=color)  
    ax2.plot(df['hx_pressure_drop'], df['payback'], color=color, linestyle='--', marker='x')
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title("v5: DIGITAL TWIN - Heat Exchanger Optimization", color='white', fontweight='bold')
    fig.tight_layout()  
    out = "assets/v5_digital_twin_opt.png"
    plt.savefig(out, dpi=150)
    print(f"Chart saved to {out}")

if __name__ == "__main__":
    run_digital_twin_study()
