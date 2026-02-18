"""
Hydra-Cool: Master Scenario Runner
====================================
Executes ALL 15 simulation scenarios, captures results,
and generates a comprehensive PDF engineering report.

Usage:
    python run_all_scenarios.py

Author: Obada Dallo
Copyright (c) 2024. All Rights Reserved.
"""

import subprocess
import sys
import os
import time
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos


# ══════════════════════════════════════════════════════════
#  SCENARIO REGISTRY
# ══════════════════════════════════════════════════════════

SCENARIOS = [
    {"id": "v1",  "file": "simulation_v1_base.py",              "title": "Base Thermosiphon Physics",        "focus": "Height sweep, buoyancy, flow rate, power generation"},
    {"id": "v2",  "file": "simulation_v2_advanced.py",          "title": "Advanced Parametric Sweep",         "focus": "Multi-parameter optimization, financial analysis"},
    {"id": "v3",  "file": "simulation_v3_feasibility.py",       "title": "Feasibility Study (Monte Carlo)",   "focus": "NPV, IRR, 20-year lifecycle, 1000-run Monte Carlo"},
    {"id": "v4",  "file": "simulation_v4_benchmark.py",         "title": "Performance Benchmark",             "focus": "Cooling capacity vs traditional systems"},
    {"id": "v5",  "file": "simulation_v5_digital_twin.py",      "title": "Digital Twin Modeling",             "focus": "Real-time system state replication"},
    {"id": "v6",  "file": "simulation_v6_hybrid.py",            "title": "Hybrid Cooling Architecture",      "focus": "Combined active/passive cooling optimization"},
    {"id": "v7",  "file": "simulation_v7_golden.py",            "title": "Golden Scenario (3D Optimization)", "focus": "Worst-case physics with 3D analysis"},
    {"id": "v8",  "file": "simulation_v8_fortress.py",          "title": "Structural Resilience (ODE)",       "focus": "Dynamic structural response via ODE solvers"},
    {"id": "v9",  "file": "simulation_v9_global.py",            "title": "Multi-Region Global Deployment",    "focus": "5+ city comparison with construction scheduling"},
    {"id": "v10", "file": "simulation_v10_depth.py",            "title": "Pipe Depth Optimization",           "focus": "Deep-sea intake pressure and thermal analysis"},
    {"id": "v11", "file": "simulation_v11_unified.py",          "title": "Unified Analysis Framework",        "focus": "Consolidated physics + financials engine"},
    {"id": "v12a","file": "simulation_v12_crashtest.py",        "title": "Crash Test & Stress Analysis",      "focus": "Extreme load scenarios and failure thresholds"},
    {"id": "v12b","file": "simulation_v12_failure_mode.py",     "title": "Failure Mode Analysis (FMEA)",      "focus": "Component-level failure probability"},
    {"id": "v13", "file": "simulation_v13_fid.py",              "title": "Final Integrated Design",           "focus": "Production-ready integrated simulation"},
    {"id": "v14", "file": "simulation_v14_structural_stress.py","title": "3D Structural Stress Test (FEA)",   "focus": "Earthquake M9.0 & missile strike survival"},
]


# ══════════════════════════════════════════════════════════
#  SCENARIO RUNNER
# ══════════════════════════════════════════════════════════

