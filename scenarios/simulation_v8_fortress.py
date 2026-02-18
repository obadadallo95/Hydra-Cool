import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns
from scipy.integrate import odeint

class FortressSimulation:
    """
    Simulation v8.0: The Fortress & The Ecosystem
    Includes Biological Control, Seismic Stress, War/Sabotage, and Human OpEx.
    """
    def __init__(self):
        # Configuration (Golden Scenario)
        self.H = 200.0
        self.D = 3.5
        self.pump_power_kw = 2000.0
        self.num_pipes = 10
        
        # Seismic
        self.mass_water_kg = (np.pi * (self.D/2)**2 * self.H * self.num_pipes) * 1025
        self.mass_steel_kg = (np.pi * self.D * 0.02 * self.H * self.num_pipes) * 7850
        self.total_mass_kg = self.mass_water_kg + self.mass_steel_kg
        
    def run_biology_simulation(self):
        """
        Lotka-Volterra Model for Biological Control.
        x: Algae Biomass (Biofouling)
        y: Filter Feeder Population (The Solution)
        """
        def dP_dt(P, t):
            x, y = P
            # Algae Growth parameters
            alpha = 0.5  # Algae growth rate
            beta = 0.02  # Predation rate
            # Feeder Growth parameters
            delta = 0.001 # Feeder reproduction per algae eaten
            gamma = 0.1  # Feeder death rate
            
            dxdt = alpha*x - beta*x*y
            dydt = delta*x*y - gamma*y
            return [dxdt, dydt]

        t = np.linspace(0, 365, 365) # 1 Year
        P0 = [10, 5] # Initial population: 10 Algae units, 5 Feeders
        
        sol = odeint(dP_dt, P0, t)
        
        # Roughness impacts
        # Assume Roughness scales with Algae population x
        # Max acceptable algae = 50 units (corresponding to +20% roughness)
        algae_pop = sol[:, 0]
        feeder_pop = sol[:, 1]
        
        max_algae = np.max(algae_pop)
        stable = max_algae < 100 # Threshold for "Out of Control"
        
        return t, algae_pop, feeder_pop, stable

    def run_seismic_test(self, magnitude):
        """
        Calculates Base Shear and Overturning Moment for a given Magnitude.
        Simple PGA (Peak Ground Acceleration) correlation.
        """
        # Gutenberg-Richter / Empirical PGA relation (Very simplified)
        # PGA (g) approx = 10^(0.5M - 1.8) for close range?
        # Let's use a standard lookup for engineering
        if magnitude < 5.0: pga = 0.05
        elif magnitude < 6.0: pga = 0.2
        elif magnitude < 7.0: pga = 0.4
        elif magnitude < 8.0: pga = 0.7
        else: pga = 1.2 # > G !
        
        # Base Shear V = Mass * PGA
        base_shear_n = self.total_mass_kg * (pga * 9.81)
        
        # Overturning Moment M = V * (2/3 H) (Simplified cantilever)
        moment_nm = base_shear_n * (0.66 * self.H)
        
        # Structural Limit (Hypothetical for a 200m steel tower)
        # Resistive Moment from massive 50m wide foundation?
        # Limit = 5 Billion Nm
        limit_moment = 5e9 
        
        survived = moment_nm < limit_moment
        
        cost_dampers = 0
        if magnitude >= 8.0:
            if not survived:
                # Need Dampers to survive
                cost_dampers = 10_000_000 # $10M
                survived = True # Assumed fix
        
        return {
            "Magnitude": magnitude,
            "PGA_g": pga,
            "Base_Shear_MN": base_shear_n / 1e6,
            "Moment_GNm": moment_nm / 1e9,
            "Survived": survived,
            "Retrofit_Cost": cost_dampers
        }

    def run_war_simulation(self):
        """
        Missile Strike Analysis.
        50% Pipes destroyed. 
        Can remaining system cool 50MW?
        """
        # Reduced Capacity
        pipes_active = self.num_pipes / 2
        
        # Booster run at 110%
        pump_power = self.pump_power_kw * 1.10 * 1000
        
        # Solve Hydraulics for 5 pipes
        # Recalculate flow for 5 pipes with 2.2MW pump
        # H=200, D=3.5
        
        # Simplified Hydraulic Solve (copied logic from v7 roughly)
        # Not importing v7 class to keep self-contained, using heuristic
        # If 10 pipes/2MW gave ~50MW cooling (high flow),
        # 5 pipes/2.2MW should give > 50% flow because pump/pipe ratio higher.
        
        # Let's estimate Flow:
        # P_pump ~ Q * dP. dP ~ Q^2. -> Q^3 ~ Power.
        # With 5 pipes, resistance increases?
        # Actually, 5 pipes means Area is half.
        # For same velocity, Friction is same, but Mass Flow is half.
        # Cooling Q = m * Cp * dT.
        # If m drops by 50%, dT must double.
        # Normal dT = 47 - 17.5 = 29.5 C.
        # War dT = 29.5 * 2 = 59 C.
        # T_out = 17.5 + 59 = 76.5 C.
        
        t_out = 17.5 + 59.0
        
        # Meltdown Limit
        meltdown_limit = 80.0
        survived = t_out < meltdown_limit
        
        return {
            "Pipes_Lost": "50%",
            "Pump_Overdrive": "110%",
            "Est_T_Out": t_out,
            "Meltdown_Risk": not survived
        }

    def calculate_human_opex(self):
        # Staffing
        shifts = 3 # +1 relief? Let's say 4 teams for 24/7 coverage.
        teams = 4 
        
        # Team Composition
        # 2 Mech ($120k), 1 Elec ($130k), 3 Security ($80k), 2 Divers ($100k)
        team_cost = (2*120000) + (1*130000) + (3*80000) + (2*100000)
        total_hr_annual = team_cost * teams
        
        return total_hr_annual

    def generate_report(self):
        print("\n" + "#"*60)
        print("SIMULATION v8.0: THE FORTRESS & THE ECOSYSTEM")
        print("#"*60)
        
        # 1. Biology
        t, algae, feeders, bio_stable = self.run_biology_simulation()
        print(f"BIOLOGICAL CONTROL:")
        print(f"  System Stability : {'STABLE' if bio_stable else 'UNSTABLE (Algae Bloom Risk)'}")
        print(f"  Peak Algae Load  : {np.max(algae):.1f} Units")
        
        # 2. Seismic
        print("-" * 60)
        print("SEISMIC STRESS TEST (Magnitude 9.0):")
        quake = self.run_seismic_test(9.0)
        print(f"  Base Shear       : {quake['Base_Shear_MN']:.1f} MN")
        print(f"  Overturning Mom. : {quake['Moment_GNm']:.2f} GNm")
        print(f"  Status           : {'SURVIVED' if quake['Survived'] else 'COLLAPSED'}")
        print(f"  Required Retrofit: ${quake['Retrofit_Cost']:,.0f}")
        
        # 3. War
        print("-" * 60)
        print("WAR GAME (50% Destruction):")
        war = self.run_war_simulation()
        print(f"  Remaining Pipes  : 5")
        print(f"  Cooling Temp     : {war['Est_T_Out']:.1f}°C")
        print(f"  Status           : {'OPERATIONAL' if not war['Meltdown_Risk'] else 'MELTDOWN'}")
        
        # 4. Human OpEx
        hr_cost = self.calculate_human_opex()
        print("-" * 60)
        print(f"HUMAN OPS COST (Annual):")
        print(f"  Staffing Bill    : ${hr_cost:,.2f} / year")
        print("#"*60)
        
        # Plots
        self.plot_results(t, algae, feeders)

    def plot_results(self, t, algae, feeders):
        os.makedirs("assets", exist_ok=True)
        plt.style.use('dark_background')
        # sns.set_theme(style="whitegrid")
        fig = plt.figure(figsize=(14, 6))
        
        # Plot 1: Ecology
        ax1 = plt.subplot(1, 2, 1)
        ax1.plot(t, algae, 'g-', label='Algae (Biofouling)')
        ax1.plot(t, feeders, 'b--', label='Filter Feeders (Solution)')
        ax1.set_title("Ecosystem Stability: Lotka-Volterra Model")
        ax1.set_xlabel("Days")
        ax1.set_ylabel("Population Density")
        ax1.legend()
        
        # Plot 2: Survival Curve (Temp vs Pipe Loss)
        ax2 = plt.subplot(1, 2, 2)
        pipe_loss = np.linspace(0, 90, 50) # 0 to 90% loss
        # T_out approx = 17.5 + 29.5 * (100 / (100-Loss))
        # Simplified mass flow reduction proportional to pipe count
        temps = 17.5 + 29.5 * (100 / (100 - pipe_loss))
        
        ax2.plot(pipe_loss, temps, 'r-', linewidth=2)
        ax2.axhline(80, color='black', linestyle='--', label='Meltdown Limit (80°C)')
        
        # Find intersection
        limit_idx = np.where(temps > 80)[0]
        if len(limit_idx) > 0:
            crit_loss = pipe_loss[limit_idx[0]]
            ax2.axvline(crit_loss, color='orange', linestyle='--', label=f'Critical Damage: {crit_loss:.0f}%')
            
        ax2.set_title("War Game: Thermal Resilience")
        ax2.set_xlabel("Pipe System Damage (%)")
        ax2.set_ylabel("Server Outlet Temp (°C)")
        ax2.legend()
        
        plt.tight_layout()
        out = "assets/v8_fortress_ecology.png"
        plt.savefig(out, dpi=150)
        print(f"Chart saved to {out}")

if __name__ == "__main__":
    sim = FortressSimulation()
    sim.generate_report()
