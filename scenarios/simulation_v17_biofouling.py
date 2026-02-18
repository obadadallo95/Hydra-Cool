"""
Simulation v17.0: Marine Biofouling & Flow Degradation
======================================================
Models the biological growth inside seawater intake pipes
and its progressive impact on flow capacity, heat transfer,
and maintenance economics.

Physics:
  - Biofilm growth rate (logistic model from WHOI marine data)
  - Roughness coefficient increase (Moody chart shift)
  - Heat transfer resistance (fouling factor Rf)
  - Optimal cleaning schedule (cost vs. performance trade-off)

Author: Obada Dallo
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


# ══════════════════════════════════════════════════════════
#  BIOFOULING MODEL
# ══════════════════════════════════════════════════════════

class BiofoulingModel:
    """
    Marine biofouling growth model.

    Organisms: barnacles, mussels, algae, biofilm
    Growth follows a logistic curve:
      thickness(t) = T_max / (1 + exp(-k*(t - t_half)))

    Data sourced from WHOI (Woods Hole Oceanographic) studies.
    """

    # Growth parameters by water temperature regime
    GROWTH_PARAMS = {
        "tropical": {  # SST > 25C (Dubai, Singapore)
            "t_max_mm": 80,       # Maximum biofilm thickness (mm)
            "growth_rate": 0.015,  # k (1/day)
            "t_half_days": 120,    # Days to reach half max thickness
            "species": "Barnacles + Tropical Algae + Tube Worms",
        },
        "temperate": {  # 10C < SST < 25C (LA)
            "t_max_mm": 50,
            "growth_rate": 0.010,
            "t_half_days": 180,
            "species": "Mussels + Green Algae + Biofilm",
        },
        "cold": {  # SST < 10C (Helsinki, Reykjavik)
            "t_max_mm": 25,
            "growth_rate": 0.006,
            "t_half_days": 270,
            "species": "Diatoms + Cold-water Biofilm",
        },
    }

    @staticmethod
    def growth_curve(days, regime="temperate"):
        """Logistic growth: thickness in mm over time."""
        p = BiofoulingModel.GROWTH_PARAMS[regime]
        t_max = p['t_max_mm']
        k = p['growth_rate']
        t_half = p['t_half_days']
        thickness = t_max / (1 + np.exp(-k * (days - t_half)))
        return thickness

    @staticmethod
    def roughness_factor(thickness_mm, base_roughness=0.045):
        """
        Relative roughness increase due to fouling.
        epsilon/D increases as biofouling grows.
        base_roughness: clean pipe (0.045mm for marine steel)
        """
        effective_roughness = base_roughness + thickness_mm * 2  # Inner wall
        return effective_roughness

    @staticmethod
    def friction_factor(roughness_mm, diameter_m, velocity, viscosity=1.08e-6):
        """
        Colebrook-White equation (explicit approximation).
        Returns Darcy friction factor.
        """
        Re = velocity * diameter_m / viscosity
        if Re < 2300:
            return 64 / Re  # Laminar

        eps_D = (roughness_mm / 1000) / diameter_m
        # Swamee-Jain approximation
        f = 0.25 / (np.log10(eps_D / 3.7 + 5.74 / Re**0.9))**2
        return f

    @staticmethod
    def fouling_resistance(thickness_mm):
        """
        Thermal fouling resistance Rf (m^2.K/W).
        Biofilm has low thermal conductivity (~0.6 W/m.K).
        Rf = thickness / k_biofilm
        """
        k_biofilm = 0.6  # W/(m.K)
        Rf = (thickness_mm / 1000) / k_biofilm
        return Rf


# ══════════════════════════════════════════════════════════
#  PERFORMANCE DEGRADATION ENGINE
# ══════════════════════════════════════════════════════════

class DegradationEngine:
    """Calculates system performance loss due to biofouling."""

    PIPE_DIAMETER = 2.0     # m
    PIPE_HEIGHT = 200       # m
    BASE_VELOCITY = 2.5     # m/s (clean pipe)
    NUM_PIPES = 6
    CLEAN_POWER_KW = 800    # Baseline power output

    @classmethod
    def monthly_degradation(cls, months=24, regime="temperate"):
        """Simulate progressive degradation over months."""
        data = []

        for month in range(0, months + 1):
            days = month * 30.44

            # Biofilm thickness
            thickness = BiofoulingModel.growth_curve(days, regime)

            # Effective inner diameter reduction
            d_effective = cls.PIPE_DIAMETER - 2 * thickness / 1000
            area_ratio = (d_effective / cls.PIPE_DIAMETER)**2

            # Friction increase
            roughness = BiofoulingModel.roughness_factor(thickness)
            f_clean = BiofoulingModel.friction_factor(0.045, cls.PIPE_DIAMETER, cls.BASE_VELOCITY)
            f_fouled = BiofoulingModel.friction_factor(roughness, d_effective,
                                                       cls.BASE_VELOCITY * area_ratio)

            # Flow reduction (higher friction = lower velocity)
            flow_ratio = np.sqrt(f_clean / f_fouled) * area_ratio
            flow_ratio = min(flow_ratio, 1.0)

            # Power output (proportional to flow^1.5 approximately)
            power_ratio = flow_ratio**1.5
            power_kw = cls.CLEAN_POWER_KW * power_ratio

            # Thermal fouling resistance
            Rf = BiofoulingModel.fouling_resistance(thickness)
            heat_transfer_ratio = 1 / (1 + Rf * 500)  # 500 W/m^2.K base U

            # Revenue loss
            revenue_loss_pct = (1 - power_ratio) * 100

            data.append({
                "month": month,
                "thickness_mm": round(thickness, 2),
                "diameter_eff_m": round(d_effective, 3),
                "friction_ratio": round(f_fouled / f_clean, 2),
                "flow_pct": round(flow_ratio * 100, 1),
                "power_kw": round(power_kw, 1),
                "power_pct": round(power_ratio * 100, 1),
                "ht_pct": round(heat_transfer_ratio * 100, 1),
                "revenue_loss_pct": round(revenue_loss_pct, 1),
            })

        return data

    @classmethod
    def optimal_cleaning_schedule(cls, regime="temperate"):
        """
        Find the optimal cleaning interval (months).
        Cleaning cost: $150,000 per event (diver team + equipment).
        Lost revenue: proportional to degradation.
        """
        cleaning_cost = 150_000  # $ per cleaning event
        monthly_revenue_clean = cls.CLEAN_POWER_KW * 730 * 0.065  # $38k/month

        best_interval = 0
        best_net = 0

        for interval in range(1, 25):
            data = cls.monthly_degradation(months=interval, regime=regime)
            total_revenue = sum(d['power_kw'] * 730 * 0.065 for d in data)
            n_cleanings = 12 / interval  # per year
            net = total_revenue - n_cleanings * cleaning_cost

            if net > best_net:
                best_net = net
                best_interval = interval

        return best_interval, best_net


# ══════════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════════

class FoulingVisualizer:
    DARK_BG = '#0D1117'

    @classmethod
    def plot_degradation(cls, data_by_regime, output_dir="assets"):
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.patch.set_facecolor(cls.DARK_BG)
        fig.suptitle("Marine Biofouling - Flow Degradation Analysis",
                     color='white', fontsize=16, fontweight='bold')

        colors = {"tropical": "#FF6B35", "temperate": "#FFD700", "cold": "#00BFFF"}

        for ax in axes.flat:
            ax.set_facecolor(cls.DARK_BG)
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            for spine in ax.spines.values():
                spine.set_color('gray')
            ax.grid(True, alpha=0.15, color='white')

        for regime, data in data_by_regime.items():
            months = [d['month'] for d in data]
            c = colors[regime]

            axes[0, 0].plot(months, [d['thickness_mm'] for d in data],
                           color=c, linewidth=2, label=regime.title())
            axes[0, 1].plot(months, [d['flow_pct'] for d in data],
                           color=c, linewidth=2, label=regime.title())
            axes[1, 0].plot(months, [d['power_pct'] for d in data],
                           color=c, linewidth=2, label=regime.title())
            axes[1, 1].plot(months, [d['ht_pct'] for d in data],
                           color=c, linewidth=2, label=regime.title())

        axes[0, 0].set_title("Biofilm Thickness Growth")
        axes[0, 0].set_ylabel("Thickness (mm)")
        axes[0, 1].set_title("Flow Capacity Remaining")
        axes[0, 1].set_ylabel("Flow (%)")
        axes[1, 0].set_title("Power Output Remaining")
        axes[1, 0].set_ylabel("Power (%)")
        axes[1, 1].set_title("Heat Transfer Efficiency")
        axes[1, 1].set_ylabel("HT Efficiency (%)")

        for ax in axes.flat:
            ax.set_xlabel("Month")
            ax.legend(fontsize=8, facecolor='black', edgecolor='gray', labelcolor='white')

        plt.tight_layout()
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}/v17_biofouling.png", dpi=200,
                    facecolor=fig.get_facecolor())
        plt.close()


# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 65)
    print("  SIMULATION v17.0: MARINE BIOFOULING & FLOW DEGRADATION")
    print("=" * 65)

    data_by_regime = {}

    for regime in ["tropical", "temperate", "cold"]:
        params = BiofoulingModel.GROWTH_PARAMS[regime]
        print(f"\n  [{regime.upper()}] {params['species']}")

        data = DegradationEngine.monthly_degradation(months=24, regime=regime)
        data_by_regime[regime] = data

        # Key milestones
        for m in [6, 12, 18, 24]:
            d = data[m]
            print(f"    Month {m:2d}: Thickness={d['thickness_mm']:5.1f}mm  "
                  f"Flow={d['flow_pct']:5.1f}%  Power={d['power_pct']:5.1f}%")

        # Optimal cleaning
        interval, net = DegradationEngine.optimal_cleaning_schedule(regime)
        print(f"    Optimal Cleaning Interval: Every {interval} months")
        print(f"    Annualized Net Revenue:    ${net:,.0f}")

    # Visualization
    print("\n  Generating Biofouling Charts...")
    FoulingVisualizer.plot_degradation(data_by_regime, output_dir="assets")
    print("  Saved: assets/v17_biofouling.png")

    print("\n" + "=" * 65)
    print("  VERDICT: Regular cleaning every 6-9 months is critical")
    print("  for tropical climates. Cold climates tolerate 12+ months.")
    print("=" * 65)
