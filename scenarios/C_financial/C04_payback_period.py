"""
Hydra-Cool Simulation [CODE] — C04: Payback Period
==================================================
Focuses on the "ROI" metric for investors.

Plots Cumulative Cash Flow (Profit view).
- Initial: -CAPEX.
- Slope: +Annual Savings.
- Crossing Zero: Payback.

Sensitivity:
- Sensitivity to Electricity Price ($0.05, $0.08, $0.12 / kWh).
- Higher elec price = Faster payback.

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool C04: Running Payback Period Analysis...")
    
    years = np.linspace(0, 15, 180) # Monthly res for 15 years
    
    capex = 458.6
    opex_hydra = 15.5
    
    # Electricity Prices to sweep ($/kWh)
    prices = [0.05, 0.08, 0.12]
    colors = ['#FFC107', '#00E676', '#29B6F6']
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for p, color in zip(prices, colors):
        # Baseline Cost at this price
        pue_air = 1.55
        cost_air = (pue_air - 1.0) * 100 * 8760 * (p*1000) / 1e6 # MW * h * $/MWh
        opex_air = cost_air + 2.0 # + Maint
        
        annual_saving = opex_air - opex_hydra
        
        cash_flow = -capex + (annual_saving * years)
        
        ax.plot(years, cash_flow, label=f'Elec Price: ${p:.2f}/kWh', color=color, linewidth=2)
        
        # Find crossing
        payback = capex / annual_saving
        ax.plot(payback, 0, 'o', color=color)
        ax.annotate(f"{payback*12:.0f} Mo", (payback, 0), xytext=(0, 10), textcoords='offset points', color=color)

    ax.axhline(0, color='white', linewidth=1)
    ax.set_xlabel("Years")
    ax.set_ylabel("Cumulative Cash Flow [$ Million]")
    ax.set_title("Payback Period Sensitivity (vs Electricity Price)", fontsize=14)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.2)
    
    output_path = os.path.join(ASSET_DIR, "C04_payback_period.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
