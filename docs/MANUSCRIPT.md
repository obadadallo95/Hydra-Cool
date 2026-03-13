# Hydra-Cool: Mapping the Feasible Design Window for Buoyancy-Assisted Retrofit Cooling in Hyperscale Data Centers

**Draft scientific manuscript**

**Project:** Hydra-Cool open research repository  
**Author:** Obada Dallo  
**Status:** Research draft for internal review and iterative refinement

## Abstract

Hydra-Cool is a buoyancy-assisted cooling concept intended to reduce the energy demand of hyperscale data center cooling systems by combining deep-water heat rejection, density-driven hydraulic assistance, elevated discharge storage, gravity return flow, and optional turbine recovery. The central research question is not whether Hydra-Cool can replace conventional cooling infrastructure outright, but whether it can serve as a retrofit assist layer that offsets a meaningful fraction of cooling energy in large coastal facilities.

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

## 2. Related Work

Hydra-Cool sits at the intersection of several established engineering literature streams, but it is not identical to any one of them. The first relevant body of work is the broad literature on data center cooling systems, including conventional mechanical plants, economizer strategies, and the transition toward direct liquid cooling for high-density computing. Reviews of data center thermal management consistently show that cooling efficiency depends not only on the heat sink itself, but also on how effectively the system reduces transport losses from chip scale to plant scale [3,5,6,11]. This literature provides the baseline context against which Hydra-Cool must be interpreted: not as a replacement for all cooling architectures, but as one candidate approach for lowering the energy burden of heat rejection in specific coastal settings.

The second literature stream concerns thermosiphons, natural-circulation loops, and buoyancy-driven heat transport. Thermosiphon and natural-circulation systems have long been studied in thermal engineering because they can move heat with limited or even no active pumping under favorable geometric and thermal conditions [4,9]. That literature is directly relevant to Hydra-Cool because the project relies on the same underlying physical idea that density differences can generate useful circulation pressure. At the same time, most thermosiphon research is not written for data center plant retrofits, nor is it generally framed around large marine heat-rejection loops serving hyperscale digital infrastructure.

The third relevant stream is seawater-based cooling and coastal thermal infrastructure. Sea water air conditioning and related marine heat-rejection concepts show that cold seawater can be an effective thermal resource where geography and civil design permit [10]. These systems demonstrate that marine cooling can be technically meaningful, but they are usually analyzed as pumped heat-rejection infrastructure or district-scale cooling systems rather than buoyancy-assisted retrofit loops for existing data center plants.

Hydra-Cool therefore overlaps conceptually with standard seawater cooling, natural circulation, and thermosiphon behavior, but it should not be reduced to any of them. It is not simply a pumped seawater loop, because it explicitly seeks hydraulic assistance from buoyancy and gravity. It is not simply a passive thermosiphon, because the dominant viable operating mode in the repository is `HYBRID_RETROFIT_ASSIST`, not universal passive standalone circulation. It is also not just a generic marine cooling proposal, because its central framing is that of a **retrofit hydraulic-assist architecture** integrated with large coastal data center cooling systems.

The gap addressed by Hydra-Cool is therefore narrow but scientifically defensible: existing work covers seawater cooling, natural circulation, and thermosiphon behavior, but limited work frames these ideas explicitly as a retrofit-assist hydraulic architecture for large coastal data center cooling systems.

## 3. Physical Basis

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

## 4. Methods

### 4.1 System interpretation

The current simulation campaign treats Hydra-Cool primarily as a **retrofit assist layer** for an existing cooling system. This distinction is central. A scenario is not required to support purely passive circulation to be useful. Instead, the principal test is whether buoyancy and gravity materially offset the energy demand of a legacy cooling plant while remaining hydraulically feasible.

Three success layers are tracked explicitly:

1. `PASSIVE_STANDALONE`: natural circulation alone sustains the thermal duty within velocity constraints.
2. `HYBRID_RETROFIT_ASSIST`: the loop remains hydraulically useful, but pump assistance is still required.
3. `TURBINE_RECOVERY_ACTIVE`: optional energy recovery is present; this is treated as a beneficial secondary effect rather than a core success condition.

