"""
Simulation v14.0: Structural Stress Test (3D FEA Visualization)
================================================================
Visualizes a 200m Cooling Tower and simulates structural failure
under Earthquake (Lateral) and Missile Strike (Point Load) scenarios
using simplified Finite Element Analysis.

Outputs:
  - assets/tower_normal.png       (Baseline geometry)
  - assets/tower_earthquake.png   (Seismic bending + Von Mises heatmap)
  - assets/tower_blast.png        (Localized punching shear failure)
  - Console safety report with retrofit suggestions

Author: Obada Dallo
Copyright (c) 2024. All Rights Reserved.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import os


# ══════════════════════════════════════════════════════════
#  TOWER GEOMETRY
# ══════════════════════════════════════════════════════════

class TowerGeometry:
    """Defines the physical properties of the hollow cylindrical tower."""

    HEIGHT = 200.0          # meters
    DIAMETER = 20.0         # meters
    RADIUS = DIAMETER / 2   # 10m
    WALL_THICKNESS = 0.8    # meters (reinforced marine concrete)
    INNER_RADIUS = RADIUS - WALL_THICKNESS

    # Material Properties (High-Grade Marine Concrete)
    COMPRESSIVE_STRENGTH = 60e6   # Pa (60 MPa)
    YOUNGS_MODULUS = 35e9         # Pa (35 GPa)
    DENSITY = 2500                # kg/m3
    POISSON_RATIO = 0.2

    # Derived Cross-Section Properties
    AREA = np.pi * (RADIUS**2 - INNER_RADIUS**2)
    I_MOMENT = (np.pi / 4) * (RADIUS**4 - INNER_RADIUS**4)  # 2nd moment of area
    WEIGHT = AREA * HEIGHT * DENSITY * 9.81  # Total weight (N)

    @classmethod
    def generate_mesh(cls, n_theta=40, n_z=60):
        """Generate cylindrical mesh points for 3D visualization."""
        theta = np.linspace(0, 2 * np.pi, n_theta)
        z = np.linspace(0, cls.HEIGHT, n_z)
        THETA, Z = np.meshgrid(theta, z)
        X = cls.RADIUS * np.cos(THETA)
        Y = cls.RADIUS * np.sin(THETA)
        return X, Y, Z, THETA


# ══════════════════════════════════════════════════════════
#  FEA STRESS ENGINE
# ══════════════════════════════════════════════════════════

class StressEngine:
    """Simplified FEA calculations for structural analysis."""

    @staticmethod
    def seismic_analysis(magnitude=9.0):
        """
        Earthquake lateral load analysis (Equivalent Static Method).
        Applies a distributed horizontal force based on seismic magnitude.
        Returns bending stress, deflection, and safety factor.
        """
        T = TowerGeometry
        g = 9.81

        # Seismic coefficient (simplified from IBC / Eurocode 8)
        # PGA for M9.0 ~ 0.6g (extreme zone)
        pga = 0.1 * magnitude * 0.067  # Approx peak ground acceleration
        seismic_coeff = 2.5 * pga       # Spectral acceleration

        # Total base shear: V = Cs * W
        total_weight = T.WEIGHT
        base_shear = seismic_coeff * total_weight

        # Distributed load (triangular: increases with height)
        # w(z) = w_max * (z / H)
        w_max = 2 * base_shear / T.HEIGHT   # Peak at top

        # Maximum bending moment at base: M = w_max * H^2 / 3
        max_moment = w_max * T.HEIGHT**2 / 3

        # Bending stress at base: sigma = M * c / I
        max_stress = max_moment * T.RADIUS / T.I_MOMENT

        # Tip deflection (cantilever with triangular load):
        # delta = w_max * H^4 / (30 * E * I)
        tip_deflection = w_max * T.HEIGHT**4 / (30 * T.YOUNGS_MODULUS * T.I_MOMENT)

        # Safety factor
        safety_factor = T.COMPRESSIVE_STRENGTH / max_stress

        return {
            "base_shear_MN": base_shear / 1e6,
            "max_moment_MNm": max_moment / 1e6,
            "max_stress_MPa": max_stress / 1e6,
            "tip_deflection_m": tip_deflection,
            "safety_factor": round(safety_factor, 2),
            "w_max": w_max,
        }

    @staticmethod
    def blast_analysis(blast_force_MN=50.0, impact_height=100.0):
        """
        Missile strike / blast point load analysis.
        Calculates punching shear and local failure radius.
        """
        T = TowerGeometry
        F = blast_force_MN * 1e6  # Convert to Newtons

        # Punching shear on wall: tau = F / (perimeter * thickness)
        # Assume impact zone diameter ~ 5m
        impact_diameter = 5.0
        perimeter = np.pi * impact_diameter
        shear_stress = F / (perimeter * T.WALL_THICKNESS)

        # Local bending moment at impact: M = F * t / 4 (plate bending)
        local_moment = F * T.WALL_THICKNESS / 4
        local_bending_stress = 6 * local_moment / T.WALL_THICKNESS**2

        # Blast radius estimate (Hopkinson-Cranz scaling)
        # R_blast ~ k * W^(1/3), assuming equivalent TNT
        equivalent_tnt_kg = F / 1e6  # Simplified
        blast_radius = 0.8 * equivalent_tnt_kg**(1/3)

        # Combined stress (Von Mises approximation)
        von_mises = np.sqrt(local_bending_stress**2 + 3 * shear_stress**2)

        safety_factor = T.COMPRESSIVE_STRENGTH / von_mises

        return {
            "blast_force_MN": blast_force_MN,
            "impact_height_m": impact_height,
            "shear_stress_MPa": shear_stress / 1e6,
            "bending_stress_MPa": local_bending_stress / 1e6,
            "von_mises_MPa": von_mises / 1e6,
            "blast_radius_m": round(blast_radius, 1),
            "safety_factor": round(safety_factor, 2),
        }


# ══════════════════════════════════════════════════════════
#  3D VISUALIZATION ENGINE
# ══════════════════════════════════════════════════════════

class TowerVisualizer:
    """Generates publication-quality 3D tower visualizations."""

    DARK_BG = '#0D1117'

    @classmethod
    def _setup_axes(cls, fig, title):
        """Configure 3D axes with dark engineering theme."""
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor(cls.DARK_BG)
        fig.patch.set_facecolor(cls.DARK_BG)
        ax.set_xlabel('X (m)', color='white', fontsize=9)
        ax.set_ylabel('Y (m)', color='white', fontsize=9)
        ax.set_zlabel('Height (m)', color='white', fontsize=9)
        ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=15)
        ax.tick_params(colors='white', labelsize=7)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor('gray')
        ax.yaxis.pane.set_edgecolor('gray')
        ax.zaxis.pane.set_edgecolor('gray')
        ax.set_xlim(-15, 15)
        ax.set_ylim(-15, 15)
        ax.set_zlim(0, 220)
        ax.view_init(elev=15, azim=135)
        return ax

    @classmethod
    def plot_normal(cls, output_dir="assets"):
        """Plot 1: Baseline tower - standing straight."""
        X, Y, Z, _ = TowerGeometry.generate_mesh()
        fig = plt.figure(figsize=(10, 12))
        ax = cls._setup_axes(fig, "Cooling Tower - Baseline Geometry (200m)")

        # Draw wireframe with structural blue
        ax.plot_wireframe(X, Y, Z, color='#00BFFF', alpha=0.5, linewidth=0.4)

        # Ground plane
        ground = plt.Circle((0, 0), 12, color='gray', alpha=0.15)
        ax.add_patch(ground)
        from mpl_toolkits.mplot3d import art3d
        art3d.pathpatch_2d_to_3d(ground, z=0, zdir="z")

        # Annotations
        ax.text(12, 0, 100, "H = 200m", color='white', fontsize=9)
        ax.text(12, 0, 10, "D = 20m", color='white', fontsize=9)
        ax.text(12, 0, 50, f"Wall = {TowerGeometry.WALL_THICKNESS}m", color='#00FFCC', fontsize=9)

        plt.tight_layout()
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}/tower_normal.png", dpi=200, facecolor=fig.get_facecolor())
        plt.close()

    @classmethod
    def plot_earthquake(cls, seismic_data, output_dir="assets"):
        """Plot 2: Tower bending under seismic load with Von Mises heatmap."""
        T = TowerGeometry
        X, Y, Z, THETA = T.generate_mesh()

        # Apply lateral deflection (cantilever bending shape)
        # delta(z) = delta_max * (z/H)^2 * (3 - z/H) / 2
        z_ratio = Z / T.HEIGHT
        deflection_profile = seismic_data['tip_deflection_m'] * z_ratio**2 * (3 - z_ratio) / 2

        # Amplify for visualization (real deflection may be too small to see)
        visual_scale = max(1.0, 5.0 / max(abs(seismic_data['tip_deflection_m']), 0.01))
        X_deformed = X + deflection_profile * visual_scale

        # Von Mises stress distribution (simplified: linear from base)
        # sigma(z) = sigma_max * (1 - z/H)
        stress_distribution = seismic_data['max_stress_MPa'] * (1 - z_ratio)

        # Add circumferential variation (tension on one side, compression on other)
        stress_field = stress_distribution * (1 + 0.4 * np.cos(THETA))

        # Normalize for colormap
        stress_norm = stress_field / max(stress_field.max(), 1e-6)

        fig = plt.figure(figsize=(10, 12))
        title = f"Earthquake Scenario (M9.0) - Tip Deflection: {seismic_data['tip_deflection_m']:.2f}m"
        ax = cls._setup_axes(fig, title)

        # Draw deformed tower with stress heatmap
        colors = cm.jet(stress_norm)
        ax.plot_surface(X_deformed, Y, Z, facecolors=colors, alpha=0.75, linewidth=0.2, edgecolor='white', shade=False)

        # Draw original position as ghost
        ax.plot_wireframe(X, Y, Z, color='white', alpha=0.08, linewidth=0.2)

        # Stress colorbar
        mappable = cm.ScalarMappable(cmap='jet')
        mappable.set_array(stress_field)
        cbar = fig.colorbar(mappable, ax=ax, shrink=0.5, pad=0.1, aspect=20)
        cbar.set_label('Von Mises Stress (MPa)', color='white', fontsize=10)
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')

        # Safety annotation
        sf = seismic_data['safety_factor']
        sf_color = '#00FF00' if sf > 1.5 else '#FFFF00' if sf > 1.0 else '#FF0000'
        ax.text2D(0.05, 0.92, f"Safety Factor: {sf:.2f}", transform=ax.transAxes,
                  color=sf_color, fontsize=12, fontweight='bold',
                  bbox=dict(boxstyle='round', facecolor='black', alpha=0.8))
        ax.text2D(0.05, 0.87, f"Max Stress: {seismic_data['max_stress_MPa']:.1f} MPa",
                  transform=ax.transAxes, color='white', fontsize=10)

        plt.tight_layout()
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}/tower_earthquake.png", dpi=200, facecolor=fig.get_facecolor())
        plt.close()

    @classmethod
    def plot_blast(cls, blast_data, output_dir="assets"):
        """Plot 3: Tower with localized blast damage zone."""
        T = TowerGeometry
        X, Y, Z, THETA = T.generate_mesh(n_theta=50, n_z=80)

        impact_z = blast_data['impact_height_m']
        blast_r = blast_data['blast_radius_m']

        # Calculate distance from impact point for each mesh vertex
        # Impact at (R, 0, impact_z) - on the surface facing +X
        impact_x = T.RADIUS
        impact_y = 0
        dist_from_impact = np.sqrt(
            (X - impact_x)**2 + Y**2 + (Z - impact_z)**2
        )

        # Create damage mask: vertices within blast radius get deformed
        damage_zone = dist_from_impact < blast_r * 2
        damage_intensity = np.exp(-dist_from_impact**2 / (2 * blast_r**2))

        # Inward deformation at impact (crater/dent)
        radial_direction_x = np.cos(THETA)
        radial_direction_y = np.sin(THETA)

        deformation_depth = 3.0  # meters inward
        X_damaged = X - radial_direction_x * damage_intensity * deformation_depth
        Y_damaged = Y - radial_direction_y * damage_intensity * deformation_depth

        # Stress field around impact (inverse square decay)
        stress_field = blast_data['von_mises_MPa'] * np.exp(-dist_from_impact / blast_r)
        stress_norm = stress_field / max(stress_field.max(), 1e-6)

        fig = plt.figure(figsize=(10, 12))
        title = f"Missile Strike at {impact_z:.0f}m - Blast Radius: {blast_r}m"
        ax = cls._setup_axes(fig, title)

        # Draw damaged tower with stress heatmap
        colors = cm.hot(stress_norm)
        # Make undamaged areas semi-transparent
        colors[..., 3] = np.where(damage_intensity > 0.05, 0.85, 0.4)

        ax.plot_surface(X_damaged, Y_damaged, Z, facecolors=colors, linewidth=0.15, edgecolor='gray', shade=False)

        # Impact marker
        ax.scatter([impact_x], [0], [impact_z], color='red', s=200, marker='x', linewidths=3, zorder=10)
        ax.text(impact_x + 3, 0, impact_z, f"IMPACT\n{blast_data['blast_force_MN']} MN",
                color='red', fontsize=10, fontweight='bold')

        # Blast radius ring
        ring_theta = np.linspace(0, 2 * np.pi, 100)
        ring_x = T.RADIUS * np.cos(ring_theta)
        ring_y = T.RADIUS * np.sin(ring_theta)
        ring_z = np.full_like(ring_theta, impact_z)
        ax.plot(ring_x, ring_y, ring_z, color='red', linewidth=1.5, alpha=0.7, linestyle='--')

        # Stress colorbar
        mappable = cm.ScalarMappable(cmap='hot')
        mappable.set_array(stress_field)
        cbar = fig.colorbar(mappable, ax=ax, shrink=0.5, pad=0.1, aspect=20)
        cbar.set_label('Blast Stress (MPa)', color='white', fontsize=10)
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')

        # Safety annotation
        sf = blast_data['safety_factor']
        sf_color = '#00FF00' if sf > 1.5 else '#FFFF00' if sf > 1.0 else '#FF0000'
        ax.text2D(0.05, 0.92, f"Safety Factor: {sf:.2f}", transform=ax.transAxes,
                  color=sf_color, fontsize=12, fontweight='bold',
                  bbox=dict(boxstyle='round', facecolor='black', alpha=0.8))
        ax.text2D(0.05, 0.87, f"Von Mises: {blast_data['von_mises_MPa']:.1f} MPa",
                  transform=ax.transAxes, color='white', fontsize=10)

        plt.tight_layout()
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}/tower_blast.png", dpi=200, facecolor=fig.get_facecolor())
        plt.close()


# ══════════════════════════════════════════════════════════
#  SAFETY REPORT ENGINE
# ══════════════════════════════════════════════════════════

class SafetyReport:
    """Generates structural assessment and retrofit recommendations."""

    @staticmethod
    def assess(label, data):
        sf = data['safety_factor']

        if sf > 2.0:
            damage = "Minor Surface Cracks"
            status = "SAFE"
            retrofit = "None required. Standard maintenance schedule."
        elif sf > 1.5:
            damage = "Minor Structural Cracks"
            status = "ACCEPTABLE"
            retrofit = "Install strain gauges for continuous monitoring."
        elif sf > 1.0:
            damage = "Severe Deformation"
            status = "WARNING"
            retrofit = "Install Tuned Mass Damper (TMD). Increase wall thickness to 1.2m."
        else:
            damage = "TOTAL COLLAPSE"
            status = "CRITICAL FAILURE"
            retrofit = "Complete redesign required. Double wall thickness. Add external steel exoskeleton."

        return {
            "label": label,
            "safety_factor": sf,
            "damage_assessment": damage,
            "status": status,
            "retrofit": retrofit,
        }

    @staticmethod
    def print_report(assessments):
        print("\n" + "=" * 70)
        print("  STRUCTURAL INTEGRITY REPORT")
        print("  Tower: 200m Reinforced Marine Concrete Cylinder")
        print("  Material: 60 MPa Compressive Strength")
        print("=" * 70)

        for a in assessments:
            sf = a['safety_factor']
            icon = "OK" if sf > 1.5 else "!!" if sf > 1.0 else "XX"
            bar_len = min(int(sf * 10), 40)
            bar_color = "=" * bar_len

            print(f"\n  [{icon}] {a['label']}")
            print(f"      Safety Factor:    {sf:.2f}  [{bar_color}{'.' * (40 - bar_len)}]")
            print(f"      Damage:           {a['damage_assessment']}")
            print(f"      Status:           {a['status']}")
            print(f"      Retrofit:         {a['retrofit']}")

        print("\n" + "=" * 70)
        overall = min(a['safety_factor'] for a in assessments)
        if overall > 1.5:
            print("  OVERALL VERDICT: STRUCTURE PASSES ALL LOAD CASES")
        elif overall > 1.0:
            print("  OVERALL VERDICT: STRUCTURE REQUIRES REINFORCEMENT")
        else:
            print("  OVERALL VERDICT: STRUCTURE FAILS - REDESIGN MANDATORY")
        print("=" * 70 + "\n")


# ══════════════════════════════════════════════════════════
#  MAIN EXECUTION
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  SIMULATION v14.0: STRUCTURAL STRESS TEST (3D FEA)")
    print("=" * 60)

    ASSETS = "assets"

    # --- Step 1: Run Physics ---
    print("\n[1/4] Running Seismic Analysis (M9.0)...")
    eq_data = StressEngine.seismic_analysis(magnitude=9.0)
    print(f"      Base Shear:      {eq_data['base_shear_MN']:.2f} MN")
    print(f"      Max Moment:      {eq_data['max_moment_MNm']:.2f} MN.m")
    print(f"      Max Stress:      {eq_data['max_stress_MPa']:.2f} MPa")
    print(f"      Tip Deflection:  {eq_data['tip_deflection_m']:.2f} m")
    print(f"      Safety Factor:   {eq_data['safety_factor']}")

    print("\n[2/4] Running Blast Analysis (50 MN Strike)...")
    bl_data = StressEngine.blast_analysis(blast_force_MN=50.0, impact_height=100.0)
    print(f"      Shear Stress:    {bl_data['shear_stress_MPa']:.2f} MPa")
    print(f"      Von Mises:       {bl_data['von_mises_MPa']:.2f} MPa")
    print(f"      Blast Radius:    {bl_data['blast_radius_m']} m")
    print(f"      Safety Factor:   {bl_data['safety_factor']}")

    # --- Step 2: Generate 3D Visuals ---
    print("\n[3/4] Generating 3D Visualizations...")
    TowerVisualizer.plot_normal(ASSETS)
    print(f"      Saved: {ASSETS}/tower_normal.png")
    TowerVisualizer.plot_earthquake(eq_data, ASSETS)
    print(f"      Saved: {ASSETS}/tower_earthquake.png")
    TowerVisualizer.plot_blast(bl_data, ASSETS)
    print(f"      Saved: {ASSETS}/tower_blast.png")

    # --- Step 3: Safety Report ---
    print("\n[4/4] Generating Safety Report...")
    assessments = [
        SafetyReport.assess("Scenario A: Earthquake M9.0 (Lateral Load)", eq_data),
        SafetyReport.assess("Scenario B: Missile Strike 50 MN (Point Load)", bl_data),
    ]
    SafetyReport.print_report(assessments)

    print("Simulation v14.0 Complete.")
