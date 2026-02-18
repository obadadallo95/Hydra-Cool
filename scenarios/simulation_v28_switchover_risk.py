"""
Hydra-Cool Simulation v28.0 — SWITCHOVER RISK ANALYSIS
======================================================
The "Pain Curve": Modeling the Transition Spike.

THE SCENARIO:
  You don't just "switch on" a new cooling system.
  You run BOTH for 6 months to prove safety.
  That means paying double bills for 6 months.

TIMELINE:
  Month 1-6:   Construction (100% Legacy OPEX)
  Month 7-12:  "Double Bill" (Legacy OPEX + Retrofit Testing OPEX)
  Month 13:    Switchover (Retrofit OPEX Only)

OBJECTIVE:
  Visualize the OPEX spike used to scare CFOs, then show the massive drop.
  Calculate the "Cost of Verification" (The price of sleeping at night).

Author: Obada Dallo
Copyright (c) 2024. All Rights Reserved.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

# ══════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════

MONTHS = 24
LEGACY_OPEX_MO    = 65_000_000 / 12   # ~$5.4M/mo
RETROFIT_OPEX_MO  = 16_000_000 / 12   # ~$1.3M/mo
TRANSITION_PREMIUM = 200_000          # Extra staff during transition

# ══════════════════════════════════════════════════════════════
#  SIMULATION ENGINE
# ══════════════════════════════════════════════════════════════

def run_transition_simulation():
    print("="*80)
    print("  HYDRA-COOL v28: SWITCHOVER RISK (The Pain Curve)")
    print("="*80)
    
    months = np.arange(1, MONTHS + 1)
    opex_curve = []
    
    # Trackers
    total_legacy_spend = 0
    total_transition_spend = 0
    
    print(f"\n  {'Month':<5} {'Phase':<20} {'Legacy $':>10} {'Retrofit $':>10} {'Total OPEX':>12} {'Notes':<30}")
    print("-" * 95)
    
    for m in months:
        if m <= 6:
            # Phase 1: Construction
            phase = "Construction"
            leg = LEGACY_OPEX_MO
            ret = 0
            # Note: CAPEX is handled in v27, this is OPEX and Transition Risk
            note = "Business as usual (burning cash)"
        elif m <= 12:
            # Phase 2: Double Bill / Validation
            phase = "Validation (Dual)"
            leg = LEGACY_OPEX_MO
            ret = RETROFIT_OPEX_MO + TRANSITION_PREMIUM # Testing load + extra staff
            total_transition_spend += ret # This is the "Extra" cost of safety
            note = "⚠️ THE SPIKE (Paying Double)"
        else:
            # Phase 3: Switchover
            phase = "Operation"
            leg = 0
            ret = RETROFIT_OPEX_MO
            note = "✅ Nirvana (75% Savings)"
            
        total = leg + ret
        opex_curve.append(total)
        total_legacy_spend += leg
        
        marker = "🔥" if m in range(7, 13) else ""
        print(f"  {m:<5} {phase:<20} ${leg/1e6:>9.2f}M ${ret/1e6:>9.2f}M ${total/1e6:>11.2f}M {note} {marker}")

    # Summary Stats
    spike_cost = total_transition_spend
    monthly_savings = LEGACY_OPEX_MO - RETROFIT_OPEX_MO
    payback_months = spike_cost / monthly_savings
    
    print("-" * 95)
    print("\n  TRANSITION RISK ANALYSIS:")
    print(f"    1. Monthly Baseline Cost:       ${LEGACY_OPEX_MO/1e6:.2f}M")
    print(f"    2. Peak Monthly Cost (Spike):   ${(LEGACY_OPEX_MO + RETROFIT_OPEX_MO + TRANSITION_PREMIUM)/1e6:.2f}M")
    print(f"    3. New Monthly Cost:            ${RETROFIT_OPEX_MO/1e6:.2f}M")
    print(f"    4. Total 'Verification Cost':   ${spike_cost/1e6:.2f}M (The price of safety)")
    print(f"    5. Payback of Verification:     {payback_months:.1f} months")
    print("\n  VERDICT: You endure 6 months of pain, pay it back in 2 months, then profit forever.")
    
    return months, opex_curve

# ══════════════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════════════

def plot_pain_curve(months, opex):
    os.makedirs("assets", exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.style.use('dark_background')
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#111')
    
    # Plot bars
    colors = []
    for m, val in zip(months, opex):
        if m <= 6: colors.append('#FF4444')   # Legacy Red
        elif m <= 12: colors.append('#FFAA00') # Warning Orange
        else: colors.append('#00FFCC')        # Hydra Green
        
    bars = ax.bar(months, [v/1e6 for v in opex], color=colors, edgecolor='black', alpha=0.9)
    
    # Annotate phases
    ax.axvline(x=6.5, color='white', linestyle='--', alpha=0.3)
    ax.axvline(x=12.5, color='white', linestyle='--', alpha=0.3)
    
    ax.text(3.5, 6, "PHASE 1:\nCONSTRUCTION\n(Legacy Cost)", ha='center', color='#FF8888', fontsize=9, fontweight='bold')
    ax.text(9.5, 7, "PHASE 2:\nVALIDATION\n(The Spike)", ha='center', color='#FFCC00', fontsize=9, fontweight='bold')
    ax.text(18.5, 2, "PHASE 3:\nOPERATION\n(75% Savings)", ha='center', color='#00FFCC', fontsize=9, fontweight='bold')
    
    # Titles
    ax.set_title("SWITCHOVER RISK: The Transition Pain Curve", fontsize=16, color='white', pad=20, fontweight='bold')
    ax.set_ylabel("Monthly OPEX ($ Millions)", fontsize=12, color='white')
    ax.set_xlabel("Project Month", fontsize=12, color='white')
    ax.set_xticks(months)
    
    # Grid
    ax.yaxis.grid(True, alpha=0.1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#333')
    ax.spines['left'].set_color('#333')
    
    out_path = "assets/v28_transition_pain_curve.png"
    plt.savefig(out_path, dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"\n  ✓ Chart saved: {out_path}")

if __name__ == "__main__":
    m, o = run_transition_simulation()
    plot_pain_curve(m, o)
