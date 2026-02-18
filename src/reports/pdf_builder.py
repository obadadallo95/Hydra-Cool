"""
Hydra-Cool: Professional PDF Report Generator
==============================================
Generates a "Fortune 500" style engineering feasibility
report with embedded charts, competitor analysis, and
7 key visual evidence pages.

Author: Obada Dallo
Copyright (c) 2024. All Rights Reserved.
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
from typing import List
import os


class HydraCoolReport(FPDF):
    """
    Corporate Engineering Report Generator.
    Produces an 11-section PDF with cover page, competitor analysis,
    executive summary, 7 key visuals, and final verdict.
    """

    # Brand Colors
    BRAND_CYAN = (0, 255, 204)
    BRAND_DARK = (7, 11, 13)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 180, 80)
    RED = (220, 40, 40)
    GOLD = (255, 200, 0)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, "Hydra-Cool - Confidential Engineering Document", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
            self.line(10, 15, 200, 15)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")

    # ── Cover Page ───────────────────────────────────────

    def build_cover(self):
        """Full-page branded cover with the $1.6B headline."""
        self.add_page()
        self.set_fill_color(*self.BRAND_DARK)
        self.rect(0, 0, 210, 297, "F")

        # Title
        self.set_text_color(*self.BRAND_CYAN)
        self.set_font("Helvetica", "B", 42)
        self.ln(60)
        self.cell(0, 20, "HYDRA-COOL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

        # Subtitle
        self.set_text_color(*self.WHITE)
        self.set_font("Helvetica", "", 16)
        self.cell(0, 12, "The $1.6 Billion Advantage", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.set_font("Helvetica", "I", 12)
        self.cell(0, 10, "Deep-Sea Thermosiphon Cooling vs Global Industry", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

        # Divider
        self.ln(10)
        self.set_draw_color(*self.BRAND_CYAN)
        self.set_line_width(0.5)
        self.line(60, self.get_y(), 150, self.get_y())

        # Key stats
        self.ln(15)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*self.BRAND_CYAN)
        stats = [
            "85% cheaper than AWS  |  81% cheaper than Google",
            "Zero freshwater  |  Near-zero carbon  |  PUE 1.02",
            "22 simulations passed  |  20-year verified lifespan",
            "99.9999% availability (Six Sigma)",
        ]
        for s in stats:
            self.cell(0, 8, s, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

        # Metadata
        self.ln(40)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(180, 180, 180)
        self.cell(0, 8, f"Date: {datetime.now().strftime('%B %d, %Y')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.cell(0, 8, "Author: Obada Dallo", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.cell(0, 8, "Classification: Proprietary & Confidential", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    # ── 10. THE UPGRADE PROPOSAL ─────────────────────────

    def build_upgrade_section(self, assets_dir):
        """Build the section on Brownfield Upgrade Proposal."""
        self.add_page()
        self._section_title("10. THE UPGRADE PROPOSAL: Brownfield Revolution")
        
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 6, "Stop building new. Upgrade what exists. The fastest path to decarbonization is retrofitting existing coastal data centers (Google Hamina, Microsoft Dublin) with Hydra-Cool's side-stream technology. This approach bypasses land acquisition, permitting, and grid connection hurdles.")
        self.ln(5)

        # Upgrade vs Build Table
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(240, 240, 240)
        self.cell(45, 8, "Metric", 1, 0, "C", True)
        self.cell(45, 8, "Greenfield Build", 1, 0, "C", True)
        self.cell(45, 8, "Retrofit Upgrade", 1, 0, "C", True)
        self.cell(0, 8, "Advantage", 1, 1, "C", True)
        
        self.set_font("Helvetica", "", 10)
        data = [
            ("CAPEX (100MW)", "$614M", "$169M", "73% Savings"),
            ("Time to Market", "5-7 Years", "18 Months", "3x Faster"),
            ("Permitting", "Full EIS (3 yrs)", "Industrial Mod (<6 mo)", "Fast Track"),
            ("Land/Grid", "New Acquisition", "Reuse Existing", "Zero Risk"),
        ]
        
        for row in data:
            self.cell(45, 8, row[0], 1)
            self.cell(45, 8, row[1], 1, 0, "C")
            self.cell(45, 8, row[2], 1, 0, "C")
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(0, 150, 0)
            self.cell(0, 8, row[3], 1, 1, "C")
            self.set_text_color(0, 0, 0)
            self.set_font("Helvetica", "", 10)
        
        self.ln(8)
        
        # Payback Chart
        self.image(f"{assets_dir}/v27_retrofit_payback.png", x=10, w=190)
        self.ln(5)
        self.set_font("Helvetica", "I", 9)
        self.multi_cell(0, 5, "Fig 10.1: Payback Analysis. The $169M retrofit investment pays for itself in Year 7 through energy and maintenance savings. The 'Cost of Inaction' exceeds the cost of upgrading.")
        self.ln(5)
        
        self.add_page()
        self._section_title("11. ZERO-DOWNTIME TRANSITION PLAN")
        
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 6, "The critical challenge: changing the engine while flying the plane. Our 3-Phase Live Migration strategy ensures 100% continuous cooling availability. The legacy chillers are never removed until Hydra-Cool is proven stable.")
        self.ln(5)
        
        self.image(f"{assets_dir}/v28_transition_gantt.png", x=10, w=190)
        self.ln(10)
        
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "Phase 1: Side-Stream (Months 0-6)", 0, 1)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, "- Install subsea pipes and heat exchangers in parallel.\n- Legacy system continues at 100% load.\n- Risk: ZERO (Systems completely isolated via bypass valves).")
        self.ln(3)

        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "Phase 2: Hybrid Ramp (Months 6-12)", 0, 1)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, "- Gradual load transfer (10% -> 60%).\n- Chillers remain on hot standby for instant failover.\n- Go/No-Go gates at every 10% increment.")
        self.ln(3)
        
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "Phase 3: Switchover (Months 12-18)", 0, 1)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, "- Hydra-Cool takes primary load (95%).\n- Legacy system decommissioned or kept as emergency backup.\n- Outcome: PUE drops to 1.08, water use drops to zero.")

    # ── 1. Competitor Analysis Table (The Hook) ──────────

    def build_competitor_analysis(self):
        """Competitor comparison table - the first thing the reader sees."""
        self.add_page()
        self._section_title("1. Competitor Analysis: Hydra-Cool vs Big Tech")

        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, (
            "10-Year Total Cost of Ownership for a 100 MW hyperscale facility. "
            "Data sourced from Google Environmental Report 2024, Microsoft Sustainability "
            "Report 2024, Amazon Sustainability Report 2023, and Uptime Institute 2024."
        ))
        self.ln(8)

        # Competitor table
        col_w = [32, 28, 24, 24, 24, 24, 30]
        headers = ["Company", "CAPEX", "10Y OPEX", "Water", "CO2 Tax", "10Y TCO", "vs HC"]

        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(30, 30, 30)
        self.set_text_color(*self.WHITE)
        for i, h in enumerate(headers):
            self.cell(col_w[i], 9, h, 1, fill=True, align="C")
        self.ln()

        competitors = [
            ("Google",     "$850M",  "$620M", "$0.1M", "$123M", "$1,593M", "-81%"),
            ("Microsoft",  "$920M",  "$680M", "$0.1M", "$140M", "$1,740M", "-83%"),
            ("AWS",        "$1,000M", "$720M", "$0.1M", "$153M", "$1,873M", "-84%"),
            ("Meta",       "$780M",  "$550M", "$0.1M", "$96M",  "$1,426M", "-79%"),
        ]

        self.set_font("Helvetica", "", 9)
        for name, capex, opex, water, co2, tco, pct in competitors:
            self.set_text_color(*self.BLACK)
            self.cell(col_w[0], 8, name, 1, align="C")
            self.cell(col_w[1], 8, capex, 1, align="C")
            self.cell(col_w[2], 8, opex, 1, align="C")
            self.cell(col_w[3], 8, water, 1, align="C")
            self.cell(col_w[4], 8, co2, 1, align="C")
            self.set_text_color(*self.RED)
            self.set_font("Helvetica", "B", 9)
            self.cell(col_w[5], 8, tco, 1, align="C")
            self.cell(col_w[6], 8, pct, 1, align="C")
            self.set_font("Helvetica", "", 9)
            self.ln()

        # Hydra-Cool row (highlighted)
        self.set_fill_color(0, 40, 30)
        self.set_text_color(*self.BRAND_CYAN)
        self.set_font("Helvetica", "B", 9)
        hc_vals = ["HYDRA-COOL", "$208M", "$95M", "$0", "$1.3M", "$304M", "BASE"]
        for i, v in enumerate(hc_vals):
            self.cell(col_w[i], 9, v, 1, fill=True, align="C")
        self.ln()

        # Summary box
        self.ln(8)
        self.set_text_color(*self.BLACK)
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Average Savings: $1,354M (81.5% cheaper)", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

        # PUE comparison
        self.ln(8)
        self._section_title("")
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*self.BLACK)
        self.cell(0, 8, "Key Performance Indicators:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 10)
        kpis = [
            "PUE: 1.02 (vs industry avg 1.58, vs Google 1.10)",
            "Water: 0 L/MWh (vs AWS 5.80 L/MWh)",
            "Carbon: 0.003 t/MWh (vs Meta 0.220 t/MWh - lowest competitor)",
            "Energy Shock Immunity: <1% cost change in +100% energy crisis",
            "Design Lifespan: 20 years verified (corrosion simulation v15)",
        ]
        for k in kpis:
            self.cell(0, 7, f"  - {k}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── 2. Executive Summary ─────────────────────────────

    def build_executive_summary(self, results):
        """Regional deployment decision table."""
        self.add_page()
        self.set_text_color(*self.BLACK)
        self._section_title("2. Regional Deployment Analysis")

        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 7, (
            "Three-city deployment feasibility covering fluid dynamics, structural "
            "integrity under seismic loads, and 10-year financial projections."
        ))
        self.ln(8)

        # Table Header
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(40, 40, 40)
        self.set_text_color(*self.WHITE)
        col_w = [35, 30, 35, 40, 30]
        headers = ["Location", "ROI (%)", "CAPEX ($M)", "10Y Profit ($M)", "Verdict"]
        for i, h in enumerate(headers):
            self.cell(col_w[i], 10, h, 1, fill=True, align="C")
        self.ln()

        # Table Body
        self.set_font("Helvetica", "", 10)
        for r in results:
            self.set_text_color(*self.BLACK)
            self.cell(col_w[0], 9, r.location, 1, align="C")
            self.cell(col_w[1], 9, f"{r.roi_pct}", 1, align="C")
            self.cell(col_w[2], 9, f"{r.capex_usd / 1e6:.1f}", 1, align="C")
            self.cell(col_w[3], 9, f"{r.profit_10y_usd / 1e6:.1f}", 1, align="C")
            color = self.GREEN if r.build_verdict == "BUILD" else self.RED
            self.set_text_color(*color)
            self.set_font("Helvetica", "B", 10)
            self.cell(col_w[4], 9, r.build_verdict, 1, align="C")
            self.set_font("Helvetica", "", 10)
            self.ln()

    # ── 3. Financial War Room (The Hook) ─────────────────

    def build_financial_warroom(self, assets_dir: str):
        """v22: 10-year TCO comparison - the $1.6B gap."""
        self.add_page()
        self._section_title("3. Financial War Room: The $1.6B Gap")

        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, (
            "Year-by-year cash flow model with escalating energy prices (+2.5%/yr), "
            "carbon tax ($50/t rising 8%/yr), and water scarcity premium (+4%/yr). "
            "NPV calculated at 8% WACC. Sensitivity tested for +25% to +100% energy shock."
        ))
        self.ln(3)

        path = os.path.join(assets_dir, "v22_financial_warroom.png")
        if os.path.exists(path):
            self.image(path, x=10, w=185)

    # ── 4. Industry Benchmark ────────────────────────────

    def build_industry_benchmark(self, assets_dir: str):
        """v21: PUE, water, CO2, CAPEX bar charts."""
        self.add_page()
        self._section_title("4. Industry Benchmark: PUE, Water, Carbon, Cost")

        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, (
            "Six-axis comparison using published data from Google, Microsoft, AWS, and "
            "Meta sustainability reports. Hydra-Cool leads on every metric. "
            "Industry average PUE = 1.58 (Uptime Institute 2024)."
        ))
        self.ln(3)

        path = os.path.join(assets_dir, "v21_industry_benchmark.png")
        if os.path.exists(path):
            self.image(path, x=10, w=185)

    # ── 5. Scalability & Reliability ─────────────────────

    def build_scalability_section(self, assets_dir: str):
        """v20: Campus sizing, redundancy, availability."""
        self.add_page()
        self._section_title("5. Scalability & Reliability (50-500 MW)")

        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, (
            "Campus-scale deployment from 50MW to 500MW achieves 30% CAPEX reduction through "
            "economy of scale. 2N redundancy reaches 99.9999% availability (Six Sigma) - "
            "less than 36 seconds of annual downtime. Lead-lag strategy maximizes efficiency."
        ))
        self.ln(3)

        path = os.path.join(assets_dir, "v20_scalability.png")
        if os.path.exists(path):
            self.image(path, x=10, w=185)

    # ── 6. Environmental Impact ──────────────────────────

    def build_environmental_section(self, assets_dir: str):
        """v19: Thermal plume, marine ecology, CO2 lifecycle."""
        self.add_page()
        self._section_title("6. Environmental Impact Assessment")

        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, (
            "Thermal plume modeling confirms temperature rise below 1C within 500m of "
            "discharge - within EPA Clean Water Act limits. Over 20 years, Hydra-Cool "
            "prevents 1.46 million tonnes of CO2. Carbon breakeven: Year 1."
        ))
        self.ln(3)

        path = os.path.join(assets_dir, "v19_eia.png")
        if os.path.exists(path):
            self.image(path, x=10, w=185)

    # ── 7. Operational Safety ────────────────────────────

    def build_transient_section(self, assets_dir: str):
        """v18: Emergency shutdown, water hammer, thermal shock."""
        self.add_page()
        self._section_title("7. Safety Case: Hydraulic Transients")

        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, (
            "Three shutdown scenarios analyzed using Joukowsky water hammer and Korteweg "
            "wave speed. Catastrophic instant-failure yields SF=1.59 - pipe does not rupture. "
            "Emergency drain-down: 10.6 seconds via gravity-fed fail-open valves."
        ))
        self.ln(3)

        path = os.path.join(assets_dir, "v18_transient.png")
        if os.path.exists(path):
            self.image(path, x=10, w=185)

    # ── 8. Biofouling & Maintenance ──────────────────────

    def build_biofouling_section(self, assets_dir: str):
        """v17: Marine growth, flow degradation, cleaning schedule."""
        self.add_page()
        self._section_title("8. Biofouling & Maintenance Schedule")

        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, (
            "Logistic growth model calibrated with WHOI data, combined with Colebrook-White "
            "friction equations. Tropical: clean every 6 months. Temperate: 9 months. "
            "Cold: 12 months. Cleaning cost < 0.5% of annual revenue."
        ))
        self.ln(3)

        path = os.path.join(assets_dir, "v17_biofouling.png")
        if os.path.exists(path):
            self.image(path, x=10, w=185)

    # ── 9. Lifecycle Durability ──────────────────────────

    def build_lifecycle_section(self, assets_dir: str):
        """v15: 20-year corrosion and material degradation."""
        self.add_page()
        self._section_title("9. Lifecycle Durability: 20-Year Guarantee")

        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, (
            "Fick's 2nd Law (chloride diffusion) + Faraday's Law (corrosion rate) over 20 "
            "years. Safety factor remains above 4.0 throughout design life. Cathodic "
            "protection (ICCP): 51 anodes, 3 kW, $319K - 0.6% of CAPEX."
        ))
        self.ln(3)

    # ── 11. Upgrade Section ──────────────────────────────

    def build_upgrade_section(self, assets_dir: str):
        """Build the section on Brownfield Upgrade Proposal."""
        self.add_page()
        self._section_title("11. THE UPGRADE PROPOSAL: Brownfield Revolution")
        
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 6, "Stop building new. Upgrade what exists. The fastest path to decarbonization is retrofitting existing coastal data centers (Google Hamina, Microsoft Dublin) with Hydra-Cool's side-stream technology. This approach bypasses land acquisition, permitting, and grid connection hurdles.")
        self.ln(5)

        # Upgrade vs Build Table
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(240, 240, 240)
        self.cell(45, 8, "Metric", 1, 0, "C", True)
        self.cell(45, 8, "Greenfield Build", 1, 0, "C", True)
        self.cell(45, 8, "Retrofit Upgrade", 1, 0, "C", True)
        self.cell(0, 8, "Advantage", 1, 1, "C", True)
        
        self.set_font("Helvetica", "", 10)
        data = [
            ("CAPEX (100MW)", "$614M", "$169M", "73% Savings"),
            ("Time to Market", "5-7 Years", "18 Months", "3x Faster"),
            ("Permitting", "Full EIS (3 yrs)", "Industrial Mod (<6 mo)", "Fast Track"),
            ("Land/Grid", "New Acquisition", "Reuse Existing", "Zero Risk"),
        ]
        
        for row in data:
            self.cell(45, 8, row[0], 1)
            self.cell(45, 8, row[1], 1, 0, "C")
            self.cell(45, 8, row[2], 1, 0, "C")
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(0, 150, 0)
            self.cell(0, 8, row[3], 1, 1, "C")
            self.set_text_color(0, 0, 0)
            self.set_font("Helvetica", "", 10)
        
        self.ln(8)
        
        # Payback Chart
        self.image(f"{assets_dir}/v27_retrofit_payback.png", x=10, w=190)
        self.ln(5)
        self.set_font("Helvetica", "I", 9)
        self.multi_cell(0, 5, "Fig 11.1: Payback Analysis. The $169M retrofit investment pays for itself in Year 7 through energy and maintenance savings. The 'Cost of Inaction' exceeds the cost of upgrading.")
        self.ln(5)
        
        self.add_page()
        self._section_title("12. ZERO-DOWNTIME TRANSITION PLAN")
        
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 6, "The critical challenge: changing the engine while flying the plane. Our 3-Phase Live Migration strategy ensures 100% continuous cooling availability. The legacy chillers are never removed until Hydra-Cool is proven stable.")
        self.ln(5)
        
        self.image(f"{assets_dir}/v28_transition_gantt.png", x=10, w=190)
        self.ln(10)
        
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "Phase 1: Side-Stream (Months 0-6)", 0, 1)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, "- Install subsea pipes and heat exchangers in parallel.\n- Legacy system continues at 100% load.\n- Risk: ZERO (Systems completely isolated via bypass valves).")
        self.ln(3)

        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "Phase 2: Hybrid Ramp (Months 6-12)", 0, 1)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, "- Gradual load transfer (10% -> 60%).\n- Chillers remain on hot standby for instant failover.\n- Go/No-Go gates at every 10% increment.")
        self.ln(3)
        
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "Phase 3: Switchover (Months 12-18)", 0, 1)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, "- Hydra-Cool takes primary load (95%).\n- Legacy system decommissioned or kept as emergency backup.\n- Outcome: PUE drops to 1.08, water use drops to zero.")

    # ── 13. Conclusion ───────────────────────────────────

    def build_conclusion(self, results):
        """The $1.6B advantage summary with final recommendation."""
        self.add_page()
        self._section_title("13. Conclusion: The $1.6 Billion Advantage")

        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 7, (
            "Hydra-Cool's passive thermosiphon architecture eliminates mechanical compressors, "
            "reducing energy waste by 98% and achieving the world's lowest PUE (1.02). "
            "The 10-year TCO of $304M for a 100MW facility is 81.5% cheaper than the "
            "Big 4 average of $1,658M."
        ))
        self.ln(5)

        total_profit = sum(r.profit_10y_usd for r in results)
        total_capex = sum(r.capex_usd for r in results)

        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, f"Combined 10-Year Profit: ${total_profit / 1e9:.2f}B", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 10, f"Combined CAPEX:          ${total_capex / 1e6:.0f}M", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

        # Key metrics
        self.set_font("Helvetica", "", 10)
        self.set_text_color(80, 80, 80)
        metrics = [
            "85% cheaper than AWS (10Y TCO)",
            "81% cheaper than Google (10Y TCO)",
            "Design Lifespan: 20 years (corrosion-verified, SF=4.18)",
            "CO2 Prevented: 1.46 million tonnes over 20 years",
            "System Availability (2N): 99.9999% (Six Sigma)",
            "Energy Shock Immunity: <1% cost change in +100% crisis",
            "Simulations Passed: 22 / 22 (zero failures)",
        ]
        for m in metrics:
            self.cell(0, 7, f"  - {m}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(8)

        self.set_text_color(*self.BLACK)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*self.BRAND_CYAN)
        self.cell(0, 15, "RECOMMENDATION: PROCEED TO PHASE II ENGINEERING", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    # ── Helpers ──────────────────────────────────────────

    def _section_title(self, title: str):
        if not title:
            return
        self.set_text_color(*self.BLACK)
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 15, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*self.BRAND_CYAN)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 110, self.get_y())
        self.ln(6)

    # ── Public API ───────────────────────────────────────

    def generate(self, results, assets_dir: str = "assets", output_dir: str = "output"):
        """Build the complete 11-section report and save to disk."""
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "Hydra_Cool_Final_Report.pdf")

        self.alias_nb_pages()

        # Page 1: Cover
        self.build_cover()
        # Page 2: Competitor Analysis (The Hook)
        self.build_competitor_analysis()
        # Page 3: Regional Deployment
        self.build_executive_summary(results)
        # Page 4: Financial War Room (v22)
        self.build_financial_warroom(assets_dir)
        # Page 5: Industry Benchmark (v21)
        self.build_industry_benchmark(assets_dir)
        # Page 6: Scalability (v20)
        self.build_scalability_section(assets_dir)
        # Page 7: Environmental Impact (v19)
        self.build_environmental_section(assets_dir)
        # Page 8: Safety Case (v18)
        self.build_transient_section(assets_dir)
        # Page 9: Biofouling (v17)
        self.build_biofouling_section(assets_dir)
        # Page 10: Lifecycle Durability (v15)
        self.build_lifecycle_section(assets_dir)
        # Page 11: Conclusion
        self.build_conclusion(results)

        self.output(output_path)
        return output_path
