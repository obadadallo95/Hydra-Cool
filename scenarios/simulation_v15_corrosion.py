"""
Simulation v15.0: Corrosion & Material Degradation (20-Year Lifecycle)
=====================================================================
Models the progressive degradation of marine concrete and steel
components in a seawater thermosiphon system over a 20-year period.

Physics:
  - Chloride ion diffusion (Fick's 2nd Law)
  - Reinforcement corrosion rate (Faraday's Law)
  - Wall thickness loss and remaining structural capacity
  - Cathodic protection sizing and maintenance schedule

Author: Obada Dallo
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


# ══════════════════════════════════════════════════════════
#  MATERIAL PROPERTIES
# ══════════════════════════════════════════════════════════

class MarineMaterial:
    """Properties of marine-grade reinforced concrete."""
    CONCRETE_COVER = 75e-3          # m  (75mm cover to rebar)
    CHLORIDE_THRESHOLD = 0.4        # % by weight of cement
    SURFACE_CHLORIDE = 5.0          # % (seawater exposure)
    DIFFUSION_COEFF = 2.0e-12       # m^2/s (marine concrete w/ silica fume)

    REBAR_DIAMETER = 32e-3          # m  (32mm rebar)
    STEEL_DENSITY = 7850            # kg/m^3
    FARADAY_CONST = 96485           # C/mol
    IRON_MOLAR_MASS = 55.845e-3     # kg/mol
    CORROSION_CURRENT = 1.0         # uA/cm^2 (active corrosion)

    WALL_INITIAL = 0.8              # m  (initial wall thickness)
    COMPRESSIVE_STRENGTH = 60e6     # Pa
    SAFETY_FACTOR_MIN = 1.5


# ══════════════════════════════════════════════════════════
#  CORROSION ENGINE
# ══════════════════════════════════════════════════════════

class CorrosionEngine:
    """Models chloride-induced reinforcement corrosion."""

    @staticmethod
    def chloride_penetration(depth_m, time_years):
        """
        Fick's 2nd Law of Diffusion:
        C(x,t) = C_s * (1 - erf(x / (2 * sqrt(D * t))))

        Returns chloride concentration at depth x after time t.
        """
        from scipy.special import erfc
        M = MarineMaterial
        t_seconds = time_years * 365.25 * 24 * 3600
        if t_seconds <= 0:
            return 0.0
        arg = depth_m / (2 * np.sqrt(M.DIFFUSION_COEFF * t_seconds))
        concentration = M.SURFACE_CHLORIDE * erfc(arg)
        return concentration

    @staticmethod
    def time_to_initiation():
        """
        Time for chloride to reach threshold at rebar depth.
        Solve: C_threshold = C_s * erfc(cover / (2*sqrt(D*t)))
        """
        from scipy.optimize import brentq
        M = MarineMaterial

        def equation(t_years):
            return CorrosionEngine.chloride_penetration(
                M.CONCRETE_COVER, t_years
            ) - M.CHLORIDE_THRESHOLD

        # Search between 1 and 200 years
        try:
            t_init = brentq(equation, 0.1, 200)
        except ValueError:
            t_init = 200  # Chloride never reaches threshold
        return t_init

    @staticmethod
    def corrosion_rate_mm_per_year(current_uA_cm2=1.0):
        """
        Faraday's Law: penetration rate
        x_rate = (M * i_corr) / (z * F * rho)
        where z=2 for Fe -> Fe2+
        """
        M_iron = 55.845e-3   # kg/mol
        F = 96485             # C/mol
        rho = 7850            # kg/m^3
        z = 2                 # valence
        i_corr = current_uA_cm2 * 1e-6 * 1e4  # A/m^2

        rate_m_per_s = (M_iron * i_corr) / (z * F * rho)
        rate_mm_per_year = rate_m_per_s * 1000 * 365.25 * 24 * 3600
        return rate_mm_per_year

    @staticmethod
    def lifecycle_analysis(years=20):
        """
        Full 20-year degradation analysis.
        Returns yearly data: chloride at rebar, section loss, capacity.
        """
        M = MarineMaterial
        t_init = CorrosionEngine.time_to_initiation()
        corr_rate = CorrosionEngine.corrosion_rate_mm_per_year(M.CORROSION_CURRENT)

        data = []
        for year in range(1, years + 1):
            cl_at_rebar = CorrosionEngine.chloride_penetration(M.CONCRETE_COVER, year)
            corrosion_active = year > t_init

            if corrosion_active:
                years_active = year - t_init
                section_loss_mm = corr_rate * years_active
                rebar_remaining = max(0, M.REBAR_DIAMETER * 1000 - 2 * section_loss_mm)
            else:
                section_loss_mm = 0
                rebar_remaining = M.REBAR_DIAMETER * 1000  # mm

            # Capacity ratio (simplified: proportional to rebar area)
            original_area = np.pi * (M.REBAR_DIAMETER * 1000 / 2)**2
            current_area = np.pi * (rebar_remaining / 2)**2
            capacity_ratio = current_area / original_area

            # Effective safety factor
            effective_sf = M.SAFETY_FACTOR_MIN * 2.81 * capacity_ratio  # Base SF = 2.81 from v14

            data.append({
                "year": year,
                "chloride_pct": round(cl_at_rebar, 3),
                "corrosion_active": corrosion_active,
                "section_loss_mm": round(section_loss_mm, 3),
                "rebar_remaining_mm": round(rebar_remaining, 2),
                "capacity_pct": round(capacity_ratio * 100, 1),
                "safety_factor": round(effective_sf, 2),
            })

        return data, t_init, corr_rate


# ══════════════════════════════════════════════════════════
#  CATHODIC PROTECTION SIZING
# ══════════════════════════════════════════════════════════

class CathodicProtection:
    """Impressed Current Cathodic Protection (ICCP) system sizing."""

    @staticmethod
    def size_system(surface_area_m2, current_density=20e-3):
        """
        Size ICCP system for submerged concrete structure.
        current_density: A/m^2 (typical 10-20 mA/m^2 for marine concrete)
        """
        total_current = surface_area_m2 * current_density  # Amps
        n_anodes = int(np.ceil(total_current / 5.0))  # 5A per anode typical
        power_kw = total_current * 12 / 1000  # 12V typical
        annual_energy_kwh = power_kw * 8760
        annual_cost = annual_energy_kwh * 0.08  # $0.08/kWh

        anode_cost = n_anodes * 2500  # $2500 per titanium anode
        install_cost = anode_cost * 1.5
        total_capex = anode_cost + install_cost

        return {
            "total_current_A": round(total_current, 1),
            "num_anodes": n_anodes,
            "power_kw": round(power_kw, 2),
            "annual_energy_kwh": round(annual_energy_kwh),
            "annual_opex_usd": round(annual_cost),
            "capex_usd": round(total_capex),
        }


# ══════════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════════

class CorrosionVisualizer:
    """Generates degradation timeline plots."""

    DARK_BG = '#0D1117'

    @classmethod
    def plot_lifecycle(cls, data, t_init, output_dir="assets"):
        years = [d['year'] for d in data]
        sf = [d['safety_factor'] for d in data]
        cap = [d['capacity_pct'] for d in data]
        cl = [d['chloride_pct'] for d in data]
        loss = [d['section_loss_mm'] for d in data]

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.patch.set_facecolor(cls.DARK_BG)
        fig.suptitle("Corrosion & Degradation - 20 Year Lifecycle",
                     color='white', fontsize=16, fontweight='bold')

        for ax in axes.flat:
            ax.set_facecolor(cls.DARK_BG)
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            for spine in ax.spines.values():
                spine.set_color('gray')
            ax.grid(True, alpha=0.15, color='white')

        # 1. Chloride Penetration
        ax1 = axes[0, 0]
        ax1.fill_between(years, cl, alpha=0.3, color='#FF6B6B')
        ax1.plot(years, cl, color='#FF6B6B', linewidth=2)
        ax1.axhline(y=MarineMaterial.CHLORIDE_THRESHOLD, color='red',
                    linestyle='--', linewidth=1, label=f'Threshold ({MarineMaterial.CHLORIDE_THRESHOLD}%)')
        ax1.axvline(x=t_init, color='yellow', linestyle=':', alpha=0.7,
                    label=f'Initiation ({t_init:.1f} yr)')
        ax1.set_title("Chloride at Rebar Depth")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Chloride (%)")
        ax1.legend(fontsize=8, facecolor='black', edgecolor='gray', labelcolor='white')

        # 2. Section Loss
        ax2 = axes[0, 1]
        ax2.fill_between(years, loss, alpha=0.3, color='#FFA500')
        ax2.plot(years, loss, color='#FFA500', linewidth=2)
        ax2.set_title("Rebar Section Loss")
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Loss (mm)")

        # 3. Structural Capacity
        ax3 = axes[1, 0]
        ax3.fill_between(years, cap, alpha=0.3, color='#00BFFF')
        ax3.plot(years, cap, color='#00BFFF', linewidth=2)
        ax3.axhline(y=70, color='yellow', linestyle='--', label='Repair Threshold (70%)')
        ax3.set_title("Structural Capacity Remaining")
        ax3.set_xlabel("Year")
        ax3.set_ylabel("Capacity (%)")
        ax3.set_ylim(0, 105)
        ax3.legend(fontsize=8, facecolor='black', edgecolor='gray', labelcolor='white')

        # 4. Safety Factor
        ax4 = axes[1, 1]
        colors_sf = ['#00FF00' if s > 1.5 else '#FFFF00' if s > 1.0 else '#FF0000' for s in sf]
        ax4.bar(years, sf, color=colors_sf, alpha=0.8)
        ax4.axhline(y=1.5, color='red', linestyle='--', linewidth=1.5, label='Min SF = 1.5')
        ax4.set_title("Effective Safety Factor")
        ax4.set_xlabel("Year")
        ax4.set_ylabel("Safety Factor")
        ax4.legend(fontsize=8, facecolor='black', edgecolor='gray', labelcolor='white')

        plt.tight_layout()
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}/v15_corrosion_lifecycle.png", dpi=200,
                    facecolor=fig.get_facecolor())
        plt.close()


# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  SIMULATION v15.0: CORROSION & MATERIAL DEGRADATION")
    print("=" * 60)

    # --- Lifecycle Analysis ---
    print("\n[1/3] Running 20-Year Degradation Model...")
    data, t_init, corr_rate = CorrosionEngine.lifecycle_analysis(years=20)

    print(f"      Chloride Initiation Time:  {t_init:.1f} years")
    print(f"      Corrosion Rate:            {corr_rate:.4f} mm/year")
    print(f"      Year 10 Capacity:          {data[9]['capacity_pct']}%")
    print(f"      Year 20 Capacity:          {data[19]['capacity_pct']}%")
    print(f"      Year 20 Safety Factor:     {data[19]['safety_factor']}")

    # --- Cathodic Protection ---
    print("\n[2/3] Sizing Cathodic Protection System...")
    tower_surface = np.pi * 20 * 200  # cylinder: pi * D * H
    cp = CathodicProtection.size_system(tower_surface)
    print(f"      Protected Area:    {tower_surface:.0f} m^2")
    print(f"      Total Current:     {cp['total_current_A']} A")
    print(f"      Number of Anodes:  {cp['num_anodes']}")
    print(f"      Power Required:    {cp['power_kw']} kW")
    print(f"      CAPEX:             ${cp['capex_usd']:,}")
    print(f"      Annual OPEX:       ${cp['annual_opex_usd']:,}/year")

    # --- Visualization ---
    print("\n[3/3] Generating Degradation Charts...")
    CorrosionVisualizer.plot_lifecycle(data, t_init, output_dir="assets")
    print("      Saved: assets/v15_corrosion_lifecycle.png")

    # --- Maintenance Schedule ---
    print("\n" + "=" * 60)
    print("  MAINTENANCE SCHEDULE")
    print("=" * 60)
    for d in data:
        if d['year'] % 5 == 0:
            status = "OK" if d['safety_factor'] > 1.5 else "REPAIR" if d['safety_factor'] > 1.0 else "CRITICAL"
            print(f"  Year {d['year']:2d}: Cl={d['chloride_pct']:.2f}%  "
                  f"Loss={d['section_loss_mm']:.2f}mm  "
                  f"Cap={d['capacity_pct']}%  "
                  f"SF={d['safety_factor']}  [{status}]")

    # --- Verdict ---
    final_sf = data[19]['safety_factor']
    print("\n" + "=" * 60)
    if final_sf > 1.5:
        print("  VERDICT: Structure safe for full 20-year design life")
        print("  WITH cathodic protection, no major repairs needed")
    elif final_sf > 1.0:
        print("  VERDICT: Repair needed before year 20")
        print("  RECOMMENDED: Concrete patch repair at year 15")
    else:
        print("  VERDICT: Structure requires major intervention")
        print("  RECOMMENDED: Full rebar replacement at year 12")
    print("=" * 60)