### 4.2 Stage-based campaign design

The simulation was reorganized into three stages to avoid the problem of exploring large numbers of scenarios without improving the design direction.

| Stage | Purpose | Scenario count | Output |
|------|---------|----------------|--------|
| Stage 1 | Broad screening of the design space | 24,000 | Identify dominant bottlenecks |
| Stage 2 | Pruned candidate window | 543 | Remove configurations that do not support concept development |
| Stage 3 | High-resolution focus-window study | 995,328 | Map the feasible design window in detail |

The progression from Stage 1 to Stage 3 is deliberate. Stage 1 is exploratory. Stage 2 discards scenarios that do not advance the concept. Stage 3 concentrates computational effort inside the most promising design region.

### 4.3 Parameter space

The high-resolution window was chosen around the most useful development region identified by the earlier screening work:

- Pipe diameter: approximately `0.8–1.5 m`
- High vertical lift
- Elevated `Delta T`
- Low to moderate heat-exchanger pressure drop
- IT load in the `50–200 MW` range

This pruning strategy is important because the value of the campaign lies not in raw scenario count, but in progressive elimination of non-productive parts of the design space.

### 4.4 Classification logic

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

### 4.5 Phase 2 scientific hardening

Phase 2 of the repository focused on scientific hardening of the Stage 3 focused design window. In this update, Hydra-Cool was formalized primarily as a `HYBRID_RETROFIT_ASSIST` architecture while retaining passive-natural circulation as a reportable but secondary operating class. The simulation engine was revised so that total assisted cooling power is evaluated as

$$
P_{\mathrm{Hydra,total}} = P_{\mathrm{pump,assist}} + P_{\mathrm{aux}} - P_{\mathrm{turbine}}
$$

and retrofit savings are computed relative to the baseline cooling burden using the verified total hydraulic-assist power. The hydraulic model now uses UNESCO-based temperature-dependent seawater density together with Darcy-Weisbach losses and the Swamee-Jain friction-factor approximation. Failure logic was also tightened so that scenarios fail when useful minimum velocity cannot be sustained or when the required thermal duty cannot be met. Under the verified rerun, the focused design window retained a `48.50%` PASS rate, of which `4.39%` corresponds to passive standalone cases and `44.10%` corresponds to hybrid retrofit-assist cases. The dominant failure mode remains `INSUFFICIENT_VELOCITY`, with a smaller secondary contribution from unmet thermal duty.

### 4.6 Current conservatism and remaining weakness

The baseline model and auxiliary loads were tightened in the latest iteration to reduce over-optimistic savings. Even so, the remaining savings values are still high enough to justify caution. Therefore, all numerical savings results in this manuscript should be read as **provisional upper-bound research outputs**, not final deployment claims.

## 5. Results

### 5.1 Stage 1: broad screening

Stage 1 screened `24,000` scenarios across a broad parameter space. The results were highly selective:

- PASS rate: `8.65%`
- FAIL rate: `91.35%`
- Passive standalone PASS rate: `0.00%`
- Hybrid retrofit-assist PASS rate: `8.65%`

The Stage 1 summary demonstrates that Hydra-Cool is not generically successful across arbitrary parameter combinations. Instead, it requires a constrained design window. The dominant failure mode in this stage was insufficient velocity, far exceeding all other failure categories.

### 5.2 Stage 2: pruned candidate window

Stage 2 reduced the design space to `543` candidate scenarios selected for relevance to concept development. This step is important because it converts the campaign from exploratory brute force into directed engineering search.

Key Stage 2 findings:

- PASS rate: `24.13%`
- FAIL rate: `75.87%`
- Passive standalone PASS rate: `0.00%`
- Hybrid retrofit-assist PASS rate: `24.13%`

The most informative result from Stage 2 is not only the higher PASS fraction, but the preservation of the same qualitative message: success remains overwhelmingly hybrid, and low velocity remains the primary failure mechanism.

### 5.3 Stage 3: high-resolution focus window

Stage 3 evaluated `995,328` scenarios in the narrowed design window and provides the clearest current picture of feasibility:

