import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

class CoolingSystemSim:
    """
    Simulation of a Data Center Cooling System using Thermosiphon & Hydro-Potential principles.
    
    Physics Principle:
    The system utilizes the waste heat from data centers to heat seawater. The density difference 
    between cold intake water and hot outlet water creates a buoyancy force (Thermosiphon effect).
    This force drives the water up a vertical pipe to an elevated tank. The potential energy 
    of the stored water is then harvested by a turbine as it flows back down.
    """
    
    def __init__(self, t_in_c=20.0, t_out_c=50.0, pipe_diameter_m=0.5, friction_factor=0.02, pump_efficiency=0.85, turbine_efficiency=0.80):
        """
        Initialize the simulation parameters.
        
        Args:
            t_in_c (float): Inlet temperature (Seawater) [deg C]
            t_out_c (float): Outlet temperature (Heated by Data Center) [deg C]
            pipe_diameter_m (float): Diameter of the riser pipe [m]
            friction_factor (float): Darcy-Weisbach friction factor for the pipe (approximate)
            pump_efficiency (float): Efficiency of a traditional pump for comparison
            turbine_efficiency (float): Efficiency of the energy recovery turbine
        """
        self.t_in_c = t_in_c
        self.t_out_c = t_out_c
        self.diameter = pipe_diameter_m
        self.area = np.pi * (self.diameter / 2)**2
        self.f = friction_factor
        self.eta_pump = pump_efficiency
        self.eta_turbine = turbine_efficiency
        self.g = 9.81  # Gravity [m/s^2]
        
        # Calculate densities once
        self.rho_in = self.calculate_water_density(self.t_in_c)
        self.rho_out = self.calculate_water_density(self.t_out_c)
        self.rho_avg = (self.rho_in + self.rho_out) / 2

    def calculate_water_density(self, temp_c):
        """
        Calculates seawater density based on temperature using a polynomial approximation.
        Assumes salinity of ~35 ppt (standard seawater).
        
        Formula approximation based on UNESCO equation of state (simplified).
        
        Args:
            temp_c (float or np.array): Temperature in Celsius.
            
        Returns:
            float or np.array: Density in kg/m^3.
        """
        # Simplified polynomial fit for seawater density range 0-100C
        # rho(T) = rho_0 - A*T - B*T^2
        # Values approximate for 35ppt salinity
        rho_0 = 1028.0 
        A = 0.05
        B = 0.0045 
        # Using a slightly more accurate fit for the 10-60C range if needed, 
        # but this quadratic captures the non-linearity well enough for demo.
        # Let's use Thiesen-Scheel-Diesselhorst equation simplified or just a standard curve fit:
        # rho = 1028.17 - 0.0663*T - 0.0038*T^2 + ...
        return 1028.17 - 0.0663 * temp_c - 0.0038 * temp_c**2

    def run_simulation_for_height(self, height_m):
        """
        Calculates system performance for a specific tower height.
        
        Physics:
        1. Buoyancy Head (Pressure): Delta_P = (rho_cold - rho_hot) * g * h
           This is the pressure driving the flow upwards.
           
        2. Flow Rate (Q): 
           In a steady-state thermosiphon, average Buoyancy Force balances Friction Force.
           Delta_P_buoyancy = Delta_P_friction
           (rho_in - rho_out) * g * h = f * (h / D) * (rho_avg * v^2 / 2)
           
           Solving for velocity v:
           v = sqrt( (2 * D * g * (rho_in - rho_out)) / (f * rho_avg) )
           
           Note: Interestingly, 'h' cancels out in the velocity equation for a pure vertical pipe 
           where friction scales linearly with height. This means flow velocity is constant 
           regardless of height, assuming fully developed flow and dominant pipe friction.
           
        3. Power Generation:
           P_gen = efficiency * rho * g * Q * h
           
        Returns:
            dict: Results containing flow rate, power, etc.
        """
        # 1. Buoyancy Pressure Head [Pa]
        # The theoretical pressure difference available at the bottom if the column was static
        pressure_head_buoyancy = (self.rho_in - self.rho_out) * self.g * height_m
        
        # 2. Theoretical Velocity [m/s]
        # Derived from equating Buoyancy Head to Friction Head:
        # (d_rho) * g * h = f * (h/D) * 0.5 * rho * v^2
        # v = sqrt( (2 * D * g * (rho_in - rho_out)) / (f * self.rho_avg) )
        delta_rho = self.rho_in - self.rho_out
        
        if delta_rho <= 0:
            velocity = 0
        else:
            velocity = np.sqrt( (2 * self.diameter * self.g * delta_rho) / (self.f * self.rho_avg) )
            
        flow_rate_q = velocity * self.area  # [m^3/s]
        
        # 3. Energy Recovery (Turbine) [Watts]
        # Power available from the falling water from height H
        # We assume the turbine is at sea level, using the potential energy m*g*h
        mass_flow_rate = flow_rate_q * self.rho_out
        power_generated = self.eta_turbine * mass_flow_rate * self.g * height_m
        
        # 4. Traditional Pump Comparison [Watts]
        # Power required to lift the same mass flow to height H (or equivalent head loss)
        # using a standard electrical pump.
        # P_pump = (rho * g * Q * H) / efficiency
        power_consumed_traditional = (mass_flow_rate * self.g * height_m) / self.eta_pump
        
        return {
            "height": height_m,
            "buoyancy_pressure": pressure_head_buoyancy,
            "velocity": velocity,
            "flow_rate": flow_rate_q,
            "power_generated": power_generated,
            "power_traditional": power_consumed_traditional,
            "net_benefit": power_generated + power_consumed_traditional # Total energy impact (Generated + Saved)
        }

    def simulate_height_range(self, min_h=10, max_h=200, step=10):
        """Runs the simulation over a range of heights."""
        heights = np.arange(min_h, max_h + 1, step)
        results = []
        for h in heights:
            results.append(self.run_simulation_for_height(h))
        return results

    def plot_dashboard(self, results):
        """Generates the visualization dashboard."""
        
        # Extract data
        heights = [r['height'] for r in results]
        power_gen = [r['power_generated'] / 1000 for r in results] # kW
        power_trad = [r['power_traditional'] / 1000 for r in results] # kW
        
        # Create temperature range for density plot
        temps = np.linspace(10, 80, 100)
        densities = self.calculate_water_density(temps)
        
        # Setup Plot
        os.makedirs("assets", exist_ok=True)
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(18, 10))
        plt.suptitle(f"v1: BASE CASE - Thermosiphon & Hydro-Energy Validation\nDelta T: {self.t_in_c}°C -> {self.t_out_c}°C | Pipe Dia: {self.diameter}m", fontsize=16, color='white', fontweight='bold')
        
        # Subplot 1: Physics Driver - Density vs Temperature
        ax1 = plt.subplot(2, 2, 1)
        ax1.plot(temps, densities, color='teal', linewidth=2)
        ax1.axvline(self.t_in_c, color='blue', linestyle='--', label=f'Inlet ({self.t_in_c}°C)')
        ax1.axvline(self.t_out_c, color='red', linestyle='--', label=f'Outlet ({self.t_out_c}°C)')
        ax1.scatter([self.t_in_c, self.t_out_c], [self.rho_in, self.rho_out], color='black', zorder=5)
        ax1.annotate(f"Buoyancy Driver\nΔρ = {self.rho_in - self.rho_out:.2f} kg/m³", 
                     xy=((self.t_in_c + self.t_out_c)/2, (self.rho_in + self.rho_out)/2),
                     textcoords="offset points", xytext=(0,10), ha='center')
        ax1.set_title("Physics Driver: Water Density vs. Temperature")
        ax1.set_xlabel("Temperature (°C)")
        ax1.set_ylabel("Density (kg/m³)")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Subplot 2: Power Generation vs Height
        ax2 = plt.subplot(2, 2, 2)
        ax2.plot(heights, power_gen, 'g-o', label='Power Generated (Hydro)', linewidth=2)
        ax2.fill_between(heights, 0, power_gen, color='green', alpha=0.1)
        ax2.set_title("Net Power Generation vs. Tower Height")
        ax2.set_xlabel("Tower Height (m)")
        ax2.set_ylabel("Power (kW)")
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Subplot 3: Comparison - Energy Cost vs Generation (at max height)
        ax3 = plt.subplot(2, 1, 2)
        
        # Pick a representative height (e.g., 100m or max)
        idx = -1 
        h_sample = heights[idx]
        p_gen_sample = power_gen[idx]
        p_trad_sample = power_trad[idx]
        
        labels = ['Green System (Generated)', 'Traditional Pump (Consumed)']
        values = [p_gen_sample, p_trad_sample]
        colors = ['#2ecc71', '#e74c3c']
        
        bars = ax3.barh(labels, values, color=colors, height=0.5)
        ax3.set_title(f"System Comparison at H = {h_sample}m")
        ax3.set_xlabel("Power (kW)")
        ax3.grid(axis='x', alpha=0.3)
        
        # Add labels to bars
        for bar in bars:
            width = bar.get_width()
            ax3.text(width + width*0.01, bar.get_y() + bar.get_height()/2, 
                     f'{width:.1f} kW', ha='left', va='center', fontweight='bold')
            
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        out = "assets/v1_base_concept.png"
        plt.savefig(out, dpi=150)
        print(f"Dashboard saved to {out}")

