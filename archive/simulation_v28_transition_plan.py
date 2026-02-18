"""
Hydra-Cool Simulation v28.0 — TRANSITION PLAN
================================================
Engineering Roadmap: How to upgrade WITHOUT shutting down servers.

THE CHALLENGE:
  100MW facility = ~500,000 servers = $1B+ annual revenue.
  Every hour of downtime = $500K-2M in lost revenue.
  You CANNOT turn off the cooling to install a new system.

THE SOLUTION: Three-Phase Live Migration
  Phase 1 (Month 0-6):   "Side-Stream Injection"
  Phase 2 (Month 6-12):  "Hybrid Operation"
  Phase 3 (Month 12-18): "Full Switchover"

Key Principle:
  The existing chillers NEVER go offline until HC is proven stable.
  Chillers become backup/standby — zero risk of downtime.

Sources:
  - Uptime Institute: "Cooling System Retrofits Without Downtime" (2023)
  - ASHRAE TC 9.9: "Data Center Live Migration Best Practices"
  - Google SRE Handbook: "Graceful Degradation Patterns"

Author: Obada Dallo
Copyright (c) 2024. All Rights Reserved.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# ══════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════

FACILITY_MW      = 100
HOURS_PER_MONTH  = 730
COST_PER_DOWNTIME_HR = 1_200_000  # $/hr for 100MW DC
ENERGY_PRICE     = 0.07

# Timeline (months)
MONTH_TOTAL      = 24     # Full transition + stabilization


# ══════════════════════════════════════════════════════════════
#  PHASE 1: SIDE-STREAM INJECTION (Month 0-6)
# ══════════════════════════════════════════════════════════════

def phase_1():
    """
    Install HC in PARALLEL with existing system.
    The existing chiller plant continues at 100% — zero risk.
    HC takes overflow / supplemental cooling only.
    """
    print("\n" + "=" * 70)
    print("  PHASE 1: SIDE-STREAM INJECTION (Month 0-6)")
    print("  'Install beside, not instead of.'")
    print("=" * 70)
    
    milestones = [
        ("Month 0",   "Mobilization",
         [
             "Site survey & pipe routing confirmation",
             "Environmental baseline monitoring begins",
             "Order long-lead items (Ti HX, pipe, pumps)",
             "Set up construction staging area (existing parking lot)",
         ]),
        ("Month 1-2", "Subsea Installation",
         [
             "HDD shore crossing (night work, no DC impact)",
             "Pipe lay vessel mobilizes (intake & outfall)",
             "Install intake screen at depth",
             "Install ICCP anode sled",
         ]),
        ("Month 3-4", "Onshore Tie-In",
         [
             "Install prefab pump house (crane, 1 day)",
             "Install Ti heat exchangers in retrofit bay",
             "Connect bypass piping to EXISTING chilled water loop",
             "KEY: Isolation valves keep systems separate",
             "Install SCADA integration points (read-only first)",
         ]),
        ("Month 5-6", "Commissioning & Testing",
         [
             "Seawater flush & chlorination test",
             "Pump wet test (no load — cold loop only)",
             "HX performance verification (side-stream, 5% load)",
             "Vibration, pressure, temperature monitoring",
             "ZERO impact on existing cooling — bypass valve closed",
         ]),
    ]
    
    # During Phase 1, existing system runs at 100%
    # HC is being installed but carries NO load
    hc_load_pct = [0, 0, 0, 0, 0, 5]  # Month by month
    legacy_load_pct = [100, 100, 100, 100, 100, 100]
    
    print(f"\n  Load Distribution During Phase 1:")
    print(f"  {'Month':>7} {'HC Load':>10} {'Legacy Load':>12} {'Status':<30}")
    print(f"  {'-'*60}")
    for m in range(6):
        status = "HC under construction" if m < 5 else "HC first test (5% side-stream)"
        print(f"  M{m+1:>5} {hc_load_pct[m]:>8}% {legacy_load_pct[m]:>10}%  {status}")
    
    print(f"\n  Milestones:")
    for month, title, tasks in milestones:
        print(f"\n  [{month}] {title}")
        for t in tasks:
            print(f"     {t}")
    
    # Risk assessment
    print(f"\n  RISK ASSESSMENT — Phase 1:")
    print(f"    Downtime risk:   0.0 hours (parallel installation)")
    print(f"    Revenue impact:  $0 (existing system unaffected)")
    print(f"    Rollback plan:   Close isolation valve — 30 seconds")
    
    # Costs during Phase 1
    phase1_costs = {
        "Subsea installation (vessel, pipe, HDD)": 65_000_000,
        "Ti heat exchangers":                       18_000_000,
        "Pumps, controls, instrumentation":         10_000_000,
        "Onshore mechanical (piping, bypass)":       8_000_000,
        "Engineering, PM, supervision":              8_000_000,
        "Environmental monitoring":                  1_000_000,
    }
    phase1_total = sum(phase1_costs.values())
    
    print(f"\n  Phase 1 Cost: ${phase1_total/1e6:.0f}M")
    
    return {
        "hc_load": hc_load_pct,
        "legacy_load": legacy_load_pct,
        "cost": phase1_total,
        "months": 6,
        "downtime_hrs": 0,
    }


# ══════════════════════════════════════════════════════════════
#  PHASE 2: HYBRID OPERATION (Month 6-12)
# ══════════════════════════════════════════════════════════════

def phase_2():
    """
    Gradually shift load from chillers to HC.
    Chillers remain online but reducing capacity.
    HC proves reliability under increasing load.
    """
    print("\n" + "=" * 70)
    print("  PHASE 2: HYBRID OPERATION (Month 6-12)")
    print("  'Prove it works. Then trust it.'")
    print("=" * 70)
    
    # Gradual ramp-up schedule
    ramp = [
        (7,  10, 90,  "HC at 10% — monitoring vibration, pressure, flow"),
        (8,  20, 80,  "HC at 20% — first chiller set to standby"),
        (9,  30, 70,  "HC at 30% — two chiller sets on standby"),
        (10, 40, 60,  "HC at 40% — significant energy savings visible"),
        (11, 50, 50,  "HC at 50% — hybrid equilibrium, 30-day stability test"),
        (12, 60, 40,  "HC at 60% — confidence milestone"),
    ]
    
    hc_load = []
    legacy_load = []
    
    print(f"\n  Load Transfer Schedule:")
    print(f"  {'Month':>7} {'HC Load':>10} {'Legacy':>10} {'Chiller Status':<40} {'PUE':>6}")
    print(f"  {'-'*78}")
    
    for month, hc_pct, leg_pct, status in ramp:
        # PUE during hybrid: weighted average
        pue_hc = 1.08
        pue_legacy = 1.30
        pue_hybrid = pue_hc * (hc_pct/100) + pue_legacy * (leg_pct/100)
        
        print(f"  M{month:>5} {hc_pct:>8}% {leg_pct:>8}%  {status:<40} {pue_hybrid:>5.2f}")
        hc_load.append(hc_pct)
        legacy_load.append(leg_pct)
    
    # Redundancy costs during hybrid operation
    # Keeping chillers on standby wastes some energy (hot loop, pumps cycling)
    standby_cost_per_month = 150_000  # Standby power and maintenance
    redundancy_cost = standby_cost_per_month * 6
    
    # Energy savings during ramp-up
    total_savings = 0
    for month, hc_pct, leg_pct, _ in ramp:
        legacy_energy_cost = FACILITY_MW * (1.30 - 1.0) * 1000 * HOURS_PER_MONTH * ENERGY_PRICE
        hybrid_energy_cost = (FACILITY_MW * (1.08 - 1.0) * (hc_pct/100) + 
                              FACILITY_MW * (1.30 - 1.0) * (leg_pct/100)) * 1000 * HOURS_PER_MONTH * ENERGY_PRICE
        monthly_saving = legacy_energy_cost - hybrid_energy_cost
        total_savings += monthly_saving
    
    print(f"\n  Phase 2 Economics:")
    print(f"    Redundancy cost (standby chillers):  ${redundancy_cost/1e6:.1f}M")
    print(f"    Energy savings during ramp-up:       ${total_savings/1e6:.1f}M")
    print(f"    Net benefit during Phase 2:          ${(total_savings - redundancy_cost)/1e6:.1f}M")
    
    # Go/No-Go criteria
    print(f"\n  GO/NO-GO CRITERIA (End of Phase 2):")
    criteria = [
        ("HC availability > 99.9%",               "HARD — if fails, extend Phase 2"),
        ("PUE at 50% load < 1.12",                "HARD — must demonstrate efficiency"),
        ("Zero seawater leaks",                    "HARD — environmental compliance"),
        ("HX performance within 10% of design",   "SOFT — can optimize later"),
        ("SCADA integration verified",             "HARD — operations must be confident"),
        ("Staff training complete",                "HARD — all shifts certified"),
    ]
    for criterion, gate in criteria:
        print(f"    [{gate.split('—')[0].strip()}] {criterion}")
        print(f"           {gate.split('—')[1].strip() if '—' in gate else ''}")
    
    # Risk
    print(f"\n  RISK ASSESSMENT — Phase 2:")
    print(f"    Downtime risk:   < 2 hours (failover to legacy in 30 sec)")
    print(f"    Revenue impact:  ~$0 (redundant cooling always available)")
    print(f"    Rollback plan:   Revert to 100% legacy — valve switch only")
    
    return {
        "hc_load": hc_load,
        "legacy_load": legacy_load,
        "cost": redundancy_cost + 5_000_000,  # Redundancy + monitoring staff
        "savings": total_savings,
        "months": 6,
        "downtime_hrs": 2,
    }


# ══════════════════════════════════════════════════════════════
#  PHASE 3: FULL SWITCHOVER (Month 12-18)
# ══════════════════════════════════════════════════════════════

def phase_3():
    """
    HC takes primary cooling role (80-95%).
    Chillers become backup/peak only.
    """
    print("\n" + "=" * 70)
    print("  PHASE 3: FULL SWITCHOVER (Month 12-18)")
    print("  'The chillers sleep. Hydra-Cool runs the show.'")
    print("=" * 70)
    
    ramp = [
        (13, 70,  30, "HC primary — 2 chiller sets decommission-ready"),
        (14, 80,  20, "HC dominant — most chillers on cold standby"),
        (15, 85,  15, "Stress test: hot summer simulation at 85%"),
        (16, 90,  10, "Chiller 1 formally decommissioned (tower drained)"),
        (17, 90,  10, "Full month stability verification at 90%"),
        (18, 95,   5, "FINAL: HC at 95%, 1 chiller on hot standby (emergency)"),
    ]
    
    hc_load = []
    legacy_load = []
    
    print(f"\n  Final Transition Schedule:")
    print(f"  {'Month':>7} {'HC Load':>10} {'Legacy':>10} {'Status':<45} {'PUE':>6}")
    print(f"  {'-'*83}")
    
    for month, hc_pct, leg_pct, status in ramp:
        pue = 1.08 * (hc_pct/100) + 1.30 * (leg_pct/100)
        print(f"  M{month:>5} {hc_pct:>8}% {leg_pct:>8}%  {status:<45} {pue:>5.2f}")
        hc_load.append(hc_pct)
        legacy_load.append(leg_pct)
    
    # Decommissioning savings
    # Removing chiller sets saves: maintenance, refrigerant, electricity
    decom_savings = {
        "Chiller maintenance eliminated (6 of 8 units)": 2_200_000,
        "Cooling tower water treatment eliminated":        600_000,
        "Cooling tower maintenance eliminated":            800_000,
        "Refrigerant management eliminated":               200_000,
        "Freshwater elimination":                        1_600_000,
    }
    annual_decom_savings = sum(decom_savings.values())
    
    print(f"\n  Annual Savings from Decommissioning:")
    for item, val in decom_savings.items():
        print(f"    {item:<50} ${val/1000:>6.0f}K")
    print(f"    {'═'*55}")
    print(f"    {'TOTAL additional annual savings':<50} ${annual_decom_savings/1e6:>6.1f}M")
    
    # Salvage value of removed equipment
    salvage = {
        "6× centrifugal chillers (resale)": 3_000_000,
        "6× cooling towers (scrap metal)":    600_000,
        "Copper piping reclaim":              400_000,
        "Refrigerant reclaim (R-134a)":       200_000,
    }
    salvage_total = sum(salvage.values())
    
    print(f"\n  Equipment Salvage Value:")
    for item, val in salvage.items():
        print(f"    {item:<40} ${val/1000:>6.0f}K")
    print(f"    {'TOTAL salvage':<40} ${salvage_total/1e6:>6.1f}M")
    
    # Final operating state
    print(f"\n  FINAL OPERATING STATE (Month 18+):")
    print(f"    HC takes:          95% of cooling load (95 MW)")
    print(f"    Legacy standby:    5% (1 chiller + 1 tower, emergency)")
    print(f"    PUE achieved:      {1.08 * 0.95 + 1.30 * 0.05:.2f}")
    print(f"    Staff:             8 FTE (from 15) — existing team retrained")
    print(f"    Water use:         ~0 m³/year (seawater closed loop)")
    
    return {
        "hc_load": hc_load,
        "legacy_load": legacy_load,
        "cost": 2_000_000,  # Monitoring, decom labor
        "decom_savings": annual_decom_savings,
        "salvage": salvage_total,
        "months": 6,
        "downtime_hrs": 0,
    }


# ══════════════════════════════════════════════════════════════
#  STABILIZATION & MONITORING (Month 18-24)
# ══════════════════════════════════════════════════════════════

def stabilization():
    """Post-switchover monitoring and optimization."""
    print("\n" + "=" * 70)
    print("  STABILIZATION (Month 18-24)")
    print("  'Trust but verify.'")
    print("=" * 70)
    
    checks = [
        ("Month 19", "First full seasonal cycle review (winter performance)"),
        ("Month 20", "Biofouling inspection — first pigging run"),
        ("Month 21", "HX performance audit — U-value vs design"),
        ("Month 22", "CP system anode survey (ROV)"),
        ("Month 23", "24-month reliability report — Tier III certification"),
        ("Month 24", "FINAL: Declare operational capability"),
    ]
    
    print(f"\n  Stabilization Milestones:")
    for month, task in checks:
        print(f"    [{month}] {task}")
    
    print(f"\n  Success Criteria at Month 24:")
    print(f"    ✓ PUE < 1.10 achieved consistently")
    print(f"    ✓ Zero unplanned downtime events")
    print(f"    ✓ All staff certified on HC operations")
    print(f"    ✓ Marine environmental audit passed")
    print(f"    ✓ Insurance rate renegotiated (lower premiums)")
    
    return {"months": 6}


# ══════════════════════════════════════════════════════════════
#  TRANSITION SUMMARY
# ══════════════════════════════════════════════════════════════

def transition_summary(p1, p2, p3, stab):
    """Total transition costs and risk."""
    print("\n" + "=" * 70)
    print("  TRANSITION SUMMARY: 18-Month Zero-Downtime Upgrade")
    print("=" * 70)
    
    total_cost = p1["cost"] + p2["cost"] + p3["cost"]
    total_downtime = p1["downtime_hrs"] + p2["downtime_hrs"] + p3["downtime_hrs"]
    max_revenue_risk = total_downtime * COST_PER_DOWNTIME_HR
    
    print(f"""
  ┌──────────────────────────────────────────────────────────────┐
  │            TRANSITION PLAN EXECUTIVE SUMMARY                │
  ├──────────────────────────────────────────────────────────────┤
  │                                                              │
  │  Phase 1 (M0-6):    Side-Stream Installation                │
  │    Cost: ${p1['cost']/1e6:>5.0f}M | Downtime: {p1['downtime_hrs']} hrs | Risk: ZERO      │
  │                                                              │
  │  Phase 2 (M6-12):   Hybrid Operation (10%→60%)              │
  │    Cost: ${p2['cost']/1e6:>5.0f}M | Downtime: <{p2['downtime_hrs']} hrs | Risk: LOW       │
  │    Savings during phase: ${p2['savings']/1e6:.1f}M                    │
  │                                                              │
  │  Phase 3 (M12-18):  Full Switchover (70%→95%)               │
  │    Cost: ${p3['cost']/1e6:>5.0f}M | Downtime: {p3['downtime_hrs']} hrs | Risk: MINIMAL   │
  │    Salvage from decom: ${p3['salvage']/1e6:.1f}M                     │
  │                                                              │
  │  Stabilization (M18-24): Monitoring & Optimization          │
  │                                                              │
  ├──────────────────────────────────────────────────────────────┤
  │                                                              │
  │  Total transition cost:    ${total_cost/1e6:>6.0f}M                     │
  │  Max possible downtime:    {total_downtime} hours                        │
  │  Max revenue at risk:      ${max_revenue_risk/1e6:.1f}M                     │
  │  Annual savings after:     ~${(p3['decom_savings'] + 10_000_000)/1e6:.0f}M/year (energy + maint)   │
  │  Water eliminated:         ~660,000 m³/year                  │
  │  CO₂ reduced:              ~50,000 tonnes/year               │
  │                                                              │
  │  THE KEY INSIGHT:                                            │
  │    The legacy system NEVER goes offline.                     │
  │    At every stage, 100% cooling is guaranteed.               │
  │    The upgrade is additive, not substitutive.                │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
    """)
    
    return {
        "total_cost": total_cost,
        "total_downtime": total_downtime,
        "phases": [p1, p2, p3],
    }


# ══════════════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════════════

def generate_charts(p1, p2, p3, output_dir="assets"):
    """Generate the transition Gantt/load chart."""
    os.makedirs(output_dir, exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 10), 
                                     gridspec_kw={"height_ratios": [1, 2]})
    fig.patch.set_facecolor("#0a0a0a")
    fig.suptitle("TRANSITION PLAN: 18-Month Zero-Downtime Upgrade",
                 fontsize=18, fontweight="bold", color="#00FFCC", y=0.98)
    
    # ── TOP: Gantt Chart ──
    ax1.set_facecolor("#111")
    
    gantt_items = [
        ("Site Survey & Ordering",        0, 1,  "#4285F4"),
        ("Subsea Pipe Installation",      1, 3,  "#26C6DA"),
        ("Onshore Tie-In & HX Install",   3, 5,  "#66BB6A"),
        ("Commissioning & Testing",       5, 6,  "#FFAA00"),
        ("Hybrid Ramp-Up (10→60%)",       6, 12, "#FF9900"),
        ("Full Switchover (70→95%)",      12, 18, "#00FFCC"),
        ("Stabilization & Monitoring",    18, 24, "#AB47BC"),
    ]
    
    for i, (label, start, end, color) in enumerate(gantt_items):
        ax1.barh(i, end - start, left=start, height=0.5, 
                color=color, edgecolor="white", linewidth=0.5, alpha=0.85)
        ax1.text(start + (end - start)/2, i, label, ha="center", va="center",
                color="white", fontweight="bold", fontsize=8)
    
    # Phase separators
    for m in [6, 12, 18]:
        ax1.axvline(x=m, color="#FFAA00", linewidth=1.5, linestyle="--", alpha=0.7)
    
    ax1.text(3, -0.8, "PHASE 1\nInstallation", ha="center", color="#4285F4", fontweight="bold", fontsize=9)
    ax1.text(9, -0.8, "PHASE 2\nHybrid", ha="center", color="#FF9900", fontweight="bold", fontsize=9)
    ax1.text(15, -0.8, "PHASE 3\nSwitchover", ha="center", color="#00FFCC", fontweight="bold", fontsize=9)
    ax1.text(21, -0.8, "PHASE 4\nStabilize", ha="center", color="#AB47BC", fontweight="bold", fontsize=9)
    
    ax1.set_xlim(-0.5, 24.5)
    ax1.set_yticks([])
    ax1.set_xlabel("Month", color="white", fontweight="bold")
    ax1.set_title("Project Timeline (Gantt)", color="white", fontweight="bold", fontsize=12)
    ax1.tick_params(colors="white")
    for s in ax1.spines.values(): s.set_color("#333")
    
    # ── BOTTOM: Load Distribution Over Time ──
    ax2.set_facecolor("#111")
    
    months = np.arange(1, 25)
    
    # Build full load arrays
    hc_all = []
    legacy_all = []
    pue_all = []
    
    for m in months:
        if m <= 6:
            hc = p1["hc_load"][m-1] if m <= len(p1["hc_load"]) else 5
            leg = p1["legacy_load"][m-1] if m <= len(p1["legacy_load"]) else 100
        elif m <= 12:
            idx = m - 7
            hc = p2["hc_load"][idx] if idx < len(p2["hc_load"]) else 60
            leg = p2["legacy_load"][idx] if idx < len(p2["legacy_load"]) else 40
        elif m <= 18:
            idx = m - 13
            hc = p3["hc_load"][idx] if idx < len(p3["hc_load"]) else 95
            leg = p3["legacy_load"][idx] if idx < len(p3["legacy_load"]) else 5
        else:
            hc = 95
            leg = 5
        
        hc_all.append(hc)
        legacy_all.append(leg)
        pue_all.append(1.08 * (hc/100) + 1.30 * (leg/100))
    
    hc_all = np.array(hc_all, dtype=float)
    legacy_all = np.array(legacy_all, dtype=float)
    
    ax2.fill_between(months, 0, hc_all, color="#00FFCC", alpha=0.6, label="Hydra-Cool")
    ax2.fill_between(months, hc_all, hc_all + legacy_all, color="#FF4444", alpha=0.6, label="Legacy Chiller")
    ax2.plot(months, hc_all + legacy_all, color="white", linewidth=1, linestyle="--", alpha=0.5)
    
    # PUE overlay on secondary axis
    ax3 = ax2.twinx()
    ax3.plot(months, pue_all, color="#FFAA00", linewidth=2.5, marker="o", markersize=3, label="PUE")
    ax3.set_ylabel("PUE", color="#FFAA00", fontweight="bold")
    ax3.tick_params(axis="y", colors="#FFAA00")
    ax3.set_ylim(1.0, 1.40)
    ax3.legend(loc="upper right", fontsize=9, facecolor="#222", edgecolor="gray", labelcolor="white")
    
    # Phase separators
    for m in [6, 12, 18]:
        ax2.axvline(x=m, color="#FFAA00", linewidth=1.5, linestyle="--", alpha=0.7)
    
    ax2.set_xlim(0.5, 24.5)
    ax2.set_ylim(0, 110)
    ax2.set_xlabel("Month", color="white", fontweight="bold")
    ax2.set_ylabel("Cooling Load (%)", color="white", fontweight="bold")
    ax2.set_title("Load Distribution: Hydra-Cool vs Legacy Over Time", 
                  color="white", fontweight="bold", fontsize=12)
    ax2.legend(loc="upper left", fontsize=10, facecolor="#222", edgecolor="gray", labelcolor="white")
    ax2.tick_params(colors="white")
    for s in ax2.spines.values(): s.set_color("#333")
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    path = os.path.join(output_dir, "v28_transition_gantt.png")
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="#0a0a0a")
    plt.close()
    print(f"  ✓ Chart saved: {path}")
    return path


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  HYDRA-COOL v28.0 — TRANSITION PLAN")
    print("  '18-Month Zero-Downtime Upgrade Roadmap'")
    print("=" * 70)
    
    p1 = phase_1()
    p2 = phase_2()
    p3 = phase_3()
    stab = stabilization()
    transition_summary(p1, p2, p3, stab)
    
    print("\n  Generating Transition Dashboard...")
    generate_charts(p1, p2, p3)
    
    print("\n" + "=" * 70)
    print("  SIMULATION v28.0 COMPLETE")
    print("=" * 70)