- PASS rate: `48.50%`
- FAIL rate: `51.50%`
- Passive standalone PASS rate: `4.39%`
- Hybrid retrofit-assist PASS rate: `44.10%`

This is the strongest result in the repository to date. It shows that once the design space is constrained to the most promising region, the current model retains a measurable feasible window. However, the success mode is still dominated by hybrid retrofit assist rather than passive standalone circulation.

### 5.4 Best observed operating patterns

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

### 5.5 Dominant failure mode

Across the campaign, the dominant hydraulic failure mechanism is **insufficient velocity**. This finding is consistent in Stage 1, Stage 2, and Stage 3. The implication is straightforward: the limiting factor is not the existence of buoyancy itself, but whether that buoyancy can support useful circulation speeds under realistic geometric and pressure-drop constraints. A smaller secondary failure family arises from scenarios that cannot satisfy the thermal duty even before a positive retrofit benefit can be established.

### 5.6 Parameter importance

Sensitivity analysis in the focused window identifies the following dominant variables:

1. IT load
2. Heat-exchanger pressure drop
3. Number of pipes
4. Pipe diameter
5. Delta T

These variables should define the next iteration of design refinement, rather than indiscriminate expansion of scenario count.

## 6. Benchmark Positioning Against Conventional and Seawater-Based Cooling Architectures

A benchmark comparison improves research credibility by placing Hydra-Cool relative to more familiar cooling architectures. The purpose of this comparison is not to claim that Hydra-Cool is already competitive with mature field-deployed plants, but to show where the concept sits within a recognizable engineering landscape.

The benchmark package compares Hydra-Cool against:

1. conventional cooling tower / mechanically driven cooling plants,
2. pumped seawater loops without buoyancy assistance,
3. Hydra-Cool hybrid retrofit assist,
4. Hydra-Cool passive-natural edge cases.

The benchmark values are explicitly mixed-source and transparent:

- the conventional plant is the normalized reference baseline,
- the pumped seawater loop is represented by conservative engineering estimate ranges,
- the Hydra-Cool hybrid benchmark is simulation-informed but conservatively framed above the raw Stage 3 hybrid median,
- and passive-natural Hydra-Cool is shown only as an uncommon edge-case class.

| System | Evidence type | Relative cooling energy burden index* | Pump dependence | Passive contribution | Validation maturity |
|--------|---------------|----------------------------------------|-----------------|---------------------|--------------------|
| Conventional cooling tower / mechanical plant | Reference baseline | `1.00` | Very high | Very low | High |
| Pumped seawater loop without buoyancy assistance | Engineering estimate | `0.70` central, `0.60–0.85` range | High | Low | Moderate to high |
| Hydra-Cool hybrid retrofit assist | Stage 3 simulation-informed, conservatively framed | `0.30` central, `0.20–0.45` range | Moderate | High partial contribution | Low / research-stage |
| Hydra-Cool passive-natural edge cases | Uncommon simulation edge-case framing | `0.18` central, `0.15–0.30` indicative range | Very low | Very high | Very low / exploratory |

\*Normalized such that the conventional mechanical plant equals `1.00`.

The comparison suggests that Hydra-Cool is most interesting as a middle-ground coastal concept between fully pump-dominant marine cooling and rare passive natural-circulation edge cases. Relative to a pumped seawater loop, the potential additional value of Hydra-Cool lies in **partial hydraulic assistance** rather than seawater access alone. Relative to a conventional mechanical plant, the concept appears promising as a constrained retrofit path, but not yet as a validated replacement architecture.

This benchmark is intended as a positioning and framing device rather than a fully calibrated techno-economic comparison. Its main limitations are that the conventional and pumped seawater benchmarks are normalized engineering references rather than repository-calibrated field datasets, and that the Hydra-Cool benchmark still inherits uncertainty from the current baseline and auxiliary-load models.

Supporting benchmark assets are available in:

- [BENCHMARK_COMPARISON.md](BENCHMARK_COMPARISON.md)
- [benchmark_assumptions.md](benchmark_assumptions.md)
- [README_BENCHMARK_NOTES.md](README_BENCHMARK_NOTES.md)

