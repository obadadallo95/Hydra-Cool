"""
Hydra-Cool Simulation [CODE] — E01: Geographic Constraints
==========================================================
"The market is smaller than you think."

Goal:
- Estimate the Total Addressable Market (TAM).
- Constraint: < 20km from Deep Water (>400m).

Data (Approximation):
- Global Data Centers: ~5000 Hyperscale/Large.
- Coastal (<50km): ~40%.
- Deep Coastal (<20km from pipe drop): ~10% (Oslo, Monterey, Tokyo, etc).
- Shallow Coastal (Virginia, NY, London, Amsterdam): Not suitable.

Output:
- Pie Chart of Market Segmentation.

Author: Obada Dallo
"""

import matplotlib.pyplot as plt
import os

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def run_simulation():
    print("Hydra-Cool E01: Running Geographic Market Analysis...")
    
    labels = [
        'Inland (Unviable)', 
        'Shallow Coastal (Unviable)', 
        'Deep Coastal (Prime)', 
        'Deep Coastal (Challenging)'
    ]
    
    # Percentages
    # Inland: Ashburn, Dallas, Phoenix, Frankfurt, Paris... (Huge chunk) -> 50%
    # Shallow Coastal: London, Amsterdam, NYC, Singapore, Dubai... (Shelf > 50km) -> 35%
    # Deep Coastal (Prime): Oslo, Vancouver, Marseille, Monterey... -> 5%
    # Deep Coastal (Challenging): Tokyo, LA (Seismic/Urban risks) -> 10%
    
    sizes = [50, 35, 5, 10]
    colors = ['#37474F', '#546E7A', '#00E676', '#FFC107']
    explode = (0, 0, 0.1, 0)
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                                      shadow=True, startangle=240, colors=colors,
                                      textprops=dict(color="white"))
    
    plt.setp(autotexts, size=10, weight="bold")
    
    ax.set_title("E01: Total Addressable Market (Constraint: Deep Water < 20km)", fontsize=14)
    
    # Annotation
    ax.text(1.2, 0.5, "Prime Market: ~5% of Global Capacity\n(Niche but High Value)", 
            bbox=dict(facecolor='#00E676', alpha=0.2), color='white')

    output_path = os.path.join(ASSET_DIR, "E01_geographic_constraint.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

if __name__ == "__main__":
    run_simulation()
