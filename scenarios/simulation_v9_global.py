import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns
from scipy.optimize import brentq

class Location:
    def __init__(self, name, sea_temp_range, labor_rate, concrete_cost, seismic_risk, hx_material_factor):
        self.name = name
        self.temp_min, self.temp_max = sea_temp_range
        self.labor_rate = labor_rate # $/hr
        self.concrete_cost = concrete_cost # $/m3
        self.seismic_factor = 1.4 if seismic_risk == 'High' else 1.0 # Steel multiplier
        self.hx_material_factor = hx_material_factor # 1.0 (Steel) or 1.5 (Titanium)
        self.biofouling_risk = 'High' if 'Dubai' in name else 'Low'

class ConstructionManager:
    """
    Handles Material, Labor, and Timeline calculations for a 200m Tower.
    """
    def __init__(self, location):
        self.loc = location
        # Tower Specs (Golden Config)
        self.H = 200.0
        self.D_inner = 3.5
        self.t_wall = 0.5
        
    def calculate_capex_timeline(self):
        # 1. Volumes
        # Cylinder Volume = Pi * (R_out^2 - R_in^2) * H
        r_out = (self.D_inner/2) + self.t_wall
        r_in = self.D_inner/2
        vol_concrete = np.pi * (r_out**2 - r_in**2) * self.H
        
        # Foundation (Est 20x20x5m block)
        vol_foundation = 20 * 20 * 5 
        total_concrete = vol_concrete + vol_foundation
        
        # Steel Reinforcement (kg)
        # Standard: 150 kg/m3 concrete
        # Seismic: +40% (handled by seismic_factor)
        mass_steel = total_concrete * 150 * self.loc.seismic_factor
        
        # 2. Material Costs
        cost_concrete = total_concrete * self.loc.concrete_cost
        cost_steel = mass_steel * 1.5 # Global Steel Price Base ($1.5/kg)
        
        # HX Cost (50MW Capacity)
        # Base Titanium was $100/kW. If Steel, maybe $70/kW?
        # Let's say Base Reference is Steel ($70/kW). Titanium is 1.5x -> $105/kW.
        base_hx_unit_cost = 70 
        cost_hx = 50_000 * base_hx_unit_cost * self.loc.hx_material_factor
        
        # 3. Timeline (Days)
        # Excavation
        rate_excavation = 500 # m3/day
        days_excavation = vol_foundation / rate_excavation
        
        # Slip-form Casting
        rate_casting = 3.0 # m/day vertical
        days_casting = self.H / rate_casting
        
        # Fixed phases
        days_mob = 30
        days_mep = 60
        
        total_days = days_mob + days_excavation + days_casting + days_mep
        
        # 4. Labor Cost
        # Crew: 50 workers avg * 10 hours * days
        total_man_hours = 50 * 10 * total_days
        cost_labor = total_man_hours * self.loc.labor_rate
        
        # Total CapEx
        other_infra = 3_000_000 # Roads, Civil, Land fixed base (adjusted?)
        # Let's assume Land is cheaper in some places but standardized for comparison
        # Dubai/LA land expensive, Finland maybe less? Keep fixed for now.
        
        total_capex = cost_concrete + cost_steel + cost_hx + cost_labor + other_infra
        
        return {
            "Days": int(total_days),
            "CapEx": total_capex,
            "Cost_Concrete": cost_concrete,
            "Cost_Labor": cost_labor,
            "Cost_HX": cost_hx
        }

