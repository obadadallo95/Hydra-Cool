# Hydra-Cool: Buoyancy-Assisted Seawater Retrofit Cooling and Feasible Design Windows for Hyperscale Data Centers

**Journal-style manuscript draft**

**Suggested running title:** Hydra-Cool retrofit cooling for hyperscale facilities

## Abstract

Hydra-Cool is a buoyancy-assisted seawater cooling concept intended to reduce the electrical burden of hyperscale data center cooling through deep-water heat rejection, density-driven hydraulic assistance, elevated discharge storage, gravity return flow, and optional micro-hydropower recovery. The central question addressed in this study is not whether Hydra-Cool can operate as a universally passive replacement for conventional cooling plants, but whether it can function as a practical retrofit-assist layer that materially reduces cooling energy in large coastal facilities. The modeling framework combines heat-removal constraints, seawater density variation, buoyancy pressure generation, Darcy-Weisbach friction losses, heat-exchanger pressure losses, pump assistance, and optional turbine recovery [1,3,7-9]. A staged simulation campaign was used to progressively refine the design space: a broad screening study (`24,000` scenarios), a pruned candidate study (`543` scenarios), and a focused high-resolution design-window study (`995,328` scenarios). The current results indicate that passive standalone operation is rare, whereas hybrid retrofit assist dominates the viable solution space. In the focused design window, the verified rerun reports a `48.50%` PASS rate, with `4.39%` of all cases classified as passive standalone and `44.10%` classified as hybrid retrofit assist. The dominant failure mode across all stages is insufficient velocity, with a smaller secondary contribution from unmet thermal duty. Sensitivity analysis shows that IT load, heat-exchanger pressure drop, number of pipes, pipe diameter, and temperature rise are the primary feasibility drivers. These results support the interpretation of Hydra-Cool as a constrained but nontrivial retrofit cooling pathway. However, the current energy-savings estimates remain too optimistic to be treated as publication-final and require stricter calibration against real data-center cooling baselines and auxiliary loads.

**Keywords:** data center cooling, seawater cooling, buoyancy-assisted flow, natural circulation, retrofit cooling, hydraulic feasibility

## 1. Introduction

Data center cooling has become a first-order energy systems problem as computational density and AI-related electrical demand continue to rise [2,5,6]. Conventional facilities rely on mechanically driven chillers, pumps, cooling towers, and associated balance-of-plant subsystems to move heat away from IT equipment. While these systems are mature and deployable, their parasitic energy demand remains substantial and can limit both economic and environmental performance [3-6].

Hydra-Cool examines whether a portion of that cooling burden can be offset by passive physical mechanisms. The concept combines deep cold seawater intake with a heat exchanger that absorbs IT thermal load, followed by a buoyancy-driven vertical leg that exploits density reduction in the heated fluid. An elevated discharge reservoir and gravity return line complete the hydraulic loop, while a small turbine may recover some energy if sufficient recoverable head remains. The engineering objective is modest but potentially valuable: reduce net cooling energy, not create perpetual motion and not assume universal self-powered circulation.

That distinction is essential. Earlier interpretations of buoyancy-assisted cooling concepts often drift toward binary framing: either the loop is fully passive and therefore successful, or it requires pumping and is therefore invalid. Such framing is not appropriate for retrofit engineering. A coastal data center may benefit materially from a system that offsets a large share of hydraulic losses while still requiring controlled pump assistance. In this manuscript, the term *success* is therefore defined primarily by retrofit energy reduction under realistic hydraulic constraints, rather than by passive purity alone.

## 2. Physical Basis and Modeling Assumptions

The Hydra-Cool model is built on standard engineering relationships:

1. Heat removal requirement  
   `\dot{m}_{req} = P_{thermal} / (C_p \Delta T)`

2. Buoyancy pressure generation  
   `\Delta P_{buoyancy} = (\rho_{cold} - \rho_{hot}) g H`

3. Hydraulic loss balance  
   `\Delta P_{losses} = \Delta P_{friction} + \Delta P_{minor} + \Delta P_{HX}`

4. Hybrid total power  
   `P_{Hydra,total} = P_{pump,assist} + P_{aux} - P_{turbine}`

Seawater density is approximated using standard UNESCO seawater property algorithms [1]. Hydraulic resistance is evaluated with a Darcy-Weisbach formulation and an explicit turbulent-flow friction-factor approximation derived from Swamee and Jain [7]. The treatment of hydraulic transients and water-hammer considerations in the broader research repository follows established numerical water-hammer literature [8]. Natural-circulation behavior is interpreted in the spirit of closed-loop thermosyphon analysis, where buoyancy and gravitational return govern the net circulation potential [9,10].

