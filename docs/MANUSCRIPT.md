# Hydra-Cool: Mapping the Feasible Design Window for Buoyancy-Assisted Retrofit Cooling in Hyperscale Data Centers

**Draft scientific manuscript**

**Project:** Hydra-Cool open research repository  
**Author:** Obada Dallo  
**Status:** Research draft for internal review and iterative refinement

## Abstract

Hydra-Cool is a buoyancy-assisted cooling concept intended to reduce the energy demand of hyperscale data center cooling systems by combining deep-water heat rejection, density-driven hydraulic assistance, elevated discharge storage, gravity return flow, and optional turbine recovery. The central research question is not whether Hydra-Cool can replace conventional cooling infrastructure outright, but whether it can serve as a high-impact retrofit assist layer that offsets a meaningful fraction of cooling energy in large coastal facilities.

We developed a staged simulation framework that evaluates Hydra-Cool using thermodynamic, hydraulic, and energy-balance constraints. The model computes required mass flow, buoyancy pressure, Darcy-Weisbach friction losses, heat-exchanger pressure losses, pump-assist burden, optional turbine recovery, and total assisted cooling power. Scenarios are classified by hydraulic feasibility and by their ability to reduce legacy cooling energy demand. The campaign was structured in three stages: a broad screening study (`24,000` scenarios), a pruned candidate window (`543` scenarios), and a focused high-resolution design window (`995,328` scenarios).

The current results show that passive standalone operation remains uncommon, while hybrid retrofit assist dominates the viable solution space. In the focused design window, the verified rerun reports a `48.50%` PASS rate, of which `4.39%` corresponds to passive standalone circulation and `44.10%` corresponds to hybrid retrofit assist. Across all stages, the dominant hydraulic failure mode is **insufficient velocity**, with a smaller residual contribution from unmet thermal duty. Sensitivity analysis indicates that IT load, heat-exchanger pressure drop, number of pipes, pipe diameter, and temperature rise are the principal variables controlling feasibility. These findings suggest that Hydra-Cool is best interpreted as a retrofit energy-reduction architecture rather than a fully passive replacement cycle. The present draft also identifies a major research priority: further tightening the baseline cooling model and auxiliary load assumptions, because the current energy-savings estimates remain too optimistic for final publication.

**Keywords:** data center cooling, buoyancy-driven flow, thermosiphon assist, retrofit cooling, seawater cooling, hydraulic feasibility

## 1. Introduction

The growth of artificial intelligence infrastructure has shifted thermal management from an operational detail to a first-order systems problem. Hyperscale data centers increasingly face limits imposed not by computation alone, but by the electrical and mechanical burden of heat rejection. Conventional cooling plants rely on electrically driven pumps, chillers, and cooling towers to move heat against natural gradients. Hydra-Cool explores whether part of that burden can be reduced by exploiting gravity, buoyancy, and coastal thermal resources.

The underlying concept is straightforward. Cold seawater is drawn from depth, passed through a heat exchanger coupled to the data center thermal loop, heated by the rejected load, and then allowed to rise through a vertical hydraulic leg. The density reduction between the cold intake and warm return generates buoyancy pressure. Discharge to an elevated reservoir enables gravity return flow, and in selected cases an inline turbine can recover part of the available head. The essential design idea is not free energy, but partial substitution of active hydraulic work with passive physical assistance.

This manuscript presents the current state of the Hydra-Cool simulation campaign. The work is framed as open engineering exploration rather than a final technology validation. The main objectives are:

1. To determine whether there exists a realistic design window in which Hydra-Cool reduces cooling energy in large data centers.
2. To distinguish clearly between passive standalone feasibility and hybrid retrofit-assist feasibility.
3. To identify the hydraulic variables that dominate success and failure.
4. To produce publication-grade visual outputs for transparent scientific communication.

## 2. Physical Basis

The Hydra-Cool model is built on five governing physical elements:

1. **Heat removal requirement**

$$
\dot{m}_{\mathrm{req}} = \frac{P_{\mathrm{thermal}}}{C_p \Delta T}
$$

2. **Buoyancy pressure generation**

$$
\Delta P_{\mathrm{buoyancy}} = \left( \rho_{\mathrm{cold}} - \rho_{\mathrm{hot}} \right) g H
$$

