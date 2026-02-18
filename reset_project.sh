#!/bin/bash
# ============================================================
# HYDRA-COOL: Project Hard Reset Script
# Transitions to a pure Python Engineering Simulation repo.
# ============================================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "╔══════════════════════════════════════════════════╗"
echo "║   HYDRA-COOL: PROJECT HARD RESET IN PROGRESS    ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# --- PHASE 1: DESTROY OLD STRUCTURE ---
echo "[1/3] Purging legacy directories..."

DIRS_TO_DELETE=("frontend" "backend" "unity_simulator" "engineering_package" "build" ".dart_tool" ".flutter-plugins" ".flutter-plugins-dependencies" "android" "ios" "web" "linux" "macos" "windows" "test")

for dir in "${DIRS_TO_DELETE[@]}"; do
    if [ -d "$dir" ]; then
        rm -rf "$dir"
        echo "  ✗ Deleted: $dir/"
    fi
done

echo "[2/3] Purging legacy root files..."

FILES_TO_DELETE=("automate_everything.sh" "Dockerfile" "pubspec.yaml" "pubspec.lock" "analysis_options.yaml" ".metadata" "HydraCool_Final_Study.pdf")

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "  ✗ Deleted: $file"
    fi
done

# --- PHASE 2: BUILD NEW STRUCTURE ---
echo ""
echo "[3/3] Building clean engineering structure..."

mkdir -p src/engine
mkdir -p src/reports
mkdir -p assets
mkdir -p output

touch src/__init__.py
touch src/engine/__init__.py
touch src/reports/__init__.py

echo "  ✓ Created: src/engine/"
echo "  ✓ Created: src/reports/"
echo "  ✓ Created: assets/"
echo "  ✓ Created: output/"

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║          RESET COMPLETE. READY TO BUILD.         ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "Next: python main.py"
