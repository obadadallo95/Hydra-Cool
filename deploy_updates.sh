#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

COMMIT_MESSAGE="${1:-Phase 2 scientific hardening update}"

WHITELIST=(
  "src/engine/hyperscale_study.py"
  "run_hyperscale_study.py"
  "scripts/export_stage_3_final_results.py"
  "deploy_updates.sh"
  "tests/test_hydraulic_physics.py"
  "README.md"
  "RELEASE_NOTES.md"
  "docs/MANUSCRIPT.md"
  "docs/PHASE_2_SUMMARY.md"
  "docs/JOURNAL_STYLE_MANUSCRIPT.md"
  "docs/paper_submission.md"
  "docs/latex/manuscript.tex"
  "output/hydra_cool_stage_3_focus_window_summary.json"
  "output/hydra_cool_stage_3_focus_window_summary.md"
  "output/hydra_cool_stage_3_focus_window_sensitivity.csv"
  "output/hydra_cool_stage_3_focus_window_top_configs.csv"
  "output/hydra_cool_stage_3_final_results.csv"
)

EXCLUDE_PATTERNS=(
  "output/hydra_cool_stage_3_focus_window_dataset.csv"
  "output/hydra_cool_focus_window_dataset.csv"
  ".DS_Store"
)

echo "Repository: $ROOT_DIR"
echo "Branch: $(git branch --show-current)"
echo
echo "Staging whitelist:"
printf '  - %s\n' "${WHITELIST[@]}"
echo
echo "Explicit exclusions:"
printf '  - %s\n' "${EXCLUDE_PATTERNS[@]}"
echo

for path in "${WHITELIST[@]}"; do
  if [[ -e "$path" ]]; then
    git add "$path"
  fi
done

echo "Staged changes:"
git diff --cached --stat
echo
echo "Git status after staging:"
git status --short
echo

git commit -m "$COMMIT_MESSAGE"
git push origin "$(git branch --show-current)"

echo
echo "Push complete."
