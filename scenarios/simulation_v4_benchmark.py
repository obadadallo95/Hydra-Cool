import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns

class DataCenterCooling:
    """Base Class for Data Center Cooling Comparison."""
    def __init__(self, name, pue, cap_ex_mw, opex_pct, water_usage_l_kwh):
        self.name = name
        self.pue = pue
        self.cap_ex_per_mw = cap_ex_mw # Cost per MW of IT Load
        self.opex_pct = opex_pct # % of CapEx per year
        self.water_usage = water_usage_l_kwh # Liters per kWh of IT load
        self.it_load_mw = 100.0 # 100 MW Data Center
        
        # Financial Constants
        self.elec_price = 0.12 # $/kWh
        self.water_price = 0.002 # $/Liter (Industrial rate approx)

    def calculate_10y_tco(self):
        # 1. CapEx
        capex = self.cap_ex_per_mw * self.it_load_mw
        
        # 2. Annual OpEx (Maintenance)
        opex_maint = capex * self.opex_pct
        
        # 3. Annual Energy Cost
        # Total Power = IT Load * PUE
        total_power_mw = self.it_load_mw * self.pue
        annual_energy_kwh = total_power_mw * 1000 * 24 * 365
        annual_energy_cost = annual_energy_kwh * self.elec_price
        
        # 4. Annual Water Cost
        annual_it_kwh = self.it_load_mw * 1000 * 24 * 365
        annual_water_liters = annual_it_kwh * self.water_usage
        annual_water_cost = annual_water_liters * self.water_price
        
        # Total Annual OpEx
        total_annual_opex = opex_maint + annual_energy_cost + annual_water_cost
        
        # 10-Year Projection
        years = np.arange(0, 11)
        cumulative_cost = [capex + (total_annual_opex * y) for y in years]
        
        return {
            "name": self.name,
            "capex": capex,
            "annual_energy_cost": annual_energy_cost,
            "annual_water_cost": annual_water_cost,
            "annual_maint": opex_maint,
            "cumulative_10y": cumulative_cost
        }

class UserHydroThermosiphon:
    """Class D: The Challenger (User System)."""
    def __init__(self):
        self.name = "Hydro-Thermosiphon (Ours)"
        self.it_load_mw = 100.0
        
        # Physics / System Stats from Feasibility v3.0 (approx optimized)
        self.height = 50 
        self.gen_capacity_mw = 20.0 # Approx from v3 results
        self.pump_avoided_mw = 15.0 # Approx
        
        # Financials
        self.capex_base = 150_000_000 # $150M Base CapEx
        self.land_premium = 5_000_000 # "Coastal Cliff" Premium
        self.capex_total = self.capex_base + self.land_premium
        
        self.elec_price = 0.12
        
        # Penalties
        self.biofouling_factor = 0.20 # +20% OpEx
        self.base_opex_pct = 0.02
        
    def calculate_thermal_pollution_cost(self):
        # Physics: Q = m * Cp * dT
        # IT Load 100MW = 100MJ/s heat rejection
        # If dT = 30C (20->50), m_hot = Q / (Cp * dT)
        cp_water = 4186
        dt_system = 30
        m_hot = (self.it_load_mw * 1e6) / (cp_water * dt_system) # kg/s (~796 kg/s)
        
        # Dilution: Target Mix Temp = 35C
        # (m_hot * 50) + (m_cold * 20) = (m_hot + m_cold) * 35
        # 50mh - 35mh = 35mc - 20mc
        # 15mh = 15mc -> m_cold = m_hot !
        # So we need to pump equal amount of cold water to dilute.
        m_cold = m_hot 
        
        # Dilution Pumping Power
        # Assume low head (just mixing) e.g., 5m head, 85% eff
        head_mix = 5
        pump_power_w = (m_cold * 9.81 * head_mix) / 0.85
        
        return pump_power_w / 1e6 # MW

    def calculate_10y_tco(self):
        # 1. CapEx
        capex = self.capex_total
        
        # 2. Annual OpEx
        # Biofouling penalty included in higher maintenance base
        opex_maint = capex * (self.base_opex_pct * (1 + self.biofouling_factor))
        
        # 3. Energy Balance
        # IT Load Energy Cost (Standard 100MW consumption)
        # Note: Previous comparison assumed "Cooling System Cost" only.
        # But standard PUE includes IT Load. Let's separate Cooling vs IT.
        # Total Power = IT Load + Cooling Power.
        # COMPETITORS: Total = 100 + (PUE-1)*100.
        # OURS: Total = 100 - NetGeneration.
        
        annual_hours = 24 * 365
        
        # Power Generation
        gen_mw = self.gen_capacity_mw
        
        # Penalty: Dilution Pumping
        dilution_mw = self.calculate_thermal_pollution_cost()
        
        net_cooling_power_mw = dilution_mw - gen_mw # Negative means Generation!
        
        # Total Facility Power = IT Load + Net Cooling Power
        facility_power_mw = self.it_load_mw + net_cooling_power_mw 
        # (If net cooling is -20MW, facility uses 80MW total from grid)
        
        annual_energy_cost = (facility_power_mw * 1000 * annual_hours) * self.elec_price
        
        # 4. Water Cost (Zero - Seawater only, no consumption charge usually, just pumping)
        annual_water_cost = 0 
        
        total_annual_opex = opex_maint + annual_energy_cost + annual_water_cost
        
        # 10-Year Projection
        years = np.arange(0, 11)
        cumulative_cost = [capex + (total_annual_opex * y) for y in years]
        
        return {
            "name": self.name,
            "capex": capex,
            "annual_energy_cost": annual_energy_cost, # Can be lower than IT cost if generating
            "annual_water_cost": 0,
            "annual_maint": opex_maint,
            "cumulative_10y": cumulative_cost
        }


