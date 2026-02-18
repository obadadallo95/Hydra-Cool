import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns
from scipy.optimize import brentq

class FinancialAndPhysicsEngine:
    """
    Simulation v11.0: The Grand Unified Model
    Integrates Location, Depth, Hybrid Physics, Stress Testing, and Financials.
    """
    def __init__(self):
        # Global Settings
        self.H_tower = 200.0
        self.D_pipe = 3.5
        self.pump_eff = 0.85
        self.turbine_eff = 0.80
        self.sys_load_mw = 50.0
        self.num_pipes = 10
        self.project_life = 10 # Years for TCO
        
        # Competitor Baselines (10y TCO for 50MW)
        # Based on v4 results scaled to 50MW
        self.competitors = {
            "Google (Water)": 1100.0, # $M
            "Microsoft (Immersion)": 1300.0, # $M
            "Standard Air": 1350.0 # $M
        }

    def get_seawater_temp(self, loc_name, depth):
        """ Thermocline Models """
        if "Dubai" in loc_name:
            # Hot Surface (35), Cold Deep (5)
            return 5.0 + (35.0 - 5.0) * np.exp(-0.01 * depth)
        elif "Helsinki" in loc_name:
            # Cold Surface (10 avg), Deep (4)
            # Shallow is actually colder in winter, but let's use annual avg.
            # Surface 8C, Deep 4C.
            return 4.0 + (8.0 - 4.0) * np.exp(-0.005 * depth)
        elif "Los Angeles" in loc_name:
             # Moderate Surface (16), Deep (5)
             return 5.0 + (16.0 - 5.0) * np.exp(-0.015 * depth)
        return 20.0

    def get_density(self, t):
         return 1028.17 - 0.0663 * t - 0.0038 * t**2
         
    def get_viscosity(self, t):
        return 1.88e-3 * ((t + 20)**(-0.6))

    def solve_hydraulics(self, loc_name, depth):
        t_in = self.get_seawater_temp(loc_name, depth)
        
        # Intake Pipe
        slope = 10.0 # degrees
        length_intake = depth / np.sin(np.radians(slope)) if depth > 0 else 0
        l_total = 400.0 + length_intake # Tower loop + intake
        
        # Booster Pump (Hybrid) - Standard 2MW
        p_booster_limit = 2.0e6 
        
        # HX Drop
        dp_hx = 50000.0
        
        def energy_balance(v):
            if v <= 1e-4: return 1e9
            
            # Flow
            area = self.num_pipes * (np.pi * (self.D_pipe/2)**2)
            q = v * area
            m_dot = q * self.get_density(t_in)
            
            # Heat & Temp Out
            d_t = (self.sys_load_mw * 1e6) / (m_dot * 4186)
            t_out = t_in + d_t
            
            # Buoyancy
            rho_in = self.get_density(t_in)
            rho_out = self.get_density(t_out)
            rho_avg = (rho_in + rho_out)/2
            p_buoy = (rho_in - rho_out) * 9.81 * self.H_tower
            
            # Friction
            mu = self.get_viscosity((t_in+t_out)/2)
            Re = (rho_avg * v * self.D_pipe) / mu
            roughness = 0.000045 # Clean pipe base (Biofouling handled in OpEx or physics margin)
            # Let's add 20% roughness safety factor for "Avg Biofouling State"
            roughness *= 1.2 
            
            if Re < 2300: f = 64/Re
            else:
                rr = roughness / self.D_pipe
                term = (rr/3.7)**1.11 + (6.9/Re)
                f = (-1.8 * np.log10(term))**-2
            
            k_minor = 2.5
            head_loss = (f * l_total / self.D_pipe) + k_minor
            p_fric = rho_avg * head_loss * (v**2 / 2)
            
            # Pump Head req
            # if Drive < Resistance, Pump makes up difference
            req_pump_pressure = (p_fric + dp_hx) - p_buoy
            
            # Check if Pump Limit Exceeded
            # Power = Q * P_pressure / eff
            # P_pressure = Power * eff / Q
            avail_pump_pressure = (p_booster_limit * self.pump_eff) / q
            
            return (p_buoy + avail_pump_pressure) - (p_fric + dp_hx)

        try:
            v = brentq(energy_balance, 0.1, 15.0)
        except ValueError:
            v = 0.0
            
        if v > 0:
            area = self.num_pipes * (np.pi * (self.D_pipe/2)**2)
            q = v * area
            m_dot = q * self.get_density(t_in)
            d_t = (self.sys_load_mw * 1e6) / (m_dot * 4186)
            t_out = t_in + d_t
            
            p_gen = self.turbine_eff * m_dot * 9.81 * self.H_tower
            
            # Parasitics
            p_cdu = 1.25e6
            p_pump = p_booster_limit # We assumed full power used/avail for max flow
            # Refine: If req_pump_pressure < limit, we use less?
            # For optimization finding "Best Depth", assume constant pump usage or scale?
            # Let's assume constant 2MW pump cost for robustness.
            
            # Dilution (Thermal Pollution)
            p_dil = 0
            if t_out > 35.0:
                 if t_in < 35.0:
                     m_dil = m_dot * (t_out - 35)/(35 - t_in)
                     p_dil = (m_dil * 9.81 * 5) / 0.85
                 else:
                     p_dil = 100e6 # Fail
            
            p_net = (p_gen - p_cdu - p_pump - p_dil) / 1e6 # MW
            
            return p_net, t_in, length_intake
        else:
            return -50.0, t_in, length_intake # Failed

    def optimize_depth(self, loc_name):
        depths = np.linspace(0, 500, 20) # 0 to 500m
        best_net = -999
        best_d = 0
        best_tin = 0
        best_len = 0
        
        for d in depths:
            net, tin, l_pipe = self.solve_hydraulics(loc_name, d)
            if net > best_net:
                best_net = net
                best_d = d
                best_tin = tin
                best_len = l_pipe
                
        return best_d, best_net, best_len

    def run_global_analysis(self):
        results = []
        
        locations = [
            {"Name": "Dubai (UAE)", "Labor": 5, "Conc": 80, "Seismic": 0, "Titanium": 1.5, "Biofoil": 500000}, # High biofoil cost
            {"Name": "Helsinki (Finland)", "Labor": 50, "Conc": 150, "Seismic": 0, "Titanium": 1.0, "Biofoil": 50000},
            {"Name": "Los Angeles (USA)", "Labor": 80, "Conc": 200, "Seismic": 10000000, "Titanium": 1.5, "Biofoil": 100000},
        ]
        
        print("\n" + "="*80)
        print("SIMULATION v11.0: THE GRAND UNIFIED REPORT")
        print("="*80)
        
        print(f"{'Location':<20} | {'Depth':<5} | {'NetPower':<9} | {'CapEx':<7} | {'OpEx/yr':<7} | {'10y Profit':<10} | {'Verdict'}")
        print("-" * 105)
        
        scorecard = []
        
        for loc in locations:
            # 1. Physics Optimization
            d_opt, net_mw, l_pipe = self.optimize_depth(loc['Name'])
            
            # 2. Financials (CapEx)
            # Base Tower (200m)
            vol_conc = 12000 # m3 approx
            mass_steel = vol_conc * 150 
            cost_struct = (vol_conc * loc['Conc']) + (mass_steel * 1.5)
            cost_hx = 50000 * 70 * loc['Titanium'] # $3.5M or $5.25M
            cost_intake = l_pipe * 2000 # $2000/m pipe cost
            cost_seismic = loc['Seismic']
            
            capex = cost_struct + cost_hx + cost_intake + cost_seismic + 5_000_000 # Land/Civil
            
            # 3. OpEx & Revenue
            # Staffing
            staff_cost = 3_240_000 * (loc['Labor']/80.0) # Base LA rate scaled? Or just fixed?
            # Let's scale roughly.
            # Revenue (Net Power * $0.12/kWh)
            energy_rev_yr = net_mw * 1000 * 24 * 365 * 0.12 if net_mw > 0 else 0
            
            opex_yr = staff_cost + loc['Biofoil']
            
            profit_yr = energy_rev_yr - opex_yr
            profit_10y = (profit_yr * 10) - capex
            
            roi = (profit_10y / capex) * 100 if capex > 0 else 0
            
            verdict = "GO" if roi > 500 else "NO-GO"
            if net_mw < 0: verdict = "FAIL"
            
            results.append({
                "Location": loc['Name'],
                "Best_Depth_m": d_opt,
                "Net_MW": net_mw,
                "CapEx_M": capex/1e6,
                "OpEx_M": opex_yr/1e6,
                "Profit_10y_M": profit_10y/1e6,
                "ROI": roi
            })
            
            print(f"{loc['Name']:<20} | {d_opt:<5.0f} | {net_mw:<9.2f} | ${capex/1e6:<6.1f} | ${opex_yr/1e6:<6.1f} | ${profit_10y/1e6:<9.1f} | {verdict}")

            # Calculate TCO (Total Cost of Ownership for Comparison)
            # TCO = Cost to User. 
            # If User Owns it: TCO = CapEx + 10*OpEx - 10*Rev(sold to grid?). 
            # Actually, "Net Benefit" is better. 
            # Or TCO = CapEx + 10*OpEx. The Cooling is "Free" value.
            # Comparison: Google spends $1.1B. We "spend" (CapEx + OpEx) - Revenue.
            # If Revenue > Costs, our TCO is Negative (Profit).
            
            my_tco = (capex + 10*opex_yr) - (net_mw * 1000 * 24 * 365 * 0.12 * 10)
            my_tco = my_tco / 1e6 # Millions
            
            scorecard.append({
                "System": f"Hybrid ({loc['Name'].split()[0]})",
                "TCO_10y_M": my_tco
            })
            
        print("-" * 105)
        
        # Add Competitors
        for name, val in self.competitors.items():
            scorecard.append({"System": name, "TCO_10y_M": val})
            
        sc_df = pd.DataFrame(scorecard)
        self.plot_scoreboard(sc_df)
        
    def plot_scoreboard(self, df):
        os.makedirs("assets", exist_ok=True)
        plt.style.use('dark_background')
        # sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Sort
        df = df.sort_values("TCO_10y_M")
        
        # Color: Green for negative (Profit), Red for positive (Cost)
        colors = ['green' if x < 0 else 'firebrick' for x in df['TCO_10y_M']]
        
        sns.barplot(data=df, x='TCO_10y_M', y='System', palette=colors, ax=ax)
        
        ax.set_title("10-Year Total Cost of Ownership (TCO) Comparison")
        ax.set_xlabel("Net Cost ($ Millions) [Negative = PROFIT]")
        
        # Add labels
        for i, v in enumerate(df['TCO_10y_M']):
            ax.text(v, i, f" ${v:.0f}M", color='black', va='center', ha='right' if v<0 else 'left')
            
        plt.tight_layout()
        out = "assets/v11_unified_tco.png"
        plt.savefig(out, dpi=150)
        print(f"Chart saved to {out}")

if __name__ == "__main__":
    sim = FinancialAndPhysicsEngine()
    sim.run_global_analysis()
