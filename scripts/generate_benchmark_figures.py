"""
Generate conservative benchmark-comparison figures for the Hydra-Cool repository.

Outputs:
  - figures/benchmark_energy_comparison.png
  - figures/benchmark_energy_comparison.svg
  - figures/benchmark_positioning_matrix.png
  - figures/benchmark_positioning_matrix.svg
  - figures/benchmark_table_summary.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
FIG_DIR = ROOT / "figures"
FINAL_RESULTS = OUTPUT / "hydra_cool_stage_3_final_results.csv"


def configure_style() -> None:
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


def export_figure(fig, stem: str, svg: bool = True) -> None:
    png_path = FIG_DIR / f"{stem}.png"
    fig.savefig(png_path, dpi=300)
    if svg:
        svg_path = FIG_DIR / f"{stem}.svg"
        fig.savefig(svg_path)
    plt.close(fig)


def load_hydra_reference() -> dict:
    final_results = pd.read_csv(FINAL_RESULTS, usecols=["hydra_total_power_mw", "baseline_cooling_energy_mw"])
    hybrid_median = float((final_results["hydra_total_power_mw"] / final_results["baseline_cooling_energy_mw"]).median())
    return {
        "hybrid_simulation_median": hybrid_median,
        # Conservative uplift used in public comparison figures.
        "hybrid_display_central": max(0.30, hybrid_median),
        "hybrid_display_low": hybrid_median,
        "hybrid_display_high": 0.45,
    }


def benchmark_rows(hydra_reference: dict):
    return [
        {
            "system": "Conventional\nmechanical plant",
            "central": 1.00,
            "low": 1.00,
            "high": 1.00,
            "source": "Reference baseline",
            "color": "#475569",
        },
        {
            "system": "Pumped seawater loop\n(no buoyancy assist)",
            "central": 0.70,
            "low": 0.60,
            "high": 0.85,
            "source": "Engineering estimate",
            "color": "#2563eb",
        },
        {
            "system": "Hydra-Cool hybrid\nretrofit assist",
            "central": hydra_reference["hybrid_display_central"],
            "low": hydra_reference["hybrid_display_low"],
            "high": hydra_reference["hybrid_display_high"],
            "source": "Simulation-informed,\nconservative framing",
            "color": "#059669",
        },
    ]


def figure_benchmark_energy_comparison(hydra_reference: dict) -> None:
    rows = benchmark_rows(hydra_reference)
    labels = [row["system"] for row in rows]
    central = np.array([row["central"] for row in rows])
    lower = central - np.array([row["low"] for row in rows])
    upper = np.array([row["high"] for row in rows]) - central
    colors = [row["color"] for row in rows]
    xpos = np.arange(len(rows))

    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    bars = ax.bar(xpos, central, color=colors, width=0.64, edgecolor="white", linewidth=1.0)
    ax.errorbar(xpos, central, yerr=np.vstack([lower, upper]), fmt="none", ecolor="#0f172a", elinewidth=1.4, capsize=6)
    ax.set_xticks(xpos, labels)
    ax.set_ylabel("Relative cooling energy burden index\n(conventional mechanical plant = 1.00)")
    ax.set_ylim(0, 1.15)
    ax.set_title("Benchmark energy comparison for Hydra-Cool research framing", loc="left", fontweight="bold")

    for bar, row in zip(bars, rows):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.035,
            f"{row['central']:.2f}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            0.03,
            row["source"],
            ha="center",
            va="bottom",
            color="#334155",
            fontsize=8,
        )

    ax.text(
        0.0,
        -0.22,
        (
            "Hydra-Cool hybrid central value is conservative. Stage 3 hybrid-candidate median from the repository is "
            f"~{hydra_reference['hybrid_simulation_median']:.2f}, but the benchmark comparison displays 0.30 to avoid overclaiming."
        ),
        transform=ax.transAxes,
        color="#475569",
        fontsize=8.5,
    )
    export_figure(fig, "benchmark_energy_comparison")


def figure_positioning_matrix() -> None:
    systems = [
        ("Conventional\nmechanical plant", 0.95, 0.05, "#475569"),
        ("Pumped seawater\nloop", 0.85, 0.10, "#2563eb"),
        ("Hydra-Cool hybrid\nretrofit assist", 0.55, 0.65, "#059669"),
        ("Hydra-Cool passive\nedge cases", 0.10, 0.95, "#f59e0b"),
    ]

    fig, ax = plt.subplots(figsize=(8.8, 6.4))
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.axhline(0.5, color="#cbd5e1", linewidth=1.0, linestyle="--")
    ax.axvline(0.5, color="#cbd5e1", linewidth=1.0, linestyle="--")

    for label, x, y, color in systems:
        ax.scatter(x, y, s=180, color=color, edgecolor="white", linewidth=1.2, zorder=3)
        ax.text(x + 0.02, y + 0.015, label, fontsize=9, color="#0f172a")

    ax.text(0.03, 0.95, "Passive-dominant\nbut exploratory", color="#92400e")
    ax.text(0.62, 0.07, "Pump-dominant\nsystems", color="#1e3a8a")
    ax.text(0.52, 0.78, "Hydra-Cool target region:\npartial passive aid,\nnot zero pumps", color="#065f46")

    ax.set_xlabel("Dependence on active pumping (0 = low, 1 = high)")
    ax.set_ylabel("Passive hydraulic contribution (0 = low, 1 = high)")
    ax.set_title("Benchmark positioning matrix for cooling architectures", loc="left", fontweight="bold")
    export_figure(fig, "benchmark_positioning_matrix")


def figure_summary_table(hydra_reference: dict) -> None:
    table_rows = [
        ["Conventional plant", "1.00", "Very high", "Very low", "High"],
        ["Pumped seawater loop", "0.70", "High", "Low", "Moderate to high"],
        ["Hydra hybrid assist", f"{hydra_reference['hybrid_display_central']:.2f}", "Moderate", "High", "Low / research-stage"],
        ["Hydra passive edge case", "0.18", "Very low", "Very high", "Very low / exploratory"],
    ]
    columns = [
        "System",
        "Relative energy\nburden index",
        "Pump\ndependence",
        "Passive\ncontribution",
        "Validation\nmaturity",
    ]

    fig, ax = plt.subplots(figsize=(10.6, 3.6))
    ax.axis("off")
    table = ax.table(
        cellText=table_rows,
        colLabels=columns,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.6)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#cbd5e1")
        if row == 0:
            cell.set_facecolor("#e2e8f0")
            cell.set_text_props(weight="bold", color="#0f172a")
        elif row == 3:
            cell.set_facecolor("#ecfdf5")
        elif row == 4:
            cell.set_facecolor("#fffbeb")
        else:
            cell.set_facecolor("white")

    ax.set_title("Benchmark summary table (normalized, conceptual framing)", loc="left", fontweight="bold")
    ax.text(
        0.0,
        -0.15,
        "Hydra-Cool values are simulation-informed and conservatively framed; comparison is not a calibrated plant benchmark.",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#475569",
    )
    export_figure(fig, "benchmark_table_summary", svg=True)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    configure_style()
    hydra_reference = load_hydra_reference()
    figure_benchmark_energy_comparison(hydra_reference)
    figure_positioning_matrix()
    figure_summary_table(hydra_reference)
    print(f"Benchmark figures written to: {FIG_DIR}")


if __name__ == "__main__":
    main()