class ScenarioRunner:
    """Executes each scenario and captures output."""

    def __init__(self, scenarios_dir="scenarios"):
        self.scenarios_dir = scenarios_dir
        self.results = []

    def run_all(self):
        """Run every registered scenario and record results."""
        total = len(SCENARIOS)
        print("=" * 65)
        print(f"  HYDRA-COOL: EXECUTING ALL {total} SIMULATION SCENARIOS")
        print("=" * 65)

        for i, scenario in enumerate(SCENARIOS, 1):
            sid = scenario['id']
            fname = scenario['file']
            title = scenario['title']
            filepath = os.path.join(self.scenarios_dir, fname)

            print(f"\n[{i}/{total}] Running {sid}: {title}...")

            if not os.path.exists(filepath):
                print(f"         FILE NOT FOUND: {filepath}")
                self.results.append({
                    **scenario,
                    "status": "SKIPPED",
                    "duration": 0,
                    "output": "File not found.",
                    "exit_code": -1,
                })
                continue

            start = time.time()
            try:
                result = subprocess.run(
                    [sys.executable, filepath],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=os.getcwd(),
                )
                duration = time.time() - start
                output = result.stdout + result.stderr
                exit_code = result.returncode

                status = "PASS" if exit_code == 0 else "FAIL"
                print(f"         Status: {status}  |  Time: {duration:.1f}s  |  Exit: {exit_code}")

            except subprocess.TimeoutExpired:
                duration = 120
                output = "TIMEOUT: Exceeded 120 seconds."
                exit_code = -2
                status = "TIMEOUT"
                print(f"         Status: TIMEOUT")
            except Exception as e:
                duration = time.time() - start
                output = f"ERROR: {str(e)}"
                exit_code = -3
                status = "ERROR"
                print(f"         Status: ERROR - {e}")

            self.results.append({
                **scenario,
                "status": status,
                "duration": round(duration, 1),
                "output": output[:8000],  # Cap at 8KB per scenario
                "exit_code": exit_code,
            })

        # Summary
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        print("\n" + "=" * 65)
        print(f"  COMPLETE: {passed} PASSED | {failed} FAILED | {total - passed - failed} OTHER")
        print("=" * 65)

        return self.results


# ══════════════════════════════════════════════════════════
#  MASTER PDF REPORT
# ══════════════════════════════════════════════════════════

