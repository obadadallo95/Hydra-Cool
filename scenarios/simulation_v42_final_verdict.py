"""
Hydra-Cool Simulation v42.0 — THE FINAL VERDICT (Investment Grade)
==================================================================
Project Status: PRE-SEED / CONCEPT VALIDATION.

OBJECTIVE:
  Determine if "Hydra-Cool" is a viable business for Big Tech (Google/Microsoft)
  or just a "Dream".

METHODOLOGY:
  Weighted Scoring Model (0-100) across 5 Dimensions:
  1. FINANCIALS (30%): ROI, NPV, Payback Period.
  2. PHYSICS (20%): Thermodynamics, Hydraulics, Feasibility.
  3. RELIABILITY (20%): Resilience to failure (Bio/Seismic/Cyber).
  4. ENVIRONMENT (15%): Sustainability, Water usage.
  5. STRATEGY (15%): Competitive Advantage vs Status Quo.

INPUTS (From v1-v41):
  - CAPEX: $169M (Optimistic) - $450M (Retrofit Reality).
  - OPEX Savings: $25M/yr (Dublin) - $5M/yr (Lulea).
  - Physics: Works (74% Efficiency).
  - Risks: High (Liquefaction, Hammer, Biofouling).
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def run_final_verdict():
    print("="*60)
    print("  HYDRA-COOL v42: THE INVESTOR VERDICT")
    print("="*60)
    
    # 1. Financial Score (0-100)
    # Best Case: $25M save on $169M -> 6.7 yr payback. (Good for Infra). Score: 80.
    # Worst Case: $5M save on $450M -> 90 yr payback. (Trash). Score: 0.
    # Weighted Avg based on v31 (Dublin/Virginia are targets):
    # Payback ~7-8 years. ROI ~12%.
    score_finance = 65.0 
    
    # 2. Physics Score
    # Smart Cycle v41 proved 74% eff gain.
    # Thermo-siphon works. Turbine works.
    # But 1GW requires TBM tunnels (v40).
    score_physics = 90.0 # The physics is solid.
    
    # 3. Reliability Score
    # Failed v33 (Jellyfish). Failed v38 (Liquefaction). Failed v39 (Stuxnet).
    # Needs massive mitigation ($$$).
    score_reliability = 40.0 # High Risk.
    
    # 4. Environmental Score
    # Zero Water Consumption (v31).
    # Net Zero Energy potential.
    # Discharge handled (v41).
    score_env = 95.0 # Best in class.
    
    # 5. Strategic Score
    # Does Google NEED this?
    # In water-stressed areas (Phoenix, Dublin): YES.
    # In Arctic (Lulea): NO.
    score_strat = 75.0
    
    # Calculation
    final_score = (
        score_finance * 0.30 +
        score_physics * 0.20 +
        score_reliability * 0.20 +
        score_env * 0.15 +
        score_strat * 0.15
    )
    
    print(f"\n  [SCORING BREAKDOWN]")
    print(f"  💰 Financials:    {score_finance}/100  (Payback is barely acceptable for Retrofit)")
    print(f"  ⚛️  Physics:       {score_physics}/100  (Solid. Gravity Engine works)")
    print(f"  🛡️  Reliability:   {score_reliability}/100  (DANGEROUS. Needs heavy engineering)")
    print(f"  🌱 Environment:   {score_env}/100  (Perfect. Zero Water is the killer app)")
    print(f"  ♟️  Strategy:      {score_strat}/100  (Strong market fit in specific regions)")
    
    print("-" * 60)
    print(f"  TOTAL SCORE:      {final_score:.1f} / 100")
    print("-" * 60)
    
    # Verdict Logic
    if final_score > 80:
        verdict = "UNICORN 🦄 (Invest Immediately)"
    elif final_score > 60:
        verdict = "VIABLE BUSINESS 🏭 (Proceed with Pilot)"
    else:
        verdict = "PIPE DREAM 💤 (Kill Project)"
        
    print(f"  VERDICT: {verdict}")
    print("\n  [RECOMMENDATION TO FOUNDER]")
    print("  1. DO NOT pitch this as a cost-saver (ROI is too slow).")
    print("  2. PITCH IT as a 'Water Solvency' & 'Grid Independence' solution.")
    print("  3. TARGET: Microsoft Dublin & AWS Virginia only.")
    print("  4. IGNORE: Meta Lulea or Google Hamina (They don't need you).")

    plot_radar(score_finance, score_physics, score_reliability, score_env, score_strat)

def plot_radar(fin, phys, rel, env, strat):
    os.makedirs("assets", exist_ok=True)
    
    labels = ['Financials', 'Physics', 'Reliability', 'Environment', 'Strategy']
    values = [fin, phys, rel, env, strat]
    
    # Close the loop
    values += [values[0]]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += [angles[0]]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    plt.style.use('dark_background')
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#111')
    
    ax.plot(angles, values, color='#00FFCC', linewidth=2)
    ax.fill(angles, values, color='#00FFCC', alpha=0.25)
    
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color='white', fontsize=12, fontweight='bold')
    
    ax.set_title("v42: PROJECT VIABILITY RADAR", color='white', fontweight='bold', pad=20)
    
    out = "assets/v42_investment_radar.png"
    plt.savefig(out, dpi=150)
    print(f"\n  ✓ Chart saved: {out}")

if __name__ == "__main__":
    run_final_verdict()
