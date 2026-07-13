# Current Parameter List (some may change into decision variables)

demand_average = 5000 # in MW
demand_peak = 6500 # in MW
demand_mining = 1000 # in MW
peak_hours = 5
non_peak_hours = 19
renewable_capacity_factor = 0.30
fossil_efficiency = 0.5
renewable_upfront_cost = 1500000 # $ dollars/mWh
fossil_generation_cost = 1000000 # $ dollars/mWh
renewable_generation_cost = 52 # $ dollars/mWh 
fossil_generation_cost = 80 # $ dollars/mWh 
mining_revenue = 90 # $ dollars/mWh
fossil_emission_factor = 450
renewable_emission_factor = 0
electriccost_peak = 200 # in dollars/mWh 
electriccost_nonpeak = 70 # in dollars/mWh
reserve_margin = 0.15 # (1+reserve margin)* peak demand must be less than total electric generation

# Current Decision Variable List

capacity_renewable = #expressed in megawatts (MW)
capacity_fossil = #expressed in megawatts (MW) - these are still arbitrary, depends on region etc.
capacity_flexible = # expressed in megawatts (MW)
capacity_total = capacity_renewable + capacity_fossil + capacity_flexible
generation_renewable =
generation_fossil =
generation_flexible =
generation_total =
blackout_time = # expressed in hours
blackout_losses =
blackout_frequency = # could be randomly generated, or could randomly generate demand
