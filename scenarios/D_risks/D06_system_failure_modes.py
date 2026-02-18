"""
Hydra-Cool Simulation [CODE] — D06: System Failure Modes
========================================================
"What happens if...?"
Decision Tree for Emergency Response.

Scenarios:
1. Power Loss (Pump stops).
2. Pipe Burst (Pressure loss).
3. Intake Blockage (Flow restriction).

Output:
- Decision Tree Visualization (Matplotlib native).

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def draw_box(ax, x, y, text, color='#455A64', width=2.5, height=0.8):
    rect = patches.FancyBboxPatch((x - width/2, y - height/2), width, height,
                                  boxstyle="round,pad=0.1", 
                                  linewidth=1, edgecolor='white', facecolor=color)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', color='white', fontsize=9, fontweight='bold')

def draw_arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color='#B0BEC5', lw=2))

def run_simulation():
    print("Hydra-Cool D06: Running Failure Mode Analysis...")
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 2)
    ax.axis('off')
    
    # Root
    draw_box(ax, 0, 1, "Normal Operations", color='#2E7D32')
    
    # Level 1 (Incidents)
    draw_box(ax, -4, -1, "Power Loss", color='#C62828')
    draw_box(ax, 0, -1, "Pipe Leak", color='#C62828')
    draw_box(ax, 4, -1, "Blockage", color='#C62828')
    
    draw_arrow(ax, 0, 0.6, -4, -0.6)
    draw_arrow(ax, 0, 0.6, 0, -0.6)
    draw_arrow(ax, 0, 0.6, 4, -0.6)
    
    # Level 2 (Responses)
    draw_box(ax, -5, -3, "Gravity Drain", color='#1565C0')
    draw_box(ax, -3, -3, "Backup Gen", color='#1565C0')
    
    draw_box(ax, 0, -3, "Iso-Valve Close", color='#1565C0')
    
    draw_box(ax, 4, -3, "Back-flush / Pig", color='#1565C0')
    
    draw_arrow(ax, -4, -1.4, -5, -2.6)
    draw_arrow(ax, -4, -1.4, -3, -2.6)
    
    draw_arrow(ax, 0, -1.4, 0, -2.6)
    
    draw_arrow(ax, 4, -1.4, 4, -2.6)
    
    # Level 3 (Outcome)
    draw_box(ax, -3, -5, "Restart Pump", color='#00695C')
    draw_arrow(ax, -3, -3.4, -3, -4.6)
    
    draw_box(ax, 0, -5, "Switch Loop", color='#00695C')
    draw_arrow(ax, 0, -3.4, 0, -4.6)

    ax.set_title("D06: Failure Mode & Response Logic", fontsize=14)

    output_path = os.path.join(ASSET_DIR, "D06_failure_modes.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
