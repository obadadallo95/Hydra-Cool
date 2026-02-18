import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

class ThermoFinancialSim:
    """
    Advanced Parametric Sweep & Financial Analysis for Green Cooling System.
    """
    
    def __init__(self):
        # Physics Constants
        self.g = 9.81
        self.rho_water_avg = 1000.0 # Simplified for sweep
        self.t_in = 20
        self.t_out = 50
        self.rho_in = self.calculate_density(self.t_in)
        self.rho_out = self.calculate_density(self.t_out)
        self.delta_rho = self.rho_in - self.rho_out
        self.viscosity = 0.001 # Pa.s dynamic viscosity approx
        
        # Efficiencies
        self.eta_turbine = 0.80
        self.eta_pump = 0.85 
        
        # Financial Constants
        self.elec_cost_per_kwh = 0.12 # USD
        self.steel_price_per_kg = 1.50 # USD (approx market rate for raw steel)
        self.steel_density = 7850 # kg/m3
        self.interest_rate = 0.05 # 5% cost of capital (optional, but good for NPV)

    def calculate_density(self, temp_c):
        """Standard seawater density approximation."""
        return 1028.17 - 0.0663 * temp_c - 0.0038 * temp_c**2

    def run_scenario(self, height, diameter, num_pipes):
        """
        Calculates Physics + Financials for a SINGLE scenario.
        """
        # --- PHYSICS ---
        # 1. Flow Velocity (v)
        # Friction factor f needed. approximate f=0.02 for turbulent flow in large pipes
        f = 0.02 
        
        # Velocity derived from Bernoulli with losses: 
        # Driving Head = Friction Loss Head
        # (d_rho/rho) * h = f * (h/D) * (v^2 / 2g) ... (simplified form)
        # v = sqrt( (2 * g * D * delta_rho) / (f * rho_avg) )
        # Note: Height cancels out for velocity in this simplified vertical pipe model!
        # Assuming diameter is large enough that minor losses are negligible compared to friction?
        # Actually, for very short pipes, minor losses matter, but let's stick to the prompt's friction model.
        
        if self.delta_rho <= 0: return None
        
        velocity = np.sqrt( (2 * self.g * diameter * self.delta_rho) / (f * self.rho_water_avg) )
        
        # 2. Flow Rate (Q)
        area = np.pi * (diameter / 2)**2
        q_per_pipe = velocity * area
        total_q = q_per_pipe * num_pipes # m3/s
        mass_flow = total_q * self.rho_out # kg/s (using hot water density for mass movement)
        
        # 3. Power (Watts)
        # Power Generated = Efficiency * m * g * h
        p_gen = self.eta_turbine * mass_flow * self.g * height
        
        # Power Saved (Traditional Pump) = (m * g * h) / Efficiency
        p_saved = (mass_flow * self.g * height) / self.eta_pump
        
        total_power_benefit = p_gen + p_saved # Watts
        
        # --- FINANCIALS ---
        
        # 1. CapEx (Capital Expenditure)
        # Construction Phase: Base cost + height scaling (taller = harder)
        # Base Cost = $10,000 per meter * Height
        # Complexity Multiplier = 1 + (Height / 500) to simulate exponential difficulty
        construction_cost = (10000 * height) * (1 + (height / 500))
        
        # Pipe Material Cost
        # Volume of Steel = Pi * D * Thickness * H * NumPipes
        # Assume Wall Thickness t = 0.02m (2cm) for high pressure potential
        wall_thickness = 0.02 
        pipe_vol_steel = np.pi * diameter * wall_thickness * height * num_pipes
        pipe_mass_steel = pipe_vol_steel * self.steel_density
        pipe_cost = pipe_mass_steel * self.steel_price_per_kg
        
        turbine_cost_per_kw = 500 # Approx $500/kW for hydro turbines
        turbine_cost = (p_gen / 1000) * turbine_cost_per_kw
        
        capex = construction_cost + pipe_cost + turbine_cost
        
        # 2. OpEx (Operational Expenditure)
        opex_annual = capex * 0.02 # 2% maintenance
        
        # 3. Revenue / Value Stream
        kwh_per_year = (total_power_benefit / 1000) * 24 * 365
        annual_value = kwh_per_year * self.elec_cost_per_kwh
        
        net_annual_profit = annual_value - opex_annual
        
        # 4. ROI & Payback
        if net_annual_profit <= 0:
            payback_years = 999 # Never
            roi_10y = -100
        else:
            payback_years = capex / net_annual_profit
            # Simple ROI over 10 years: (Total Profit 10y - CapEx) / CapEx
            total_profit_10y = (net_annual_profit * 10) - capex
            roi_10y = (total_profit_10y / capex) * 100
            
        return {
            "height": height,
            "diameter": diameter,
            "num_pipes": num_pipes,
            "velocity": velocity,
            "flow_rate_total": total_q,
            "power_gen_kw": p_gen / 1000,
            "power_saved_kw": p_saved / 1000,
            "capex": capex,
            "opex": opex_annual,
            "annual_revenue": annual_value,
            "payback_years": payback_years,
            "roi_10y": roi_10y,
            "net_profit_10y": (net_annual_profit * 10) - capex
        }

    def run_sweep(self):
        """Iterates through all parameter combinations."""
        print("Starting Parametric Sweep...")
        heights = np.arange(50, 310, 10) # 50 to 300
        diameters = np.arange(0.5, 3.5, 0.5) # 0.5 to 3.0
        pipes = np.arange(1, 21, 1) # 1 to 20
        
        results = []
        
        total_iterations = len(heights) * len(diameters) * len(pipes)
        count = 0
        
        for h in heights:
            for d in diameters:
                for p in pipes:
                    r = self.run_scenario(h, d, p)
                    if r: results.append(r)
                    count += 1
                    if count % 1000 == 0:
                        print(f"Processed {count}/{total_iterations} scenarios...")
                        
        self.df = pd.DataFrame(results)
        return self.df
    
    def analyze_and_plot(self):
        """Finds winners and generates plots."""
        if not hasattr(self, 'df'): return
        
        # 1. Identify "Winner Scenario" (Best Payback Period that is > 0)
        valid_profits = self.df[self.df['payback_years'] > 0]
        if valid_profits.empty:
            print("No profitable scenarios found!")
            return

        winner = valid_profits.loc[valid_profits['payback_years'].idxmin()]
        best_roi = valid_profits.loc[valid_profits['roi_10y'].idxmax()]
        
        print("\n" + "="*60)
        print("OPTIMIZATION RESULTS - THE SWEET SPOT")
        print("="*60)
        print(f"WINNER SCENARIO (Fastest Payback):")
        print(f"  Configuration: Height={winner['height']}m, Diameter={winner['diameter']}m, Pipes={winner['num_pipes']}")
        print(f"  Financials   : CapEx=${winner['capex']:,.2f}, Annual Profit=${winner['annual_revenue'] - winner['opex']:,.2f}")
        print(f"  Performance  : Payback={winner['payback_years']:.2f} Years, ROI (10y)={winner['roi_10y']:.1f}%")
        print(f"  Power Impact : {winner['power_gen_kw'] + winner['power_saved_kw']:.2f} kW Net Benefit")
        print("-" * 60)
        print(f"HIGHEST ROI SCENARIO (10 Years):")
        print(f"  Configuration: Height={best_roi['height']}m, Diameter={best_roi['diameter']}m, Pipes={best_roi['num_pipes']}")
        print(f"  Dimensions   : Payback={best_roi['payback_years']:.2f} Years, ROI (10y)={best_roi['roi_10y']:.1f}%")
        print("="*60)

        # 2. Visualization
        os.makedirs("assets", exist_ok=True)
        plt.style.use('dark_background')
        sns.set_theme(style="darkgrid") # Seaborn overrides, need to be careful
        # Better just use plt style
        
        fig = plt.figure(figsize=(20, 10))
        
        # Plot 1: Heatmap of Net Profit 10y (Avg across pipe counts for simplicity, or peak pipe count)
        # Let's pick the optimal Pipe count for each H/D pair to show the "Potential" of that geometry
        pivot_df = self.df.loc[self.df.groupby(['height', 'diameter'])['net_profit_10y'].idxmax()]
        pivot_table = pivot_df.pivot(index="height", columns="diameter", values="net_profit_10y")
        
        ax1 = plt.subplot(1, 2, 1)
        sns.heatmap(pivot_table, annot=False, cmap="viridis", cbar_kws={'label': 'Max Net Profit (10y) [$]'})
        ax1.set_title("Financial Heatmap: Height vs. Diameter\n(Color = Net Profit 10y for best pipe count)")
        ax1.invert_yaxis()
        
        # Plot 2: 3D Surface for Energy Generation vs Height/Diameter
        ax2 = plt.subplot(1, 2, 2, projection='3d')
        
        # Prepare 3D data (using pivot_df again for unique H, D)
        X = pivot_df['diameter']
        Y = pivot_df['height']
        Z = pivot_df['power_gen_kw'] # Just generated power
        
        # Scatter for 3D is safer than plot_surface for non-grid regular data without meshgrid prep
        scatter = ax2.scatter(X, Y, Z, c=Z, cmap='plasma', s=50)
        
        ax2.set_xlabel('Diameter (m)')
        ax2.set_ylabel('Height (m)')
        ax2.set_zlabel('Hydro Power Gen (kW)')
        ax2.set_title("3D Landscape: Power Generation Capacity")
        fig.colorbar(scatter, ax=ax2, shrink=0.5, aspect=5, label='Power (kW)')
        
        plt.tight_layout()
        out = "assets/v2_advanced_sweep.png"
        plt.savefig(out, dpi=150)
        print(f"Chart saved to {out}")

if __name__ == "__main__":
    sim = ThermoFinancialSim()
    sim.run_sweep()
    sim.analyze_and_plot()