3. **Hydraulic losses**

$$
\Delta P_{\mathrm{losses}} = \Delta P_{\mathrm{friction}} + \Delta P_{\mathrm{minor}} + \Delta P_{\mathrm{HX}}
$$

4. **Hybrid Hydra-Cool total power**

$$
P_{\mathrm{Hydra,total}} = P_{\mathrm{pump,assist}} + P_{\mathrm{aux}} - P_{\mathrm{turbine}}
$$

5. **Retrofit savings fraction**

$$
\eta_{\mathrm{savings}} = \frac{P_{\mathrm{baseline}} - P_{\mathrm{Hydra,total}}}{P_{\mathrm{baseline}}}
$$

Water density is now evaluated with a UNESCO-based seawater density formulation at atmospheric pressure, using representative ocean salinity. Friction losses are calculated using Darcy-Weisbach with the Swamee-Jain approximation in the turbulent regime. The optional turbine is treated as a recoverable bonus layer, not a required condition for viability.

Supporting derivations and assumptions are documented in:

- [PHYSICS_BASIS.md](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/docs/PHYSICS_BASIS.md)
- [ASSUMPTIONS.md](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/docs/ASSUMPTIONS.md)

## 3. Methods

### 3.1 System interpretation

The current simulation campaign treats Hydra-Cool primarily as a **retrofit assist layer** for an existing cooling system. This distinction is central. A scenario is not required to support purely passive circulation to be useful. Instead, the principal test is whether buoyancy and gravity materially offset the energy demand of a legacy cooling plant while remaining hydraulically feasible.

Three success layers are tracked explicitly:

1. `PASSIVE_STANDALONE`: natural circulation alone sustains the thermal duty within velocity constraints.
2. `HYBRID_RETROFIT_ASSIST`: the loop remains hydraulically useful, but pump assistance is still required.
3. `TURBINE_RECOVERY_ACTIVE`: optional energy recovery is present; this is treated as a beneficial secondary effect rather than a core success condition.

### 3.2 Stage-based campaign design

The simulation was reorganized into three stages to avoid the problem of exploring large numbers of scenarios without improving the design direction.

| Stage | Purpose | Scenario count | Output |
|------|---------|----------------|--------|
| Stage 1 | Broad screening of the design space | 24,000 | Identify dominant bottlenecks |
| Stage 2 | Pruned candidate window | 543 | Remove configurations that do not support concept development |
| Stage 3 | High-resolution focus-window study | 995,328 | Map the feasible design window in detail |

The progression from Stage 1 to Stage 3 is deliberate. Stage 1 is exploratory. Stage 2 discards scenarios that do not advance the concept. Stage 3 concentrates computational effort inside the most promising design region.

### 3.3 Parameter space

The high-resolution window was chosen around the most useful development region identified by the earlier screening work:

- Pipe diameter: approximately `0.8–1.5 m`
- High vertical lift
- Elevated `Delta T`
- Low to moderate heat-exchanger pressure drop
- IT load in the `50–200 MW` range

This pruning strategy is important because the value of the campaign lies not in raw scenario count, but in progressive elimination of non-productive parts of the design space.

### 3.4 Classification logic

Each scenario is evaluated for:

- Required thermal mass flow
- Resulting volumetric flow and velocity
- Buoyancy pressure
- Hydraulic losses
- Passive natural-circulation capacity
- Pump-assisted feasibility
- Net retrofit energy savings relative to a legacy baseline

The current classification is:

- **PASS**: hydraulically feasible, satisfies the thermal duty, and achieves at least `10%` positive retrofit energy reduction
- **MARGINAL**: hydraulically feasible, satisfies the thermal duty, and achieves at least `2%` but less than `10%` reduction
- **FAIL**: hydraulically infeasible, fails the thermal duty, or does not produce a positive retrofit benefit

Scenarios now fail explicitly when either of the following conditions is violated:

- the required operating velocity falls below the minimum useful threshold,
- or the achievable mass flow cannot sustain the required thermal duty.

When both are present, the primary reported failure mode is **INSUFFICIENT_VELOCITY**.

### 3.5 Phase 2 scientific hardening

