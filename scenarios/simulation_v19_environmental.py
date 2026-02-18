"""
Simulation v19.0: Environmental Impact Assessment (EIA)
=======================================================
Assesses the environmental footprint of the Hydra-Cool system:
thermal discharge effects on marine ecology, CO2 savings vs.
traditional cooling, and regulatory compliance.

Physics & Ecology:
  - Thermal plume modeling (Gaussian dispersion)
  - Marine species thermal tolerance thresholds
  - CO2 lifecycle comparison vs. conventional cooling
  - Regulatory compliance (EPA/EU thermal discharge limits)

Author: Obada Dallo
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


# ══════════════════════════════════════════════════════════
#  THERMAL PLUME MODEL
# ══════════════════════════════════════════════════════════

class ThermalPlumeModel:
    """
    Models the temperature rise in the receiving water body
    when warm discharge water is released from the system.

    Uses simplified Gaussian plume dispersion adapted for
    buoyant thermal discharge in coastal waters.
    """

    @staticmethod
    def plume_temperature(distance_m, discharge_temp_c, ambient_temp_c,
                          flow_rate_m3s, current_speed=0.3, depth=10):
        """
        Temperature rise at distance from discharge point.
        Based on Fischer et al. (1979) mixing zone model.

        delta_T(x) = delta_T_0 * (Q / (u * h * sqrt(2*pi*sigma_y*sigma_z))) * exp(...)

        Simplified to near-field dilution:
          S = 0.32 * (F^(1/3) * x^(2/3)) / Q   [Froude dilution]
        """
        delta_T_0 = discharge_temp_c - ambient_temp_c
        Q = flow_rate_m3s

        # Densimetric Froude number
        g_prime = 9.81 * 0.00025 * delta_T_0  # g * beta * delta_T
        if g_prime <= 0:
            g_prime = 0.001
        D_port = 1.0  # discharge port diameter (m)
        u_jet = Q / (np.pi * (D_port/2)**2)
        Fr = u_jet / np.sqrt(g_prime * D_port)

        # Near-field dilution (within 100m)
        if isinstance(distance_m, np.ndarray):
            dilution = np.where(distance_m < 1, 1.0,
                       0.32 * (Fr**(1/3)) * (distance_m**(2/3)) / np.sqrt(Q))
        else:
            distance_m = max(distance_m, 1.0)
            dilution = 0.32 * (Fr**(1/3)) * (distance_m**(2/3)) / np.sqrt(Q)

        dilution = np.maximum(dilution, 1.0)
        temp_rise = delta_T_0 / dilution

        return ambient_temp_c + temp_rise, temp_rise

    @staticmethod
    def mixing_zone_radius(discharge_temp_c, ambient_temp_c, flow_rate_m3s,
                           threshold_rise=1.0):
        """
        Find distance where temperature rise drops below threshold.
        EPA typically allows 1-3 deg C rise outside mixing zone.
        """
        distances = np.linspace(1, 2000, 2000)
        for d in distances:
            _, rise = ThermalPlumeModel.plume_temperature(
                d, discharge_temp_c, ambient_temp_c, flow_rate_m3s
            )
            if rise <= threshold_rise:
                return round(d, 0)
        return 2000  # Beyond 2km


# ══════════════════════════════════════════════════════════
#  MARINE ECOLOGY IMPACT
# ══════════════════════════════════════════════════════════

class MarineEcologyAssessment:
    """
    Evaluates thermal impact on marine species.
    Temperature thresholds from peer-reviewed marine biology literature.
    """

    # Species thermal tolerance ranges (deg C)
    SPECIES = [
        {"name": "Coral Reefs",           "min": 18, "max": 30, "lethal": 32, "sensitivity": "HIGH"},
        {"name": "Seagrass (Posidonia)",   "min": 10, "max": 28, "lethal": 32, "sensitivity": "HIGH"},
        {"name": "Green Sea Turtle",       "min": 20, "max": 33, "lethal": 36, "sensitivity": "MEDIUM"},
        {"name": "Atlantic Cod",           "min": 0,  "max": 15, "lethal": 20, "sensitivity": "HIGH"},
        {"name": "Blue Mussel",            "min": 0,  "max": 25, "lethal": 30, "sensitivity": "LOW"},
        {"name": "Phytoplankton",          "min": -2, "max": 30, "lethal": 35, "sensitivity": "LOW"},
        {"name": "Zooplankton (Copepods)", "min": 0,  "max": 25, "lethal": 30, "sensitivity": "MEDIUM"},
        {"name": "Lobster (American)",     "min": 5,  "max": 22, "lethal": 25, "sensitivity": "HIGH"},
    ]

    @classmethod
    def assess_impact(cls, ambient_temp, temp_rise_at_boundary):
        """Assess impact on each species given temp rise at mixing zone boundary."""
        results = []
        max_temp = ambient_temp + temp_rise_at_boundary

        for sp in cls.SPECIES:
            if max_temp > sp['lethal']:
                impact = "LETHAL RISK"
                status = "CRITICAL"
            elif max_temp > sp['max']:
                impact = "Thermal stress (above comfort range)"
                status = "WARNING"
            elif max_temp > sp['max'] - 2:
                impact = "Near upper tolerance limit"
                status = "CAUTION"
            else:
                impact = "Within safe range"
                status = "SAFE"

            results.append({
                "species": sp['name'],
                "tolerance": f"{sp['min']}-{sp['max']}C",
                "lethal": f"{sp['lethal']}C",
                "sensitivity": sp['sensitivity'],
                "impact": impact,
                "status": status,
            })

        return results


# ══════════════════════════════════════════════════════════
#  CO2 LIFECYCLE COMPARISON
# ══════════════════════════════════════════════════════════

class CarbonFootprint:
    """Compares CO2 emissions: Hydra-Cool vs. traditional cooling."""

    @staticmethod
    def annual_comparison(cooling_load_mw=50):
        """
        Traditional cooling:
          - COP ~3.0 for mechanical chillers
          - Grid carbon intensity: 0.5 kg CO2/kWh (global average)

        Hydra-Cool:
          - Zero operational energy for cooling (thermosiphon)
          - Embodied carbon in construction only
          - Concrete: ~300 kg CO2/m^3
        """
        hours_per_year = 8760

        # Traditional system
        trad_electric_mw = cooling_load_mw / 3.0  # COP = 3
        trad_energy_mwh = trad_electric_mw * hours_per_year
        trad_co2_tonnes = trad_energy_mwh * 0.5  # tonnes/year

        # Water consumption (evaporative cooling)
        trad_water_m3 = cooling_load_mw * 2.5 * hours_per_year / 1000  # ~2.5 L/kWh

        # Hydra-Cool
        # Embodied carbon (one-time construction)
        concrete_volume = np.pi * (10**2 - 9.2**2) * 200  # hollow cylinder
        embodied_co2 = concrete_volume * 300 / 1000  # tonnes

        # Operational CO2 (near zero - only monitoring systems)
        hydra_annual_co2 = 50  # tonnes (monitoring, maintenance vehicles)

        # 20-year comparison
        years = np.arange(1, 21)
        trad_cumulative = trad_co2_tonnes * years
        hydra_cumulative = embodied_co2 + hydra_annual_co2 * years

        # Breakeven year (when Hydra-Cool total < traditional total)
        breakeven = None
        for y in years:
            if embodied_co2 + hydra_annual_co2 * y < trad_co2_tonnes * y:
                breakeven = y
                break

        return {
            "trad_annual_co2": round(trad_co2_tonnes),
            "trad_annual_water_m3": round(trad_water_m3),
            "hydra_embodied_co2": round(embodied_co2),
            "hydra_annual_co2": hydra_annual_co2,
            "co2_saving_20yr": round(trad_cumulative[-1] - hydra_cumulative[-1]),
            "breakeven_year": breakeven,
            "years": years,
            "trad_cumulative": trad_cumulative,
            "hydra_cumulative": hydra_cumulative,
        }


# ══════════════════════════════════════════════════════════
#  REGULATORY COMPLIANCE
# ══════════════════════════════════════════════════════════

class RegulatoryCompliance:
    """Checks against international thermal discharge regulations."""

    REGULATIONS = [
        {"name": "US EPA (Clean Water Act)", "max_rise_c": 1.0,
         "zone_m": 100, "note": "Mixing zone max 100m radius"},
        {"name": "EU Water Framework Directive", "max_rise_c": 1.5,
         "zone_m": 200, "note": "Good ecological status required"},
        {"name": "UAE Federal Law No. 24", "max_rise_c": 2.0,
         "zone_m": 500, "note": "Industrial discharge permit required"},
        {"name": "Singapore ENV Act", "max_rise_c": 1.0,
         "zone_m": 50, "note": "Strict tropical ecosystem protection"},
    ]

    @classmethod
    def check_compliance(cls, mixing_zone_m, temp_rise_at_boundary):
        results = []
        for reg in cls.REGULATIONS:
            compliant = (mixing_zone_m <= reg['zone_m'] and
                        temp_rise_at_boundary <= reg['max_rise_c'])
            results.append({
                "regulation": reg['name'],
                "max_rise": f"{reg['max_rise_c']}C",
                "max_zone": f"{reg['zone_m']}m",
                "actual_zone": f"{mixing_zone_m}m",
                "actual_rise": f"{temp_rise_at_boundary:.1f}C",
                "compliant": "PASS" if compliant else "FAIL",
                "note": reg['note'],
            })
        return results


# ══════════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════════

class EIAVisualizer:
    DARK_BG = '#0D1117'

    @classmethod
    def plot_assessment(cls, carbon_data, plume_data, output_dir="assets"):
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        fig.patch.set_facecolor(cls.DARK_BG)
        fig.suptitle("Environmental Impact Assessment (EIA)",
                     color='white', fontsize=16, fontweight='bold')

        for ax in axes:
            ax.set_facecolor(cls.DARK_BG)
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            for spine in ax.spines.values():
                spine.set_color('gray')
            ax.grid(True, alpha=0.15, color='white')

        # 1. CO2 Cumulative Comparison
        ax1 = axes[0]
        ax1.fill_between(carbon_data['years'], carbon_data['trad_cumulative'] / 1000,
                        alpha=0.3, color='#FF6B6B')
        ax1.plot(carbon_data['years'], carbon_data['trad_cumulative'] / 1000,
                color='#FF6B6B', linewidth=2, label='Traditional Cooling')
        ax1.fill_between(carbon_data['years'], carbon_data['hydra_cumulative'] / 1000,
                        alpha=0.3, color='#00FFCC')
        ax1.plot(carbon_data['years'], carbon_data['hydra_cumulative'] / 1000,
                color='#00FFCC', linewidth=2, label='Hydra-Cool')
        if carbon_data['breakeven_year']:
            ax1.axvline(x=carbon_data['breakeven_year'], color='yellow',
                       linestyle='--', alpha=0.7,
                       label=f"Carbon Breakeven (Year {carbon_data['breakeven_year']})")
        ax1.set_title("Cumulative CO2 Emissions")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("CO2 (thousand tonnes)")
        ax1.legend(fontsize=8, facecolor='black', edgecolor='gray', labelcolor='white')

        # 2. Thermal Plume Profile
        ax2 = axes[1]
        distances = np.linspace(1, 1000, 500)
        _, rises = ThermalPlumeModel.plume_temperature(
            distances, plume_data['discharge_temp'], plume_data['ambient_temp'],
            plume_data['flow_rate']
        )
        ax2.plot(distances, rises, color='#FF6B35', linewidth=2)
        ax2.axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='EPA Limit (1.0C)')
        ax2.axhline(y=2.0, color='yellow', linestyle='--', alpha=0.5, label='UAE Limit (2.0C)')
        ax2.set_title("Thermal Plume - Temperature Rise vs Distance")
        ax2.set_xlabel("Distance from Discharge (m)")
        ax2.set_ylabel("Temperature Rise (C)")
        ax2.legend(fontsize=8, facecolor='black', edgecolor='gray', labelcolor='white')

        plt.tight_layout()
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}/v19_eia.png", dpi=200,
                    facecolor=fig.get_facecolor())
        plt.close()


# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 65)
    print("  SIMULATION v19.0: ENVIRONMENTAL IMPACT ASSESSMENT (EIA)")
    print("=" * 65)

    discharge_temp = 45.0   # deg C (cooled from 50C by heat exchange)
    ambient_temp = 22.0     # deg C (Dubai SST)
    flow_rate = 15.0        # m^3/s

    # 1. Thermal Plume
    print("\n[1/4] Thermal Plume Analysis...")
    mixing_zone = ThermalPlumeModel.mixing_zone_radius(
        discharge_temp, ambient_temp, flow_rate, threshold_rise=1.0
    )
    _, rise_at_50m = ThermalPlumeModel.plume_temperature(
        50, discharge_temp, ambient_temp, flow_rate
    )
    _, rise_at_boundary = ThermalPlumeModel.plume_temperature(
        mixing_zone, discharge_temp, ambient_temp, flow_rate
    )
    print(f"      Discharge Temp:     {discharge_temp}C")
    print(f"      Ambient (Dubai):    {ambient_temp}C")
    print(f"      Rise at 50m:        {rise_at_50m:.1f}C")
    print(f"      Mixing Zone (1C):   {mixing_zone}m")

    # 2. Marine Ecology
    print("\n[2/4] Marine Ecology Assessment...")
    eco_results = MarineEcologyAssessment.assess_impact(ambient_temp, rise_at_50m)
    for e in eco_results:
        icon = "OK" if e['status'] == 'SAFE' else "!!" if e['status'] == 'CAUTION' else "XX"
        print(f"      [{icon}] {e['species']:<25} Tol: {e['tolerance']:<12} {e['status']}")

    # 3. CO2 Comparison
    print("\n[3/4] Carbon Footprint Lifecycle...")
    carbon = CarbonFootprint.annual_comparison(cooling_load_mw=50)
    print(f"      Traditional Annual CO2:  {carbon['trad_annual_co2']:,} tonnes")
    print(f"      Traditional Annual Water: {carbon['trad_annual_water_m3']:,} m^3")
    print(f"      Hydra-Cool Embodied CO2: {carbon['hydra_embodied_co2']:,} tonnes")
    print(f"      Hydra-Cool Annual CO2:   {carbon['hydra_annual_co2']} tonnes")
    print(f"      20-Year CO2 Savings:     {carbon['co2_saving_20yr']:,} tonnes")
    print(f"      Carbon Breakeven Year:   {carbon['breakeven_year']}")

    # 4. Regulatory Compliance
    print("\n[4/4] Regulatory Compliance Check...")
    compliance = RegulatoryCompliance.check_compliance(mixing_zone, rise_at_boundary)
    for c in compliance:
        icon = "OK" if c['compliant'] == 'PASS' else "XX"
        print(f"      [{icon}] {c['regulation']:<35} Zone: {c['actual_zone']:<8} "
              f"Rise: {c['actual_rise']:<6} {c['compliant']}")

    # Visualization
    print("\n  Generating EIA Charts...")
    plume_data = {"discharge_temp": discharge_temp, "ambient_temp": ambient_temp,
                  "flow_rate": flow_rate}
    EIAVisualizer.plot_assessment(carbon, plume_data, output_dir="assets")
    print("  Saved: assets/v19_eia.png")

    # Verdict
    print("\n" + "=" * 65)
    passed = sum(1 for c in compliance if c['compliant'] == 'PASS')
    print(f"  REGULATORY: {passed}/{len(compliance)} jurisdictions PASS")
    print(f"  CO2 SAVINGS: {carbon['co2_saving_20yr']:,} tonnes over 20 years")
    print(f"  WATER SAVED: {carbon['trad_annual_water_m3'] * 20:,.0f} m^3 freshwater (20yr)")
    print("=" * 65)