## 7. Limitations

The current manuscript should be read with the following limitations in mind:

1. The baseline cooling model is still simplified and likely too favorable to Hydra-Cool.
2. Auxiliary loads remain lumped rather than broken down into component-level control, monitoring, and water-handling parasitics.
3. The model does not yet represent full site-specific bathymetry, intake civil works, or marine operations.
4. The present study is steady-state and does not include startup, control transients, fouling progression, or seasonal dynamics.
5. No external benchmark dataset has yet been used to calibrate the retrofit baseline against operating hyperscale facilities.

These are not minor caveats. They define the most important next steps before any claim of deployment-grade performance should be made.

## 8. Discussion

### 8.1 Interpretation of the main findings

The main result of the repository is that Hydra-Cool has a **non-zero but constrained** feasible design window. The progression from Stage 1 through Stage 3 is important because it shows that the concept does not become stronger through larger scenario counts alone; it becomes clearer through successive refinement. Stage 1 establishes that broad parameter exploration is dominated by failure. Stage 2 shows that targeted pruning improves the signal. Stage 3 demonstrates that, within a narrowed design window, a meaningful pass fraction is retained. The overall pattern supports the interpretation that Hydra-Cool is not a generally self-validating concept, but a conditional one whose plausibility depends on a narrow range of hydraulic and thermal conditions.

The same staged structure also clarifies the operating-mode hierarchy. The dominant viable mode is `HYBRID_RETROFIT_ASSIST`, while passive standalone cases remain uncommon. That distinction is scientifically useful because it replaces an all-or-nothing narrative with a more realistic engineering interpretation: a system may still have value even if it does not eliminate active pumping altogether.

### 8.2 Engineering meaning of the results

The dominant failure mode, `INSUFFICIENT_VELOCITY`, has a straightforward hydraulic meaning. Buoyancy can exist without producing enough circulation to sustain useful thermal duty. This is why vertical lift, pipe count, pipe diameter, and heat-exchanger pressure drop emerge so strongly in the sensitivity results. Large hydraulic penalties or oversized flow area can reduce effective circulation velocity below the range required for meaningful cooling transport. In practical terms, Hydra-Cool appears to be limited less by the existence of buoyancy than by the ability to convert buoyancy into adequate loop flow.

Heat-exchanger pressure drop is especially important because it consumes pressure head in exactly the portion of the loop where the retrofit concept is supposed to create benefit. If that loss becomes too large, the buoyancy contribution is quickly overwhelmed and the system reverts toward a pump-dominant loop. This helps explain why the design space must be narrowed rather than searched blindly: the underlying coupling among thermal lift, loop geometry, and hydraulic resistance is too strong for broad random sweeps to be informative on their own.

### 8.3 Why hybrid retrofit assist is the most credible framing

The current results support a more mature framing in which Hydra-Cool is treated as a **retrofit hydraulic-assist concept** rather than a passive-purity claim. From an engineering perspective, partial passive hydraulic contribution can still be valuable. A cooling retrofit does not need to eliminate pumping to be useful; it only needs to reduce the net burden of active cooling infrastructure in a repeatable and defensible way. This is why negative net head or non-zero pump assist should not automatically be interpreted as conceptual failure. What matters is whether buoyancy and gravity materially offset transport work within a realistic operating envelope.

This framing is also more compatible with the way real infrastructure evolves. Large cooling plants are rarely replaced wholesale by highly idealized passive systems. They are more often improved through partial assistance, operational simplification, or reduced parasitic load. Under that lens, `HYBRID_RETROFIT_ASSIST` is not a fallback interpretation but the most credible current interpretation of the repository's results.

### 8.4 Benchmark interpretation

The benchmark package further clarifies this positioning. Hydra-Cool sits conceptually between conventional pump-dominant cooling architectures and uncommon passive-natural edge cases. Relative to a conventional mechanical plant, it appears promising as a coastal retrofit concept that could reduce cooling-energy burden if the hydraulic conditions are favorable. Relative to a pumped seawater loop, its distinguishing feature is not seawater use by itself, but the attempt to recover part of the hydraulic burden through buoyancy and gravity.

