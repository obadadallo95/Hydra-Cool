"""
Generate publication-grade Hydra-Cool figures.

Outputs:
  - PNG for GitHub
  - SVG for publication workflows
  - PDF for papers
  - Markdown captions
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
FIG_DIR = OUTPUT / "publication_figures"
CAPTION_FILE = FIG_DIR / "figure_captions.md"

STAGE3_DATASET = OUTPUT / "hydra_cool_stage_3_focus_window_dataset.csv"
STAGE3_SUMMARY = OUTPUT / "hydra_cool_stage_3_focus_window_summary.json"
STAGE3_SENSITIVITY = OUTPUT / "hydra_cool_stage_3_focus_window_sensitivity.csv"


def configure_style():
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#334155",
            "axes.labelcolor": "#0f172a",
            "axes.titlecolor": "#0f172a",
            "xtick.color": "#334155",
            "ytick.color": "#334155",
            "font.size": 10,
            "font.family": "DejaVu Sans",
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "legend.frameon": False,
            "savefig.bbox": "tight",
        }
    )


def export_figure(fig, stem: str):
    for ext in ("png", "svg", "pdf"):
        path = FIG_DIR / f"{stem}.{ext}"
        save_kwargs = {"dpi": 300} if ext == "png" else {}
        fig.savefig(path, **save_kwargs)
    plt.close(fig)


def add_flow_arrow(ax, start, end, color="#1d4ed8", label=None, label_offset=(0, 0)):
    arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12, linewidth=2, color=color)
    ax.add_patch(arrow)
    if label:
        mx = (start[0] + end[0]) / 2 + label_offset[0]
        my = (start[1] + end[1]) / 2 + label_offset[1]
        ax.text(mx, my, label, fontsize=9, color=color, ha="center", va="center")


def load_inputs():
    usecols = [
        "classification",
        "circulation_regime",
        "failure_mode",
        "energy_savings_fraction",
        "baseline_cooling_energy_mw",
        "hydra_net_energy_mw",
        "velocity_ms",
        "pipe_diameter_m",
        "number_of_pipes",
        "delta_t_c",
        "it_load_mw",
        "buoyancy_pressure_pa",
        "total_losses_pa",
        "gravity_assist_fraction",
        "turbine_recovery_active",
    ]
    df = pd.read_csv(STAGE3_DATASET, usecols=usecols)
    with open(STAGE3_SUMMARY, "r", encoding="utf-8") as handle:
        summary = json.load(handle)
    sensitivity = pd.read_csv(STAGE3_SENSITIVITY)
    return df, summary, sensitivity


def figure_1_system_architecture():
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    sea = Rectangle((0, 0), 14, 2.2, facecolor="#dbeafe", edgecolor="none")
    ax.add_patch(sea)
    ax.text(0.5, 1.8, "Sea level", fontsize=10, color="#1e3a8a")

    deep_intake = Rectangle((1.0, 0.2), 1.6, 1.1, facecolor="#93c5fd", edgecolor="#1d4ed8", linewidth=1.5)
    hx = Rectangle((4.3, 3.0), 2.2, 1.3, facecolor="#fde68a", edgecolor="#b45309", linewidth=1.5)
    riser = Rectangle((7.1, 2.0), 0.5, 4.4, facecolor="#bfdbfe", edgecolor="#2563eb", linewidth=1.5)
    reservoir = Rectangle((8.3, 6.0), 3.0, 1.2, facecolor="#c7d2fe", edgecolor="#4338ca", linewidth=1.5)
    return_pipe = Rectangle((10.3, 2.0), 0.5, 4.0, facecolor="#e0f2fe", edgecolor="#0891b2", linewidth=1.5)
    turbine = Circle((10.55, 4.4), 0.35, facecolor="#d1fae5", edgecolor="#047857", linewidth=1.5)

    for patch in (deep_intake, hx, riser, reservoir, return_pipe, turbine):
        ax.add_patch(patch)

    ax.text(1.8, 0.75, "Deep water\nintake", ha="center", va="center")
    ax.text(5.4, 3.65, "Data center\nheat exchanger", ha="center", va="center")
    ax.text(7.35, 4.4, "Buoyancy-driven\nvertical rise", ha="center", va="center", rotation=90)
    ax.text(9.8, 6.6, "Elevated reservoir", ha="center", va="center")
    ax.text(10.9, 4.0, "Gravity\nreturn", ha="left", va="center", rotation=90)
    ax.text(11.2, 4.4, "Optional turbine", ha="left", va="center", color="#065f46")

    add_flow_arrow(ax, (2.6, 0.8), (4.3, 3.5), label="cold seawater")
    add_flow_arrow(ax, (6.5, 3.65), (7.1, 3.65), label="heat absorption", label_offset=(0.0, 0.55), color="#b45309")
    add_flow_arrow(ax, (7.35, 4.2), (7.35, 6.0), label="density change\n+ buoyancy head", label_offset=(1.0, 0.0), color="#2563eb")
    add_flow_arrow(ax, (8.3, 6.6), (10.3, 6.6), label="elevated discharge")
    add_flow_arrow(ax, (10.55, 6.0), (10.55, 2.0), label="gravity return", label_offset=(-1.0, 0.0), color="#0891b2")
    add_flow_arrow(ax, (10.3, 2.0), (2.0, 1.1), color="#0f766e")

    ax.set_title("Figure 1. Hydra-Cool system architecture schematic", loc="left", fontweight="bold")
    export_figure(fig, "figure_01_system_architecture")


def figure_2_buoyancy_flow_cycle():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    nodes = {
        "intake": (1.5, 4.0, "Cold seawater\nT_cold, rho_high"),
        "hx": (4.0, 6.2, "Heat exchanger\n+Q from IT load"),
        "warm": (6.7, 6.2, "Warm water\nT_hot, rho_low"),
        "rise": (8.2, 4.2, "Vertical rise\nDelta P_buoyancy"),
        "reservoir": (6.6, 1.8, "Elevated discharge"),
        "return": (3.6, 1.8, "Gravity return"),
    }

    for x, y, label in nodes.values():
        box = Rectangle((x - 0.9, y - 0.55), 1.8, 1.1, facecolor="white", edgecolor="#334155", linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, label, ha="center", va="center")

    add_flow_arrow(ax, (2.4, 4.45), (3.2, 5.6), color="#1d4ed8")
    add_flow_arrow(ax, (4.9, 6.2), (5.8, 6.2), color="#b45309", label="Delta T > 0", label_offset=(0, 0.45))
    add_flow_arrow(ax, (7.6, 5.8), (8.2, 4.8), color="#2563eb", label="rho_cold - rho_hot", label_offset=(0.8, 0.2))
    add_flow_arrow(ax, (7.9, 3.6), (7.0, 2.35), color="#0891b2", label="gravity return", label_offset=(0.9, 0.1))
    add_flow_arrow(ax, (5.7, 1.8), (4.5, 1.8), color="#0f766e")
    add_flow_arrow(ax, (2.7, 2.15), (1.8, 3.45), color="#1d4ed8")

    ax.text(7.9, 5.3, "Buoyancy pressure:\nDelta P = (rho_cold - rho_hot) g H", color="#1d4ed8", ha="left")
    ax.set_title("Figure 2. Buoyancy-assisted thermodynamic loop", loc="left", fontweight="bold")
    export_figure(fig, "figure_02_buoyancy_flow_cycle")


def figure_3_pressure_balance(df):
    sample = df.sample(n=min(20000, len(df)), random_state=42)
    x = sample["buoyancy_pressure_pa"] / 1000.0
    y = sample["total_losses_pa"] / 1000.0
    colors = np.where(sample["classification"] == "PASS", "#059669", "#c2410c")

    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    ax.scatter(x, y, c=colors, s=8, alpha=0.25, linewidths=0)
    limit = max(float(x.max()), float(y.max())) * 1.05
    ax.plot([0, limit], [0, limit], linestyle="--", color="#334155", linewidth=1.5)
    ax.fill_between([0, limit], [0, 0], [0, limit], color="#dcfce7", alpha=0.5)
    ax.text(limit * 0.58, limit * 0.18, "Feasible circulation region\nDelta P_buoyancy > Delta P_losses", color="#166534")
    ax.text(limit * 0.18, limit * 0.72, "Hydraulic deficit region", color="#9a3412")
    ax.set_xlabel("Buoyancy pressure [kPa]")
    ax.set_ylabel("Hydraulic losses [kPa]")
    ax.set_title("Figure 3. Pressure balance and circulation feasibility", loc="left", fontweight="bold")
    export_figure(fig, "figure_03_pressure_balance")


def figure_4_pass_fail(summary):
    pass_rate = summary["pass_rate"] * 100.0
    fail_rate = summary["fail_rate"] * 100.0

    fig, ax = plt.subplots(figsize=(8.5, 2.6))
    ax.barh(["Simulation campaign"], [pass_rate], color="#059669", label="PASS")
    ax.barh(["Simulation campaign"], [fail_rate], left=[pass_rate], color="#dc2626", label="FAIL")
    ax.text(pass_rate / 2, 0, f"PASS\n{pass_rate:.1f}%", ha="center", va="center", color="white", fontweight="bold")
    ax.text(pass_rate + fail_rate / 2, 0, f"FAIL\n{fail_rate:.1f}%", ha="center", va="center", color="white", fontweight="bold")
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of scenarios [%]")
    ax.set_title("Figure 4. PASS/FAIL distribution across the focus-window campaign", loc="left", fontweight="bold")
    ax.legend(ncol=2, loc="upper center")
    export_figure(fig, "figure_04_pass_fail_distribution")


def figure_5_parameter_importance(sensitivity):
    rename = {
        "it_load_mw": "IT load",
        "hx_pressure_drop_kpa": "HX pressure drop",
        "number_of_pipes": "Number of pipes",
        "pipe_diameter_m": "Pipe diameter",
        "delta_t_c": "Delta T",
    }
    top = sensitivity[sensitivity["parameter"].isin(rename)].copy()
    top["label"] = top["parameter"].map(rename)
    top = top.sort_values("importance_score")

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.barh(top["label"], top["importance_score"], color="#2563eb")
    for _, row in top.iterrows():
        ax.text(row["importance_score"] + 0.005, row["label"], f"{row['importance_score']:.3f}", va="center")
    ax.set_xlabel("Composite importance score")
    ax.set_title("Figure 5. Ranked parameter importance for Hydra-Cool feasibility", loc="left", fontweight="bold")
    export_figure(fig, "figure_05_parameter_importance")


def figure_6_failure_modes(df):
    counts = (
        df[df["classification"] == "FAIL"]["failure_mode"]
        .value_counts()
        .loc[["VELOCITY_TOO_LOW", "VELOCITY_TOO_HIGH"]]
    )
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    bars = ax.bar(counts.index, counts.values, color=["#b91c1c", "#f97316"])
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + counts.max() * 0.015, f"{int(bar.get_height()):,}", ha="center")
    ax.set_ylabel("Scenario count")
    ax.set_title("Figure 6. Dominant hydraulic failure modes", loc="left", fontweight="bold")
    ax.text(0, counts.max() * 0.92, "Insufficient velocity is the dominant failure mechanism", color="#7f1d1d")
    export_figure(fig, "figure_06_failure_modes")


def figure_7_energy_comparison(df):
    feasible = df[df["classification"].isin(["PASS", "MARGINAL"])].copy()
    baseline = feasible["baseline_cooling_energy_mw"]
    hydra = feasible["hydra_net_energy_mw"]
    savings = feasible["energy_savings_fraction"] * 100.0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))
    ax1.boxplot(
        [baseline, hydra],
        tick_labels=["Baseline cooling", "Hydra-Cool assist"],
        patch_artist=True,
        boxprops={"facecolor": "#bfdbfe"},
        medianprops={"color": "#1e3a8a"},
    )
    ax1.set_ylabel("Cooling energy demand [MW]")
    ax1.set_title("Absolute energy demand")

    ax2.hist(savings, bins=30, color="#0f766e", alpha=0.85, edgecolor="white")
    ax2.axvline(np.median(savings), color="#134e4a", linestyle="--", linewidth=1.5, label=f"Median = {np.median(savings):.1f}%")
    ax2.set_xlabel("Energy savings relative to baseline [%]")
    ax2.set_ylabel("Scenario count")
    ax2.set_title("Savings distribution")
    ax2.legend()

    fig.suptitle("Figure 7. Energy comparison between baseline cooling and Hydra-Cool assist", x=0.02, ha="left", fontweight="bold")
    export_figure(fig, "figure_07_energy_comparison")


def figure_8_design_window_map(df):
    heat = (
        df.groupby(["delta_t_c", "it_load_mw"])["classification"]
        .apply(lambda s: (s == "PASS").mean())
        .unstack(fill_value=0.0)
        .sort_index()
    )

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    im = ax.imshow(heat.values, origin="lower", aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(heat.columns)))
    ax.set_xticklabels([f"{int(v)}" for v in heat.columns], rotation=45, ha="right")
    ax.set_yticks(np.arange(len(heat.index)))
    ax.set_yticklabels([f"{int(v)}" for v in heat.index])
    ax.set_xlabel("IT load [MW]")
    ax.set_ylabel("Delta T [C]")
    ax.set_title("Figure 8. Feasible design window map (PASS rate)", loc="left", fontweight="bold")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("PASS fraction")
    export_figure(fig, "figure_08_design_window_map")


def figure_9_velocity_distribution(df):
    velocity = df["velocity_ms"]
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.hist(velocity, bins=50, color="#60a5fa", edgecolor="white")
    ax.axvline(0.5, color="#b91c1c", linestyle="--", linewidth=1.5, label="Minimum velocity")
    ax.axvline(3.0, color="#b45309", linestyle="--", linewidth=1.5, label="Maximum velocity")
    ax.set_xlabel("Flow velocity [m/s]")
    ax.set_ylabel("Scenario count")
    ax.set_title("Figure 9. Flow velocity distribution across the focus-window study", loc="left", fontweight="bold")
    ax.legend()
    export_figure(fig, "figure_09_velocity_distribution")


def figure_10_hybrid_vs_passive(summary):
    passive = summary["passive_natural_pass_rate"] * 100.0
    hybrid = summary["hybrid_assisted_pass_rate"] * 100.0

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    labels = ["Passive\nstandalone", "Hybrid retrofit\nassist"]
    values = [passive, hybrid]
    colors = ["#7c3aed", "#0f766e"]
    bars = ax.bar(labels, values, color=colors)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 1.2, f"{value:.1f}%", ha="center")
    ax.set_ylabel("PASS share of all scenarios [%]")
    ax.set_title("Figure 10. Hybrid vs passive operation", loc="left", fontweight="bold")
    ax.text(1, hybrid * 0.55, "Hybrid retrofit assist dominates viability", ha="center", color="white", fontweight="bold")
    export_figure(fig, "figure_10_hybrid_vs_passive")


def write_captions():
    captions = [
        "Figure 1. Engineering schematic of the Hydra-Cool architecture showing deep-water intake, data-center heat exchanger, buoyancy-driven riser, elevated reservoir, gravity return loop, and optional turbine placement.",
        "Figure 2. Thermodynamic circulation loop highlighting cold seawater intake, heat absorption, density reduction after heating, buoyancy-driven rise, elevated discharge, and gravity-assisted return.",
        "Figure 3. Pressure-balance plot comparing buoyancy pressure and total hydraulic losses. Scenarios below the one-to-one line satisfy the pressure condition for circulation.",
        "Figure 4. PASS/FAIL distribution across the focused simulation campaign. Approximately 48.5% of scenarios pass within the narrowed design window.",
        "Figure 5. Ranked sensitivity chart showing that IT load, heat-exchanger pressure drop, number of pipes, pipe diameter, and Delta T dominate Hydra-Cool feasibility.",
        "Figure 6. Dominant hydraulic failure modes. Velocity that is too low is the primary reason for failure across the campaign, far exceeding high-velocity failure cases.",
        "Figure 7. Comparison between baseline cooling energy demand and Hydra-Cool assisted cooling demand, together with the resulting energy-savings distribution for viable scenarios.",
        "Figure 8. Feasible design-window heatmap expressed as PASS fraction over Delta T and IT-load combinations, highlighting where retrofit viability is concentrated.",
        "Figure 9. Distribution of flow velocities with minimum and maximum design constraints marked, showing the large share of sub-threshold velocity cases.",
        "Figure 10. Comparison of passive-standalone and hybrid-retrofit operating modes. Hybrid retrofit assist accounts for the majority of viable scenarios.",
    ]
    CAPTION_FILE.write_text("\n\n".join(captions), encoding="utf-8")


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    configure_style()
    df, summary, sensitivity = load_inputs()

    figure_1_system_architecture()
    figure_2_buoyancy_flow_cycle()
    figure_3_pressure_balance(df)
    figure_4_pass_fail(summary)
    figure_5_parameter_importance(sensitivity)
    figure_6_failure_modes(df)
    figure_7_energy_comparison(df)
    figure_8_design_window_map(df)
    figure_9_velocity_distribution(df)
    figure_10_hybrid_vs_passive(summary)
    write_captions()

    print(f"Publication figures written to: {FIG_DIR}")


if __name__ == "__main__":
    main()
