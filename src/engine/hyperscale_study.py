"""
Hydra-Cool hyperscale scenario study.

Builds a large scenario dataset using:
  - Deterministic parameter sweeps
  - Monte Carlo sampling
  - Feasibility screening
  - Sensitivity analysis
"""

import json
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass
class StudyConfig:
    monte_carlo_samples: int = 6000
    baseline_cooling_fraction_min: float = 0.025
    baseline_cooling_fraction_max: float = 0.050
    marginal_savings_fraction: float = 0.02
    min_velocity_ms: float = 0.5
    max_velocity_ms: float = 3.0
    salinity_ppt: float = 35.0
    cp_j_per_kgk: float = 3993.0
    gravity_ms2: float = 9.81
    dynamic_viscosity_pa_s: float = 1.35e-3
    minor_loss_k: float = 3.0
    auxiliary_load_fraction: float = 0.008
    auxiliary_load_floor_w: float = 400e3
    pump_design_margin: float = 1.20
    focused_final_min_it_load_mw: float = 150.0
    focused_final_max_it_load_mw: float = 200.0
    focused_final_min_pipe_diameter_m: float = 1.0
    focused_final_max_pipe_diameter_m: float = 1.2
    focused_final_min_delta_t_c: float = 32.0


class HydraCoolHyperscaleStudy:
    def __init__(self, config: StudyConfig = None):
        self.config = config or StudyConfig()
        self.latest_outputs: Dict[str, object] = {}

    def seawater_density_kgm3(self, temp_c: float, salinity_ppt: float = None) -> float:
        """
        UNESCO 1983 density of seawater at atmospheric pressure.

        Reference formulation:
        Fofonoff NP, Millard RC Jr. UNESCO Technical Papers in Marine Science No. 44.
        """
        salinity = self.config.salinity_ppt if salinity_ppt is None else salinity_ppt
        rho_w = (
            999.842594
            + 6.793952e-2 * temp_c
            - 9.095290e-3 * temp_c ** 2
            + 1.001685e-4 * temp_c ** 3
            - 1.120083e-6 * temp_c ** 4
            + 6.536332e-9 * temp_c ** 5
        )
        a = (
            0.824493
            - 4.0899e-3 * temp_c
            + 7.6438e-5 * temp_c ** 2
            - 8.2467e-7 * temp_c ** 3
            + 5.3875e-9 * temp_c ** 4
        )
        b = -5.72466e-3 + 1.0227e-4 * temp_c - 1.6546e-6 * temp_c ** 2
        c = 4.8314e-4
        return rho_w + (a * salinity) + (b * (salinity ** 1.5)) + (c * salinity ** 2)

    @staticmethod
    def darcy_friction_factor(reynolds: float, roughness_m: float, diameter_m: float) -> float:
        if reynolds <= 0:
            return np.nan
        if reynolds < 2300:
            return 64.0 / reynolds

        rel_roughness = roughness_m / max(diameter_m, 1e-9)
        term = (rel_roughness / 3.7) + (5.74 / (reynolds ** 0.9))
        return 0.25 / (math.log10(term) ** 2)

    def baseline_cooling_fraction(self, it_load_mw: float, surface_temp_c: float, deep_temp_c: float) -> float:
        """
        Conservative legacy cooling baseline.

        Keeps baseline in an efficient but realistic range instead of a flat generous value.
        """
        cfg = self.config
        load_factor = np.clip((it_load_mw - 50.0) / 150.0, 0.0, 1.0)
        ambient_factor = np.clip((surface_temp_c - 10.0) / 25.0, 0.0, 1.0)
        seawater_delta_factor = np.clip((surface_temp_c - deep_temp_c - 8.0) / 25.0, 0.0, 1.0)

        fraction = (
            cfg.baseline_cooling_fraction_min
            + 0.010 * load_factor
            + 0.008 * ambient_factor
            + 0.007 * seawater_delta_factor
        )
        return float(min(cfg.baseline_cooling_fraction_max, max(cfg.baseline_cooling_fraction_min, fraction)))

    def hydraulic_dynamic_losses_pa(
        self,
        velocity_ms: float,
        rho_avg: float,
        pipe_diameter_m: float,
        loop_length_m: float,
        pipe_roughness_mm: float,
    ) -> Tuple[float, float, float]:
        reynolds = (rho_avg * velocity_ms * pipe_diameter_m) / self.config.dynamic_viscosity_pa_s
        friction_factor = self.darcy_friction_factor(
            reynolds=reynolds,
            roughness_m=pipe_roughness_mm / 1000.0,
            diameter_m=pipe_diameter_m,
        )
        dynamic_pressure_pa = rho_avg * (velocity_ms ** 2) / 2.0
        pipe_friction_pa = friction_factor * (loop_length_m / pipe_diameter_m) * dynamic_pressure_pa
        minor_losses_pa = self.config.minor_loss_k * dynamic_pressure_pa
        return pipe_friction_pa, minor_losses_pa, reynolds

    def solve_natural_circulation_velocity(
        self,
        buoyancy_pressure_pa: float,
        hx_pressure_drop_pa: float,
        rho_avg: float,
        pipe_diameter_m: float,
        loop_length_m: float,
        pipe_roughness_mm: float,
    ) -> float:
        if buoyancy_pressure_pa <= hx_pressure_drop_pa:
            return 0.0

        def residual(velocity_ms: float) -> float:
            pipe_friction_pa, minor_losses_pa, _ = self.hydraulic_dynamic_losses_pa(
                velocity_ms=velocity_ms,
                rho_avg=rho_avg,
                pipe_diameter_m=pipe_diameter_m,
                loop_length_m=loop_length_m,
                pipe_roughness_mm=pipe_roughness_mm,
            )
            return buoyancy_pressure_pa - hx_pressure_drop_pa - pipe_friction_pa - minor_losses_pa

        low = 0.0
        high = self.config.max_velocity_ms

        if residual(high) >= 0.0:
            return high

        for _ in range(60):
            mid = 0.5 * (low + high)
            if residual(mid) >= 0.0:
                low = mid
            else:
                high = mid

        return low

    def evaluate_scenario(self, scenario: Dict[str, float]) -> Dict[str, float]:
        deep_temp_c = scenario["deep_temp_c"]
        surface_temp_c = scenario["surface_temp_c"]
        intake_depth_m = scenario["intake_depth_m"]
        pipe_diameter_m = scenario["pipe_diameter_m"]
        pipe_length_m = scenario["pipe_length_m"]
        vertical_lift_height_m = scenario["vertical_lift_height_m"]
        number_of_pipes = int(scenario["number_of_pipes"])
        it_load_mw = scenario["it_load_mw"]
        delta_t_c = scenario["delta_t_c"]
        hx_pressure_drop_kpa = scenario["hx_pressure_drop_kpa"]
        pipe_roughness_mm = scenario["pipe_roughness_mm"]
        turbine_efficiency = scenario["turbine_efficiency"]
        pump_efficiency = scenario["pump_efficiency"]

        cfg = self.config
        issues: List[str] = []

        if surface_temp_c <= deep_temp_c:
            issues.append("INVALID_TEMPERATURE_GRADIENT")
        if pipe_length_m < intake_depth_m:
            issues.append("INTAKE_TOO_SHORT_FOR_DEPTH")
        if delta_t_c <= 0:
            issues.append("INVALID_DELTA_T")
        if number_of_pipes < 1:
            issues.append("INVALID_PIPE_COUNT")

        hot_temp_c = deep_temp_c + delta_t_c
        rho_cold = self.seawater_density_kgm3(deep_temp_c)
        rho_hot = self.seawater_density_kgm3(hot_temp_c)
        rho_avg = (rho_cold + rho_hot) / 2.0

        it_load_w = it_load_mw * 1e6
        required_mass_flow_kg_s = it_load_w / (cfg.cp_j_per_kgk * delta_t_c)
        required_volumetric_flow_m3_s = required_mass_flow_kg_s / rho_avg

        total_area_m2 = number_of_pipes * math.pi * (pipe_diameter_m ** 2) / 4.0
        required_velocity_ms = required_volumetric_flow_m3_s / max(total_area_m2, 1e-12)

        if required_velocity_ms < cfg.min_velocity_ms:
            issues.append("INSUFFICIENT_VELOCITY")
        if required_velocity_ms > cfg.max_velocity_ms:
            issues.append("EXCESSIVE_VELOCITY")

        loop_length_m = (2.0 * pipe_length_m) + (2.0 * vertical_lift_height_m)
        pipe_friction_pa, minor_losses_pa, reynolds = self.hydraulic_dynamic_losses_pa(
            velocity_ms=required_velocity_ms,
            rho_avg=rho_avg,
            pipe_diameter_m=pipe_diameter_m,
            loop_length_m=loop_length_m,
            pipe_roughness_mm=pipe_roughness_mm,
        )
        heat_exchanger_loss_pa = hx_pressure_drop_kpa * 1000.0
        total_losses_pa = pipe_friction_pa + minor_losses_pa + heat_exchanger_loss_pa

        buoyancy_pressure_pa = max(0.0, (rho_cold - rho_hot) * cfg.gravity_ms2 * vertical_lift_height_m)
        buoyancy_head_m = buoyancy_pressure_pa / max(rho_avg * cfg.gravity_ms2, 1e-12)
        total_loss_head_m = total_losses_pa / max(rho_avg * cfg.gravity_ms2, 1e-12)
        net_head_m = buoyancy_head_m - total_loss_head_m

        max_mass_flow_capacity_kg_s = total_area_m2 * cfg.max_velocity_ms * rho_avg
        max_cooling_capacity_w = max_mass_flow_capacity_kg_s * cfg.cp_j_per_kgk * delta_t_c
        required_flow_capacity_ratio = max_cooling_capacity_w / max(it_load_w, 1e-9)

        natural_velocity_ms = self.solve_natural_circulation_velocity(
            buoyancy_pressure_pa=buoyancy_pressure_pa,
            hx_pressure_drop_pa=heat_exchanger_loss_pa,
            rho_avg=rho_avg,
            pipe_diameter_m=pipe_diameter_m,
            loop_length_m=loop_length_m,
            pipe_roughness_mm=pipe_roughness_mm,
        )
        natural_volumetric_flow_m3_s = natural_velocity_ms * total_area_m2
        natural_mass_flow_kg_s = natural_volumetric_flow_m3_s * rho_avg
        natural_cooling_capacity_w = natural_mass_flow_kg_s * cfg.cp_j_per_kgk * delta_t_c
        natural_cooling_capacity_ratio = natural_cooling_capacity_w / max(it_load_w, 1e-9)
        natural_velocity_margin_ms = natural_velocity_ms - cfg.min_velocity_ms

        pump_assisted_feasible = (
            required_flow_capacity_ratio >= 1.0
            and cfg.min_velocity_ms <= required_velocity_ms <= cfg.max_velocity_ms
            and "INVALID_TEMPERATURE_GRADIENT" not in issues
            and "INTAKE_TOO_SHORT_FOR_DEPTH" not in issues
            and "INVALID_DELTA_T" not in issues
            and "INVALID_PIPE_COUNT" not in issues
        )

        passive_natural_feasible = (
            natural_cooling_capacity_ratio >= 1.0
            and cfg.min_velocity_ms <= natural_velocity_ms <= cfg.max_velocity_ms
            and "INVALID_TEMPERATURE_GRADIENT" not in issues
            and "INTAKE_TOO_SHORT_FOR_DEPTH" not in issues
            and "INVALID_DELTA_T" not in issues
            and "INVALID_PIPE_COUNT" not in issues
        )

        if not passive_natural_feasible:
            issues.append("INSUFFICIENT_NATURAL_CIRCULATION")

        if not pump_assisted_feasible:
            issues.append("THERMAL_DUTY_UNMET")

        if passive_natural_feasible:
            achieved_mass_flow_kg_s = natural_mass_flow_kg_s
            achieved_volumetric_flow_m3_s = natural_volumetric_flow_m3_s
            achieved_velocity_ms = natural_velocity_ms
            achieved_cooling_capacity_ratio = natural_cooling_capacity_ratio
        elif pump_assisted_feasible:
            achieved_mass_flow_kg_s = required_mass_flow_kg_s
            achieved_volumetric_flow_m3_s = required_volumetric_flow_m3_s
            achieved_velocity_ms = required_velocity_ms
            achieved_cooling_capacity_ratio = 1.0
        else:
            achieved_mass_flow_kg_s = min(required_mass_flow_kg_s, max_mass_flow_capacity_kg_s, natural_mass_flow_kg_s)
            achieved_volumetric_flow_m3_s = achieved_mass_flow_kg_s / max(rho_avg, 1e-12)
            achieved_velocity_ms = achieved_volumetric_flow_m3_s / max(total_area_m2, 1e-12)
            achieved_cooling_capacity_ratio = (
                achieved_mass_flow_kg_s * cfg.cp_j_per_kgk * delta_t_c
            ) / max(it_load_w, 1e-9)

        pump_pressure_deficit_pa = max(0.0, total_losses_pa - buoyancy_pressure_pa)
        pump_assist_power_w = (
            (pump_pressure_deficit_pa * required_volumetric_flow_m3_s) / max(pump_efficiency, 1e-9)
        ) * cfg.pump_design_margin

        available_turbine_head_m = max(0.0, net_head_m)
        turbine_power_w = (
            turbine_efficiency
            * rho_avg
            * cfg.gravity_ms2
            * achieved_volumetric_flow_m3_s
            * available_turbine_head_m
        )

        auxiliary_power_w = max(cfg.auxiliary_load_floor_w, it_load_w * cfg.auxiliary_load_fraction)
        hydra_total_power_w = pump_assist_power_w + auxiliary_power_w - turbine_power_w
        baseline_fraction = self.baseline_cooling_fraction(
            it_load_mw=it_load_mw,
            surface_temp_c=surface_temp_c,
            deep_temp_c=deep_temp_c,
        )
        baseline_cooling_power_w = it_load_w * baseline_fraction
        energy_savings_fraction = (
            baseline_cooling_power_w - hydra_total_power_w
        ) / max(baseline_cooling_power_w, 1e-9)
        gravity_assist_fraction = min(1.0, buoyancy_pressure_pa / max(total_losses_pa, 1e-9))
        pump_offset_fraction = min(1.0, buoyancy_pressure_pa / max(total_losses_pa, 1e-9))
        positive_retrofit_benefit = energy_savings_fraction > 0.0
        velocity_margin_ms = min(
            required_velocity_ms - cfg.min_velocity_ms,
            cfg.max_velocity_ms - required_velocity_ms,
        )

        if passive_natural_feasible:
            circulation_regime = "PASSIVE_NATURAL"
        elif pump_assisted_feasible:
            circulation_regime = "RETROFIT_ASSIST"
        else:
            circulation_regime = "INFEASIBLE"

        if circulation_regime == "PASSIVE_NATURAL":
            success_layer = "PASSIVE_STANDALONE"
        elif circulation_regime == "RETROFIT_ASSIST":
            success_layer = "HYBRID_RETROFIT_ASSIST"
        else:
            success_layer = "NO_VALID_LAYER"

        turbine_recovery_active = bool(turbine_power_w > 1e3)

        if not pump_assisted_feasible:
            classification = "FAIL"
        elif not positive_retrofit_benefit:
            classification = "FAIL"
            issues.append("NO_POSITIVE_RETROFIT_BENEFIT")
        elif energy_savings_fraction >= 0.10:
            classification = "PASS"
        elif energy_savings_fraction >= cfg.marginal_savings_fraction:
            classification = "MARGINAL"
        else:
            classification = "FAIL"
            issues.append("LOW_RETROFIT_BENEFIT")

        constraint_flags = "|".join(issues) if issues else "NONE"
        failure_mode = "NONE"
        if classification == "FAIL":
            failure_mode = self.select_failure_mode(issues)

        return {
            "deep_temp_c": deep_temp_c,
            "surface_temp_c": surface_temp_c,
            "intake_depth_m": intake_depth_m,
            "pipe_diameter_m": pipe_diameter_m,
            "pipe_length_m": pipe_length_m,
            "vertical_lift_height_m": vertical_lift_height_m,
            "number_of_pipes": number_of_pipes,
            "it_load_mw": it_load_mw,
            "delta_t_c": delta_t_c,
            "hx_pressure_drop_kpa": hx_pressure_drop_kpa,
            "pipe_roughness_mm": pipe_roughness_mm,
            "turbine_efficiency": turbine_efficiency,
            "pump_efficiency": pump_efficiency,
            "required_mass_flow_kg_s": required_mass_flow_kg_s,
            "required_volumetric_flow_m3_s": required_volumetric_flow_m3_s,
            "actual_mass_flow_kg_s": achieved_mass_flow_kg_s,
            "actual_volumetric_flow_m3_s": achieved_volumetric_flow_m3_s,
            "velocity_ms": achieved_velocity_ms,
            "rho_cold_kgm3": rho_cold,
            "rho_hot_kgm3": rho_hot,
            "buoyancy_pressure_pa": buoyancy_pressure_pa,
            "buoyancy_head_m": buoyancy_head_m,
            "friction_losses_pa": pipe_friction_pa + minor_losses_pa,
            "heat_exchanger_losses_pa": heat_exchanger_loss_pa,
            "total_losses_pa": total_losses_pa,
            "net_head_m": net_head_m,
            "turbine_generation_mw": turbine_power_w / 1e6,
            "pump_assist_power_mw": pump_assist_power_w / 1e6,
            "pump_energy_mw": pump_assist_power_w / 1e6,
            "aux_energy_mw": auxiliary_power_w / 1e6,
            "hydra_total_power_mw": hydra_total_power_w / 1e6,
            "hydra_net_energy_mw": hydra_total_power_w / 1e6,
            "baseline_cooling_energy_mw": baseline_cooling_power_w / 1e6,
            "baseline_cooling_fraction": baseline_fraction,
            "energy_savings_fraction": energy_savings_fraction,
            "gravity_assist_fraction": gravity_assist_fraction,
            "pump_offset_fraction": pump_offset_fraction,
            "positive_retrofit_benefit": positive_retrofit_benefit,
            "required_velocity_ms": required_velocity_ms,
            "velocity_margin_ms": velocity_margin_ms,
            "natural_velocity_ms": natural_velocity_ms,
            "natural_velocity_margin_ms": natural_velocity_margin_ms,
            "required_flow_capacity_ratio": required_flow_capacity_ratio,
            "actual_cooling_capacity_ratio": achieved_cooling_capacity_ratio,
            "natural_cooling_capacity_ratio": natural_cooling_capacity_ratio,
            "pressure_balance_ratio": buoyancy_pressure_pa / max(total_losses_pa, 1e-9),
            "pump_fraction_of_baseline": pump_assist_power_w / max(baseline_cooling_power_w, 1e-9),
            "pump_fraction_of_hydra_total": pump_assist_power_w / max(hydra_total_power_w, 1e-9),
            "classification": classification,
            "failure_mode": failure_mode,
            "constraint_flags": constraint_flags,
            "issue_count": len(issues),
            "cooling_works": pump_assisted_feasible,
            "passive_natural_feasible": passive_natural_feasible,
            "requires_pump_assist": bool(pump_assisted_feasible and not passive_natural_feasible),
            "circulation_regime": circulation_regime,
            "success_layer": success_layer,
            "turbine_recovery_active": turbine_recovery_active,
            "meets_10pct_target": bool(energy_savings_fraction >= 0.10 and pump_assisted_feasible and positive_retrofit_benefit),
        }

    @staticmethod
    def select_failure_mode(issues: List[str]) -> str:
        priority_order = [
            "INSUFFICIENT_VELOCITY",
            "THERMAL_DUTY_UNMET",
            "EXCESSIVE_VELOCITY",
            "NO_POSITIVE_RETROFIT_BENEFIT",
            "LOW_RETROFIT_BENEFIT",
            "INSUFFICIENT_NATURAL_CIRCULATION",
            "INVALID_TEMPERATURE_GRADIENT",
            "INTAKE_TOO_SHORT_FOR_DEPTH",
            "INVALID_DELTA_T",
            "INVALID_PIPE_COUNT",
        ]
        for mode in priority_order:
            if mode in issues:
                return mode
        return issues[0] if issues else "UNSPECIFIED_FAIL"

    def generate_parameter_sweep(self) -> pd.DataFrame:
        sweep_rows: List[Dict[str, float]] = []

        depth_values = [30.0, 100.0, 300.0, 600.0, 1000.0]
        diameter_values = [0.5, 1.0, 2.0, 4.0, 6.0]
        lift_values = [10.0, 50.0, 100.0, 175.0, 250.0]
        pipe_count_values = [1, 2, 4, 10, 20, 40]
        load_values = [5.0, 25.0, 50.0, 100.0, 150.0, 200.0]
        delta_t_values = [10.0, 20.0, 30.0, 40.0]

        for depth in depth_values:
            for diameter in diameter_values:
                for lift in lift_values:
                    for pipe_count in pipe_count_values:
                        for load in load_values:
                            for delta_t in delta_t_values:
                                sweep_rows.append(
                                    self.evaluate_scenario(
                                        {
                                            "deep_temp_c": 5.0,
                                            "surface_temp_c": 24.0,
                                            "intake_depth_m": depth,
                                            "pipe_diameter_m": diameter,
                                            "pipe_length_m": max(50.0, depth * 1.25),
                                            "vertical_lift_height_m": lift,
                                            "number_of_pipes": pipe_count,
                                            "it_load_mw": load,
                                            "delta_t_c": delta_t,
                                            "hx_pressure_drop_kpa": 40.0,
                                            "pipe_roughness_mm": 0.045,
                                            "turbine_efficiency": 0.85,
                                            "pump_efficiency": 0.82,
                                        }
                                    )
                                )

        df = pd.DataFrame(sweep_rows)
        df["scenario_family"] = "parameter_sweep"
        return df

    def generate_monte_carlo(self, samples: int = None, seed: int = 42) -> pd.DataFrame:
        sample_count = samples or self.config.monte_carlo_samples
        rng = np.random.default_rng(seed)
        rows: List[Dict[str, float]] = []

        for _ in range(sample_count):
            depth = rng.uniform(30.0, 1000.0)
            length_lower_bound = max(50.0, depth * 1.02)
            rows.append(
                self.evaluate_scenario(
                    {
                        "deep_temp_c": rng.uniform(2.0, 12.0),
                        "surface_temp_c": rng.uniform(10.0, 35.0),
                        "intake_depth_m": depth,
                        "pipe_diameter_m": rng.uniform(0.5, 6.0),
                        "pipe_length_m": rng.uniform(length_lower_bound, 2000.0),
                        "vertical_lift_height_m": rng.uniform(10.0, 250.0),
                        "number_of_pipes": int(rng.integers(1, 41)),
                        "it_load_mw": rng.uniform(5.0, 200.0),
                        "delta_t_c": rng.uniform(10.0, 40.0),
                        "hx_pressure_drop_kpa": rng.uniform(10.0, 80.0),
                        "pipe_roughness_mm": rng.uniform(0.01, 0.1),
                        "turbine_efficiency": rng.uniform(0.7, 0.9),
                        "pump_efficiency": rng.uniform(0.7, 0.9),
                    }
                )
            )

        df = pd.DataFrame(rows)
        df["scenario_family"] = "monte_carlo"
        return df

    def generate_focus_window_sweep(self) -> pd.DataFrame:
        rows: List[Dict[str, float]] = []

        diameter_values = np.round(np.arange(0.8, 1.51, 0.1), 2)
        lift_values = np.arange(140.0, 251.0, 10.0)
        delta_t_values = np.arange(24.0, 40.1, 2.0)
        hx_values = np.arange(10.0, 45.1, 5.0)
        load_values = np.arange(50.0, 200.1, 10.0)
        depth_values = [60.0, 120.0, 250.0]
        pipe_count_values = [1, 2, 3]

        for diameter in diameter_values:
            for lift in lift_values:
                for delta_t in delta_t_values:
                    for hx_drop in hx_values:
                        for load in load_values:
                            for depth in depth_values:
                                for pipe_count in pipe_count_values:
                                    rows.append(
                                        self.evaluate_scenario(
                                            {
                                                "deep_temp_c": 4.5,
                                                "surface_temp_c": 24.0,
                                                "intake_depth_m": depth,
                                                "pipe_diameter_m": float(diameter),
                                                "pipe_length_m": max(90.0, depth * 1.2),
                                                "vertical_lift_height_m": float(lift),
                                                "number_of_pipes": pipe_count,
                                                "it_load_mw": float(load),
                                                "delta_t_c": float(delta_t),
                                                "hx_pressure_drop_kpa": float(hx_drop),
                                                "pipe_roughness_mm": 0.03,
                                                "turbine_efficiency": 0.85,
                                                "pump_efficiency": 0.84,
                                            }
                                        )
                                    )

        df = pd.DataFrame(rows)
        df["scenario_family"] = "focus_window"
        return df

    @staticmethod
    def prune_candidate_window(dataset: pd.DataFrame) -> pd.DataFrame:
        candidate_mask = (
            dataset["pipe_diameter_m"].between(0.8, 1.5)
            & (dataset["vertical_lift_height_m"] >= 140.0)
            & (dataset["delta_t_c"] >= 24.0)
            & (dataset["hx_pressure_drop_kpa"] <= 45.0)
            & dataset["it_load_mw"].between(50.0, 200.0)
            & (~dataset["failure_mode"].isin(["INVALID_TEMPERATURE_GRADIENT", "INTAKE_TOO_SHORT_FOR_DEPTH"]))
        )
        pruned = dataset[candidate_mask].copy()
        pruned["scenario_family"] = "stage_2_candidates"
        return pruned

    def build_stage_3_final_results(self, focus_window: pd.DataFrame) -> pd.DataFrame:
        cfg = self.config
        final = focus_window[
            (focus_window["classification"] == "PASS")
            & (focus_window["success_layer"] == "HYBRID_RETROFIT_ASSIST")
            & focus_window["it_load_mw"].between(cfg.focused_final_min_it_load_mw, cfg.focused_final_max_it_load_mw)
            & focus_window["pipe_diameter_m"].between(
                cfg.focused_final_min_pipe_diameter_m,
                cfg.focused_final_max_pipe_diameter_m,
            )
            & (focus_window["delta_t_c"] >= cfg.focused_final_min_delta_t_c)
        ].copy()

        final = final.sort_values(
            ["energy_savings_fraction", "velocity_margin_ms", "pump_fraction_of_baseline"],
            ascending=[False, False, True],
        ).reset_index(drop=True)
        final.insert(0, "rank", np.arange(1, len(final) + 1))

        selected_columns = [
            "rank",
            "classification",
            "success_layer",
            "circulation_regime",
            "it_load_mw",
            "pipe_diameter_m",
            "number_of_pipes",
            "vertical_lift_height_m",
            "delta_t_c",
            "hx_pressure_drop_kpa",
            "deep_temp_c",
            "surface_temp_c",
            "required_mass_flow_kg_s",
            "actual_mass_flow_kg_s",
            "required_velocity_ms",
            "velocity_ms",
            "velocity_margin_ms",
            "natural_velocity_ms",
            "actual_cooling_capacity_ratio",
            "natural_cooling_capacity_ratio",
            "energy_savings_fraction",
            "pump_fraction_of_baseline",
            "pump_fraction_of_hydra_total",
            "gravity_assist_fraction",
            "pump_assist_power_mw",
            "aux_energy_mw",
            "turbine_generation_mw",
            "hydra_total_power_mw",
            "baseline_cooling_energy_mw",
            "buoyancy_head_m",
            "net_head_m",
            "pressure_balance_ratio",
        ]
        return final[selected_columns]

    @staticmethod
    def build_summary(dataset: pd.DataFrame) -> Dict[str, object]:
        class_counts = dataset["classification"].value_counts().to_dict()
        failure_counts = dataset[dataset["classification"] == "FAIL"]["failure_mode"].value_counts().head(10).to_dict()
        regime_counts = dataset["circulation_regime"].value_counts().to_dict()
        layer_counts = dataset["success_layer"].value_counts().to_dict()
        feasible = dataset[dataset["cooling_works"]]
        passing = dataset[dataset["classification"] == "PASS"]
        marginal = dataset[dataset["classification"] == "MARGINAL"]
        passive_pass = passing[passing["circulation_regime"] == "PASSIVE_NATURAL"]
        hybrid_pass = passing[passing["circulation_regime"] == "RETROFIT_ASSIST"]
        hybrid_marginal = marginal[marginal["circulation_regime"] == "RETROFIT_ASSIST"]

        best_roi = dataset.sort_values("energy_savings_fraction", ascending=False).head(1)
        best_row = best_roi.iloc[0].to_dict() if not best_roi.empty else {}

        return {
            "scenario_count": int(len(dataset)),
            "classification_counts": class_counts,
            "pass_rate": float((dataset["classification"] == "PASS").mean()),
            "marginal_rate": float((dataset["classification"] == "MARGINAL").mean()),
            "fail_rate": float((dataset["classification"] == "FAIL").mean()),
            "feasible_rate": float(dataset["cooling_works"].mean()),
            "target_10pct_rate": float(dataset["meets_10pct_target"].mean()),
            "median_energy_savings_fraction": float(dataset["energy_savings_fraction"].median()),
            "mean_energy_savings_fraction": float(dataset["energy_savings_fraction"].mean()),
            "feasible_mean_energy_savings_fraction": float(feasible["energy_savings_fraction"].mean()) if not feasible.empty else 0.0,
            "feasible_median_energy_savings_fraction": float(feasible["energy_savings_fraction"].median()) if not feasible.empty else 0.0,
            "median_net_head_m": float(dataset["net_head_m"].median()),
            "median_velocity_ms": float(dataset["velocity_ms"].median()),
            "median_pump_energy_mw": float(dataset["pump_energy_mw"].median()),
            "median_turbine_generation_mw": float(dataset["turbine_generation_mw"].median()),
            "top_failure_modes": failure_counts,
            "circulation_regime_counts": regime_counts,
            "success_layer_counts": layer_counts,
            "passive_natural_pass_rate": float(len(passive_pass) / max(len(dataset), 1)),
            "hybrid_assisted_pass_rate": float(len(hybrid_pass) / max(len(dataset), 1)),
            "hybrid_assisted_marginal_rate": float(len(hybrid_marginal) / max(len(dataset), 1)),
            "best_scenario": best_row,
            "best_pass_scenario": passing.sort_values("energy_savings_fraction", ascending=False).head(1).to_dict("records"),
            "best_passive_pass_scenario": passive_pass.sort_values("energy_savings_fraction", ascending=False).head(1).to_dict("records"),
            "best_hybrid_pass_scenario": hybrid_pass.sort_values("energy_savings_fraction", ascending=False).head(1).to_dict("records"),
            "best_marginal_scenario": marginal.sort_values("energy_savings_fraction", ascending=False).head(1).to_dict("records"),
            "best_feasible_scenario": feasible.sort_values("energy_savings_fraction", ascending=False).head(1).to_dict("records"),
            "feasible_examples": feasible.sort_values("energy_savings_fraction", ascending=False).head(5).to_dict("records"),
        }

    @staticmethod
    def sensitivity_analysis(dataset: pd.DataFrame) -> pd.DataFrame:
        input_columns = [
            "deep_temp_c",
            "surface_temp_c",
            "intake_depth_m",
            "pipe_diameter_m",
            "pipe_length_m",
            "vertical_lift_height_m",
            "number_of_pipes",
            "it_load_mw",
            "delta_t_c",
            "hx_pressure_drop_kpa",
            "pipe_roughness_mm",
            "turbine_efficiency",
            "pump_efficiency",
        ]

        working = dataset.copy()
        working["pass_binary"] = (working["classification"] == "PASS").astype(int)

        rows = []
        for col in input_columns:
            rows.append(
                {
                    "parameter": col,
                    "spearman_energy_savings": working[col].corr(working["energy_savings_fraction"], method="spearman"),
                    "spearman_pass_probability": working[col].corr(working["pass_binary"], method="spearman"),
                    "spearman_net_head": working[col].corr(working["net_head_m"], method="spearman"),
                }
            )

        sensitivity = pd.DataFrame(rows)
        sensitivity["importance_score"] = (
            sensitivity["spearman_energy_savings"].abs()
            + sensitivity["spearman_pass_probability"].abs()
            + sensitivity["spearman_net_head"].abs()
        ) / 3.0
        sensitivity = sensitivity.sort_values("importance_score", ascending=False).reset_index(drop=True)
        return sensitivity

    @staticmethod
    def write_markdown_summary(summary: Dict[str, object], sensitivity: pd.DataFrame, output_path: str, title: str) -> None:
        top_params = sensitivity.head(5)
        best = (summary.get("best_pass_scenario") or [{}])[0]

        lines = [
            f"# {title}",
            "",
            "- Study intent: evaluate Hydra-Cool as a retrofit assist layer that reduces legacy cooling energy, not as a standalone replacement requirement.",
            f"- Scenario count: {summary['scenario_count']}",
            f"- PASS rate: {summary['pass_rate']:.2%}",
            f"- MARGINAL rate: {summary['marginal_rate']:.2%}",
            f"- FAIL rate: {summary['fail_rate']:.2%}",
            f"- Feasible hydraulic rate: {summary['feasible_rate']:.2%}",
            f"- >=10% retrofit energy reduction rate: {summary['target_10pct_rate']:.2%}",
            f"- Passive-natural PASS rate: {summary['passive_natural_pass_rate']:.2%}",
            f"- Retrofit-assist PASS rate: {summary['hybrid_assisted_pass_rate']:.2%}",
            f"- Retrofit-assist MARGINAL rate: {summary['hybrid_assisted_marginal_rate']:.2%}",
            f"- Success layers: {summary['success_layer_counts']}",
            f"- Mean energy savings fraction: {summary['mean_energy_savings_fraction']:.2%}",
            f"- Median energy savings fraction: {summary['median_energy_savings_fraction']:.2%}",
            f"- Feasible mean energy savings fraction: {summary['feasible_mean_energy_savings_fraction']:.2%}",
            f"- Feasible median energy savings fraction: {summary['feasible_median_energy_savings_fraction']:.2%}",
            "",
            "## Dominant Failure Modes",
        ]

        for mode, count in summary["top_failure_modes"].items():
            lines.append(f"- {mode}: {count}")

        lines.extend(
            [
                "",
                "## Most Important Parameters",
            ]
        )
        for _, row in top_params.iterrows():
            lines.append(f"- {row['parameter']}: importance={row['importance_score']:.3f}")

        lines.extend(
            [
                "",
                "## Best Scenario Snapshot",
                f"- Classification: {best.get('classification', 'N/A')}",
                f"- Regime: {best.get('circulation_regime', 'N/A')}",
                f"- IT load: {best.get('it_load_mw', 0.0):.2f} MW",
                f"- Number of pipes: {int(best.get('number_of_pipes', 0)) if best else 0}",
                f"- Diameter: {best.get('pipe_diameter_m', 0.0):.2f} m",
                f"- Vertical lift: {best.get('vertical_lift_height_m', 0.0):.2f} m",
                f"- Baseline cooling fraction: {best.get('baseline_cooling_fraction', 0.0):.2%}",
                f"- Energy savings: {best.get('energy_savings_fraction', 0.0):.2%}",
                f"- Net head: {best.get('net_head_m', 0.0):.2f} m",
                f"- Natural cooling capacity ratio: {best.get('natural_cooling_capacity_ratio', 0.0):.2f}",
                f"- Gravity assist fraction of hydraulic losses: {best.get('gravity_assist_fraction', 0.0):.2%}",
                f"- Turbine recovery active: {best.get('turbine_recovery_active', False)}",
                f"- Interpretation: negative net head here means pump-assisted retrofit operation, not invalidity by itself.",
            ]
        )

        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines))

    def run(self, output_dir: str) -> Tuple[pd.DataFrame, Dict[str, object], pd.DataFrame]:
        os.makedirs(output_dir, exist_ok=True)

        sweep = self.generate_parameter_sweep()
        monte_carlo = self.generate_monte_carlo()
        dataset = pd.concat([sweep, monte_carlo], ignore_index=True)
        dataset["scenario_family"] = dataset["scenario_family"].fillna("stage_1_screening")
        stage_2_candidates = self.prune_candidate_window(dataset)
        focus_window = self.generate_focus_window_sweep()

        summary = self.build_summary(dataset)
        sensitivity = self.sensitivity_analysis(dataset)
        stage_2_summary = self.build_summary(stage_2_candidates)
        stage_2_sensitivity = self.sensitivity_analysis(stage_2_candidates) if not stage_2_candidates.empty else pd.DataFrame()
        focus_summary = self.build_summary(focus_window)
        focus_sensitivity = self.sensitivity_analysis(focus_window)

        dataset_path = os.path.join(output_dir, "hydra_cool_stage_1_screening_dataset.csv")
        summary_path = os.path.join(output_dir, "hydra_cool_stage_1_screening_summary.json")
        sensitivity_path = os.path.join(output_dir, "hydra_cool_stage_1_screening_sensitivity.csv")
        top_configs_path = os.path.join(output_dir, "hydra_cool_stage_1_screening_top_configs.csv")
        markdown_path = os.path.join(output_dir, "hydra_cool_stage_1_screening_summary.md")
        stage_2_dataset_path = os.path.join(output_dir, "hydra_cool_stage_2_candidates_dataset.csv")
        stage_2_summary_path = os.path.join(output_dir, "hydra_cool_stage_2_candidates_summary.json")
        stage_2_sensitivity_path = os.path.join(output_dir, "hydra_cool_stage_2_candidates_sensitivity.csv")
        stage_2_top_configs_path = os.path.join(output_dir, "hydra_cool_stage_2_candidates_top_configs.csv")
        stage_2_markdown_path = os.path.join(output_dir, "hydra_cool_stage_2_candidates_summary.md")
        focus_dataset_path = os.path.join(output_dir, "hydra_cool_stage_3_focus_window_dataset.csv")
        focus_summary_path = os.path.join(output_dir, "hydra_cool_stage_3_focus_window_summary.json")
        focus_sensitivity_path = os.path.join(output_dir, "hydra_cool_stage_3_focus_window_sensitivity.csv")
        focus_top_configs_path = os.path.join(output_dir, "hydra_cool_stage_3_focus_window_top_configs.csv")
        focus_markdown_path = os.path.join(output_dir, "hydra_cool_stage_3_focus_window_summary.md")
        focus_final_results_path = os.path.join(output_dir, "hydra_cool_stage_3_final_results.csv")

        dataset.to_csv(dataset_path, index=False)
        sensitivity.to_csv(sensitivity_path, index=False)
        dataset[dataset["classification"].isin(["PASS", "MARGINAL"])].sort_values(
            "energy_savings_fraction", ascending=False
        ).head(250).to_csv(top_configs_path, index=False)
        with open(summary_path, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)
        self.write_markdown_summary(summary, sensitivity, markdown_path, "Hydra-Cool Stage 1 Screening Summary")

        stage_2_candidates.to_csv(stage_2_dataset_path, index=False)
        if not stage_2_sensitivity.empty:
            stage_2_sensitivity.to_csv(stage_2_sensitivity_path, index=False)
        stage_2_candidates[stage_2_candidates["classification"].isin(["PASS", "MARGINAL"])].sort_values(
            "energy_savings_fraction", ascending=False
        ).head(250).to_csv(stage_2_top_configs_path, index=False)
        with open(stage_2_summary_path, "w", encoding="utf-8") as handle:
            json.dump(stage_2_summary, handle, indent=2)
        self.write_markdown_summary(
            stage_2_summary,
            stage_2_sensitivity if not stage_2_sensitivity.empty else pd.DataFrame(columns=["parameter", "importance_score"]),
            stage_2_markdown_path,
            "Hydra-Cool Stage 2 Candidate Window Summary",
        )

        focus_window.to_csv(focus_dataset_path, index=False)
        focus_sensitivity.to_csv(focus_sensitivity_path, index=False)
        focus_window[focus_window["classification"].isin(["PASS", "MARGINAL"])].sort_values(
            "energy_savings_fraction", ascending=False
        ).head(250).to_csv(focus_top_configs_path, index=False)
        self.build_stage_3_final_results(focus_window).to_csv(focus_final_results_path, index=False)
        with open(focus_summary_path, "w", encoding="utf-8") as handle:
            json.dump(focus_summary, handle, indent=2)
        self.write_markdown_summary(focus_summary, focus_sensitivity, focus_markdown_path, "Hydra-Cool Stage 3 Focus Window Summary")

        self.latest_outputs = {
            "stage_1_summary": summary,
            "stage_1_sensitivity": sensitivity,
            "stage_2_summary": stage_2_summary,
            "stage_2_sensitivity": stage_2_sensitivity,
            "stage_3_summary": focus_summary,
            "stage_3_sensitivity": focus_sensitivity,
            "stage_3_final_results_path": focus_final_results_path,
        }

        return dataset, summary, sensitivity
