"""
Hydra-Cool Simulation [CODE] — E03: Permitting & Legal Risk
===========================================================
"The lawyer is more expensive than the engineer."

Timeline risk analysis for Marine Permitting (US vs EU vs Gulf).
- Fast Track (Dubai/Saudi): 1 Year.
- Standard (EU): 3 Years.
- Nightmare (California/Coastal Commission): 7+ Years.

Output:
- Gantt Chart comparing Project Timelines.

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import numpy as np
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool E03: Running Permitting Risk Analysis...")
    
    scenarios = ['Fast Track (Middle East)', 'Standard (Northern Europe)', 'Litigious (California)']
    
    # Durations in Years
    permit_time = [1.0, 3.0, 7.0]
    const_time = [1.5, 2.0, 2.5] # Construction
    
    y_pos = np.arange(len(scenarios))
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Permit Bar
    ax.barh(y_pos, permit_time, color='#FF5252', label='Permitting & Legal', height=0.4)
    
    # Construction Bar (starts after permit)
    ax.barh(y_pos, const_time, left=permit_time, color='#29B6F6', label='Construction', height=0.4)
    
    ax.set_xlabel("Time to Operational [Years]")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(scenarios)
    ax.set_title("E03: Regulatory Risk Timeline", fontsize=14)
    ax.legend()
    
    # Annotate totals
    for i, (p, c) in enumerate(zip(permit_time, const_time)):
        total = p + c
        ax.text(total + 0.2, i, f"{total:.1f} Years", va='center', fontweight='bold', color='white')
        
        # Cost of Delay annotation
        if i == 2:
            ax.text(p/2, i-0.3, "Legal Hell", ha='center', color='#FFC107', fontsize=9)

    output_path = os.path.join(ASSET_DIR, "E03_permitting_risk.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
