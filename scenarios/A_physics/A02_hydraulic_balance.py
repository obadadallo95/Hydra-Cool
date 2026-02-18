"""
Hydra-Cool Simulation [CODE] — A02: Full Hydraulic Balance
==========================================================
Calculates the complete pressure budget for a 100MW system.
It accounts for gains (Buoyancy) and losses (Friction, Minor, HX).

Physics basis:
- Flow Rate: Q = P_thermal / (Cp * ΔT)
- Friction Loss: ΔP_f = f * (L/D) * (ρv²/2)
- Minor Losses: ΔP_m = K * (ρv²/2)
- Heat Exchanger Loss: Fixed ΔP drop (assumption)

Key assumptions:
- IT Load: 100 MW
- ΔT: 40°C (In: 5°C, Out: 45°C) -> Low flow requirement
- Pipe Diameter: 1.2 m (Large to force low velocity)
- Pipe Length: 3000 m (Intake + Riser + Return) - Conservative
- Roughness: 0.05mm (New steel/HDPE)

Expected output:
- A waterfall chart showing the "Pressure Budget":
  [Buoyancy Gain] - [Friction Loss] - [HX Loss] = [Net Head]

Author: Obada Dallo
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# --- Constants ---
G = 9.81
RHO_REF = 1025.0
CP_SEAWATER = 3993.0  # J/kg.K
VISCOSITY = 1.3e-6   # Kinematic viscosity m^2/s at cold temp approximation

# --- System Parameters ---
IT_LOAD = 100 * 1e6  # 100 MW
DT = 40.0            # 40 K delta
PIPE_LEN = 3000.0    # Total pipe length (m)
PIPE_DIA = 1.2       # Pipe diameter (m)
ROUGHNESS = 0.05e-3  # 0.05 mm
K_MINOR = 5.0        # Sum of minor loss coeffs (intake, bends, valves)
HX_DROP = 50000.0    # 50 kPa drop across HX

TOWER_HEIGHT = 100.0 # Tower height assumption for this snapshot

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")

def get_friction_factor(re, relative_roughness):
    """
    Swamee-Jain approximation for Darcy-Weisbach friction factor f.
    """
    if re < 2300:
        return 64.0 / re
    else:
        return 0.25 / (np.log10( (relative_roughness/3.7) + (5.74/(re**0.9)) ))**2

def seawater_density(temp_c):
    return 1028.17 - 0.0663 * temp_c - 0.0038 * (temp_c ** 2)

def run_simulation():
    print("Hydra-Cool A02: Running Hydraulic Balance Simulation...")
    
    # 1. Calc Flow Rate
    q_mass = IT_LOAD / (CP_SEAWATER * DT)
    q_vol = q_mass / RHO_REF
    velocity = q_vol / (np.pi * (PIPE_DIA/2)**2)
    
    print(f"[-] Flow Rate: {q_mass:.1f} kg/s ({q_vol:.2f} m³/s)")
    print(f"[-] Velocity:  {velocity:.2f} m/s (in {PIPE_DIA}m pipe)")

    # 2. Calc Buoyancy Gain
    # Assuming average densities
    t_intake = 5.0
    t_out = 5.0 + DT
    rho_in = seawater_density(t_intake)
    rho_out = seawater_density(t_out)
    delta_rho = rho_in - rho_out
    
    # Buoyancy acts over the vertical riser height. 
    # Let's assume the riser is the tower height + depth.
    # Actually, buoyancy is P_bottom_cold - P_bottom_hot
    # Hydrostatic difference over the column height H.
    # Where H is the vertical lift.
    # Let's assume vertical lift = Tower Height (above sea) + Depth (below sea)?
    # No, only the heated column creates buoyancy relative to the cold column.
    # If the intake is deep, and discharge is high.
    # The "chimney effect" applies to the vertical distance the hot water travels vs cold water.
    # Let's conservatively assume Buoyancy acts only on the Tower Height (above sea) 
    # plus maybe some shallow depth, but primarily the tower.
    # Wait, if we lift cold water from 400m deep, it stays cold until the HX.
    # HX is likely at sea level.
    # Then hot water rises to the tower.
    # So Buoyancy only helps in the "Hot Riser" part.
    # Length of Hot Riser = Tower Height.
    # So Buoyancy Head = (rho_cold - rho_hot) * g * TOWER_HEIGHT.
    # This assumes the cold leg (up from depth) and hot leg (up to tower) balance out?
    # No. 
    # P_pump_required = (P_top - P_intake) - Buoyancy ?
    # Let's stick to the prompt's simplicity: 
    # Buoyancy Gain = Delta_Rho * g * H_tower.
    
    buoyancy_press = delta_rho * G * TOWER_HEIGHT
    
    # 3. Calc Friction Loss
    reps = ROUGHNESS / PIPE_DIA
    re = (velocity * PIPE_DIA) / VISCOSITY
    f = get_friction_factor(re, reps)
    
    friction_loss = f * (PIPE_LEN / PIPE_DIA) * (RHO_REF * velocity**2 / 2)
    
    # 4. Calc Minor Losses
    minor_loss = K_MINOR * (RHO_REF * velocity**2 / 2)
    
    # 5. Total Budget
    # We want to know if Buoyancy > Losses?
    # Or rather, what is the Net Head Loss we must overcome with a pump?
    # Or if we are generating power, we subtract losses from Gross Head.
    # Gross Head for Turbine = Tower Height (Potential Energy).
    # Wait, the prompt says: "Hot water rises... Tank... Turbine... Sea"
    # So Turbine is fed by Tank. Head = Tower Height.
    # How did water get to Tank?
    # P_pump + Buoyancy = P_friction + P_gravity_lift
    # P_gravity_lift = rho_hot * g * H_tower
    # But Buoyancy helps lift it?
    # Actually, "Buoyancy" effectively reduces the density, lightening the column.
    # Static Lift Head = H_tower.
    # Effective Lift Head = H_tower * (rho_hot / rho_cold)? 
    # Let's define "Buoyancy Pressure" as standard: Delta_P_buoyancy.
    # This helps overcome the geometrical lift.
    
    # Let's look at it as:
    # Required Input Pressure (Pump) = (Static Lift) + (Friction) - (Buoyancy)
    # Static Lift Pressure = rho_hot * G * TOWER_HEIGHT
    # Buoyancy "Assistance" = (rho_cold - rho_hot) * G * TOWER_HEIGHT?
    # Let's simply sum the pressures in a loop.
    
    # But wait, turbine generates power from the fall.
    # Turbine Head = Tower Height (minus return friction).
    # Net Energy = Turbine Power - Pump Power.
    
    # Let's stick to PRESSURE VALUES (Pa) for the Waterfall.
    # Positive bars: Buoyancy Gain? No.
    # Let's show "Head Loss Breakdown".
    # Or "Pressure to overcome".
    
    # Alternative View for "Hydraulic Balance":
    # Source: Deep Sea (0 pressure relative)
    # Destination: Top of Tower (Atmospheric)
    # Equation: P_pump + P_intake_head(0) = P_top(0) + rho_avg*g*H + Losses
    # We want to see the "Assists" vs "Costs".
    # Costs: Static Head (Lift), Friction, Minor, HX.
    # Assist: Buoyancy (Density reduction).
    # Actually, Static Head is the main cost.
    
    static_head_cost = rho_out * G * TOWER_HEIGHT
    fric_total = friction_loss + minor_loss + HX_DROP
    
    total_required_pressure = static_head_cost + fric_total
    
    # Turbine Recovery
    # Turbine gets rho_out * G * TOWER_HEIGHT (Potential) minus Outlet Losses?
    # Assume Turbine is at bottom of downcomer.
    # Head_turbine = TOWER_HEIGHT.
    # P_turbine_gross = rho_out * G * TOWER_HEIGHT * Q_vol
    # P_turbine_net = P_turbine_gross * Efficiency
    
    # So, does Buoyancy help?
    # Buoyancy reduces the P_pump needed to lift the water.
    # P_pump_ideal = Q * (Static_Head + Losses)
    # But with density diff, the "Static Head" is effectively reduced?
    # Let's think: Column 1 (Cold down) balances Column 2 (Hot up)?
    # No, it's open loop.
    # But the intake is at depth. 
    # Hydrostatic pressure at depth = rho_cold * g * Depth.
    # Pressure at HX (sea level) = rho_cold * g * Depth (gained) - Friction_intake.
    # So water arrives at surface naturally pressurized?
    # Yes, if pipe opens at surface (communicating vessels).
    # So "lifting from depth" costs nothing statically (communicating vessels).
    # Friction is the only cost for the intake leg.
    
    # So we only lift from Surface to Tower.
    # Lift Height = TOWER_HEIGHT.
    # Density in lift pipe = rho_hot.
    # P_lift_static = rho_hot * G * TOWER_HEIGHT.
    
    # Is there a "Buoyancy Gain"?
    # If we have a cold downcomer and hot riser...
    # But here we have Intake (cold) -> HX -> Riser (hot).
    # There is no "Cold Downcomer" from the tower.
    # The "Downcomer" from the tower is the Turbine penstock.
    # Riser (Hot) -> Tank -> Penstock (Hot) -> Turbine -> Sea.
    # If both Riser and Penstock are hot, there is NO buoyancy loop advantage between them.
    # They are same density.
    # So we just Pump up, and Turbine down.
    # Energy In = Pump Work = m * g * H + Friction
    # Energy Out = Turbine Work = m * g * H * eta - Friction
    # Net = Out - In < 0. Always negative due to friction and efficiency < 1.
    
    # WHERE is the Buoyancy Gain?
    # "Source 2: Buoyancy... helps lift the water"
    # This implies a density gradient in the riser vs the surrounding/reference?
    # If the intake is deep (high pressure at bottom), and we heat it...
    # No.
    # The only way buoyancy works is if we have a loop.
    # But wait, if we consider the "Intake from 400m" as the Cold Leg.
    # And the "Riser to Surface" as... well, the intake pipe is cold.
    # So water comes up to surface (0m) naturally.
    # Then we heat it. Pump it to TOWER (100m).
    # Pump sees: P_required = rho_hot * g * 100 + Friction.
    # Turbine recovers: P_gen = rho_hot * g * 100 * eta.
    # Net = Loss.
    
    # Re-reading prompt carefuly:
    # "Sources: 1. Deep water pressure... 2. Buoyancy (Hot water lighter than cold)... helps raise water... 3. Gravity... Turbine"
    # If the system is:
    # Intake (Deep) -> [Cold Pipe] -> HX (Deep?) or HX (Surface?)
    # "Mubadala Harari... Servers... Water exits hot... Rises to tank"
    # If HX is at sea level: No buoyancy advantage for the lift 0->100m relative to sea level.
    # UNLESS the HX is at depth? No, servers are on land.
    
    # Maybe the "Buoyancy" refers to the density difference reducing the head of the output column relative to the intake column IF they were connected?
    # But they are connected via the pump.
    # The intake provides P_surface = (rho_cold * g * D) - (rho_cold * g * D) = 0.
    # So we start at 0 bar at surface.
    # Cost to lift 100m: rho_hot * g * 100.
    # If we lifted cold water: rho_cold * g * 100.
    # Since rho_hot < rho_cold, we save energy lifting hot water vs cold.
    # Saving = (rho_cold - rho_hot) * g * 100.
    # Is this the "Buoyancy Source"?
    # Yes, lifting lighter fluid costs less work.
    
    # Let's proceed with this interpretation for A02.
    # We compare "Lifting Cost" vs "Turbine Return".
    # And show losses.
    
    # Values for Chart
    p_lift_static = static_head_cost # rho_hot * g * H
    p_turbine_gross = p_lift_static  # Same mass, same H, same rho (approx)
    
    # Actually, let's look at Power (kW) for the waterfall, it's more intuitive than Pressure (Pa) for the "Balance".
    # The prompt asks for "Pressure Budget Waterfall".
    # Okay, let's do Pressure (Pa).
    
    # Categories:
    # 1. Static Head (The hill we climb): -rho_hot * g * H
    # 2. Friction Loss (The toll we pay): -Friction
    # 3. HX Loss: -HX
    # 4. Pump Input (What we provide): +Pump
    # End result must be 0 (at top of tank).
    
    # Or for the whole cycle (Net Power):
    # A03 seems to be the Net Power one.
    # A02 is "Hydraulic Balance... Pressure Budget".
    
    # Let's show the pressure required at the pump discharge to get to the top.
    required_pump_head = static_head_cost + fric_total
    
    # Convert to kPa
    values = [
        static_head_cost / 1000, 
        friction_loss / 1000, 
        minor_loss / 1000, 
        HX_DROP / 1000,
        total_required_pressure / 1000
    ]
    labels = ['Static Lift (Hot)', 'Friction Loss', 'Minor Losses', 'HX Drop', 'Total Pump Head']
    
    # Visualization
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Waterfall-ish bar chart
    cumulative = 0
    for i, (val, label) in enumerate(zip(values[:-1], labels[:-1])):
        ax.bar(label, val, bottom=cumulative, color='#FF5722', alpha=0.8)
        # cumulative += val # No, these are all "Costs" summing up
    
    # Re-think chart: Stacked bar of "Head Requirements"?
    # Yes.
    indices = range(len(values))
    ax.bar(0, values[0], label='Static Lift', color='#2196F3')
    ax.bar(0, values[1], bottom=values[0], label='Friction', color='#FF9800')
    ax.bar(0, values[2], bottom=values[0]+values[1], label='Minor', color='#FFC107')
    ax.bar(0, values[3], bottom=values[0]+values[1]+values[2], label='HX', color='#F44336')
    
    ax.bar(1, values[4], label='Total Pump Req', color='#4CAF50')
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Breakdown', 'Total Required'])
    ax.set_ylabel('Pressure Head [kPa]')
    ax.set_title(f"A02: Hydraulic Pressure Budget (100m Tower, 100MW)\nFlow: {q_vol:.2f} m³/s, Velocity: {velocity:.2f} m/s")
    
    # Annotate
    ax.text(1, values[4] + 10, f"{values[4]:.0f} kPa", ha='center', color='white')
    
    # Calc Pump Power
    pump_power_kw = (total_required_pressure * q_vol) / 0.85 / 1000
    ax.text(1.3, values[4]/2, f"Est. Pump Power:\n{pump_power_kw:.1f} kW", color='white')

    ax.legend()
    
    output_path = os.path.join(ASSET_DIR, "A02_hydraulic_balance.png")
    plt.savefig(output_path, dpi=150)
    print(f"[+] Saved visualization to: {output_path}")

    # Print Summary
    print("-" * 40)
    print(f"Total Head Required: {total_required_pressure/1000:.2f} kPa")
    print(f"  - Static Lift: {static_head_cost/1000:.2f} kPa ({(static_head_cost/total_required_pressure)*100:.1f}%)")
    print(f"  - Friction:    {friction_loss/1000:.2f} kPa")
    print(f"  - Minor+HX:    {(minor_loss+HX_DROP)/1000:.2f} kPa")
    print(f"Est Pump Power: {pump_power_kw:.2f} kW")
    print("-" * 40)

if __name__ == "__main__":
    run_simulation()