The current model assumes a single-salinity seawater approximation, steady-state hydraulic behavior, and simplified auxiliary loads. Those assumptions are acceptable for early-stage design-window mapping, but they are not sufficient for final techno-economic claims. The model therefore should be read as a screening and prioritization tool rather than a deployment-certified plant simulator.

## 3. Methods

### 3.1 Retrofit-centered interpretation

Hydra-Cool is modeled primarily as a **retrofit assist architecture** layered onto an existing cooling plant. Three operating layers are tracked:

1. `PASSIVE_STANDALONE`: natural circulation alone sustains the thermal duty within velocity limits.
2. `HYBRID_RETROFIT_ASSIST`: the loop is hydraulically useful and reduces cooling energy, but pump assistance remains necessary.
3. `TURBINE_RECOVERY_ACTIVE`: optional energy recovery is present, treated as a bonus layer rather than a required success condition.

### 3.2 Stage-based campaign

To avoid wasting computation on uninformative regions of the design space, the simulation campaign was structured in three stages:

| Stage | Purpose | Scenario count |
|------|---------|----------------|
| Stage 1 | Broad screening | 24,000 |
| Stage 2 | Candidate pruning | 543 |
| Stage 3 | High-resolution focus window | 995,328 |

Stage 1 was intentionally broad. Stage 2 excluded configurations that did not help develop the concept further. Stage 3 concentrated the computational effort in the most promising design window, centered on moderate pipe diameters, high lift, high thermal rise, and low-to-moderate heat-exchanger loss.

### 3.3 Classification

Each scenario is classified by hydraulic feasibility and energy effect:

- **PASS**: hydraulically feasible and at least `10%` retrofit cooling-energy reduction
- **MARGINAL**: hydraulically feasible and at least `2%` but less than `10%` reduction
- **FAIL**: hydraulically infeasible or insufficient energy benefit

The present workflow therefore distinguishes clearly between *circulation viability* and *energy usefulness*.

## 4. Results

### 4.1 Stage 1: broad screening

The broad screening stage confirms that Hydra-Cool is not a generic solution over arbitrary parameter combinations:

- PASS rate: `8.65%`
- FAIL rate: `91.35%`
- Passive standalone PASS rate: `0.00%`
- Hybrid retrofit-assist PASS rate: `8.65%`

The strongest conclusion from Stage 1 is that low flow velocity dominates the failure population. This means the core bottleneck is not whether buoyancy exists, but whether that buoyancy can be converted into useful flow under realistic hydraulic losses.

### 4.2 Stage 2: candidate pruning

After pruning the design space to a candidate region relevant to concept development, the results improve:

- PASS rate: `24.13%`
- FAIL rate: `75.87%`
- Passive standalone PASS rate: `0.00%`
- Hybrid retrofit-assist PASS rate: `24.13%`

The importance of Stage 2 is methodological. It demonstrates that development should proceed by structured exclusion of weak scenario families, not by indefinite expansion of random sweeps.

### 4.3 Stage 3: focused design window

The focused Stage 3 window provides the clearest current view of feasibility:

- PASS rate: `48.50%`
- FAIL rate: `51.50%`
- Passive standalone PASS rate: `4.39%`
- Hybrid retrofit-assist PASS rate: `44.10%`

This result indicates that Hydra-Cool possesses a real design window when the geometry and thermal conditions are chosen carefully. However, the dominant success mode remains **hybrid retrofit assist**, not passive standalone circulation.

### 4.4 Design trends

The strongest-performing Stage 3 cases generally occur near:

- IT load near the upper portion of the study range
- Pipe diameter around `1.0-1.2 m`
- Two-pipe configurations
- High vertical lift
- High `Delta T`
- Low heat-exchanger pressure drop

The strongest currently observed passive case occurs near `200 MW` load, `1.2 m` pipe diameter, `250 m` lift, and `10 kPa` heat-exchanger loss. That case is physically interesting, but it should be treated as an edge case inside the design window rather than as the default operating regime.

### 4.5 Parameter importance

Sensitivity ranking in the focused window identifies the following principal variables:

1. IT load
2. Heat-exchanger pressure drop
3. Number of pipes
4. Pipe diameter
5. Delta T

These parameters should define the next phase of the research rather than further undirected scenario expansion.

## 5. Discussion

