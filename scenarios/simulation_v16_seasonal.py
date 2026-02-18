"""
Simulation v16.0: Seasonal Thermal Variation (12-Month Ocean Profiles)
======================================================================
Models the thermosiphon system performance across all 12 months
using real ocean temperature profiles for each deployment city.

Physics:
  - Monthly sea surface temperature (SST) from NOAA climatology
  - Deep-water temperature stability (bathymetric thermal inertia)
  - Seasonal flow rate and power output variation
  - Revenue impact: monthly profit/loss accounting

Author: Obada Dallo
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


# ══════════════════════════════════════════════════════════
#  OCEAN TEMPERATURE DATABASE (NOAA Climatology)
# ══════════════════════════════════════════════════════════

# Monthly mean SST (deg C) - sourced from NOAA OISST v2.1
# Deep water temperature (400m) is nearly constant year-round
OCEAN_DATA = {
    "Dubai": {
        "sst": [22.1, 21.5, 22.8, 25.6, 29.3, 32.1, 34.0, 34.5, 33.2, 30.5, 27.0, 23.8],
        "deep_temp": 5.2,  # Persian Gulf is shallow; approximation for Arabian Sea intake
        "latitude": 25.2,
        "data_center_load_mw": 50,
    },
    "Helsinki": {
        "sst": [1.0, 0.5, 0.8, 3.5, 8.2, 14.0, 17.5, 18.2, 14.8, 9.5, 5.0, 2.5],
        "deep_temp": 3.8,  # Baltic Sea ~100m (shallower)
        "latitude": 60.2,
        "data_center_load_mw": 30,
    },
    "Los Angeles": {
        "sst": [14.5, 14.0, 14.2, 15.0, 16.2, 17.8, 19.5, 20.2, 19.8, 18.0, 16.0, 14.8],
        "deep_temp": 4.5,  # Pacific Ocean 400m
        "latitude": 33.9,
        "data_center_load_mw": 45,
    },
    "Singapore": {
        "sst": [27.5, 28.0, 29.2, 30.0, 30.5, 30.2, 29.8, 29.5, 29.2, 28.8, 28.2, 27.8],
        "deep_temp": 5.0,  # South China Sea / Indian Ocean
        "latitude": 1.35,
        "data_center_load_mw": 60,
    },
    "Reykjavik": {
        "sst": [5.5, 4.8, 4.5, 5.0, 6.8, 9.0, 10.5, 10.8, 9.5, 7.5, 6.2, 5.8],
        "deep_temp": 2.5,  # North Atlantic deep
        "latitude": 64.1,
        "data_center_load_mw": 20,
    },
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ══════════════════════════════════════════════════════════
#  SEASONAL PHYSICS ENGINE
# ══════════════════════════════════════════════════════════

class SeasonalEngine:
    """Computes monthly thermosiphon performance."""

    # System geometry
    PIPE_HEIGHT = 200       # m
    PIPE_DIAMETER = 2.0     # m
    NUM_PIPES = 6
    FRICTION_FACTOR = 0.018
    TURBINE_EFF = 0.82
    ELECTRICITY_PRICE = 0.065  # $/kWh

    @classmethod
    def seawater_density(cls, temp_c):
        """UNESCO equation simplified for 35ppt salinity."""
        return 1028.1 - 0.0735 * temp_c - 0.00469 * temp_c**2

    @classmethod
    def monthly_performance(cls, sst_c, deep_temp_c, dc_load_mw):
        """
        Calculate flow rate, cooling capacity, and power for one month.

        The thermosiphon is driven by:
          delta_P = (rho_cold - rho_hot) * g * H

        The heated water temperature is:
          T_hot = T_sst + delta_T_from_datacenter

        On hot months the delta_T is LARGER (more cooling needed),
        which actually helps the thermosiphon drive.
        """
        g = 9.81

        # The data center heats the seawater by ~30C above SST
        t_hot = sst_c + 30.0
        t_cold = deep_temp_c

        rho_cold = cls.seawater_density(t_cold)
        rho_hot = cls.seawater_density(t_hot)
        delta_rho = rho_cold - rho_hot

        if delta_rho <= 0:
            return {"flow_m3s": 0, "cooling_mw": 0, "power_kw": 0,
                    "revenue_usd": 0, "delta_t": 0, "efficiency": 0}

        # Buoyancy pressure
        delta_P = delta_rho * g * cls.PIPE_HEIGHT

        # Flow velocity (Darcy-Weisbach balance)
        A_pipe = np.pi * (cls.PIPE_DIAMETER / 2)**2
        # v = sqrt(2 * delta_P / (f * H/D * rho_avg + rho_avg))
        rho_avg = (rho_cold + rho_hot) / 2
        friction_head = cls.FRICTION_FACTOR * cls.PIPE_HEIGHT / cls.PIPE_DIAMETER
        v = np.sqrt(2 * delta_P / (rho_avg * (friction_head + 1)))
        v = min(v, 4.0)  # Cap at realistic 4 m/s

        # Total flow
        Q = v * A_pipe * cls.NUM_PIPES  # m^3/s

        # Cooling capacity: Q_cooling = rho * Cp * Q * delta_T
        cp = 4000  # J/(kg.K) seawater
        delta_T = t_hot - t_cold
        cooling_mw = rho_avg * cp * Q * delta_T / 1e6

        # Power generation from turbine
        power_kw = cls.TURBINE_EFF * rho_avg * g * Q * cls.PIPE_HEIGHT / 1000

        # Monthly revenue (730 hours/month)
        revenue = power_kw * 730 * cls.ELECTRICITY_PRICE

        # COP equivalent (cooling per unit electricity)
        efficiency = cooling_mw / max(power_kw / 1000, 0.01)

        return {
            "flow_m3s": round(Q, 2),
            "cooling_mw": round(cooling_mw, 1),
            "power_kw": round(power_kw, 1),
            "revenue_usd": round(revenue),
            "delta_t": round(delta_T, 1),
            "efficiency": round(efficiency, 1),
        }

    @classmethod
    def annual_simulation(cls, city_name):
        """Run 12-month simulation for a city."""
        city = OCEAN_DATA[city_name]
        monthly = []

        for i, sst in enumerate(city['sst']):
            perf = cls.monthly_performance(sst, city['deep_temp'], city['data_center_load_mw'])
            perf['month'] = MONTHS[i]
            perf['sst'] = sst
            monthly.append(perf)

        # Annual totals
        annual_revenue = sum(m['revenue_usd'] for m in monthly)
        avg_cooling = np.mean([m['cooling_mw'] for m in monthly])
        avg_power = np.mean([m['power_kw'] for m in monthly])
        min_cooling = min(m['cooling_mw'] for m in monthly)

        return {
            "city": city_name,
            "monthly": monthly,
            "annual_revenue": annual_revenue,
            "avg_cooling_mw": round(avg_cooling, 1),
            "avg_power_kw": round(avg_power, 1),
            "min_cooling_mw": round(min_cooling, 1),
            "worst_month": monthly[np.argmin([m['cooling_mw'] for m in monthly])]['month'],
        }


# ══════════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════════

class SeasonalVisualizer:
    DARK_BG = '#0D1117'
    CITY_COLORS = {
        "Dubai": "#FF6B35",
        "Helsinki": "#00BFFF",
        "Los Angeles": "#FFD700",
        "Singapore": "#FF1493",
        "Reykjavik": "#00FFCC",
    }

    @classmethod
    def plot_all_cities(cls, results, output_dir="assets"):
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.patch.set_facecolor(cls.DARK_BG)
        fig.suptitle("Seasonal Performance Analysis - 5 Global Sites",
                     color='white', fontsize=16, fontweight='bold')

        for ax in axes.flat:
            ax.set_facecolor(cls.DARK_BG)
            ax.tick_params(colors='white', labelsize=8)
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            for spine in ax.spines.values():
                spine.set_color('gray')
            ax.grid(True, alpha=0.15, color='white')

        # 1. SST Profiles
        ax1 = axes[0, 0]
        for r in results:
            c = r['city']
            sst = [m['sst'] for m in r['monthly']]
            ax1.plot(MONTHS, sst, color=cls.CITY_COLORS[c], linewidth=2,
                     marker='o', markersize=4, label=c)
        ax1.set_title("Sea Surface Temperature (SST)")
        ax1.set_ylabel("Temperature (C)")
        ax1.legend(fontsize=7, facecolor='black', edgecolor='gray', labelcolor='white')

        # 2. Monthly Cooling Capacity
        ax2 = axes[0, 1]
        for r in results:
            c = r['city']
            cool = [m['cooling_mw'] for m in r['monthly']]
            ax2.plot(MONTHS, cool, color=cls.CITY_COLORS[c], linewidth=2,
                     marker='s', markersize=4, label=c)
        ax2.set_title("Cooling Capacity (MW)")
        ax2.set_ylabel("MW thermal")
        ax2.legend(fontsize=7, facecolor='black', edgecolor='gray', labelcolor='white')

        # 3. Monthly Power Generation
        ax3 = axes[1, 0]
        for r in results:
            c = r['city']
            pwr = [m['power_kw'] for m in r['monthly']]
            ax3.plot(MONTHS, pwr, color=cls.CITY_COLORS[c], linewidth=2,
                     marker='^', markersize=4, label=c)
        ax3.set_title("Power Generation (kW)")
        ax3.set_ylabel("kW electric")
        ax3.legend(fontsize=7, facecolor='black', edgecolor='gray', labelcolor='white')

        # 4. Annual Revenue Comparison
        ax4 = axes[1, 1]
        cities = [r['city'] for r in results]
        revenues = [r['annual_revenue'] / 1e6 for r in results]
        bars = ax4.bar(cities, revenues,
                       color=[cls.CITY_COLORS[c] for c in cities], alpha=0.85)
        ax4.set_title("Annual Revenue ($M)")
        ax4.set_ylabel("$ Million")
        for bar, val in zip(bars, revenues):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                     f"${val:.1f}M", ha='center', color='white', fontsize=9)

        plt.tight_layout()
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}/v16_seasonal_analysis.png", dpi=200,
                    facecolor=fig.get_facecolor())
        plt.close()


# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 65)
    print("  SIMULATION v16.0: SEASONAL THERMAL VARIATION")
    print("  (12-Month Ocean Temperature Profiles)")
    print("=" * 65)

    results = []
    for city in OCEAN_DATA:
        print(f"\n  [{city}]")
        r = SeasonalEngine.annual_simulation(city)
        results.append(r)

        print(f"    Avg Cooling:  {r['avg_cooling_mw']} MW")
        print(f"    Avg Power:    {r['avg_power_kw']} kW")
        print(f"    Min Cooling:  {r['min_cooling_mw']} MW (worst: {r['worst_month']})")
        print(f"    Annual Rev:   ${r['annual_revenue']:,}")

    print("\n  Generating Seasonal Charts...")
    SeasonalVisualizer.plot_all_cities(results, output_dir="assets")
    print("  Saved: assets/v16_seasonal_analysis.png")

    # Summary table
    print("\n" + "=" * 65)
    print(f"  {'City':<14} {'Avg Cool MW':<14} {'Avg Pwr kW':<14} {'Annual Rev':>14}")
    print("-" * 65)
    total_rev = 0
    for r in results:
        print(f"  {r['city']:<14} {r['avg_cooling_mw']:<14} {r['avg_power_kw']:<14} "
              f"${r['annual_revenue']:>12,}")
        total_rev += r['annual_revenue']
    print("-" * 65)
    print(f"  {'TOTAL':<14} {'':<14} {'':<14} ${total_rev:>12,}")
    print("=" * 65)
