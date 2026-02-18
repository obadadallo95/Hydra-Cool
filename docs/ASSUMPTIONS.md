# Hydra-Cool Assumptions & Reference Values

## 1. Environmental Parameters
| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| **Gravity** | 9.81 | m/s² | Standard gravity |
| **Seawater Salinity** | 35 | ppt | Standard ocean salinity |
| **Deep Sea Temp (Cold)** | 4 - 6 | °C | North Sea / Atlantic at >300m depth |
| **Surface Temp** | 20 | °C | Reference surface temp (varies by location) |
| **Air Density** | 1.225 | kg/m³ | Sea level |

## 2. System Efficiencies
| Component | Efficiency ($\eta$) | Notes |
|-----------|---------------------|-------|
| **Turbine** | 0.85 (85%) | Standard Francis/Kaplan turbine |
| **Pump** | 0.82 (82%) | Large centrifugal pump |
| **Generator** | 0.96 (96%) | Electric generator efficiency |
| **Heat Exchanger** | 0.90 (effectiveness) | Plate & Frame HX |

## 3. Reference Loads
| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| **Base IT Load** | 100 | MW | Hyperscale Data Center Module |
| **Target $\Delta T$** | 40 | °C | $T_{in}=5^\circ C \to T_{out}=45-50^\circ C$ |

## 4. Hydraulic Parameters
| Parameter | Value | Notes |
|-----------|-------|-------|
| **Pipe Roughness ($\epsilon$)** | 0.045 mm | Commercial Steel / HDPE |
| **Minor Loss Coeff ($K$)** | 3.0 | Estimate for bends, valves, intake/outlet |
| **HX Pressure Drop** | 50,000 Pa | Typical 0.5 bar drop across HX |

## 5. Constraints
- **Max Pressure**: Pipes must withstand hydrostatic pressure at depth.
- **Min Velocity**: > 0.6 m/s to prevent sediment settling.
- **Max Velocity**: < 3.0 m/s to prevent erosion/noise and limit head loss.