At the same time, the benchmark should not be misread as proof. It is a **conceptual framing layer**, not a calibrated plant-level techno-economic comparison. The conventional and pumped seawater baselines are normalized engineering references, while the Hydra-Cool values are simulation-informed and conservatively framed. The benchmark therefore strengthens context, but it does not replace validation.

### 8.5 Limits of the current claims

The repository still supports only model-based claims. Energy savings remain a function of the current baseline cooling assumptions, auxiliary-load formulation, and steady-state hydraulic treatment. These assumptions may still remain optimistic, particularly when compared against the control sophistication and operational variability of real data center plants. In addition, the present work does not yet account for site-specific marine civil design, fouling growth, seasonal variability, startup and shutdown transients, control logic, or plant-integration penalties. For those reasons, Hydra-Cool should currently be understood as a simulation-based research concept rather than a validated cooling technology.

### 8.6 What would be required for stronger validation

Stronger validation would require several next steps. The baseline plant model should be calibrated more explicitly against measured or literature-supported cooling-plant performance. Dynamic controls and transient behavior should be added so that the concept is evaluated under startup, disturbance, and part-load conditions rather than steady-state operation alone. Marine site constraints, including intake civil works and coastal depth accessibility, should be integrated into scenario selection. Finally, stronger evidence would eventually require experimental or prototype-scale validation. None of those steps has yet been completed in the repository, but together they define a realistic path from conceptual simulation toward more defensible engineering assessment.

## 9. Conclusion

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

## References

[1] Fofonoff NP, Millard RC Jr. *Algorithms for Computation of Fundamental Properties of Seawater*. UNESCO Technical Papers in Marine Science No. 44. Paris: UNESCO; 1983.

[2] The Green Grid. *Recommendations for Measuring and Reporting Overall Data Center Efficiency Version 2: Measuring PUE for Data Centers*. Portland, OR: The Green Grid; 2011.

[3] Ebrahimi K, Jones GF, Fleischer AS. A review of data center cooling technology, operating conditions and the corresponding low-grade waste heat recovery opportunities. *Renew Sustain Energy Rev.* 2014;31:622-638. doi:10.1016/j.rser.2013.12.007

[4] Zhang H, Shao S, Tian C, Zhang K. A review on thermosyphon and its integrated system with vapor compression for free cooling of data centers. *Renew Sustain Energy Rev.* 2018;81(P1):789-798. doi:10.1016/j.rser.2017.08.011

[5] Masanet E, Shehabi A, Lei N, Smith S, Koomey J. Recalibrating global data center energy-use estimates. *Science.* 2020;367(6481):984-986. doi:10.1126/science.aba3758

[6] Shehabi A, Smith SJ, Hubbard A, et al. *2024 United States Data Center Energy Usage Report*. Lawrence Berkeley National Laboratory; 2024. doi:10.71468/P1WC7Q

[7] Swamee PK, Jain AK. Explicit equations for pipe-flow problems. *J Hydraul Div.* 1976;102(5):657-664. doi:10.1061/JYCEAJ.0004542

[8] Pal S, Hanmaiahgari PR, Karney BW. An overview of the numerical approaches to water hammer modelling: The ongoing quest for practical and accurate numerical approaches. *Water.* 2021;13(11):1597. doi:10.3390/w13111597

[9] Swart R, Dobson RT. Thermal-hydraulic simulation and evaluation of a natural circulation thermosyphon loop for a reactor cavity cooling system of a high-temperature reactor. *Nucl Eng Technol.* 2020;52(2):271-278. doi:10.1016/j.net.2019.07.031

[10] Sanjivy K, Marc O, Davies N, Lucas F. Energy performance assessment of sea water air conditioning (SWAC) as a solution toward net zero carbon emissions: A case study in French Polynesia. *Energy Reports.* 2023;9:437-446. doi:10.1016/j.egyr.2022.11.201

[11] Khalaj AH, Halgamuge SK. A review on efficient thermal management of air- and liquid-cooled data centers: From chip to the cooling system. *Applied Energy.* 2017;205:1165-1188. doi:10.1016/j.apenergy.2017.08.037