Phase 2 of the repository focused on scientific hardening of the Stage 3 focused design window. In this update, Hydra-Cool was formalized primarily as a `HYBRID_RETROFIT_ASSIST` architecture while retaining passive-natural circulation as a reportable but secondary operating class. The simulation engine was revised so that total assisted cooling power is evaluated as

$$
P_{\mathrm{Hydra,total}} = P_{\mathrm{pump,assist}} + P_{\mathrm{aux}} - P_{\mathrm{turbine}}
$$

and retrofit savings are computed relative to the baseline cooling burden using the verified total hydraulic-assist power. The hydraulic model now uses UNESCO-based temperature-dependent seawater density together with Darcy-Weisbach losses and the Swamee-Jain friction-factor approximation. Failure logic was also tightened so that scenarios fail when useful minimum velocity cannot be sustained or when the required thermal duty cannot be met. Under the verified rerun, the focused design window retained a `48.50%` PASS rate, of which `4.39%` corresponds to passive standalone cases and `44.10%` corresponds to hybrid retrofit-assist cases. The dominant failure mode remains `INSUFFICIENT_VELOCITY`, with a smaller secondary contribution from unmet thermal duty.

### 3.6 Current conservatism and remaining weakness

The baseline model and auxiliary loads were tightened in the latest iteration to reduce over-optimistic savings. Even so, the remaining savings values are still high enough to justify caution. Therefore, all numerical savings results in this manuscript should be read as **provisional upper-bound research outputs**, not final deployment claims.

## 4. Results

### 4.1 Stage 1: broad screening

Stage 1 screened `24,000` scenarios across a broad parameter space. The results were highly selective:

- PASS rate: `8.65%`
- FAIL rate: `91.35%`
- Passive standalone PASS rate: `0.00%`
- Hybrid retrofit-assist PASS rate: `8.65%`

The Stage 1 summary demonstrates that Hydra-Cool is not generically successful across arbitrary parameter combinations. Instead, it requires a constrained design window. The dominant failure mode in this stage was insufficient velocity, far exceeding all other failure categories.

### 4.2 Stage 2: pruned candidate window

Stage 2 reduced the design space to `543` candidate scenarios selected for relevance to concept development. This step is important because it converts the campaign from exploratory brute force into directed engineering search.

Key Stage 2 findings:

- PASS rate: `24.13%`
- FAIL rate: `75.87%`
- Passive standalone PASS rate: `0.00%`
- Hybrid retrofit-assist PASS rate: `24.13%`

The most informative result from Stage 2 is not only the higher PASS fraction, but the preservation of the same qualitative message: success remains overwhelmingly hybrid, and low velocity remains the primary failure mechanism.

### 4.3 Stage 3: high-resolution focus window

Stage 3 evaluated `995,328` scenarios in the narrowed design window and provides the clearest current picture of feasibility:

- PASS rate: `48.50%`
- FAIL rate: `51.50%`
- Passive standalone PASS rate: `4.39%`
- Hybrid retrofit-assist PASS rate: `44.10%`

This is the strongest result in the repository to date. It shows that once the design space is constrained to the most promising region, Hydra-Cool becomes plausible at meaningful scale. However, the success mode is still dominated by hybrid retrofit assist rather than passive standalone circulation.

### 4.4 Best observed operating patterns

The strongest-performing Stage 3 cases cluster around:

- IT load near the upper end of the study range
- Pipe diameter near `1.0–1.2 m`
- Two-pipe configurations
- High vertical lift
- High `Delta T`
- Low heat-exchanger pressure loss

The best currently observed Stage 3 PASS case has:

- IT load: `200 MW`
- Pipe diameter: `1.2 m`
- Vertical lift: `250 m`
- Delta T: `40 C`
- HX pressure drop: `10 kPa`
- Energy savings fraction: approximately `82.0%`

That scenario is physically interesting because it reaches passive-standalone feasibility, but it should not be interpreted as representative of the whole design window.

### 4.5 Dominant failure mode

Across the campaign, the dominant hydraulic failure mechanism is **insufficient velocity**. This finding is consistent in Stage 1, Stage 2, and Stage 3. The implication is straightforward: the limiting factor is not the existence of buoyancy itself, but whether that buoyancy can support useful circulation speeds under realistic geometric and pressure-drop constraints. A smaller secondary failure family arises from scenarios that cannot satisfy the thermal duty even before a positive retrofit benefit can be established.