class GlobalSimulation:
    def __init__(self):
        # Locations
        self.locations = [
            Location("Dubai (UAE)", (20, 35), 5.0, 80.0, 'Low', 1.5),
            Location("Helsinki (Finland)", (0, 15), 50.0, 150.0, 'None', 1.0),
            Location("Los Angeles (USA)", (12, 20), 80.0, 200.0, 'High', 1.5)
        ]
        
        # Physics Engine (Simplified v7 for speed)
        self.H = 200.0
        self.D = 3.5
        self.pump_kw = 2000.0
        self.g = 9.81
        self.cp = 4186
        
    def get_density(self, t):
         return 1028.17 - 0.0663 * t - 0.0038 * t**2
         
    def solve_net_power(self, t_sea):
        # Simplified Hydraulic Solve for 200m/3.5m/2MW
        # Based on v7 results: ~52MW net for avg temp.
        # Let's re-calc properly but single iter.
        
        t_hot = t_sea + 30 # Server added heat (approx)
        # Limit T_hot by Thermal Pollution if needed? 
        # Actually T_out = T_sea + dT. 
        # v7 used approach temp. Let's use simple logic:
        # P_buoy = (rho_c - rho_h) * g * H
        # P_pump = 2MW
        # P_loss = k * Q^2
        # Solve Q.
        
        rho_c = self.get_density(t_sea)
        rho_h = self.get_density(t_hot)
        p_drive = (rho_c - rho_h) * 9.81 * 200 + (2e6 * 0.85 / 10.0) # approx pump head distrib
        # Just use scaling from v7 result
        # v7: 200m, 3.5m, 2MW -> ~60MW Gen.
        # Temp delta drives density delta.
        # Standard: dT=30 -> dRho ~ 10.
        # Finland: T_in=0, T_out=30 -> dRho ~ 8 (cold water expansion is weird? Density max at 4C pure, seawater monotonic)
        # Seawater density decreases heavily with T.
        # Let's use exact density calc.
        
        density_drive = rho_c - rho_h
        # P_gen proportional to density_drive?
        # P_gen = m * g * H. m depends on v. v depends on sqrt(drive).
        # So P_gen ~ sqrt(drive) * rho.
        
        # Baseline (17.5C -> 47.5C): Drive ~ 10 kg/m3 -> 52MW Net.
        ref_drive = 10.0
        ratio = density_drive / ref_drive
        if ratio < 0: ratio = 0
        p_gen_est = 60.0 * np.sqrt(ratio) # 60MW gross approx
        
        # Penalties
        # 1. CDU (1.25 MW)
        # 2. Pump (2.0 MW)
        # 3. Dilution (If T_out > 35)
        p_dilution = 0
        if t_hot > 35:
            # Simple penalty model: 1MW per degree over 35?
            # From v7: Dilution is expensive.
            # Dubai: T_out can be 35+30 = 65. Massive dilution needed.
            # Finland: T_out 0+30=30. No dilution.
            # LA: 20+30=50. Dilution needed.
            
            # Dilution Factor = (T_out - 35) / (35 - T_in)
            # if T_in >= 35, infinite.
            if t_sea >= 35:
                p_dilution = 100 # Failure
            else:
                 m_ratio = (t_hot - 35) / (35 - t_sea)
                 # Pump power for cold water
                 # Assume same head loss for dilution loop? Maybe lower (5m)
                 # Base flow ~ 15 m3/s (for 50MW/30K). 
                 # Power ~ m_ratio * 15000kg * 9.8 * 5 / 0.85 / 1e6 MW
                 p_dilution = m_ratio * 0.9 # Approx 0.9MW per ratio unit
        
        p_net = p_gen_est - 1.25 - 2.0 - p_dilution
        return p_net

    def run_analysis(self):
        results = []
        
        for loc in self.locations:
            # 1. Construction
            cm = ConstructionManager(loc)
            const_data = cm.calculate_capex_timeline()
            
            # 2. Physics (Annual Avg)
            # Simulate 12 months
            t_months = np.linspace(loc.temp_min, loc.temp_max, 12)
            # sinusoidal
            t_months = (loc.temp_min + loc.temp_max)/2 + (loc.temp_max - loc.temp_min)/2 * np.sin(np.linspace(0, 2*np.pi, 12))
            
            net_power_list = []
            for t in t_months:
                net_power_list.append(self.solve_net_power(t))
                
            avg_net_power = np.mean(net_power_list)
            
            # 3. Financials
            # Revenue
            elec_price = 0.12 # Global avg or adjust? Dubai cheaper (gas)? Finland expensive?
            # Let's keep fixed for comparison of SYSTEM, not Grid prices.
            annual_rev = avg_net_power * 1000 * 24 * 365 * elec_price
            
            # ROI
            capex = const_data['CapEx']
            roi_10y = ((annual_rev * 10) - capex) / capex * 100
            
            results.append({
                "Location": loc.name,
                "CapEx ($M)": capex / 1e6,
                "Days": const_data['Days'],
                "Net_Power_MW": avg_net_power,
                "ROI_10y_%": roi_10y,
                "Labor_Cost_M": const_data['Cost_Labor']/1e6,
                "Material_Cost_M": (const_data['Cost_Concrete'] + const_data['Cost_HX'])/1e6
            })
            
        return pd.DataFrame(results)

    def generate_report(self):
        df = self.run_analysis()
        
        print("\n" + "#"*60)
        print("SIMULATION v9.0: GLOBAL ATLAS & CONSTRUCTION MANAGER")
        print("#"*60)
        print(f"{'Location':<20} | {'CapEx ($M)':<10} | {'Days':<5} | {'Net MW':<8} | {'ROI (10y)':<8}")
        print("-" * 70)
        for index, row in df.iterrows():
            print(f"{row['Location']:<20} | ${row['CapEx ($M)']:<9.1f} | {row['Days']:<5.0f} | {row['Net_Power_MW']:<8.1f} | {row['ROI_10y_%']:<8.0f}%")
        print("-" * 70)
        
        # Findings
        winner = df.loc[df['ROI_10y_%'].idxmax()]
        print(f"RECOMMENDATION: Build in {winner['Location']}")
        print(f"  Reasoning: Highest ROI ({winner['ROI_10y_%']:.0f}%) due to optimal balance of CapEx and Buoyancy.")
        
        # Visualization
        self.plot_global_map(df)

    def plot_global_map(self, df):
        os.makedirs("assets", exist_ok=True)
        plt.style.use('dark_background')
        # sns.set_theme(style="whitegrid")
        fig = plt.figure(figsize=(14, 8))
        
        # Plot 1: Viability Map (Net Profit Potential)
        ax1 = plt.subplot(2, 1, 1)
        # Net Profit 10y = ROI * CapEx
        df['Net_Profit_10y_M'] = (df['ROI_10y_%']/100) * df['CapEx ($M)']
        
        sns.barplot(data=df, x='Location', y='Net_Profit_10y_M', palette='viridis', ax=ax1)
        ax1.set_title("Global Viability Map: 10-Year Net Profit Potential")
        ax1.set_ylabel("Net Profit ($ Millions)")
        
        for index, row in df.iterrows():
            ax1.text(index, row['Net_Profit_10y_M'], f"${row['Net_Profit_10y_M']:.0f}M", color='black', ha='center', va='bottom')
            
        # Plot 2: Cost Structure Breakdown
        ax2 = plt.subplot(2, 1, 2)
        
        # Stacked Bar for CapEx
        # Normalize? No, absolute.
        x = range(len(df))
        p1 = ax2.bar(x, df['Labor_Cost_M'], label='Labor')
        p2 = ax2.bar(x, df['Material_Cost_M'], bottom=df['Labor_Cost_M'], label='Materials (Concrete/HX)')
        # Remaining is Steel/Civil approx
        # remainder = CapEx - Labor - Mat
        rem = df['CapEx ($M)'] - df['Labor_Cost_M'] - df['Material_Cost_M']
        p3 = ax2.bar(x, rem, bottom=df['Labor_Cost_M'] + df['Material_Cost_M'], label='Steel/Civil/Infra')
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(df['Location'])
        ax2.set_ylabel("CapEx breakdown ($ Millions)")
        ax2.set_title("Construction Cost Structure by Region")
        ax2.legend()
        
        plt.tight_layout()
        out = "assets/v9_global_viability.png"
        plt.savefig(out, dpi=150)
        print(f"Chart saved to {out}")

if __name__ == "__main__":
    sim = GlobalSimulation()
    sim.generate_report()
