# Hydra-Cool Stage 3 Focus Window Summary

- Study intent: evaluate Hydra-Cool as a retrofit assist layer that reduces legacy cooling energy, not as a standalone replacement requirement.
- Scenario count: 995328
- PASS rate: 48.50%
- MARGINAL rate: 0.00%
- FAIL rate: 51.50%
- Feasible hydraulic rate: 48.50%
- >=10% retrofit energy reduction rate: 48.50%
- Passive-natural PASS rate: 2.64%
- Retrofit-assist PASS rate: 45.86%
- Retrofit-assist MARGINAL rate: 0.00%
- Success layers: {'HYBRID_RETROFIT_ASSIST': 456442, 'NO_VALID_LAYER': 444579, 'PASSIVE_STANDALONE': 94307}
- Mean energy savings fraction: 78.06%
- Median energy savings fraction: 78.19%
- Feasible mean energy savings fraction: 78.69%
- Feasible median energy savings fraction: 78.94%

## Dominant Failure Modes
- VELOCITY_TOO_LOW: 507456
- VELOCITY_TOO_HIGH: 5184

## Most Important Parameters
- it_load_mw: importance=0.504
- hx_pressure_drop_kpa: importance=0.337
- number_of_pipes: importance=0.247
- pipe_diameter_m: importance=0.235
- delta_t_c: importance=0.190

## Best Scenario Snapshot
- Classification: PASS
- Regime: PASSIVE_NATURAL
- IT load: 200.00 MW
- Number of pipes: 2
- Diameter: 1.20 m
- Vertical lift: 250.00 m
- Baseline cooling fraction: 4.27%
- Energy savings: 81.43%
- Net head: 1.31 m
- Natural cooling capacity ratio: 3.22
- Gravity assist fraction of hydraulic losses: 100.00%
- Turbine recovery active: True
- Interpretation: negative net head here means pump-assisted retrofit operation, not invalidity by itself.