def run_benchmark():
    # 1. Define Competitors
    # Class A: Google Hamina (Seawater Pumps)
    # CapEx: $8M/MW (High end DC). PUE 1.10.
    google = DataCenterCooling("Google Hamina (Class A)", 1.10, 8_000_000, 0.03, 0.0) 
    
    # Class B: Microsoft Azure (2-Phase Immersion)
    # CapEx: $12M/MW (Very expensive fluids). PUE 1.07.
    microsoft = DataCenterCooling("Microsoft Azure (Class B)", 1.07, 12_000_000, 0.02, 0.0)
    
    # Class C: Standard Air (Chillers)
    # CapEx: $7M/MW. PUE 1.58. Water: Evaporative cooling uses ~2 L/kWh.
    standard = DataCenterCooling("Standard Air (Class C)", 1.58, 7_000_000, 0.04, 2.0)
    
    # Class D: User
    user = UserHydroThermosiphon()
    
    systems = [google, microsoft, standard, user]
    results = [s.calculate_10y_tco() for s in systems]
    
    # 2. Print Executive Summary
    print("\n" + "="*80)
    print("SIMULATION v4.0: THE GLOBAL BENCHMARK BATTLE")
    print("="*80)
    print(f"{'System':<30} | {'CapEx ($M)':<12} | {'Annual Energy ($M)':<18} | {'10y TCO ($M)':<15}")
    print("-" * 80)
    
    for r in results:
        print(f"{r['name']:<30} | ${r['capex']/1e6:<11.1f} | ${r['annual_energy_cost']/1e6:<17.1f} | ${r['cumulative_10y'][-1]/1e6:<14.1f}")
        
    print("-" * 80)
    
    # 3. Visualization
    os.makedirs("assets", exist_ok=True)
    plt.style.use('dark_background')
    # sns.set_theme(style="whitegrid") # removed
    fig = plt.figure(figsize=(16, 8))
    
    # Plot 1: 10-Year TCO Race
    ax1 = plt.subplot(1, 2, 1)
    years = np.arange(0, 11)
    
    colors = ['#EA4335', '#0078D4', '#7f8c8d', '#2ecc71'] # Google Red, MS Blue, Grey, Green
    markers = ['o', 's', '^', '*']
    
    for i, r in enumerate(results):
        ax1.plot(years, np.array(r['cumulative_10y'])/1e6, label=r['name'], color=colors[i], marker=markers[i], linewidth=2)
        
    ax1.set_title("10-Year Total Cost of Ownership (TCO) Race")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Cumulative Cost ($ Millions)")
    ax1.legend()
    ax1.grid(True)
    
    # Plot 2: Annual Operating Cost Breakdown
    ax2 = plt.subplot(1, 2, 2)
    names = [r['name'].split("(")[0].strip() for r in results]
    energy = [r['annual_energy_cost']/1e6 for r in results]
    maint = [r['annual_maint']/1e6 for r in results]
    water = [r['annual_water_cost']/1e6 for r in results]
    
    x = np.arange(len(names))
    width = 0.6
    
    p1 = ax2.bar(x, energy, width, label='Energy Bill', color='#f1c40f')
    p2 = ax2.bar(x, maint, width, bottom=energy, label='Maintenance (OpEx)', color='#e67e22')
    p3 = ax2.bar(x, water, width, bottom=np.array(energy)+np.array(maint), label='Water Cost', color='#3498db')
    
    ax2.set_title("Annual Operating Cost Structure")
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, rotation=30, ha='right')
    ax2.set_ylabel("Annual Cost ($ Millions)")
    ax2.legend()
    
    # Add labels to User's Energy bar to show it's mostly IT load
    # (Since distinct IT vs Cooling isn't separated in bar, just total bill)
    
    plt.tight_layout()
    out = "assets/v4_benchmark_battle.png"
    plt.savefig(out, dpi=150)
    print(f"Chart saved to {out}")

if __name__ == "__main__":
    run_benchmark()
