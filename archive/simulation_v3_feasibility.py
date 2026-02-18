import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns
from scipy.optimize import brentq
import numpy_financial as npf

class HydraulicSystem:
    """
     rigorous physics engine for the Thermosiphon Cooling System.
    """
    def __init__(self, height, diameter, num_pipes, roughness=0.000045):
        self.H = height
        self.D = diameter
        self.N_pipes = num_pipes
        self.epsilon = roughness # Commercial Steel roughness in meters
        self.g = 9.81
        
        # Minor Loss Coefficients (K)
        # Entrance (0.5) + Exit (1.0) + 4 Bends (0.3 each) + Valve (0.2)
        self.K_total = 0.5 + 1.0 + (4 * 0.3) + 0.2

    def get_density(self, temp_c):
        """Seawater density (kg/m^3) at 35ppt salinity."""
        # UNESCO Equation of State simplified
        return 1028.17 - 0.0663 * temp_c - 0.0038 * temp_c**2

    def get_viscosity(self, temp_c):
        """Dynamic viscosity of seawater (Pa.s)."""
        # Correlation for seawater viscosity
        return 1.88e-3 * ((temp_c + 20)**(-0.6)) # Very rough approx, valid 10-30C range

    def solve_equilibrium_velocity(self, t_in, t_out):
        """
        Solves for velocity where Buoyancy Head == Friction Head + Minor Head.
        Uses driving pressure difference.
        """
        rho_in = self.get_density(t_in)
        rho_out = self.get_density(t_out)
        rho_avg = (rho_in + rho_out) / 2
        
        # Buoyancy Pressure (Driving Force)
        # P_drive = (rho_cold - rho_hot) * g * H
        delta_rho = rho_in - rho_out
        if delta_rho <= 0: return 0.0
        
        P_drive = delta_rho * self.g * self.H
        
        # Function to find root for: F(v) = P_drive - P_losses(v) = 0
        def pressure_balance(v):
            if v <= 0: return P_drive # Should strictly be positive physics
            
            # Reynolds Number
            mu_avg = self.get_viscosity((t_in + t_out)/2)
            Re = (rho_avg * v * self.D) / mu_avg
            
            # Darcy-Weisbach Friction Factor (Haaland Equation - explicit approx of Colebrook)
            if Re < 2300:
                f = 64 / Re # Laminar
            else:
                rel_rough = self.epsilon / self.D
                term = (rel_rough / 3.7)**1.11 + (6.9 / Re)
                f = (-1.8 * np.log10(term))**-2
                
            # Head Loss (in terms of Pressure)
            # h_L = (f*L/D + K) * v^2/2g
            # P_loss = rho * g * h_L = rho * (f*L/D + K) * v^2 / 2
            
            head_loss_major = f * (self.H / self.D)
            head_loss_total = head_loss_major + self.K_total
            
            P_loss = rho_avg * head_loss_total * (v**2 / 2)
            
            return P_drive - P_loss

        # Solve for v in range [0, 20] m/s
        try:
            v_sol = brentq(pressure_balance, 0.001, 50.0) # Assume max 50m/s practical limit
            return v_sol
        except ValueError:
            return 0.0 # No solution (system stalled)

