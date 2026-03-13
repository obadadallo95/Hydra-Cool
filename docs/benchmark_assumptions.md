# Hydra-Cool Benchmark Assumptions

This document defines the benchmark assumptions used for the Hydra-Cool comparison package.

## Purpose

The benchmark package is intended to provide **comparative research framing**, not a calibrated plant-design claim. For that reason, the benchmark values below are intentionally conservative and are explicitly labeled by evidence type.

## Evidence Categories

- **Reference baseline**: a normalized anchor used for comparison.
- **Engineering estimate**: a transparent conceptual range used where precise repository-backed plant data is not available.
- **Hydra-Cool simulation output**: a value derived from the repository's own Stage 3 focused-window results.
- **Conservative benchmark framing**: a deliberately less optimistic display value used for comparison figures when the raw Hydra-Cool simulation output appears too favorable to treat as field-representative.

## Normalized Energy Burden Index

All benchmark energy values are expressed as a **relative cooling energy burden index**, normalized such that:

$$
\text{Conventional mechanical cooling plant} = 1.00
$$

This normalized index is used instead of absolute MW values because the current repository does not yet contain calibrated site-specific benchmark datasets for competing architectures.

## Assumption Table

| System | Evidence type | Relative cooling energy burden index | Basis |
|--------|---------------|--------------------------------------|-------|
| Conventional cooling tower / mechanical plant | Reference baseline | `1.00` | Defined as the normalization anchor |
| Pumped seawater loop without buoyancy assistance | Engineering estimate | `0.70` central, `0.60–0.85` range | Assumes coastal water-side heat rejection can reduce mechanical cooling burden, but full hydraulic transport still depends strongly on pumping |
| Hydra-Cool hybrid retrofit assist | Hydra-Cool simulation output + conservative benchmark framing | Stage 3 hybrid median `~0.20`; benchmark comparison uses `0.30` central, `0.20–0.45` range | The comparison figure intentionally uses a less optimistic central value than the raw Stage 3 hybrid candidate median to reflect unresolved baseline and auxiliary-load uncertainty |
| Hydra-Cool passive-natural edge cases | Uncommon Hydra-Cool simulation edge-case framing | `0.18` central, `0.15–0.30` indicative range | Included only as an uncommon edge case; not treated as the main expected design mode |

## Positioning Matrix Indices

The benchmark positioning matrix uses qualitative normalized indices on a `0–1` scale:

- **Active pumping dependence index**
  - `0.0` = very low dependence on active pumping
  - `1.0` = very high dependence on active pumping
- **Passive hydraulic contribution index**
  - `0.0` = negligible passive hydraulic contribution
  - `1.0` = dominant passive hydraulic contribution

These values are not measured plant data; they are transparent engineering judgments used to place the architectures relative to one another.

| System | Active pumping dependence index | Passive hydraulic contribution index | Basis |
|--------|---------------------------------|--------------------------------------|-------|
| Conventional cooling tower / mechanical plant | `0.95` | `0.05` | Cooling and circulation remain dominated by active machinery |
| Pumped seawater loop without buoyancy assistance | `0.85` | `0.10` | Water-side rejection improves source conditions but does not materially reduce hydraulic dependence on pumps |
| Hydra-Cool hybrid retrofit assist | `0.55` | `0.65` | Pumping still required, but buoyancy and gravity meaningfully offset hydraulic burden |
| Hydra-Cool passive-natural edge cases | `0.10` | `0.95` | Included only to show the edge-case passive limit of the concept |

## Validation Maturity Categories

| System | Validation maturity |
|--------|---------------------|
| Conventional cooling tower / mechanical plant | High / commercially mature |
| Pumped seawater loop without buoyancy assistance | Moderate to high / site-dependent mature practice |
| Hydra-Cool hybrid retrofit assist | Low / research-stage simulation concept |
| Hydra-Cool passive-natural edge cases | Very low / exploratory edge case |

## Benchmark Limitations

1. The benchmark values are normalized and conceptual, not plant-certified performance values.
2. The pumped seawater loop benchmark is an engineering reference estimate, not a repository-calibrated field dataset.
3. Hydra-Cool benchmark values are informed by repository simulation outputs but deliberately adjusted conservatively for public comparison.
4. No lifecycle cost, controls, fouling growth, or site-specific civil works are included in this benchmark layer.
5. The benchmark package is intended as a positioning and framing device rather than a final techno-economic comparison.
