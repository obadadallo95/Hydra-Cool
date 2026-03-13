# Phase 2 Scientific Hardening Summary

This file contains short, publication-ready summaries of the Phase 2 Hydra-Cool update.

## Manuscript-Ready Summary

Phase 2 of the Hydra-Cool repository focused on scientific hardening of the Stage 3 focused design window. In this update, the system was formalized primarily as a `HYBRID_RETROFIT_ASSIST` architecture while retaining passive-natural circulation as a reportable but secondary operating class. The simulation engine was revised so that total assisted cooling power is evaluated as \(P_{\mathrm{Hydra,total}} = P_{\mathrm{pump,assist}} + P_{\mathrm{aux}} - P_{\mathrm{turbine}}\), and retrofit savings are computed relative to the baseline cooling burden using the verified total hydraulic-assist power. The hydraulic model now uses UNESCO-based temperature-dependent seawater density together with Darcy-Weisbach losses and the Swamee-Jain friction-factor approximation. Failure logic was also tightened so that scenarios fail when useful minimum velocity cannot be sustained or when the required thermal duty cannot be met. Under this verified rerun, the focused design window retained a `48.50%` PASS rate, of which `4.39%` corresponds to passive standalone cases and `44.10%` corresponds to hybrid retrofit-assist cases. The dominant failure mode remains `INSUFFICIENT_VELOCITY`, with a smaller secondary contribution from unmet thermal duty.

## Release-Ready Summary

- Phase 2 hardens the Hydra-Cool model around the `HYBRID_RETROFIT_ASSIST` interpretation.
- Pump-assist power is now explicitly included in total assisted cooling energy.
- Seawater density is evaluated with a UNESCO-based temperature-dependent formulation.
- Hydraulic losses continue to use Darcy-Weisbach with the Swamee-Jain approximation.
- Failure logic now rejects scenarios that cannot sustain minimum useful velocity or required thermal duty.
- The verified Stage 3 rerun retains a `48.50%` PASS rate:
  - `4.39%` passive standalone
  - `44.10%` hybrid retrofit assist
- The dominant failure mode remains `INSUFFICIENT_VELOCITY`.

## Suggested Use

- Use the manuscript-ready paragraph in `MANUSCRIPT.md`, `JOURNAL_STYLE_MANUSCRIPT.md`, or a methods/results addendum.
- Use the release-ready bullets in `RELEASE_NOTES.md`, GitHub release text, or Zenodo record notes.