The present results support a narrower but scientifically stronger interpretation of Hydra-Cool than early concept framing suggested. The project now supports the claim that buoyancy-assisted seawater cooling has a meaningful design window as a retrofit-assist architecture. It does **not** yet support the stronger claim that passive standalone Hydra-Cool should be considered the primary expected operating mode for deployment-scale systems.

This distinction matters for two reasons. First, it reframes negative net head correctly: negative net head invalidates passive-only claims, but not necessarily retrofit usefulness if the net cooling-energy burden still falls. Second, it aligns the concept with the engineering reality of legacy data centers, where additive assist architectures are often more practical than full-plant replacement [3-6].

At the same time, an important caution remains. Even after tightening the baseline and auxiliary assumptions, the savings estimates remain high enough to justify skepticism. The model clearly establishes a feasibility window, but it does not yet justify publication-final claims of `70-80%` savings without stronger calibration against real-world cooling-plant performance, part-load behavior, controls, and marine civil constraints.

## 6. Benchmark Positioning Against Conventional and Seawater-Based Cooling Architectures

To strengthen research framing, Hydra-Cool was also positioned against three recognizable reference architectures: a conventional mechanically driven cooling plant, a pumped seawater loop without buoyancy assistance, and uncommon Hydra-Cool passive-natural edge cases. This benchmark is not intended as a calibrated techno-economic comparison. Instead, it provides a conservative comparative layer showing where Hydra-Cool sits relative to known cooling approaches.

| System | Evidence type | Relative cooling energy burden index* | Pump dependence | Passive contribution | Validation maturity |
|--------|---------------|----------------------------------------|-----------------|---------------------|--------------------|
| Conventional cooling tower / mechanical plant | Reference baseline | `1.00` | Very high | Very low | High |
| Pumped seawater loop without buoyancy assistance | Engineering estimate | `0.70` central, `0.60–0.85` range | High | Low | Moderate to high |
| Hydra-Cool hybrid retrofit assist | Stage 3 simulation-informed, conservatively framed | `0.30` central, `0.20–0.45` range | Moderate | High partial contribution | Low / research-stage |
| Hydra-Cool passive-natural edge cases | Uncommon simulation edge-case framing | `0.18` central, `0.15–0.30` indicative range | Very low | Very high | Very low / exploratory |

\*Normalized such that the conventional mechanical plant equals `1.00`.

The comparison supports a cautious but useful interpretation. Hydra-Cool hybrid retrofit assist appears potentially more attractive than a purely pumped seawater loop in the narrow case where buoyancy and gravity meaningfully offset hydraulic burden, but it remains far less mature than conventional cooling infrastructure. Passive-natural Hydra-Cool remains scientifically interesting, yet too uncommon and site-sensitive to be treated as the main deployment target.

## 7. Limitations

The major limitations of the current study are:

1. The baseline cooling model is still simplified and likely remains favorable to Hydra-Cool.
2. Auxiliary loads are lumped rather than resolved into plant-level subsystems.
3. The model is steady-state and does not include transient controls, startup, seasonal operation, or fouling growth.
4. Site-specific bathymetry, marine intake civil design, and regulatory constraints are not yet embedded in the performance model.
5. The study remains a design-window mapping exercise, not a validated plant digital twin.

These limitations define the next research priorities.

## 8. Conclusion

Hydra-Cool currently appears most promising as a **buoyancy-assisted retrofit cooling architecture** for coastal hyperscale data centers. The simulation campaign shows that:

1. Hydra-Cool does have a non-zero and mappable feasible design window.
2. Hybrid retrofit assist is the dominant viable mode.
3. Passive standalone operation exists but is uncommon.
4. Flow-velocity sustainability is the primary engineering bottleneck.

The most useful path forward is therefore not a broader random search, but sharper calibration and candidate refinement. If stricter baseline and auxiliary models still preserve a meaningful retrofit benefit window, Hydra-Cool could become a serious engineering pathway for low-energy coastal cooling retrofits.

## Data, Code, and Figures

Core outputs used in this manuscript:

- [hydra_cool_stage_1_screening_summary.md](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/output/hydra_cool_stage_1_screening_summary.md)
- [hydra_cool_stage_2_candidates_summary.md](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/output/hydra_cool_stage_2_candidates_summary.md)
- [hydra_cool_stage_3_focus_window_summary.md](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/output/hydra_cool_stage_3_focus_window_summary.md)
- [PUBLICATION_FIGURES.md](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/docs/PUBLICATION_FIGURES.md)

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
