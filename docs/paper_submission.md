# Paper Submission Package

## Recommended Title

**Hydra-Cool: Buoyancy-Assisted Seawater Retrofit Cooling and Feasible Design Windows for Hyperscale Data Centers**

## Recommended Article Type

- Journal article: full-length research article
- Conference article: extended paper / archival proceedings version

## Submission Template

### Title

Hydra-Cool: Buoyancy-Assisted Seawater Retrofit Cooling and Feasible Design Windows for Hyperscale Data Centers

### Authors

Obada Dallo  
Affiliation to be finalized

### Corresponding Author

Obada Dallo  
Email to be added before submission

### Abstract

Hydra-Cool is a buoyancy-assisted seawater cooling concept intended to reduce the electrical burden of hyperscale data center cooling through deep-water heat rejection, density-driven hydraulic assistance, elevated discharge storage, gravity return flow, and optional micro-hydropower recovery. This study evaluates Hydra-Cool as a retrofit-assist architecture rather than as a universally passive standalone replacement. A staged simulation campaign was used to map the feasible design window using broad screening, candidate pruning, and high-resolution focus-window exploration. The strongest current results show that hybrid retrofit assist dominates the viable solution space, while passive standalone operation remains rare. In the focused design window, the verified rerun reports a PASS rate of approximately `48.50%`, with `44.10%` of all cases belonging to the hybrid retrofit-assist class and `4.39%` belonging to the passive standalone class. The dominant failure mode across all stages is insufficient velocity. Sensitivity analysis identifies IT load, heat-exchanger pressure drop, number of pipes, pipe diameter, and Delta T as the principal feasibility drivers. The results support further development of Hydra-Cool as a constrained retrofit cooling pathway, while also showing that the baseline and auxiliary-load models still need stricter calibration before publication-final savings claims can be defended.

### Keywords

Data center cooling; seawater cooling; buoyancy-assisted flow; retrofit cooling; natural circulation; hydraulic feasibility

### Highlights

- Hydra-Cool was evaluated as a retrofit-assist architecture rather than a standalone passive replacement.
- A three-stage simulation campaign progressively narrowed the feasible design region.
- Hybrid retrofit assist dominated viability; passive standalone operation was uncommon.
- Insufficient flow velocity was the dominant hydraulic failure mechanism.
- IT load, HX pressure drop, number of pipes, pipe diameter, and Delta T controlled success.

### Novelty Statement

The novelty of this work lies in reframing buoyancy-driven cooling as a retrofit-assist problem rather than as an all-or-nothing passive cooling claim. The study also contributes a staged design-window workflow that filters broad scenarios into actionable candidate sets and produces publication-grade visual evidence for feasibility mapping.

## Journal-Style Main Text

### 1. Introduction

Data center cooling is an increasingly important systems-level energy challenge [2-6]. Hydra-Cool is proposed as a seawater-based buoyancy-assisted architecture designed to offset part of the cooling burden in coastal hyperscale facilities. The present work asks whether Hydra-Cool has a real, bounded retrofit design window.

### 2. Methods

The model combines thermal flow requirements, seawater density variation, buoyancy pressure, Darcy-Weisbach loss modeling, heat-exchanger pressure losses, pump assistance, and optional turbine recovery [1,3,7-9]. Scenarios are evaluated in three stages:

- Stage 1: broad screening (`24,000` scenarios)
- Stage 2: candidate pruning (`543` scenarios)
- Stage 3: focused design window (`995,328` scenarios)

### 3. Results

The broad screening stage produced a PASS rate of `8.65%`. After pruning, the candidate window showed a PASS rate of `24.13%`. In the focused design window, the PASS rate increased to `48.50%`, with `44.10%` of all cases belonging to the hybrid retrofit-assist class and `4.39%` belonging to the passive standalone class. Insufficient velocity was the dominant failure mode.

### 4. Discussion

The project currently supports Hydra-Cool most strongly as a hybrid retrofit assist layer. Passive standalone circulation exists in a small subset of the focus window, but it is not the dominant solution path. The current savings numbers remain too optimistic to treat as final and require stronger calibration against real cooling-plant baselines.

### 4A. Benchmark Positioning

The repository now includes a benchmark-comparison package that positions Hydra-Cool against:

- conventional mechanically driven cooling plants,
- pumped seawater loops without buoyancy assistance,
- Hydra-Cool hybrid retrofit assist,
- and uncommon Hydra-Cool passive-natural edge cases.

The benchmark layer is intentionally conservative and normalized. It should be read as a **positioning and framing device**, not as a plant-calibrated techno-economic comparison. In that framing, Hydra-Cool hybrid retrofit assist occupies a scientifically interesting middle ground: less pump-dominant than a fully pumped seawater loop, but much less validated than conventional mature cooling infrastructure.

### 5. Conclusion

Hydra-Cool has a non-zero feasible design window and should currently be treated as a constrained retrofit energy-reduction concept rather than a universal passive cooling replacement. The dominant technical bottleneck is sustaining useful flow velocity under realistic hydraulic losses.

## Conference Adaptation Notes

For a conference submission:

- Keep the abstract and highlights unchanged.
- Compress the Methods and Results sections.
- Use only Figures 1, 3, 4, 8, and 10.
- Focus the paper on the Stage 3 focus-window results.
- Move detailed limitations and extended discussion to an appendix or supplementary note.

## Journal Adaptation Notes

For a journal submission:

- Retain the full staged methodology.
- Expand the baseline calibration section.
- Add a dedicated uncertainty analysis section.
- Add a stronger comparison against conventional liquid-cooling and water-side economizer baselines.
- Include a more explicit site-selection and permitting discussion.

## Figures to Include

- Figure 1: system architecture
- Figure 3: pressure balance
- Figure 4: PASS/FAIL distribution
- Figure 5: parameter importance
- Figure 6: failure modes
- Figure 8: design window map
- Figure 10: hybrid vs passive operation

See:

- [PUBLICATION_FIGURES.md](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/docs/PUBLICATION_FIGURES.md)
- [publication_figures](/Users/obadadallo/Desktop/Cooling_System_Sim/cooling_project/output/publication_figures)

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
