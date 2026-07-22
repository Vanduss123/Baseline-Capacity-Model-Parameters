"""
Bitcoin Mining + Electricity Market Scenario Model

Includes:
- S0-S15 scenarios
- Hourly simulation (8760 hours)
- Mining flexibility strategies
- Emissions
- Profitability
- System costs
- Welfare decomposition

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


# ==========================================================
# BASIC SETTINGS
# ==========================================================

np.random.seed(42)

HOURS = 8760

RESULT_FOLDER = "results"

os.makedirs(
    RESULT_FOLDER,
    exist_ok=True
)



# ==========================================================
# SCENARIOS
# ==========================================================


SCENARIOS = {


"S0":
{
"scenario_name":
"no_mining_baseline",

"strategy":
"none",

"market_structure":
"restructured"
},



"S1":
{
"scenario_name":
"always_on_mining",

"strategy":
"always_on",

"market_structure":
"restructured"
},



"S2":
{
"scenario_name":
"surplus_following",

"strategy":
"surplus",

"market_structure":
"restructured"
},



"S3":
{
"scenario_name":
"carbon_aware",

"strategy":
"carbon",

"market_structure":
"restructured"
},



"S4":
{
"scenario_name":
"price_responsive",

"strategy":
"price",

"market_structure":
"restructured"
},



"S5":
{
"scenario_name":
"reliability_demand_response",

"strategy":
"reliability",

"market_structure":
"restructured"
},



"S6":
{
"scenario_name":
"municipal_surplus_utilization",

"strategy":
"municipal_surplus",

"market_structure":
"municipal"
},



"S7":
{
"scenario_name":
"municipal_carbon_aware",

"strategy":
"municipal_carbon",

"market_structure":
"municipal"
},



"S8":
{
"scenario_name":
"regulated_utility",

"strategy":
"reliability",

"market_structure":
"regulated"
},



"S9":
{
"scenario_name":
"wholesale_market",

"strategy":
"price",

"market_structure":
"restructured"
},



"S10":
{
"scenario_name":
"high_carbon_price",

"strategy":
"carbon",

"carbon_price":
100,

"market_structure":
"restructured"
},



"S11":
{
"scenario_name":
"low_bitcoin_price",

"strategy":
"price",

"bitcoin_price":
30000,

"market_structure":
"restructured"
},



"S12":
{
"scenario_name":
"high_bitcoin_price",

"strategy":
"price",

"bitcoin_price":
100000,

"market_structure":
"restructured"
},



"S13":
{
"scenario_name":
"high_renewable_penetration",

"strategy":
"surplus",

"renewable_multiplier":
1.5,

"market_structure":
"restructured"
},



"S14":
{
"scenario_name":
"constrained_grid",

"strategy":
"reliability",

"grid_capacity":
6100,

"reserve_requirement":
850,

"market_structure":
"restructured"
},



"S15":
{
"scenario_name":
"mining_with_new_renewable_investment",

"strategy":
"price",

"renewable_investment":
True,

"market_structure":
"restructured"
}

}




# ==========================================================
# MODEL PARAMETERS
# ==========================================================


PARAMETERS = {


# --------------------------
# Demand
# --------------------------

"base_demand_mw":
5000,



# --------------------------
# Generation Capacity
# --------------------------

"solar_capacity_mw":
4000,


"wind_capacity_mw":
3000,


"fossil_capacity_mw":
8000,



# --------------------------
# Mining
# --------------------------

"mining_capacity_mw":
1000,


"bitcoin_price":
60000,


"bitcoin_revenue_per_mwh":
100,



# --------------------------
# Carbon
# --------------------------

"carbon_factor":
0.4,


"private_carbon_price":
50,


"social_carbon_cost":
150,



# --------------------------
# Costs
# --------------------------

"solar_om":
5,


"wind_om":
4,


"fossil_fuel_cost":
60,


"value_of_lost_load":
10000,



# --------------------------
# Investment
# --------------------------

"solar_capex":
900000,


"wind_capex":
1200000

}




# ==========================================================
# GRID GENERATION
# ==========================================================


def generate_grid(
        scenario):


    hour = np.arange(
        HOURS
    )



    # Demand profile

    daily_pattern = (

        1

        +
        0.25 *
        np.sin(
            2*np.pi*hour/24
        )

    )


    demand = (

        PARAMETERS[
            "base_demand_mw"
        ]

        *

        daily_pattern

        *

        np.random.uniform(
            0.9,
            1.1,
            HOURS
        )

    )



    # Renewable adjustment

    renewable_multiplier = scenario.get(

        "renewable_multiplier",

        1

    )



    solar = (

        PARAMETERS[
            "solar_capacity_mw"
        ]

        *

        renewable_multiplier

        *

        np.maximum(

            np.sin(
                np.pi*(hour%24)/24
            ),

            0

        )

    )



    wind = (

        PARAMETERS[
            "wind_capacity_mw"
        ]

        *

        renewable_multiplier

        *

        np.random.uniform(

            0.3,
            1,

            HOURS

        )

    )



    fossil_capacity = scenario.get(

        "grid_capacity",

        PARAMETERS[
            "fossil_capacity_mw"
        ]

    )


    fossil = np.minimum(

        fossil_capacity,

        demand

    )



    # electricity market price

    price = (

        30

        +

        0.015*demand

        -

        0.004*(solar+wind)

    )



    carbon_intensity = np.where(

        fossil>0,

        PARAMETERS[
            "carbon_factor"
        ],

        0

    )



    return pd.DataFrame({

        "hour":
        hour,


        "demand":
        demand,


        "solar":
        solar,


        "wind":
        wind,


        "fossil":
        fossil,


        "price":
        price,


        "carbon_intensity":
        carbon_intensity

    })

# ==========================================================
# MINING OPERATING STRATEGY
# ==========================================================


def determine_mining_load(
        row,
        scenario):


    strategy = scenario["strategy"]


    mining_capacity = PARAMETERS[
        "mining_capacity_mw"
    ]


    bitcoin_price = scenario.get(
        "bitcoin_price",
        PARAMETERS["bitcoin_price"]
    )


    private_carbon_price = scenario.get(
        "carbon_price",
        PARAMETERS["private_carbon_price"]
    )



    renewable_surplus = (

        row.solar
        +
        row.wind
        -
        row.demand

    )



    # S0

    if strategy == "none":

        return 0



    # S1

    elif strategy == "always_on":

        return mining_capacity



    # S2, S6, S13

    elif strategy in [
        "surplus",
        "municipal_surplus"
    ]:

        return max(
            0,
            min(
                mining_capacity,
                renewable_surplus
            )
        )



    # S3, S7

    elif strategy in [
        "carbon",
        "municipal_carbon"
    ]:


        carbon_cost = (

            row.carbon_intensity

            *

            private_carbon_price

        )


        if carbon_cost < 30:

            return mining_capacity

        else:

            return 0



    # S4, S9, S11, S12, S15

    elif strategy == "price":


        mining_revenue_per_mwh = (

            bitcoin_price
            /
            100000
            *
            PARAMETERS[
                "bitcoin_revenue_per_mwh"
            ]

        )


        if mining_revenue_per_mwh > row.price:

            return mining_capacity

        else:

            return 0



    # S5, S8, S14

    elif strategy == "reliability":


        available_reserve = (

            PARAMETERS[
                "fossil_capacity_mw"
            ]

            -

            row.demand

        )


        if available_reserve > 1000:

            return mining_capacity

        else:

            return 0



    return 0







# ==========================================================
# COMPLETE SCENARIO SIMULATION
# ==========================================================


def simulate_scenario(
        scenario_id,
        scenario):


    grid = generate_grid(
        scenario
    )



    mining=[]



    for _,row in grid.iterrows():

        mining.append(

            determine_mining_load(

                row,

                scenario

            )

        )



    grid["mining"] = mining



    # ======================================================
    # POWER BALANCE
    # ======================================================


    grid["total_load"] = (

        grid.demand

        +

        grid.mining

    )


    grid["renewable_generation"] = (

        grid.solar

        +

        grid.wind

    )



    grid["renewable_used"] = np.minimum(

        grid.renewable_generation,

        grid.total_load

    )



    grid["curtailment"] = (

        grid.renewable_generation

        -

        grid.renewable_used

    ).clip(
        lower=0
    )



    grid["total_generation"] = (

        grid.solar

        +

        grid.wind

        +

        grid.fossil

    )



    grid["energy_not_served"] = (

        grid.total_load

        -

        grid.total_generation

    ).clip(
        lower=0
    )


    grid["blackout"] = (

        grid.energy_not_served > 0

    )






    # ======================================================
    # EMISSIONS
    # ======================================================


    total_emissions = (

        grid.fossil.sum()

        *

        PARAMETERS[
            "carbon_factor"
        ]

    )



    private_carbon_cost = (

        total_emissions

        *

        scenario.get(

            "carbon_price",

            PARAMETERS[
                "private_carbon_price"
            ]

        )

    )



    social_carbon_damage = (

        total_emissions

        *

        PARAMETERS[
            "social_carbon_cost"
        ]

    )





    # ======================================================
    # MINING ECONOMICS
    # ======================================================


    bitcoin_price = scenario.get(

        "bitcoin_price",

        PARAMETERS[
            "bitcoin_price"
        ]

    )



    bitcoin_revenue = (

        grid.mining.sum()

        *

        (
            bitcoin_price

            /

            100000

        )

        *

        PARAMETERS[
            "bitcoin_revenue_per_mwh"
        ]

    )



    mining_energy_cost = (

        grid.mining

        *

        grid.price

    ).sum()



    mining_carbon_cost = (

        grid.mining

        *

        grid.carbon_intensity

        *

        scenario.get(

            "carbon_price",

            PARAMETERS[
                "private_carbon_price"
            ]

        )

    ).sum()



    mining_profit = (

        bitcoin_revenue

        -

        mining_energy_cost

        -

        mining_carbon_cost

    )



    profit_per_mwh = (

        mining_profit

        /

        max(
            grid.mining.sum(),
            1
        )

    )






    # ======================================================
    # GENERATION COSTS
    # ======================================================


    solar_cost = (

        grid.solar.sum()

        *

        PARAMETERS[
            "solar_om"
        ]

    )



    wind_cost = (

        grid.wind.sum()

        *

        PARAMETERS[
            "wind_om"
        ]

    )



    fossil_cost = (

        grid.fossil.sum()

        *

        PARAMETERS[
            "fossil_fuel_cost"
        ]

    )



    generation_cost = (

        solar_cost

        +

        wind_cost

        +

        fossil_cost

    )





    # ======================================================
    # RELIABILITY COST
    # ======================================================


    reliability_cost = (

        grid.energy_not_served.sum()

        *

        PARAMETERS[
            "value_of_lost_load"
        ]

    )





    # ======================================================
    # INVESTMENT COST
    # ======================================================


    investment_cost = 0



    if scenario.get(
        "renewable_investment",
        False
    ):


        investment_cost = (

            PARAMETERS[
                "solar_capex"
            ]

            *

            1000

        )






    # ======================================================
    # TOTAL SYSTEM COST
    # ======================================================


    total_system_cost = (

        generation_cost

        +

        mining_energy_cost

        +

        social_carbon_damage

        +

        reliability_cost

        +

        investment_cost

    )



    average_system_cost = (

        total_system_cost

        /

        max(
            grid.total_load.sum(),
            1
        )

    )



    # ======================================================
    # WELFARE COMPONENTS
    # ======================================================


    producer_surplus = (

        grid.price

        *

        grid.total_generation

    ).sum()



    consumer_cost = (

        grid.price

        *

        grid.demand

    ).sum()



    social_welfare = (

        producer_surplus

        -

        consumer_cost

        +

        bitcoin_revenue

        -

        social_carbon_damage

        -

        reliability_cost

        -

        investment_cost

    )

# ==========================================================
# RUN ALL SCENARIOS
# ==========================================================

scenario_results = []

hourly_results = []


for scenario_id, scenario in SCENARIOS.items():

    print(
        f"Running {scenario_id}: {scenario['scenario_name']}"
    )

    summary, hourly = simulate_scenario(
        scenario_id,
        scenario
    )

    scenario_results.append(summary)

    hourly_results.append(hourly)



# Combine results

summary_df = pd.DataFrame(
    scenario_results
)


hourly_df = pd.concat(
    hourly_results,
    ignore_index=True
)



# ==========================================================
# EXPORT RESULTS
# ==========================================================

summary_df.to_csv(
    RESULT_FOLDER + "/scenario_results.csv",
    index=False
)


hourly_df.to_csv(
    RESULT_FOLDER + "/hourly_results.csv",
    index=False
)



# ==========================================================
# WELFARE DECOMPOSITION EXPORT
# ==========================================================

welfare_df = summary_df[
    [
        "scenario",
        "producer_surplus_$",
        "bitcoin_revenue_$",
        "consumer_cost_$",
        "social_carbon_damage_$",
        "reliability_cost_$",
        "renewable_investment_$",
        "social_welfare_$"
    ]
]


welfare_df.to_csv(
    RESULT_FOLDER + "/welfare_decomposition.csv",
    index=False
)



# ==========================================================
# COST BREAKDOWN EXPORT
# ==========================================================

cost_df = summary_df[
    [
        "scenario",
        "generation_cost_$",
        "mining_energy_cost_$",
        "social_carbon_damage_$",
        "reliability_cost_$",
        "renewable_investment_$",
        "total_system_cost_$"
    ]
]


cost_df.to_csv(
    RESULT_FOLDER + "/cost_breakdown.csv",
    index=False
)





# ==========================================================
# GRAPH FUNCTION
# ==========================================================


def make_bar_chart(
        column,
        title,
        filename):

    plt.figure(
        figsize=(12,6)
    )

    plt.bar(
        summary_df["scenario"],
        summary_df[column]
    )

    plt.title(title)

    plt.xticks(
        rotation=45
    )

    plt.tight_layout()

    plt.savefig(
        RESULT_FOLDER + "/" + filename,
        dpi=300
    )

    plt.close()





# ==========================================================
# GENERATE FIGURES
# ==========================================================


make_bar_chart(
    "total_system_cost_$",
    "Total System Cost by Scenario",
    "system_cost.png"
)


make_bar_chart(
    "social_welfare_$",
    "Social Welfare by Scenario",
    "social_welfare.png"
)


make_bar_chart(
    "mining_profit_$",
    "Bitcoin Mining Profitability",
    "mining_profit.png"
)


make_bar_chart(
    "CO2_emissions_tons",
    "Annual CO2 Emissions",
    "emissions.png"
)


make_bar_chart(
    "renewable_utilization",
    "Renewable Utilization",
    "renewable_utilization.png"
)


make_bar_chart(
    "curtailment_MWh",
    "Renewable Curtailment",
    "curtailment.png"
)


make_bar_chart(
    "blackout_hours",
    "Reliability Performance",
    "reliability.png"
)





# ==========================================================
# MINING LOAD PROFILE FIGURE
# ==========================================================


plt.figure(
    figsize=(12,5)
)


plot_scenarios = [
    "S0",
    "S1",
    "S2",
    "S4",
    "S12",
    "S15"
]


for s in plot_scenarios:

    temp = hourly_df[
        hourly_df["scenario"] == s
    ]

    if len(temp) > 0:

        plt.plot(
            temp["hour"].iloc[:500],
            temp["mining"].iloc[:500],
            label=s
        )



plt.title(
    "Bitcoin Mining Load Profiles"
)


plt.xlabel(
    "Hour"
)


plt.ylabel(
    "Mining Load (MW)"
)


plt.legend()


plt.tight_layout()


plt.savefig(
    RESULT_FOLDER + "/mining_profiles.png",
    dpi=300
)


plt.close()





# ==========================================================
# FINAL OUTPUT
# ==========================================================


print("\n===================================")
print("SIMULATION COMPLETE")
print("===================================")

print(
    f"Generated {len(summary_df)} scenarios"
)

print(
    "Results saved in:",
    RESULT_FOLDER
)

