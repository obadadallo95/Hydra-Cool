"""
Export the focused Hydra-Cool Stage 3 candidate set used for Phase 2 review.

Usage:
    python3 scripts/export_stage_3_final_results.py
"""

from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.engine.hyperscale_study import HydraCoolHyperscaleStudy

OUTPUT_DIR = ROOT / "output"
FOCUS_DATASET = OUTPUT_DIR / "hydra_cool_stage_3_focus_window_dataset.csv"
FINAL_RESULTS = OUTPUT_DIR / "hydra_cool_stage_3_final_results.csv"


def main() -> None:
    study = HydraCoolHyperscaleStudy()
    if FOCUS_DATASET.exists():
        focus_window = pd.read_csv(FOCUS_DATASET)
    else:
        print("Stage 3 focus-window dataset not found; generating it now...")
        focus_window = study.generate_focus_window_sweep()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        focus_window.to_csv(FOCUS_DATASET, index=False)

    final_results = study.build_stage_3_final_results(focus_window)
    final_results.to_csv(FINAL_RESULTS, index=False)
    print(f"Exported {len(final_results)} ranked Stage 3 candidates to: {FINAL_RESULTS}")


if __name__ == "__main__":
    main()
