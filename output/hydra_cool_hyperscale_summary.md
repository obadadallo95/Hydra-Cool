# Hydra-Cool Hyperscale Study Summary

- Study intent: evaluate Hydra-Cool as a retrofit assist layer that reduces legacy cooling energy, not as a standalone replacement requirement.
- Scenario count: 24000
- PASS rate: 8.76%
- MARGINAL rate: 0.00%
- FAIL rate: 91.24%
- Feasible hydraulic rate: 8.76%
- >=10% retrofit energy reduction rate: 8.76%
- Passive-natural PASS rate: 0.00%
- Retrofit-assist PASS rate: 8.76%
- Retrofit-assist MARGINAL rate: 0.00%
- Success layers: {'NO_VALID_LAYER': 21837, 'HYBRID_RETROFIT_ASSIST': 2102, 'PASSIVE_STANDALONE': 61}
- Mean energy savings fraction: 80.74%
- Median energy savings fraction: 91.01%
- Feasible mean energy savings fraction: 89.61%
- Feasible median energy savings fraction: 91.18%

## Dominant Failure Modes
- VELOCITY_TOO_LOW: 20984
- VELOCITY_TOO_HIGH: 861
- INVALID_TEMPERATURE_GRADIENT: 53

## Most Important Parameters
- it_load_mw: importance=0.360
- delta_t_c: importance=0.257
- pipe_diameter_m: importance=0.235
- hx_pressure_drop_kpa: importance=0.230
- number_of_pipes: importance=0.166

## Best Scenario Snapshot
- Classification: PASS
- Regime: RETROFIT_ASSIST
- IT load: 187.32 MW
- Number of pipes: 7
- Diameter: 0.77 m
- Vertical lift: 215.80 m
- Baseline cooling fraction: 6.20%
- Energy savings: 93.93%
- Net head: -2.17 m
- Natural cooling capacity ratio: 0.00
- Gravity assist fraction of hydraulic losses: 30.61%
- Turbine recovery active: False
- Interpretation: negative net head here means pump-assisted retrofit operation, not invalidity by itself.