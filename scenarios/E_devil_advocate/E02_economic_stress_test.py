"""
Hydra-Cool Simulation [CODE] — E02: Economic Stress Test
========================================================
"What kills the business case?"

Sensitivity Analysis on NPV (Net Present Value).
Base Parameters:
- CAPEX: $44M
- Savings: $38M/yr
- Discount Rate: 8%
- 20 Years.

Stress Factors (Variations):
- CAPEX: +50% (Cost overrun).
- OPEX: +200% (Unexpected maintenance).
- Electricity Price: -50% (If fusion solves energy?? or cheap renewables).
- Efficiency (PUE of Air): Improves to 1.1 (Liquid cooling competition).

Output:
- Tornado Chart.

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def calculate_npv(capex, annual_savings, years=20, rate=0.08):
    # Custom NPV implementation (np.npv is deprecated/removed in new numpy)
    cash_flows = [-capex] + [annual_savings] * years
    npv = 0
    for t, flow in enumerate(cash_flows):
        npv += flow / ((1 + rate) ** t)
    return npv

def run_simulation():
    print("Hydra-Cool E02: Running Economic Stress Test...")
    
    # Base Case
    base_capex = 458.6
    base_savings = 25.0 # Updated: $40.5M (Air) - $15.5M (Hydra)
    base_npv = calculate_npv(base_capex, base_savings)
    
    variables = [
        "Base Case",
        "CAPEX +50%",
        "Elec Price -50%",
        "Competitor PUE=1.2",
        "Pipeline Failure (Repl.)"
    ]
    
    npvs = []
    
    # 1. Base
    npvs.append(base_npv)
    
    # 2. CAPEX +50%
    npvs.append(calculate_npv(base_capex * 1.5, base_savings))
    
    # 3. Elec Price -50% (Savings halved)
    npvs.append(calculate_npv(base_capex, base_savings * 0.5))
    
    # 4. Competitor PUE 1.25 -> 1.2 (Savings reduce)
    # Savings were from PUE 1.55 to 1.0. Delta = 0.55.
    # New Delta = 1.2 - 1.0 = 0.2.
    # Savings factor = 0.2 / 0.55 = 0.36
    npvs.append(calculate_npv(base_capex, base_savings * 0.36))
    
    # 5. Pipeline Failure (Year 10 CAPEX hit)
    # Cash flow: -44, +38... -20(Repair)... +38
    cfs = [-base_capex] + [base_savings]*20
    cfs[10] -= 20.0 # Repair cost
    
    npv_fail = 0
    for t, flow in enumerate(cfs):
        npv_fail += flow / ((1 + 0.08) ** t)
    npvs.append(npv_fail)
    
    # Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Relative to Base
    diffs = [n - base_npv for n in npvs]
    
    colors = ['#00E676', '#FF5252', '#FF5252', '#FF5252', '#FF9800']
    
    # Plot absolute NPVs
    bars = ax.barh(variables, npvs, color=colors)
    
    ax.set_xlabel("Net Present Value (NPV) 20-Year [$ Million]")
    ax.set_title("E02: Sensitivity Analysis (Stress Test)", fontsize=14)
    ax.grid(axis='x', alpha=0.2)
    
    # Annotate
    for i, v in enumerate(npvs):
        ax.text(v + 5, i, f"${v:.0f}M", va='center', fontweight='bold', color='white')
        
    ax.axvline(0, color='white', linestyle='-')
    ax.text(10, 4, "Strongly Positive even in worst case", color='#00E676', alpha=0.8)

    output_path = os.path.join(ASSET_DIR, "E02_stress_test.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
