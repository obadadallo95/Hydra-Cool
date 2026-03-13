# Hydra-Cool v2026.1

## Release Title

**Hydra-Cool v2026.1: Open Research Release for Buoyancy-Assisted Retrofit Cooling**

## Summary

This release packages the current open research state of Hydra-Cool as a buoyancy-assisted retrofit cooling concept for coastal hyperscale data centers.

The repository now includes:

- a staged simulation campaign,
- focused design-window studies,
- publication-grade scientific figures,
- manuscript and journal-style writing packages,
- LaTeX and BibTeX source files,
- citation metadata and repository licensing.

Hydra-Cool should currently be interpreted primarily as a **hybrid retrofit assist architecture**, not as a universally passive standalone cooling replacement.

## Included in This Release

### Research and modeling

- staged Hydra-Cool simulation workflow:
  - Stage 1 broad screening
  - Stage 2 candidate pruning
  - Stage 3 focused design window
- feasibility classification for:
  - PASS
  - MARGINAL
  - FAIL
- distinction between:
  - passive standalone operation
  - hybrid retrofit assist operation
  - optional turbine recovery layer

### Outputs

- summary datasets and top-configuration tables
- sensitivity analyses
- publication-grade figures in PNG, SVG, and PDF
- manuscript materials in Markdown and LaTeX

### Documentation

- updated README
- `CITATION.cff`
- MIT license
- concept origin and citation guidance

## Key Findings

- The focused design window reports a PASS rate of approximately `48.50%`.
- The dominant viable operating mode is **hybrid retrofit assist**.
- Passive standalone operation exists but remains uncommon.
- The dominant failure mechanism is **insufficient flow velocity**.
- The strongest controlling variables are:
  - IT load
  - heat-exchanger pressure drop
  - number of pipes
  - pipe diameter
  - temperature rise (`Delta T`)

## Scientific Positioning

This release does **not** claim that Hydra-Cool is already validated as a deployment-ready passive cooling plant.

Instead, it presents Hydra-Cool as an **open engineering research project** with:

- a non-zero feasible design window,
- transparent assumptions,
- explicit limitations,
- and a reproducible computational basis for further refinement.

## Limitations

Current results should be interpreted cautiously because:

- baseline cooling assumptions remain simplified,
- auxiliary loads are still modeled conservatively but not yet plant-resolved,
- the model is primarily steady-state,
- marine civil and site-specific constraints are not yet fully embedded.

## Citation

If you use Hydra-Cool in academic work, please cite:

```text
Dallo, O. (2026).
Hydra-Cool: Buoyancy-Assisted Seawater Retrofit Cooling and Feasible Design Windows for Hyperscale Data Centers.
Hydra-Cool Open Research Project.
GitHub: https://github.com/obadadallo95/Hydra-Cool
DOI: to be assigned by Zenodo for this archival release.
```

## Concept Origin

**Concept origin:** Obada Dallo (2026)  
**Project type:** Hydra-Cool open engineering research project

## Notes on Large Data

Two full high-resolution dataset files were intentionally kept out of the GitHub commit history because they are too large for standard GitHub repository storage. These should be attached separately as release assets or archived via Zenodo if needed.