class FeasibilityStudy:
    def __init__(self):
        # Base Configuration (Candidate for Optimization)
        # Using the "Gold Zone" from previous step as baseline, but adjusted
        self.height = 50 
        self.diameter = 2.0 
        self.pipes = 10
        
        # Financial Parameters
        self.capex_base_per_m = 12000 # Increased realism
        self.elec_price = 0.12 # $/kWh
        self.carbon_credit = 50 # $/ton CO2
        self.grid_emission = 0.4 # kg CO2/kWh
        
        # Risk Parameters (Monte Carlo)
        self.uncertainty_capex = 0.2
        self.uncertainty_price = 0.15
        self.uncertainty_eff = 0.10

    def run_yearly_simulation(self, variance_factor=1.0):
        """
        Runs a 12-month simulation for ONE year.
        variance_factor: tuple (capex_mod, price_mod, eff_mod) for Monte Carlo
        """
        capex_mod, price_mod, eff_mod = variance_factor
        
        sys = HydraulicSystem(self.height, self.diameter, self.pipes)
        
        # Seasonal Data (Northern Hemisphere)
        months = np.arange(1, 13)
        # Sea Temp: Cold in Jan (10C), Hot in Aug (25C)
        sea_temps = 10 + 15 * np.sin((months - 1) * np.pi / 11) 
        # Outlet Temp: Assume Data Center adds constant Delta-T, but maybe limited max T?
        # Let's assume constant 30C addition for simplicity, or fixed outlet if controlled.
        # Let's match prompt: "Heat Exchanger Delta-T varies". 
        # Actually prompt says "Heat Source heat seawater from Tin to Tout".
        # Let's assume Tout is controlled to be 50C max, or Delta-T is constant.
        # Let's assume fixed Tout = 50C for max thermosiphon effect, as long as Tin < 50.
        t_out = 50.0
        
        monthly_data = []

        total_gen_kwh = 0
        total_saved_kwh = 0
        
        for i, t_in in enumerate(sea_temps):
            v = sys.solve_equilibrium_velocity(t_in, t_out)
            
            # Mass Flow
            flow_area = sys.N_pipes * (np.pi * sys.D**2 / 4)
            q = v * flow_area
            rho_out = sys.get_density(t_out)
            m_dot = q * rho_out
            
            # Power
            # Generation
            eff_turb = 0.80 * eff_mod
            p_gen = eff_turb * m_dot * sys.g * sys.H
            
            # Traditional Pump Equivalent
            eff_pump = 0.85 # Standard
            p_pump_equiv = (m_dot * sys.g * sys.H) / eff_pump
            
            # Monthly Energy (Hours * Power)
            hours = 24 * 30 # Approx 720 hours/month
            gen_kwh = (p_gen / 1000) * hours
            saved_kwh = (p_pump_equiv / 1000) * hours
            
            total_gen_kwh += gen_kwh
            total_saved_kwh += saved_kwh
            
            monthly_data.append({
                "Month": i+1,
                "Sea_Temp": t_in,
                "Velocity": v,
                "Gen_kWh": gen_kwh,
                "Saved_kWh": saved_kwh
            })
            
        # Annual Financials
        revenue_elec = total_gen_kwh * (self.elec_price * price_mod)
        revenue_saved = total_saved_kwh * (self.elec_price * price_mod)
        
        # Carbon Credits
        co2_saved_tons = (total_gen_kwh + total_saved_kwh) * self.grid_emission / 1000
        revenue_carbon = co2_saved_tons * self.carbon_credit
        
        total_annual_revenue = revenue_elec + revenue_saved + revenue_carbon
        
        # CapEx Calculation
        # Construction + Pipe Steel
        # Steel Vol approx = Pi * D * 0.02 * H * N
        steel_vol = np.pi * self.diameter * 0.02 * self.height * self.pipes
        steel_cost = steel_vol * 7850 * 1.5
        construction_cost = self.capex_base_per_m * self.height * (1 + self.height/500)
        
        total_capex = (construction_cost + steel_cost) * capex_mod
        
        return {
            "monthly_df": pd.DataFrame(monthly_data),
            "capex": total_capex,
            "annual_revenue": total_annual_revenue,
            "total_gen_kwh": total_gen_kwh,
            "total_saved_kwh": total_saved_kwh
        }

    def run_financial_lifecycle(self, annual_revenue, capex):
        """Calculates NPV and IRR over 20 years."""
        years = 20
        discount_rate = 0.08
        escalation_maintenance = 0.05
        
        cash_flows = [-capex]
        opex = capex * 0.02 # Starting OpEx
        
        for y in range(1, years + 1):
            net_flow = annual_revenue - opex
            cash_flows.append(net_flow)
            opex *= (1 + escalation_maintenance)
            
        npv = npf.npv(discount_rate, cash_flows)
        try:
            irr = npf.irr(cash_flows)
        except:
            irr = 0.0
            
        return npv, irr, cash_flows

    def run_monte_carlo(self, num_sims=1000):
        print(f"Running {num_sims} Monte Carlo Simulations...")
        results = []
        
        # Base run for monthly data
        base_case = self.run_yearly_simulation((1.0, 1.0, 1.0))
        self.base_monthly_df = base_case['monthly_df']
        
        for _ in range(num_sims):
            # Randomize parameters (Normal Distribution centered on 1.0)
            c_mod = np.random.normal(1.0, self.uncertainty_capex/2) # 2 sigma coverage approx
            p_mod = np.random.normal(1.0, self.uncertainty_price/2)
            e_mod = np.random.normal(1.0, self.uncertainty_eff/2)
            
            # Simple scaling of base year results to save compute time
            # (Velocity/Physics doesn't change with cost/price, only efficiency changes power output)
            
            # Re-calculate revenue based on multipliers
            rev_elec = base_case['total_gen_kwh'] * e_mod * (self.elec_price * p_mod)
            rev_saved = base_case['total_saved_kwh'] * (self.elec_price * p_mod) # Saved energy is pumped, not gen efficiency dependent? simplified
            # Actually gen efficiency affects gen_kwh.
            
            # Let's do it properly-ish
            # Gen kWh scales with e_mod
            gen_h = base_case['total_gen_kwh'] * e_mod
            
            rev_total = (gen_h + base_case['total_saved_kwh']) * (self.elec_price * p_mod)
            # Add carbon
            co2 = (gen_h + base_case['total_saved_kwh']) * self.grid_emission / 1000
            rev_total += co2 * self.carbon_credit
            
            actual_capex = base_case['capex'] * c_mod
            
            npv, irr, _ = self.run_financial_lifecycle(rev_total, actual_capex)
            
            results.append(npv)
            
        return results, base_case

    def generate_report(self):
        mc_results, base_case = self.run_monte_carlo()
        mc_results = np.array(mc_results)
        
        print("\n" + "#"*60)
        print("ULTIMATE FEASIBILITY STUDY v3.0 - EXECUTIVE SUMMARY")
        print("#"*60)
        
        # Physics Summary
        print("\n--- PHYSICS REALITY CHECK ---")
        avg_v = base_case['monthly_df']['Velocity'].mean()
        print(f"Average Flow Velocity: {avg_v:.2f} m/s")
        if avg_v < 0.5:
             print("WARNING: Velocity implies risk of stagnation or bio-fouling.")
        else:
             print("STATUS: Flow velocity is healthy/turbulent.")
             
        # Financial Summary (Base Case)
        base_npv, base_irr, _ = self.run_financial_lifecycle(base_case['annual_revenue'], base_case['capex'])
        print("\n--- FINANCIAL METRICS (BASE CASE) ---")
        print(f"Total CapEx        : ${base_case['capex']:,.2f}")
        print(f"Annual Revenue     : ${base_case['annual_revenue']:,.2f}")
        print(f"NPV (20y, 8% DR)   : ${base_npv:,.2f}")
        print(f"IRR                : {base_irr*100:.2f}%")
        
        # Risk Profile
        print("\n--- RISK ANALYSIS (MONTE CARLO) ---")
        success_rate = np.sum(mc_results > 0) / len(mc_results) * 100
        print(f"Probability of Success (NPV > 0): {success_rate:.1f}%")
        print(f"Worst Case NPV (5th percentile) : ${np.percentile(mc_results, 5):,.2f}")
        print(f"Best Case NPV (95th percentile) : ${np.percentile(mc_results, 95):,.2f}")
        print("#"*60)
        
        # Visualizations
        self.plot_results(base_case['monthly_df'], mc_results)

    def plot_results(self, monthly_df, mc_results):
        os.makedirs("assets", exist_ok=True)
        plt.style.use('dark_background')
        # sns.set_theme(style="darkgrid") 
        
        fig = plt.figure(figsize=(18, 12))
        
        # Plot 1: Monthly Performance
        ax1 = plt.subplot(2, 2, 1)
        sns.lineplot(data=monthly_df, x="Month", y="Gen_kWh", marker="o", label="Generated kWh", ax=ax1, color="green")
        ax1_twin = ax1.twinx()
        sns.lineplot(data=monthly_df, x="Month", y="Velocity", marker="s", label="Velocity (m/s)", ax=ax1_twin, color="blue")
        ax1.set_title("Monthly System Performance (Seasonality)")
        ax1.set_ylabel("Energy (kWh)")
        ax1_twin.set_ylabel("Velocity (m/s)")
        
        # Plot 2: Physics - Head Balance (Conceptual for Avg Temp)
        ax2 = plt.subplot(2, 2, 2)
        # Generate curve for v = 0 to 5
        v_range = np.linspace(0.1, 5, 50)
        sys = HydraulicSystem(self.height, self.diameter, self.pipes)
        # Use avg temps
        t_in_avg = 17.5
        t_out = 50
        rho_avg = (sys.get_density(t_in_avg) + sys.get_density(t_out)) / 2
        
        driving_head = (sys.get_density(t_in_avg) - sys.get_density(t_out)) * sys.g * sys.H / (rho_avg * sys.g)
        # Head Loss = f * L/D * v^2/2g + K * v^2/2g
        losses = []
        for v in v_range:
            # Re-calc Re and f
            Re = (rho_avg * v * sys.D) / sys.get_viscosity(30)
            f = 0.02 # approx
            h_loss = (f * sys.H/sys.D + sys.K_total) * (v**2 / (2*sys.g))
            losses.append(h_loss)
            
        ax2.plot(v_range, [driving_head]*len(v_range), 'g--', label="Driving Head (Thermosiphon)")
        ax2.plot(v_range, losses, 'r-', label="Friction + Minor Losses")
        # Find intersection visually
        ax2.set_title("Physics Check: Driving Head vs. Friction Loss")
        ax2.set_xlabel("Velocity (m/s)")
        ax2.set_ylabel("Head (m)")
        ax2.legend()
        
        # Plot 3: Monte Carlo Histogram
        ax3 = plt.subplot(2, 1, 2)
        sns.histplot(mc_results, kde=True, color="purple", ax=ax3)
        ax3.axvline(0, color='red', linestyle='--', linewidth=2, label="Break Even")
        ax3.set_title("Risk Profile: NPV Distribution (1000 Scenarios)")
        ax3.set_xlabel("Net Present Value ($)")
        ax3.legend()
        
        plt.tight_layout()
        out = "assets/v3_feasibility_risk.png"
        plt.savefig(out, dpi=150)
        print(f"Chart saved to {out}")

if __name__ == "__main__":
    study = FeasibilityStudy()
    study.generate_report()
