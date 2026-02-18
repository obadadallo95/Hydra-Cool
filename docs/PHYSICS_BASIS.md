# Hydra-Cool Physics Basis

## 1. Flow Rate (Mass Constraint)
To remove a specific heat load (IT Load), the mass flow rate is determined by the specific heat capacity of seawater and the allowed temperature rise.

$$ Q_{mass} = \frac{P_{thermal}}{C_p \cdot \Delta T} $$

Where:
- $Q_{mass}$: Mass flow rate [kg/s]
- $P_{thermal}$: IT Load [W]
- $C_p$: Specific heat capacity of seawater $\approx 3993$ [J/kg·K]
- $\Delta T$: Temperature difference ($T_{out} - T_{in}$) [K]

## 2. Seawater Density
Density is a function of temperature (and salinity, assumed constant at 35 ppt). We use a polynomial approximation accurate for 0-80°C.

$$ \rho(T) = 1028.17 - 0.0663T - 0.0038T^2 $$

Where:
- $\rho$: Density [kg/m³]
- $T$: Temperature [°C]

## 3. Buoyancy Pressure (Driving Force)
The density difference between the cold intake column and the hot riser column creates a natural pressure differential (buoyancy).

$$ \Delta P_{buoyancy} = (\rho_{cold} - \rho_{hot}) \cdot g \cdot H $$

Where:
- $\Delta P_{buoyancy}$: Buoyancy pressure [Pa]
- $\rho_{cold}$: Density of intake water [kg/m³]
- $\rho_{hot}$: Density of discharge water [kg/m³]
- $g$: Acceleration due to gravity ($9.81$ m/s²)
- $H$: Height of the water column [m]

## 4. Friction Losses (Darcy-Weisbach)
Resistance to flow in pipes reduces the available pressure head.

$$ \Delta P_{friction} = f \cdot \frac{L}{D} \cdot \frac{\rho v^2}{2} $$

Where:
- $f$: Darcy friction factor (calculated via Colebrook-White or Swamee-Jain approximation)
- $L$: Pipe length [m]
- $D$: Pipe diameter [m]
- $v$: Flow velocity [m/s] ($v = \frac{Q_{vol}}{A}$)

## 5. Turbine Power Generation
Energy recovered from the water falling from the high reservoir back to sea level.

$$ P_{turbine} = \eta_{turbine} \cdot \rho \cdot g \cdot Q_{vol} \cdot H_{net} $$

Where:
- $\eta_{turbine}$: Turbine efficiency (0.82-0.88 for Francis)
- $H_{net}$: Net head available after losses [m]

## 6. Net Energy Balance
The ultimate metric for system viability.

$$ P_{net} = P_{turbine} - P_{pumps} - P_{auxiliary} $$

- Positive $P_{net}$: System generates electricity.
- Negative $P_{net}$ (but small): System is highly efficient (low cooling cost).
