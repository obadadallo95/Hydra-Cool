# Benchmark Package Notes

This note explains how the Hydra-Cool benchmark-comparison package was produced.

## What the benchmark package is

The benchmark package is a **comparative framing layer** for the Hydra-Cool research repository. Its role is to show where Hydra-Cool sits relative to conventional and seawater-based alternatives without overstating scientific certainty.

## What the benchmark package is not

- It is **not** a field-validated plant comparison.
- It is **not** a lifecycle cost model.
- It is **not** proof that Hydra-Cool outperforms existing cooling systems in practice.

## Data provenance

The benchmark package mixes three classes of information:

1. **Reference baseline**
   - Conventional mechanical plant normalized to `1.00`

2. **Engineering reference estimate**
   - Pumped seawater loop without buoyancy assistance
   - used only as a conceptual coastal comparison baseline

3. **Hydra-Cool repository outputs**
   - Stage 3 focused design window summary
   - `output/hydra_cool_stage_3_final_results.csv`

## Conservative treatment of Hydra-Cool values

The Stage 3 hybrid candidate dataset produces a median normalized cooling-energy burden near `0.20` relative to the internal baseline. For public benchmark positioning, the benchmark package deliberately uses a **more conservative central comparison value of `0.30`** with a wider range of `0.20–0.45`. This avoids presenting the current simulation outputs as if they were already field-calibrated plant benchmarks.

## How to regenerate the figures

Run:

```bash
python3 scripts/generate_benchmark_figures.py
```

This writes:

- `figures/benchmark_energy_comparison.png`
- `figures/benchmark_energy_comparison.svg`
- `figures/benchmark_positioning_matrix.png`
- `figures/benchmark_positioning_matrix.svg`
- `figures/benchmark_table_summary.png`
- `figures/benchmark_table_summary.svg`

## Suggested citation language in comparative contexts

When discussing the benchmark package, the recommended phrasing is:

> The benchmark comparison is intended as a positioning and framing device rather than a fully calibrated techno-economic comparison.

This wording should remain consistent across README, manuscript, and release material.
