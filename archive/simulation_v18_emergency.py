"""
Simulation v18.0: Emergency Shutdown & Transient Analysis
==========================================================
Simulates what happens during rapid system shutdown:
thermal shock, pressure transients, and water hammer cascades.

Physics:
  - Valve closure transient (Joukowsky water hammer)
  - Thermal shock on pipe walls (Fourier heat conduction)
  - Pressure wave propagation and reflection
  - Emergency drain-down time and flooding risk

Author: Obada Dallo
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


# ══════════════════════════════════════════════════════════
#  SYSTEM PARAMETERS
# ══════════════════════════════════════════════════════════

class SystemConfig:
    PIPE_LENGTH = 400          # m (deep sea intake)
    PIPE_DIAMETER = 2.0        # m
    WALL_THICKNESS = 0.025     # m (steel pipe wall)
    SOUND_SPEED_WATER = 1480   # m/s
    SOUND_SPEED_STEEL = 5100   # m/s
    WATER_DENSITY = 1025       # kg/m^3
    WATER_BULK_MODULUS = 2.2e9 # Pa
    STEEL_YOUNGS = 200e9       # Pa
    PIPE_ROUGHNESS = 0.045e-3  # m
    INITIAL_VELOCITY = 2.5     # m/s (steady state)
    WATER_TEMP_HOT = 50        # deg C
    WATER_TEMP_COLD = 5        # deg C
    STEEL_THERMAL_DIFF = 1.2e-5  # m^2/s (thermal diffusivity)
    PIPE_YIELD_STRESS = 250e6  # Pa (carbon steel)
    GRAVITY = 9.81


# ══════════════════════════════════════════════════════════
#  WATER HAMMER ENGINE
# ══════════════════════════════════════════════════════════

class WaterHammerEngine:
    """Models pressure transients during valve closure."""

    @staticmethod
    def effective_wave_speed():
        """
        Wave speed in elastic pipe (Korteweg formula):
        a = sqrt(K/rho / (1 + (K*D)/(E*e)))
        """
        S = SystemConfig
        K = S.WATER_BULK_MODULUS
        rho = S.WATER_DENSITY
        D = S.PIPE_DIAMETER
        E = S.STEEL_YOUNGS
        e = S.WALL_THICKNESS

        a = np.sqrt((K / rho) / (1 + (K * D) / (E * e)))
        return a

    @staticmethod
    def joukowsky_surge(closure_time_s=0.5):
        """
        Joukowsky equation: delta_P = rho * a * delta_V
        For rapid closure (tc < 2L/a), full hammer develops.
        For slow closure, pressure is reduced proportionally.
        """
        S = SystemConfig
        a = WaterHammerEngine.effective_wave_speed()

        # Critical time (wave round trip)
        t_critical = 2 * S.PIPE_LENGTH / a

        if closure_time_s < t_critical:
            # Instantaneous closure (worst case)
            delta_P = S.WATER_DENSITY * a * S.INITIAL_VELOCITY
            scenario = "INSTANTANEOUS"
        else:
            # Slow closure (pressure reduced)
            delta_P = S.WATER_DENSITY * a * S.INITIAL_VELOCITY * (t_critical / closure_time_s)
            scenario = "GRADUAL"

        return {
            "wave_speed_m_s": round(a, 1),
            "critical_time_s": round(t_critical, 3),
            "closure_time_s": closure_time_s,
            "scenario": scenario,
            "delta_P_Pa": delta_P,
            "delta_P_MPa": round(delta_P / 1e6, 2),
            "delta_P_bar": round(delta_P / 1e5, 1),
        }

    @staticmethod
    def pressure_wave_timeline(duration_s=5.0, dt=0.001):
        """
        Simulate pressure wave propagation and reflection.
        Returns time series of pressure at the valve.
        """
        S = SystemConfig
        a = WaterHammerEngine.effective_wave_speed()
        t_round = 2 * S.PIPE_LENGTH / a  # Round-trip time

        # Joukowsky peak
        peak = S.WATER_DENSITY * a * S.INITIAL_VELOCITY

        # Damping coefficient (friction-based)
        f = 0.02  # Darcy friction factor
        damping = f * S.INITIAL_VELOCITY / (2 * S.PIPE_DIAMETER)

        t = np.arange(0, duration_s, dt)
        pressure = np.zeros_like(t)

        for i, ti in enumerate(t):
            # Number of reflections
            n_reflections = int(ti / t_round)
            phase = (ti % t_round) / t_round

            # Alternating positive/negative pressure waves
            sign = 1 if n_reflections % 2 == 0 else -1
            # Exponential damping with each reflection
            amplitude = peak * np.exp(-damping * ti)
            # Square wave approximation with smoothing
            pressure[i] = sign * amplitude * (1 if phase < 0.5 else -1)

        # Add static pressure (hydrostatic head)
        static_P = S.WATER_DENSITY * S.GRAVITY * S.PIPE_LENGTH
        pressure += static_P

        return t, pressure, static_P


# ══════════════════════════════════════════════════════════
#  THERMAL SHOCK ENGINE
# ══════════════════════════════════════════════════════════

class ThermalShockEngine:
    """Models thermal shock when hot water suddenly contacts cold pipe."""

    @staticmethod
    def thermal_stress(delta_T, alpha=12e-6, E=200e9, nu=0.3):
        """
        Thermal stress in constrained pipe wall:
        sigma = alpha * E * delta_T / (1 - nu)
        """
        stress = alpha * E * delta_T / (1 - nu)
        return stress

    @staticmethod
    def shutdown_scenarios():
        """
        Three shutdown scenarios:
        1. Normal: Gradual cooldown over 30 min
        2. Emergency: Rapid valve closure in 2s
        3. Catastrophic: Instantaneous failure
        """
        S = SystemConfig
        delta_T = S.WATER_TEMP_HOT - S.WATER_TEMP_COLD  # 45 deg C

        scenarios = []

        # Normal shutdown (gradual)
        normal_dT = delta_T * 0.1  # Only 10% thermal shock
        normal_stress = ThermalShockEngine.thermal_stress(normal_dT)
        scenarios.append({
            "name": "Normal Shutdown (30 min cooldown)",
            "delta_T": normal_dT,
            "thermal_stress_MPa": round(normal_stress / 1e6, 1),
            "closure_time": 1800,
            "risk_level": "LOW",
        })

        # Emergency shutdown (2s valve closure)
        emergency_dT = delta_T * 0.6
        emergency_stress = ThermalShockEngine.thermal_stress(emergency_dT)
        scenarios.append({
            "name": "Emergency Shutdown (2s valve close)",
            "delta_T": emergency_dT,
            "thermal_stress_MPa": round(emergency_stress / 1e6, 1),
            "closure_time": 2,
            "risk_level": "MEDIUM",
        })

        # Catastrophic (instant)
        catastrophic_stress = ThermalShockEngine.thermal_stress(delta_T)
        scenarios.append({
            "name": "Catastrophic Failure (instant)",
            "delta_T": delta_T,
            "thermal_stress_MPa": round(catastrophic_stress / 1e6, 1),
            "closure_time": 0.1,
            "risk_level": "CRITICAL",
        })

        # Add water hammer for each
        for s in scenarios:
            wh = WaterHammerEngine.joukowsky_surge(s['closure_time'])
            s['water_hammer_MPa'] = wh['delta_P_MPa']
            combined = s['thermal_stress_MPa'] + s['water_hammer_MPa']
            s['combined_stress_MPa'] = round(combined, 1)
            s['safety_factor'] = round(S.PIPE_YIELD_STRESS / 1e6 / combined, 2)

        return scenarios

    @staticmethod
    def drain_down_time():
        """Time to drain the full pipe system under gravity."""
        S = SystemConfig
        A = np.pi * (S.PIPE_DIAMETER / 2)**2
        volume = A * S.PIPE_LENGTH  # m^3
        # Torricelli's theorem for drain rate
        v_drain = np.sqrt(2 * S.GRAVITY * S.PIPE_LENGTH * 0.5)
        drain_rate = A * v_drain * 0.6  # 0.6 discharge coefficient
        t_drain = volume / drain_rate
        return round(t_drain, 1), round(volume, 1)


# ══════════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════════

class TransientVisualizer:
    DARK_BG = '#0D1117'

    @classmethod
    def plot_transients(cls, output_dir="assets"):
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        fig.patch.set_facecolor(cls.DARK_BG)
        fig.suptitle("Emergency Shutdown - Pressure Transient Analysis",
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

        # 1. Water hammer pressure wave
        t, pressure, static_P = WaterHammerEngine.pressure_wave_timeline(duration_s=3.0)
        ax1 = axes[0]
        ax1.plot(t, pressure / 1e6, color='#FF6B6B', linewidth=1.5, alpha=0.9)
        ax1.axhline(y=static_P / 1e6, color='gray', linestyle='--', alpha=0.5,
                    label='Static Pressure')
        ax1.axhline(y=SystemConfig.PIPE_YIELD_STRESS / 1e6, color='red',
                    linestyle='--', label='Yield Stress (250 MPa)')
        ax1.set_title("Pressure Wave at Valve (Instantaneous Closure)")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Pressure (MPa)")
        ax1.legend(fontsize=8, facecolor='black', edgecolor='gray', labelcolor='white')

        # 2. Closure time vs peak pressure
        ax2 = axes[1]
        closure_times = np.logspace(-1, 2, 50)  # 0.1s to 100s
        peak_pressures = []
        for tc in closure_times:
            wh = WaterHammerEngine.joukowsky_surge(tc)
            peak_pressures.append(wh['delta_P_MPa'])

        ax2.semilogx(closure_times, peak_pressures, color='#00BFFF', linewidth=2)
        a = WaterHammerEngine.effective_wave_speed()
        t_crit = 2 * SystemConfig.PIPE_LENGTH / a
        ax2.axvline(x=t_crit, color='yellow', linestyle='--', alpha=0.7,
                    label=f'Critical Time ({t_crit:.2f}s)')
        ax2.scatter([0.5, 2.0, 30.0], [
            WaterHammerEngine.joukowsky_surge(0.5)['delta_P_MPa'],
            WaterHammerEngine.joukowsky_surge(2.0)['delta_P_MPa'],
            WaterHammerEngine.joukowsky_surge(30.0)['delta_P_MPa'],
        ], color=['red', 'yellow', 'green'], s=100, zorder=5)
        ax2.set_title("Peak Pressure vs Valve Closure Time")
        ax2.set_xlabel("Closure Time (s)")
        ax2.set_ylabel("Peak Surge (MPa)")
        ax2.legend(fontsize=8, facecolor='black', edgecolor='gray', labelcolor='white')

        plt.tight_layout()
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}/v18_transient.png", dpi=200,
                    facecolor=fig.get_facecolor())
        plt.close()


# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 65)
    print("  SIMULATION v18.0: EMERGENCY SHUTDOWN & TRANSIENT ANALYSIS")
    print("=" * 65)

    # Wave speed
    a = WaterHammerEngine.effective_wave_speed()
    print(f"\n  Effective Wave Speed: {a:.1f} m/s")
    print(f"  Critical Time (2L/a): {2 * SystemConfig.PIPE_LENGTH / a:.3f} s")

    # Shutdown scenarios
    print("\n  Shutdown Scenarios:")
    print(f"  {'Scenario':<38} {'Thermal':>10} {'Hammer':>10} {'Combined':>10} {'SF':>8}")
    print("  " + "-" * 76)

    scenarios = ThermalShockEngine.shutdown_scenarios()
    for s in scenarios:
        icon = "OK" if s['safety_factor'] > 1.5 else "!!" if s['safety_factor'] > 1.0 else "XX"
        print(f"  [{icon}] {s['name']:<34} {s['thermal_stress_MPa']:>8.1f} MPa "
              f"{s['water_hammer_MPa']:>7.1f} MPa {s['combined_stress_MPa']:>8.1f} MPa "
              f"{s['safety_factor']:>6.2f}")

    # Drain-down
    t_drain, volume = ThermalShockEngine.drain_down_time()
    print(f"\n  System Volume:     {volume:,.1f} m^3 ({volume * 1000:.0f} liters)")
    print(f"  Drain-Down Time:   {t_drain:.1f} seconds ({t_drain/60:.1f} min)")

    # Visualization
    print("\n  Generating Transient Charts...")
    TransientVisualizer.plot_transients(output_dir="assets")
    print("  Saved: assets/v18_transient.png")

    # Safety protocol
    print("\n" + "=" * 65)
    print("  EMERGENCY PROTOCOL RECOMMENDATIONS")
    print("=" * 65)
    print("  1. Minimum valve closure time: 10 seconds (pneumatic actuator)")
    print("  2. Install pressure relief valves at pipe junctions")
    print("  3. Surge tank capacity: minimum 50 m^3")
    print("  4. Thermal gradient monitoring: max 5 C/min cooldown rate")
    print("  5. Emergency drain valves: gravity-fed, fail-open design")
    print("=" * 65)