# --- Main Execution ---
if __name__ == "__main__":
    # 1. Initialize Simulation
    sim = CoolingSystemSim(t_in_c=20, t_out_c=50, pipe_diameter_m=0.5)
    
    # 2. Run Computations
    # Simulating a tower from 10m to 150m
    results = sim.simulate_height_range(min_h=10, max_h=150, step=10)
    
    # 3. Text Summary
    best_case = results[-1] # Taller is better for power in this model
    print("-" * 60)
    print("SIMULATION RESULTS SUMMARY")
    print("-" * 60)
    print(f"Operational Parameters:")
    print(f"  Water Delta T     : {sim.t_in_c}°C -> {sim.t_out_c}°C")
    print(f"  Pipe Diameter     : {sim.diameter} m")
    print(f"  Simulation Height : {best_case['height']} m")
    print("-" * 60)
    print(f"Physics Outputs:")
    print(f"  Density Difference: {sim.rho_in - sim.rho_out:.3f} kg/m³")
    print(f"  Buoyancy Head     : {best_case['buoyancy_pressure']/1000:.2f} kPa")
    print(f"  Induced Velocity  : {best_case['velocity']:.2f} m/s")
    print(f"  Mass Flow Rate    : {best_case['flow_rate'] * sim.rho_out:.1f} kg/s")
    print("-" * 60)
    print(f"Energy Analysis (at {best_case['height']}m):")
    print(f"  1. Hydro Power Generated  : {best_case['power_generated']/1000:.2f} kW")
    print(f"  2. Traditional Pump Cost  : {best_case['power_traditional']/1000:.2f} kW (Energy avoided)")
    print(f"  TOTAL NET BENEFIT         : {(best_case['power_generated'] + best_case['power_traditional'])/1000:.2f} kW")
    print("-" * 60)
    
    # 4. Visual Dashboard
    print("Generating Dashboard...")
    sim.plot_dashboard(results)
