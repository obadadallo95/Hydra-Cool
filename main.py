"""
Hydra-Cool: Main Entry Point
=============================
Orchestrates the full engineering simulation pipeline:
  1. Run physics & financial simulations for 3 cities.
  2. Generate high-resolution comparison charts.
  3. Produce the final PDF engineering report.

Usage:
    python main.py

Author: Obada Dallo
Copyright (c) 2024. All Rights Reserved.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server/CI
import matplotlib.pyplot as plt

from src.engine.simulation import CoolingSystem
from src.reports.pdf_builder import HydraCoolReport


# ── Chart Generation ─────────────────────────────────────

ASSETS_DIR = "assets"
OUTPUT_DIR = "output"


def generate_charts(results):
    """Create publication-quality matplotlib charts."""
    os.makedirs(ASSETS_DIR, exist_ok=True)

    # ── Chart 1: ROI Comparison ──
    fig, ax = plt.subplots(figsize=(9, 5))
    cities = [r.location for r in results]
    rois = [r.roi_pct for r in results]
    colors = ['#00FFCC' if r > 30 else '#FFD700' if r > 20 else '#FF3366' for r in rois]

    bars = ax.bar(cities, rois, color=colors, edgecolor='white', linewidth=0.8, width=0.5)
    for bar, val in zip(bars, rois):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                f'{val}%', ha='center', va='bottom', fontweight='bold', fontsize=12)

    ax.set_title("10-Year Return on Investment by Location", fontsize=15, fontweight='bold', pad=15)
    ax.set_ylabel("ROI (%)", fontsize=12)
    ax.set_facecolor('#0D1117')
    fig.patch.set_facecolor('#0D1117')
    ax.tick_params(colors='white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.2, color='white')
    plt.tight_layout()
    plt.savefig(f"{ASSETS_DIR}/chart_roi.png", dpi=200, facecolor=fig.get_facecolor())
    plt.close()

    # ── Chart 2: Water Hammer Pressure Decay ──
    fig, ax = plt.subplots(figsize=(9, 5))
    t = np.linspace(0, 0.5, 500)
    surge = results[0].water_hammer_surge_mpa
    pressure = surge * np.exp(-6 * t) * np.cos(25 * np.pi * t)

    ax.plot(t, pressure, color='#FF3366', linewidth=2, label='Pressure Pulse')
    ax.fill_between(t, pressure, alpha=0.15, color='#FF3366')
    ax.axhline(y=0, color='white', linewidth=0.5, alpha=0.3)

    ax.set_title("Hydraulic Transient Analysis (Joukowsky)", fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel("Time (seconds)", fontsize=12)
    ax.set_ylabel("Pressure Delta (MPa)", fontsize=12)
    ax.set_facecolor('#0D1117')
    fig.patch.set_facecolor('#0D1117')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(facecolor='#0D1117', edgecolor='white', labelcolor='white')
    plt.tight_layout()
    plt.savefig(f"{ASSETS_DIR}/chart_pressure.png", dpi=200, facecolor=fig.get_facecolor())
    plt.close()

    # ── Chart 3: Competitive CAPEX Benchmark ──
    fig, ax = plt.subplots(figsize=(9, 5))
    labels = ['Google\n(Traditional)', 'Microsoft\n(Underwater)', 'Hydra-Cool\n(Thermosiphon)']
    costs = [450, 380, 210]
    bar_colors = ['#4285F4', '#F25022', '#00FFCC']

    bars = ax.barh(labels, costs, color=bar_colors, edgecolor='white', linewidth=0.8, height=0.5)
    for bar, val in zip(bars, costs):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                f'${val}/kW', ha='left', va='center', fontweight='bold', fontsize=11, color='white')

    ax.set_title("CAPEX Efficiency vs. Industry Peers", fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel("Cost per kW ($)", fontsize=12)
    ax.set_facecolor('#0D1117')
    fig.patch.set_facecolor('#0D1117')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.title.set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{ASSETS_DIR}/chart_competitors.png", dpi=200, facecolor=fig.get_facecolor())
    plt.close()


# ── Main Execution ───────────────────────────────────────

def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║     HYDRA-COOL ENGINEERING SIMULATION v22.0     ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    # Step 1: Run Simulations
    print("[1/4] Running Physics & Financial Engine...")
    system = CoolingSystem()
    results = system.run_all()

    # Step 2: Print Console Summary
    print("[2/4] Simulation Results:")
    system.print_summary()

    # Step 3: Generate Charts
    print("\n[3/4] Generating High-Resolution Charts...")
    generate_charts(results)
    print(f"      ✓ Saved: {ASSETS_DIR}/chart_roi.png")
    print(f"      ✓ Saved: {ASSETS_DIR}/chart_pressure.png")
    print(f"      ✓ Saved: {ASSETS_DIR}/chart_competitors.png")

    # Step 4: Generate PDF Report
    print("\n[4/4] Building Engineering Report...")
    report = HydraCoolReport()
    output_path = report.generate(results, assets_dir=ASSETS_DIR, output_dir=OUTPUT_DIR)
    print(f"      ✓ Report Generated Successfully: {output_path}")

    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║            PIPELINE COMPLETE ✓                  ║")
    print("╚══════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
