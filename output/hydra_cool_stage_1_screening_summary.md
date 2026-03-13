# Hydra-Cool Stage 1 Screening Summary

- Study intent: evaluate Hydra-Cool as a retrofit assist layer that reduces legacy cooling energy, not as a standalone replacement requirement.
- Scenario count: 24000
- PASS rate: 8.65%
- MARGINAL rate: 0.00%
- FAIL rate: 91.35%
- Feasible hydraulic rate: 8.76%
- >=10% retrofit energy reduction rate: 8.65%
- Passive-natural PASS rate: 0.00%
- Retrofit-assist PASS rate: 8.65%
- Retrofit-assist MARGINAL rate: 0.00%
- Success layers: {'NO_VALID_LAYER': 21837, 'HYBRID_RETROFIT_ASSIST': 2102, 'PASSIVE_STANDALONE': 61}
- Mean energy savings fraction: 39.31%
- Median energy savings fraction: 74.08%
- Feasible mean energy savings fraction: 70.16%
- Feasible median energy savings fraction: 75.65%

## Dominant Failure Modes
- VELOCITY_TOO_LOW: 20984
- VELOCITY_TOO_HIGH: 861
- INVALID_TEMPERATURE_GRADIENT: 53
- INSUFFICIENT_NATURAL_CIRCULATION: 25

## Most Important Parameters
- it_load_mw: importance=0.383
- pipe_diameter_m: importance=0.227
- delta_t_c: importance=0.224
- hx_pressure_drop_kpa: importance=0.214
- number_of_pipes: importance=0.159

## Best Scenario Snapshot
- Classification: PASS
- Regime: RETROFIT_ASSIST
- IT load: 187.32 MW
- Number of pipes: 7
- Diameter: 0.77 m
- Vertical lift: 215.80 m
- Baseline cooling fraction: 4.75%
- Energy savings: 82.48%
- Net head: -2.17 m
- Natural cooling capacity ratio: 0.00
- Gravity assist fraction of hydraulic losses: 30.61%
- Turbine recovery active: False
- Interpretation: negative net head here means pump-assisted retrofit operation, not invalidity by itself.