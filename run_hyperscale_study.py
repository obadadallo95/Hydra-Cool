"""
Run the large Hydra-Cool hyperscale scenario study.

Usage:
    python3 run_hyperscale_study.py
"""

import os

from src.engine.hyperscale_study import HydraCoolHyperscaleStudy


OUTPUT_DIR = "output"


def main():
    print("Hydra-Cool: running retrofit-assist scenario exploration...")
    study = HydraCoolHyperscaleStudy()
    _, summary, sensitivity = study.run(output_dir=OUTPUT_DIR)

    print(f"Scenarios evaluated: {summary['scenario_count']}")
    print(f"PASS rate: {summary['pass_rate']:.2%}")
    print(f"MARGINAL rate: {summary['marginal_rate']:.2%}")
    print(f"FAIL rate: {summary['fail_rate']:.2%}")
    print(f">=10% retrofit energy reduction rate: {summary['target_10pct_rate']:.2%}")
    print(f"Retrofit-assist PASS rate: {summary['hybrid_assisted_pass_rate']:.2%}")
    print(f"Passive-natural PASS rate: {summary['passive_natural_pass_rate']:.2%}")
    print("Top sensitivity drivers:")
    for _, row in sensitivity.head(5).iterrows():
        print(f"  - {row['parameter']}: importance={row['importance_score']:.3f}")
    print(f"Artifacts written to: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()