### 4.6 Parameter importance

Sensitivity analysis in the focused window identifies the following dominant variables:

1. IT load
2. Heat-exchanger pressure drop
3. Number of pipes
4. Pipe diameter
5. Delta T

These variables should define the next iteration of design refinement, rather than indiscriminate expansion of scenario count.

## 5. Discussion

### 5.1 What the project currently supports

The present evidence supports the following interpretation:

- Hydra-Cool has a real and non-zero design window.
- The most credible operating mode is **hybrid retrofit assist**.
- Gravity and buoyancy can offset a substantial fraction of hydraulic losses in selected cases.
- Passive standalone operation exists, but it is rare and should not be treated as the default design target.

This is a scientifically useful outcome. It means the idea survives physical scrutiny, but in a narrower and more disciplined form than a purely passive narrative would suggest.

### 5.2 What the results do not yet prove

The current results do **not** yet prove that Hydra-Cool can deliver `80%` or `90%` energy savings in practice. Those numbers remain too high to accept without stronger calibration against real data-center cooling baselines, part-load effects, control logic, and balance-of-plant parasitics.

In other words, the project has moved past the question of *whether there is any window at all*, but it has not yet earned the right to claim final savings percentages with publication-level confidence.

### 5.3 Scientific meaning of negative net head

Earlier versions of the analysis risked misinterpretation by treating negative net head as if it automatically invalidated useful scenarios. The current formulation resolves that ambiguity. Negative net head is incompatible with passive standalone circulation, but it can still be consistent with **valuable retrofit operation** if the system reduces net cooling energy when integrated into an existing plant. This clarification is one of the most important conceptual corrections in the repository.

## 6. Limitations

The current manuscript should be read with the following limitations in mind:

1. The baseline cooling model is still simplified and likely too favorable to Hydra-Cool.
2. Auxiliary loads remain lumped rather than broken down into component-level control, monitoring, and water-handling parasitics.
3. The model does not yet represent full site-specific bathymetry, intake civil works, or marine operations.
4. The present study is steady-state and does not include startup, control transients, fouling progression, or seasonal dynamics.
5. No external benchmark dataset has yet been used to calibrate the retrofit baseline against operating hyperscale facilities.

These are not minor caveats. They define the most important next steps before any claim of deployment-grade performance should be made.

## 7. Conclusion

Hydra-Cool should currently be understood as a **buoyancy-assisted retrofit cooling concept** with a nontrivial but bounded design window. The simulation campaign indicates that the architecture is not broadly viable as a universal passive standalone solution. However, it does show repeated evidence that buoyancy and gravity can reduce the energy burden of cooling loops when the geometry, thermal lift, and hydraulic losses are tightly controlled.

The present state of the research supports three clear conclusions:

1. **Passive standalone Hydra-Cool is possible, but uncommon.**
2. **Hybrid retrofit assist is the dominant and most credible success mode.**
3. **Velocity sustainability, not buoyancy existence, is the principal engineering bottleneck.**

The scientific path forward is therefore not wider scenario generation, but better calibration: tighter baseline models, stricter auxiliary-load accounting, and progressively more realistic candidate filtering. If those next steps preserve a meaningful energy-reduction window, Hydra-Cool could become a serious research direction for coastal hyperscale cooling retrofits.

## Figures

The current figure set supporting this manuscript is available in:

- [PUBLICATION_FIGURES.md](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/docs/PUBLICATION_FIGURES.md)
- [publication_figures](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/output/publication_figures)

Selected figures:

![Figure 1](../output/publication_figures/figure_01_system_architecture.png)

![Figure 3](../output/publication_figures/figure_03_pressure_balance.png)

![Figure 8](../output/publication_figures/figure_08_design_window_map.png)

## Reproducibility

To regenerate the core study outputs:

```bash
python3 run_hyperscale_study.py
python3 scripts/generate_publication_figures.py
```

The main stage outputs used in this manuscript are:

- [hydra_cool_stage_1_screening_summary.md](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/output/hydra_cool_stage_1_screening_summary.md)
- [hydra_cool_stage_2_candidates_summary.md](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/output/hydra_cool_stage_2_candidates_summary.md)
- [hydra_cool_stage_3_focus_window_summary.md](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/output/hydra_cool_stage_3_focus_window_summary.md)