class MasterReport(FPDF):
    """Generates the comprehensive all-scenarios PDF report."""

    CYAN = (0, 255, 204)
    DARK = (7, 11, 13)
    WHITE = (255, 255, 255)
    GREEN = (0, 200, 80)
    RED = (220, 50, 50)
    YELLOW = (255, 200, 0)
    GRAY = (180, 180, 180)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*self.GRAY)
            self.cell(0, 10, "Hydra-Cool - Master Simulation Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
            self.line(10, 15, 200, 15)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*self.GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")

    def build_cover(self):
        self.add_page()
        self.set_fill_color(*self.DARK)
        self.rect(0, 0, 210, 297, "F")

        self.set_text_color(*self.CYAN)
        self.set_font("Helvetica", "B", 40)
        self.ln(70)
        self.cell(0, 20, "HYDRA-COOL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

        self.set_text_color(*self.WHITE)
        self.set_font("Helvetica", "", 18)
        self.cell(0, 12, "Master Simulation Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.set_font("Helvetica", "I", 13)
        self.cell(0, 10, "15 Engineering Scenarios - Complete Results", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

        self.ln(8)
        self.set_draw_color(*self.CYAN)
        self.set_line_width(0.5)
        self.line(55, self.get_y(), 155, self.get_y())

        self.ln(80)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(*self.GRAY)
        self.cell(0, 8, f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.cell(0, 8, "Author: Obada Dallo", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    def build_summary_table(self, results):
        self.add_page()
        self.set_text_color(*self.dark_title())
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 15, "1. Executive Summary - All Scenarios", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

        # Table header
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(40, 40, 40)
        self.set_text_color(*self.WHITE)
        cols = [12, 65, 18, 18, 77]
        headers = ["ID", "Scenario", "Status", "Time(s)", "Focus Area"]
        for i, h in enumerate(headers):
            self.cell(cols[i], 8, h, 1, fill=True, align="C")
        self.ln()

        # Table rows
        self.set_font("Helvetica", "", 7)
        for r in results:
            self.set_text_color(0, 0, 0)
            self.cell(cols[0], 7, r['id'], 1, align="C")
            self.cell(cols[1], 7, r['title'][:40], 1)

            # Status coloring
            if r['status'] == 'PASS':
                self.set_text_color(*self.GREEN)
            elif r['status'] == 'FAIL':
                self.set_text_color(*self.RED)
            else:
                self.set_text_color(*self.YELLOW)
            self.set_font("Helvetica", "B", 7)
            self.cell(cols[2], 7, r['status'], 1, align="C")
            self.set_font("Helvetica", "", 7)

            self.set_text_color(0, 0, 0)
            self.cell(cols[3], 7, str(r['duration']), 1, align="C")
            self.cell(cols[4], 7, r['focus'][:50], 1)
            self.ln()

        # Stats
        self.ln(10)
        passed = sum(1 for r in results if r['status'] == 'PASS')
        total = len(results)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"Total: {total} scenarios | Passed: {passed} | Failed: {total - passed}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def build_detail_pages(self, results):
        for i, r in enumerate(results):
            self.add_page()
            self.set_text_color(0, 0, 0)
            self.set_font("Helvetica", "B", 16)
            self.cell(0, 12, f"Scenario {r['id']}: {r['title']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            self.set_draw_color(*self.CYAN)
            self.set_line_width(0.6)
            self.line(10, self.get_y(), 90, self.get_y())
            self.ln(5)

            # Metadata
            self.set_font("Helvetica", "B", 10)
            self.cell(25, 7, "File:", 0)
            self.set_font("Helvetica", "", 10)
            self.cell(0, 7, r['file'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            self.set_font("Helvetica", "B", 10)
            self.cell(25, 7, "Focus:", 0)
            self.set_font("Helvetica", "", 10)
            self.cell(0, 7, r['focus'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            self.set_font("Helvetica", "B", 10)
            self.cell(25, 7, "Status:", 0)
            if r['status'] == 'PASS':
                self.set_text_color(*self.GREEN)
            else:
                self.set_text_color(*self.RED)
            self.set_font("Helvetica", "B", 10)
            self.cell(0, 7, f"{r['status']}  ({r['duration']}s)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(0, 0, 0)

            self.ln(5)
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 8, "Console Output:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(2)

            # Output box
            self.set_font("Courier", "", 6)
            self.set_fill_color(245, 245, 245)

            # Clean and truncate output
            output = r['output']
            # Replace problematic characters for latin-1
            output = output.encode('ascii', 'replace').decode('ascii')
            # Limit to fit the page
            lines = output.split('\n')
            max_lines = 80
            if len(lines) > max_lines:
                lines = lines[:max_lines] + [f"... ({len(lines) - max_lines} more lines truncated)"]

            for line in lines:
                clean = line[:130]  # Max chars per line
                if self.get_y() > 270:
                    self.add_page()
                    self.set_font("Courier", "", 6)
                    self.set_fill_color(245, 245, 245)
                self.cell(0, 3.5, f"  {clean}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

    def dark_title(self):
        return (0, 0, 0)

    def generate(self, results, output_dir="output"):
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, "Hydra_Cool_Master_Report.pdf")

        self.alias_nb_pages()
        self.build_cover()
        self.build_summary_table(results)
        self.build_detail_pages(results)
        self.output(path)
        return path


# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    print("=" * 65)
    print("  HYDRA-COOL: MASTER SCENARIO RUNNER v1.0")
    print("=" * 65)

    # Step 1: Run All Scenarios
    runner = ScenarioRunner(scenarios_dir="scenarios")
    results = runner.run_all()

    # Step 2: Generate Master PDF
    print("\nGenerating Master PDF Report...")
    report = MasterReport()
    output_path = report.generate(results, output_dir="output")
    print(f"Report saved: {output_path}")

    # Step 3: Print final stats
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total_time = sum(r['duration'] for r in results)
    print(f"\nTotal Execution Time: {total_time:.1f}s")
    print(f"Success Rate: {passed}/{len(results)}")
    print("\nDone.")
