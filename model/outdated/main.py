# IMPORT REQUIRED PACKAGES
#
#
import shutil
import sys
import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import chart_studio
import chart_studio.plotly as py
import seaborn as sns
import chart_studio.plotly as py
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import folium
from folium.plugins import MarkerCluster
import json
import geopy as gpy
from IPython.display import display
from geopy import distance
from pyomo.environ import *
print("IMPORTING PACKAGES SUCCEEDED.")


# SET PACKAGE SETTINGS
#
#
pd.set_option("precision", 3)


# DEFINE CONSTANTS
#
#
import constants

MMBtu_LNG, MMBtu_Gas, mt_LNG_BCM, mt_MMBtu, t_oil_MMBtu, LNG_to_Gas = constants.get_values()

if False:
    print("Check parameter settings.")
    print("MMBtu_LNG : %s" % np.round(MMBtu_LNG, 2))
    print("MMBtu_Gas : %s" % np.round(MMBtu_Gas, 3))
    print("mt_LNG_BCM : %s" % np.round(mt_LNG_BCM, 0))
    print("mt_MMBtu : %s" % np.round(mt_MMBtu, 1))
    print("t_oil_MMBtu : %s" % np.round(t_oil_MMBtu, 3))

import_countries = [
    "Japan",
    "China",
    "South Korea",
    "India",
    "Taiwan",
    "Pakistan",
    "France",
    "Spain",
    "UK",
    "Italy",
    "Turkey",
    "Belgium",
    "Other Asia Pacific",
    "Other Europe",
    "Total North America",
    "Total S. & C. America",
    "Total ME & Africa",
]

# Countries that are large exporters and possibly missing are:
# (in billion cubic meters "bcm")
#       Papua New Guinea (11.4)
#       Egypt (8.9)
#       United Arab Emirates (7.6)
#       Brunei (6.4)
#       Angola (4.1)
# Source: https://www.statista.com/statistics/274528/major-exporting-countries-of-lng/

export_countries = [
    "Qatar",
    "Australia",
    "USA",
    "Russia",
    "Malaysia",
    "Nigeria",
    "Trinidad & Tobago",
    "Algeria",
    "Indonesia",
    "Oman",
    "Other Asia Pacific",
    "Other Europe",
    "Other Americas",
    "Other ME",
    "Other Africa",
]
###############################################################################

###############################################################################

# ADD DATA
#
#
from add_data import add_dataframes
(
    Imp_Nodes,
    Exp_Nodes,
    Distances,
    Distances_Suez_Closed,
    LNG_Carrier,
    Additional_Costs,
    CO2,
    CH4,
    empty_df,
) = add_dataframes()


if True:
    Imp_Nodes.drop('Location', axis=1).to_excel('data/import_nodes.xlsx', index=False)
    Exp_Nodes.to_excel('data/export_nodes.xlsx', index=False)
    Distances.to_excel('data/distances.xlsx', index=True)
    Distances_Suez_Closed.to_excel('data/distances_suez_closed.xlsx', index=True)
    LNG_Carrier.to_excel('data/lng_carrier.xlsx', index=False)
    Additional_Costs.to_excel('data/additional_costs.xlsx', index=False)
    CO2.to_excel('data/carbon.xlsx', index=False)
    CH4.to_excel('data/methane.xlsx') 
    # empty_df ... matrix of import nodes (x-axis) and export nodes (y-axis)
    print('SAVE DATA TO EXCEL FILES SUCCEEDED.')
    

# PLOT DATA
#
#
# from plots import plot_map
# plot_map(Imp_Nodes, Exp_Nodes)
# print('PRINTING INPUT DATA SUCCEEDED.')

###############################################################################

###############################################################################

# ADD COSTS
#
#
from add_data import add_costs







(Time, Time_Suez_Closed, CO2_Emissions, CH4_Emissions, Total_Costs) = add_costs(
    Distances, Distances_Suez_Closed, LNG_Carrier, Additional_Costs, CO2, CH4
)

Cost = {}
for index in Total_Costs.index:
    for column in Total_Costs.columns:
        Cost[column, index] = Total_Costs.loc[index, column]

_destination = []
_origin = []
_costs = [] # ... in $ / MMBtu

for _i in Cost.keys():
    _destination.append(_i[0])
    _origin.append(_i[1])
    _costs.append(Cost[_i])
    
_cost_file = pd.DataFrame(
    data = {
        'Origin' : _origin,
        'Destination' : _destination,
        'Costs in $/MMBtu' : _costs
        }
    )

_cost_file.to_excel('data/input/calculated_costs_in_dollar_per_mmbtu.xlsx', index=False)
        
        
        
        

###############################################################################
### 2) create model and solve for every month
###############################################################################
from utils import create_and_solve_model
from utils import calculate_model_month

# calculate supply and demand in every month
Supply = Exp_Nodes.set_index("Country")[
    "Nominal Liquefaction Capacity (MMBtu)"
].to_dict()
Supply_Jan = Exp_Nodes.set_index("Country")["Export Jan (MMBtu)"].to_dict()
Supply_Jun = Exp_Nodes.set_index("Country")["Export Jun (MMBtu)"].to_dict()
Supply_Aug = Exp_Nodes.set_index("Country")["Export Aug (MMBtu)"].to_dict()
Supply_Sep = Exp_Nodes.set_index("Country")["Export Sep (MMBtu)"].to_dict()
Supply_Nov = Exp_Nodes.set_index("Country")["Export Nov (MMBtu)"].to_dict()
Supply_Dec = Exp_Nodes.set_index("Country")["Export Dec (MMBtu)"].to_dict()
Supply_2019 = Exp_Nodes.set_index("Country")[
    "Nominal Liquefaction Capacity 2019 (MMBtu)"
].to_dict()
Supply_2030 = Exp_Nodes.set_index("Country")["Export 2030 (MMBtu)"].to_dict()
Supply_2040 = Exp_Nodes.set_index("Country")["Export 2040 (MMBtu)"].to_dict()
Supply_HC = Exp_Nodes.set_index("Country")[
    "Nominal Liquefaction Capacity 2019 HC (MMBtu)"
].to_dict()

Demand_Jan = Imp_Nodes.set_index("Country")["Import Jan (MMBtu)"].to_dict()
Demand_Feb = Imp_Nodes.set_index("Country")["Import Feb (MMBtu)"].to_dict()
Demand_Mar = Imp_Nodes.set_index("Country")["Import Mar (MMBtu)"].to_dict()
Demand_Apr = Imp_Nodes.set_index("Country")["Import Apr (MMBtu)"].to_dict()
Demand_May = Imp_Nodes.set_index("Country")["Import May (MMBtu)"].to_dict()
Demand_Jun = Imp_Nodes.set_index("Country")["Import Jun (MMBtu)"].to_dict()
Demand_Jul = Imp_Nodes.set_index("Country")["Import Jul (MMBtu)"].to_dict()
Demand_Aug = Imp_Nodes.set_index("Country")["Import Aug (MMBtu)"].to_dict()
Demand_Sep = Imp_Nodes.set_index("Country")["Import Sep (MMBtu)"].to_dict()
Demand_Oct = Imp_Nodes.set_index("Country")["Import Oct (MMBtu)"].to_dict()
Demand_Nov = Imp_Nodes.set_index("Country")["Import Nov (MMBtu)"].to_dict()
Demand_Dec = Imp_Nodes.set_index("Country")["Import Dec (MMBtu)"].to_dict()
Demand_2019 = Imp_Nodes.set_index("Country")["Import (MMBtu)"].to_dict()
Demand_2030 = Imp_Nodes.set_index("Country")["Import 2030 (MMBtu)"].to_dict()
Demand_2040 = Imp_Nodes.set_index("Country")["Import 2040 (MMBtu)"].to_dict()
Demand_2019_EU = Imp_Nodes.set_index("Country")["Import Europe +33% (MMBtu)"].to_dict()
Demand_2019_Asia = Imp_Nodes.set_index("Country")[
    "Import Asia Pacific -20% (MMBtu)"
].to_dict()

CUS = list(Demand_2019.keys())
SRC = list(Supply_2019.keys())




















###############################################################################
# January
model_2019_Jan = create_and_solve_model(Demand_Jan, Supply_Jan, Cost)

Import = [
    10.5651,
    9.2547,
    6.279,
    2.83,
    2.2386,
    1.1288,
    1.632,
    1.42,
    1.741,
    1.074,
    2.353,
    0.585,
    1.7,
    1.9584,
    0.911,
    0.3536,
    0.0952,
]
transported_LNG_3_Jan, DES_Price_Jan = calculate_model_month(
    model_2019_Jan, Total_Costs, Distances, "Jan", Import
)

###############################################################################
# February
model_2019_Feb = create_and_solve_model(Demand_Feb, Supply, Cost)

Import = [
    10.30575,
    5.93775,
    4.095,
    2.56,
    1.46055,
    0.9248,
    1.83,
    1.374,
    1.17,
    0.93,
    1.782,
    0.299,
    1.768,
    1.8496,
    0.6528,
    1.02,
    0.3536,
]
transported_LNG_3_Feb, DES_Price_Feb = calculate_model_month(
    model_2019_Feb, Total_Costs, Distances, "Feb", Import
)


###############################################################################
# March
model_2019_Mar = create_and_solve_model(Demand_Mar, Supply, Cost)

Import = [
    10.22385,
    5.5419,
    3.78105,
    2.38,
    2.0475,
    1.2104,
    2.335,
    1.493,
    1.78,
    1.605,
    1.4,
    1.115,
    2.1986,
    1.6864,
    0.9656,
    0.9112,
    0.1768,
]
transported_LNG_3_Mar, DES_Price_Mar = calculate_model_month(
    model_2019_Mar, Total_Costs, Distances, "Mar", Import
)

###############################################################################
# April
model_2019_Apr = create_and_solve_model(Demand_Apr, Supply, Cost)

Import = [
    7.7532,
    6.1971,
    3.9585,
    2.62,
    2.0748,
    1.1832,
    2.572,
    1.596,
    2.244,
    1.115,
    0.707,
    0.8074,
    2.2168,
    2.1624,
    1.02,
    1.0744,
    0.748,
]
transported_LNG_3_Apr, DES_Price_Apr = calculate_model_month(
    model_2019_Apr, Total_Costs, Distances, "Apr", Import
)

###############################################################################
# May
model_2019_May = create_and_solve_model(Demand_May, Supply, Cost)

Import = [
    7.7259,
    6.04695,
    4.05405,
    2.75,
    2.03385,
    1.1152,
    1.832,
    1.656,
    2.19,
    1.115,
    0.503,
    0.7028,
    2.9784,
    2.4072,
    0.9656,
    1.1424,
    1.4144,
]
transported_LNG_3_May, DES_Price_May = calculate_model_month(
    model_2019_May, Total_Costs, Distances, "May", Import
)

###############################################################################
# June
model_2019_Jun = create_and_solve_model(Demand_Jun, Supply_Jun, Cost)

Import = [
    7.7259,
    6.04695,
    4.05405,
    2.75,
    2.03385,
    1.1152,
    1.832,
    1.656,
    2.19,
    1.115,
    0.503,
    0.7028,
    2.9784,
    2.4072,
    0.9656,
    1.1424,
    1.4144,
]
transported_LNG_3_Jun, DES_Price_Jun = calculate_model_month(
    model_2019_Jun, Total_Costs, Distances, "Jun", Import
)

###############################################################################
# July
model_2019_Jul = create_and_solve_model(Demand_Jul, Supply, Cost)

Import = [
    7.2345,
    6.18345,
    4.54545,
    2.73,
    1.89735,
    1.0744,
    1.739,
    1.903,
    0.76,
    1.387,
    0.68,
    0.6528,
    2.0264,
    2.312,
    1.2784,
    1.904,
    1.3192,
]
transported_LNG_3_Jul, DES_Price_Jul = calculate_model_month(
    model_2019_Jul, Total_Costs, Distances, "Jul", Import
)

###############################################################################
# August
model_2019_Aug = create_and_solve_model(Demand_Aug, Supply_Aug, Cost)

Import = [
    8.463,
    7.5075,
    4.914,
    2.82,
    1.8837,
    1.0064,
    1.638,
    2.144,
    0.19,
    1.265,
    0.816,
    0.9112,
    2.4888,
    1.9176,
    1.088,
    1.7408,
    1.8496,
]
transported_LNG_3_Aug, DES_Price_Aug = calculate_model_month(
    model_2019_Aug, Total_Costs, Distances, "Aug", Import
)

###############################################################################
# September
model_2019_Sep = create_and_solve_model(Demand_Sep, Supply_Sep, Cost)

Import = [
    8.94075,
    6.92055,
    3.4125,
    2.79,
    2.0475,
    0.9928,
    1.2745,
    2.139,
    1.3,
    1.13,
    0.558,
    0.2856,
    2.3256,
    1.8088,
    1.0064,
    1.0472,
    1.5776,
]
transported_LNG_3_Sep, DES_Price_Sep = calculate_model_month(
    model_2019_Sep, Total_Costs, Distances, "Sep", Import
)

###############################################################################
# October
model_2019_Oct = create_and_solve_model(Demand_Oct, Supply, Cost)

Import = [
    8.85885,
    5.6511,
    4.368,
    2.83,
    2.00655,
    1.0608,
    1.7745,
    1.95,
    1.85,
    1.35,
    0.843,
    0.7616,
    2.1986,
    2.0944,
    0.9248,
    0.8024,
    1.1016,
]
transported_LNG_3_Oct, DES_Price_Oct = calculate_model_month(
    model_2019_Oct, Total_Costs, Distances, "Oct", Import
)

###############################################################################
# November
model_2019_Nov = create_and_solve_model(Demand_Nov, Supply_Nov, Cost)

Import = [
    8.83155,
    8.66775,
    5.1597,
    2.79,
    1.51515,
    0.6664,
    2.84,
    1.931,
    2.4,
    0.94,
    1.115,
    1.0336,
    3.876,
    2.2848,
    0.5984,
    0.9384,
    0.476,
]
transported_LNG_3_Nov, DES_Price_Nov = calculate_model_month(
    model_2019_Nov, Total_Costs, Distances, "Nov", Import
)

###############################################################################
# December
model_2019_Dec = create_and_solve_model(Demand_Dec, Supply_Dec, Cost)

Import = [
    9.4185,
    10.30575,
    6.51105,
    2.83,
    1.7745,
    0.9792,
    2.56,
    1.81,
    3.05,
    1.1,
    1.89,
    0.9928,
    4.148,
    2.0808,
    0.9656,
    0.5576,
    0.276,
]
transported_LNG_3_Dec, DES_Price_Dec = calculate_model_month(
    model_2019_Dec, Total_Costs, Distances, "Dec", Import
)


###############################################################################
### 4 Baseline (2019)
###############################################################################
### 4.1 Monthly DES Prices
###############################################################################
Des_2019 = DES_Price_Jan
Des_2019 = Des_2019.append(DES_Price_Feb)
Des_2019 = Des_2019.append(DES_Price_Mar)
Des_2019 = Des_2019.append(DES_Price_Apr)
Des_2019 = Des_2019.append(DES_Price_May)
Des_2019 = Des_2019.append(DES_Price_Jun)
Des_2019 = Des_2019.append(DES_Price_Jul)
Des_2019 = Des_2019.append(DES_Price_Aug)
Des_2019 = Des_2019.append(DES_Price_Sep)
Des_2019 = Des_2019.append(DES_Price_Oct)
Des_2019 = Des_2019.append(DES_Price_Nov)
Des_2019 = Des_2019.append(DES_Price_Dec)

ax = plt.gca()

Des_2019.plot(kind="line", y="Japan", color="darkred", ax=ax, figsize=(9, 6))
Des_2019.plot(kind="line", y="China", ax=ax, color="red")
Des_2019.plot(kind="line", y="France", ax=ax, color="dodgerblue")
Des_2019.plot(kind="line", y="Other Europe", ax=ax, color="green")
Des_2019.plot(kind="line", y="UK", ax=ax, color="orange")
Des_2019.plot(kind="line", y="South Korea", ax=ax, color="purple")
# Des_2019.plot(kind='line',y='Pakistan', ax=ax, color = 'grey')

# ax.set_xlabel(fontsize = 12)
ax.set_ylabel("$/mmBtu", fontsize=12)
plt.legend(bbox_to_anchor=(1, 0.5))
plt.grid(axis="y", linestyle="--", linewidth=0.25)

###############################################################################
### 4.2 Monthly costs
###############################################################################
Monthly_Costs = pd.DataFrame(
    [
        (
            round(model_2019_Jan.Cost() / 10 ** 9, 2),
            round(model_2019_Feb.Cost() / 10 ** 9, 2),
            round(model_2019_Mar.Cost() / 10 ** 9, 2),
            round(model_2019_Apr.Cost() / 10 ** 9, 2),
            round(model_2019_May.Cost() / 10 ** 9, 2),
            round(model_2019_Jun.Cost() / 10 ** 9, 2),
            round(model_2019_Jul.Cost() / 10 ** 9, 2),
            round(model_2019_Aug.Cost() / 10 ** 9, 2),
            round(model_2019_Sep.Cost() / 10 ** 9, 2),
            round(model_2019_Oct.Cost() / 10 ** 9, 2),
            round(model_2019_Nov.Cost() / 10 ** 9, 2),
            round(model_2019_Dec.Cost() / 10 ** 9, 2),
        )
    ],
    index=["Monthly Costs for Imported LNG"],  # "Import (MMBtu)"
    columns=[
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ],
).T


ax_monthly_costs = Monthly_Costs.plot(
    figsize=(9, 6), kind="bar", color="lightcoral", rot=0, width=0.7
)
for container in ax_monthly_costs.containers:
    ax_monthly_costs.bar_label(container)

ax_monthly_costs.set_ylabel("Billions of $")
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax_monthly_costs.get_legend().remove()
plt.show()
plt.savefig("Monthly_Costs_for_Imported_LNG.svg")

###############################################################################
### 4.3 Transported Volumes
###############################################################################
Transported_LNG_2019 = pd.DataFrame(
    np.zeros((len(Distances.index), len(Distances.columns))),
    index=[
        "Qatar",
        "Australia",
        "USA",
        "Russia",
        "Malaysia",
        "Nigeria",
        "Trinidad & Tobago",
        "Algeria",
        "Indonesia",
        "Oman",
        "Other Asia Pacific",
        "Other Europe",
        "Other Americas",
        "Other ME",
        "Other Africa",
    ],
    columns=(
        "Japan",
        "China",
        "South Korea",
        "India",
        "Taiwan",
        "Pakistan",
        "France",
        "Spain",
        "UK",
        "Italy",
        "Turkey",
        "Belgium",
        "Other Asia Pacific",
        "Other Europe",
        "Total North America",
        "Total S. & C. America",
        "Total ME & Africa",
    ),
)

Transported_LNG_2019 = (
    transported_LNG_3_Jan
    + transported_LNG_3_Feb
    + transported_LNG_3_Mar
    + transported_LNG_3_Apr
    + transported_LNG_3_May
    + transported_LNG_3_Jun
    + transported_LNG_3_Jul
    + transported_LNG_3_Aug
    + transported_LNG_3_Sep
    + transported_LNG_3_Oct
    + transported_LNG_3_Nov
    + transported_LNG_3_Dec
)
Transported_LNG_2019

###############################################################################
### 4.4 LNG Shippments Table and Sankey Diagram
###############################################################################
colours_exp = [
    "steelblue",
    "orange",
    "mediumseagreen",
    "lightcoral",
    "purple",
    "peru",
    "deeppink",
    "gray",
    "gold",
    "turquoise",
    "cornflowerblue",
    "lime",
    "teal",
    "darksalmon",
    "slateblue",
]

colours_imp = [
    "crimson",
    "red",
    "lightskyblue",
    "saddlebrown",
    "lightsalmon",
    "seagreen",
    "dodgerblue",
    "darkorange",
    "mediumblue",
    "limegreen",
    "darkred",
    "indigo",
    "yellow",
    "purple",
    "steelblue",
    "seagreen",
    "springgreen",
]

# Generate a colour pallet to let us colour in each line
palette = sns.color_palette("pastel", len(Transported_LNG_2019.index))
colours = palette.as_hex()

# Nodes & links

nodes = [
    ["ID", "Label", "Color"],
    [0, "Qatar", "steelblue"],
    [1, "Australia", "darkorange"],
    [2, "USA", "mediumseagreen"],
    [3, "Russia", "lightcoral"],
    [4, "Malaysia", "purple"],
    [5, "Nigeria", "peru"],
    [6, "Trinidad & Tobago", "deeppink"],
    [7, "Algeria", "gray"],
    [8, "Indonesia", "gold"],
    [9, "Oman", "turquoise"],
    [10, "Other Asia Pacific", "cornflowerblue"],
    [11, "Other Europe", "sandybrown"],
    [12, "Other Americas", "teal"],
    [13, "Other Middle East", "darksalmon"],
    [14, "Other Africa", "slateblue"],
    [15, "Japan", "crimson"],
    [16, "China", "red"],
    [17, "South Korea", "lightskyblue"],
    [18, "India", "saddlebrown"],
    [19, "Taiwan", "lightsalmon"],
    [20, "Pakistan", "seagreen"],
    [21, "France", "dodgerblue"],
    [22, "Spain", "darkorange"],
    [23, "UK", "mediumblue"],
    [24, "Italy", "limegreen"],
    [25, "Turkey", "darkred"],
    [26, "Belgium", "indigo"],
    [27, "Other Asia Pacific", "yellow"],
    [28, "Other Europe", "purple"],
    [29, "Total North America", "steelblue"],
    [30, "Total S. & C. America", "seagreen"],
    [31, "Total ME & Africa", "springgreen"],
]


# links with your data
links = [["Source", "Target", "Value", "Link Color"]]

c_count = 0  # colour counter
i = 0
j = 14

for index in Transported_LNG_2019.index:
    for column in Transported_LNG_2019.columns:
        j += 1
        if Transported_LNG_2019.loc[index, column] != 0:
            links.append(
                [i, j, Transported_LNG_2019.loc[index, column], colours[c_count]]
            )
            # print(i+1,",", j+1, ",", Transported_LNG_3.loc[index, column])
    i += 1
    j = 14
    c_count += 1

# links

# Retrieve headers and build dataframes
nodes_headers = nodes.pop(0)
links_headers = links.pop(0)
df_nodes = pd.DataFrame(nodes, columns=nodes_headers)
df_links = pd.DataFrame(links, columns=links_headers)

# Sankey plot setup
data_trace = dict(
    type="sankey",
    domain=dict(x=[0, 1], y=[0, 1]),
    orientation="h",
    valueformat=".0f",
    node=dict(
        pad=14,
        thickness=45,
        line=dict(color="black", width=0),
        label=df_nodes["Label"].dropna(axis=0, how="any"),
        color=df_nodes["Color"],
    ),
    link=dict(
        source=df_links["Source"].dropna(axis=0, how="any"),
        target=df_links["Target"].dropna(axis=0, how="any"),
        value=df_links["Value"].dropna(axis=0, how="any"),
        color=df_links["Link Color"].dropna(axis=0, how="any"),
    ),
)

layout = dict(
    width=1000,
    height=1000,
    paper_bgcolor="white",
    # title = "LNG Shipments",
    font=dict(size=15),
)

fig_LNG_shipment = dict(data=[data_trace], layout=layout)
iplot(fig_LNG_shipment, validate=False)
# plt.rcParams['figure.dpi'] = 200

###############################################################################
### 4.5 Number of Carriers
###############################################################################
LNG_Carrier_Number_Jan = pd.DataFrame(
    np.zeros((len(Distances.index), len(Distances.columns))),
    index=[
        "Qatar",
        "Australia",
        "USA",
        "Russia",
        "Malaysia",
        "Nigeria",
        "Trinidad & Tobago",
        "Algeria",
        "Indonesia",
        "Oman",
        "Other Asia Pacific",
        "Other Europe",
        "Other Americas",
        "Other ME",
        "Other Africa",
    ],
    columns=(
        "Japan",
        "China",
        "South Korea",
        "India",
        "Taiwan",
        "Pakistan",
        "France",
        "Spain",
        "UK",
        "Italy",
        "Turkey",
        "Belgium",
        "Other Asia Pacific",
        "Other Europe",
        "Total North America",
        "Total S. & C. America",
        "Total ME & Africa",
    ),
)

LNG_Carrier_Number_Feb = (
    LNG_Carrier_Number_Mar
) = (
    LNG_Carrier_Number_Apr
) = (
    LNG_Carrier_Number_May
) = (
    LNG_Carrier_Number_Jun
) = (
    LNG_Carrier_Number_Jul
) = (
    LNG_Carrier_Number_Aug
) = (
    LNG_Carrier_Number_Sep
) = (
    LNG_Carrier_Number_Oct
) = LNG_Carrier_Number_Nov = LNG_Carrier_Number_Dec = LNG_Carrier_Number_Jan

LNG_Carrier_Number_Jan = (
    (transported_LNG_3_Jan * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * (Time + 3)
    / 31
)
JanC = round(LNG_Carrier_Number_Jan.to_numpy().sum())

LNG_Carrier_Number_Feb = (
    (transported_LNG_3_Feb * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * (Time + 3)
    / 28
)
FebC = round(LNG_Carrier_Number_Feb.to_numpy().sum())

LNG_Carrier_Number_Mar = (
    (transported_LNG_3_Mar * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * (Time + 3)
    / 31
)
MarC = round(LNG_Carrier_Number_Mar.to_numpy().sum())

LNG_Carrier_Number_Apr = (
    (transported_LNG_3_Apr * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * (Time + 3)
    / 30
)
AprC = round(LNG_Carrier_Number_Apr.to_numpy().sum())

LNG_Carrier_Number_May = (
    (transported_LNG_3_May * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * (Time + 3)
    / 31
)
MayC = round(LNG_Carrier_Number_May.to_numpy().sum())

LNG_Carrier_Number_Jun = (
    (transported_LNG_3_Jun * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * (Time + 3)
    / 30
)
JunC = round(LNG_Carrier_Number_Jun.to_numpy().sum())

LNG_Carrier_Number_Jul = (
    (transported_LNG_3_Jul * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * (Time + 3)
    / 31
)
JulC = round(LNG_Carrier_Number_Jul.to_numpy().sum())

LNG_Carrier_Number_Aug = (
    (transported_LNG_3_Aug * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * (Time + 3)
    / 31
)
AugC = round(LNG_Carrier_Number_Aug.to_numpy().sum())

LNG_Carrier_Number_Sep = (
    (transported_LNG_3_Sep * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * (Time + 3)
    / 30
)
SepC = round(LNG_Carrier_Number_Sep.to_numpy().sum())

LNG_Carrier_Number_Oct = (
    (transported_LNG_3_Oct * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * (Time + 3)
    / 31
)
OctC = round(LNG_Carrier_Number_Oct.to_numpy().sum())

LNG_Carrier_Number_Nov = (
    (transported_LNG_3_Nov * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * (Time + 3)
    / 30
)
NovC = round(LNG_Carrier_Number_Nov.to_numpy().sum())

LNG_Carrier_Number_Dec = (
    (transported_LNG_3_Dec * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * (Time + 3)
    / 31
)
DecC = round(LNG_Carrier_Number_Dec.to_numpy().sum())

LNG_Carr_2019 = [JanC, FebC, MarC, AprC, MayC, JunC, JulC, AugC, SepC, OctC, NovC, DecC]


LNG_Carriers_2019 = pd.DataFrame(
    LNG_Carr_2019,
    index=[
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ],  # "Import (MMBtu)"
    columns=["Number of LNG Carriers"],
)


ax_LNG_carriers = LNG_Carriers_2019.plot(
    figsize=(9, 6), kind="bar", color="orange", rot=0, width=0.7
)
for container in ax_LNG_carriers.containers:
    ax_LNG_carriers.bar_label(container)

plt.legend(bbox_to_anchor=(1.0, 1.0))
ax_LNG_carriers.get_legend().remove()
plt.show()
# LNG_Carrier_Number_Jan
# plt.savefig("Number of LNG Carriers.svg")

###############################################################################
### 4.6 Monthly Transport Emissions 2019
###############################################################################
Emissions_CO2_Jan_ = (transported_LNG_3_Jan * 10 ** 9) / (
    0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
    - LNG_Carrier.loc[0, "Capacity (m³)"]
    * LNG_to_Gas
    * LNG_Carrier.loc[0, "Boil off"]
    * Time
)  # * CO2_Emissions
Emissions_CO2_Jan_

Emissions_CO2_Jan = (
    (transported_LNG_3_Jan * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
    * CO2_Emissions
)
Jan_CO2 = round(Emissions_CO2_Jan.to_numpy().sum() / 10 ** 6, 2)

Emissions_CO2_Feb = (
    CO2_Emissions
    * (transported_LNG_3_Feb * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Feb_CO2 = round(Emissions_CO2_Feb.to_numpy().sum() / 10 ** 6, 2)

Emissions_CO2_Mar = (
    CO2_Emissions
    * (transported_LNG_3_Mar * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Mar_CO2 = round(Emissions_CO2_Mar.to_numpy().sum() / 10 ** 6, 2)

Emissions_CO2_Apr = (
    CO2_Emissions
    * (transported_LNG_3_Apr * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Apr_CO2 = round(Emissions_CO2_Apr.to_numpy().sum() / 10 ** 6, 2)

Emissions_CO2_May = (
    CO2_Emissions
    * (transported_LNG_3_May * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
May_CO2 = round(Emissions_CO2_May.to_numpy().sum() / 10 ** 6, 2)

Emissions_CO2_Jun = (
    CO2_Emissions
    * (transported_LNG_3_Jun * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Jun_CO2 = round(Emissions_CO2_Jun.to_numpy().sum() / 10 ** 6, 2)

Emissions_CO2_Jul = (
    CO2_Emissions
    * (transported_LNG_3_Jul * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Jul_CO2 = round(Emissions_CO2_Jul.to_numpy().sum() / 10 ** 6, 2)

Emissions_CO2_Aug = (
    CO2_Emissions
    * (transported_LNG_3_Aug * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Aug_CO2 = round(Emissions_CO2_Aug.to_numpy().sum() / 10 ** 6, 2)

Emissions_CO2_Sep = (
    CO2_Emissions
    * (transported_LNG_3_Sep * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Sep_CO2 = round(Emissions_CO2_Sep.to_numpy().sum() / 10 ** 6, 2)

Emissions_CO2_Oct = (
    CO2_Emissions
    * (transported_LNG_3_Oct * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Oct_CO2 = round(Emissions_CO2_Oct.to_numpy().sum() / 10 ** 6, 2)

Emissions_CO2_Nov = (
    CO2_Emissions
    * (transported_LNG_3_Nov * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Nov_CO2 = round(Emissions_CO2_Nov.to_numpy().sum() / 10 ** 6, 2)

Emissions_CO2_Dec = (
    CO2_Emissions
    * (transported_LNG_3_Dec * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Dec_CO2 = round(Emissions_CO2_Dec.to_numpy().sum() / 10 ** 6, 2)


Emi_2019_CO2 = [
    Jan_CO2,
    Feb_CO2,
    Mar_CO2,
    Apr_CO2,
    May_CO2,
    Jun_CO2,
    Jul_CO2,
    Aug_CO2,
    Sep_CO2,
    Oct_CO2,
    Nov_CO2,
    Dec_CO2,
]

Emissions_2019_CO2 = pd.DataFrame(
    Emi_2019_CO2,
    index=[
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ],  # "Import (MMBtu)"
    columns=["CO2 Emissions"],
)


ax = Emissions_2019_CO2.plot(
    figsize=(9, 6), kind="bar", color="lightgray", rot=0, width=0.7
)
for container in ax.containers:
    ax.bar_label(container)

ax.set_ylabel("megatonnes")

plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()

CO2_per_mmBtu = (
    Emissions_2019_CO2.to_numpy().sum()
)  # /(Transported_LNG_2019.to_numpy().sum() * MMBtu_Gas * 10**3)
CO2_per_mmBtu

# Emissions_CO2_Jan

CO2_2019 = (
    Emissions_CO2_Jan
    + Emissions_CO2_Feb
    + Emissions_CO2_Mar
    + Emissions_CO2_Apr
    + Emissions_CO2_May
    + Emissions_CO2_Jun
    + Emissions_CO2_Jul
    + Emissions_CO2_Aug
    + Emissions_CO2_Sep
    + Emissions_CO2_Oct
    + Emissions_CO2_Nov
    + Emissions_CO2_Dec
)
# CO2_2019.to_numpy().sum()
CO2_2019

Emissions_CH4_Jan = (
    CH4_Emissions
    * (transported_LNG_3_Jan * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Jan_CH4 = round(Emissions_CH4_Jan.to_numpy().sum() / 10 ** 3, 2)

Emissions_CH4_Feb = (
    CH4_Emissions
    * (transported_LNG_3_Feb * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Feb_CH4 = round(Emissions_CH4_Feb.to_numpy().sum() / 10 ** 3, 2)

Emissions_CH4_Mar = (
    CH4_Emissions
    * (transported_LNG_3_Mar * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Mar_CH4 = round(Emissions_CH4_Mar.to_numpy().sum() / 10 ** 3, 2)

Emissions_CH4_Apr = (
    CH4_Emissions
    * (transported_LNG_3_Apr * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Apr_CH4 = round(Emissions_CH4_Apr.to_numpy().sum() / 10 ** 3, 2)

Emissions_CH4_May = (
    CH4_Emissions
    * (transported_LNG_3_May * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
May_CH4 = round(Emissions_CH4_May.to_numpy().sum() / 10 ** 3, 2)

Emissions_CH4_Jun = (
    CH4_Emissions
    * (transported_LNG_3_Jun * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Jun_CH4 = round(Emissions_CH4_Jun.to_numpy().sum() / 10 ** 3, 2)

Emissions_CH4_Jul = (
    CH4_Emissions
    * (transported_LNG_3_Jul * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Jul_CH4 = round(Emissions_CH4_Jul.to_numpy().sum() / 10 ** 3, 2)

Emissions_CH4_Aug = (
    CH4_Emissions
    * (transported_LNG_3_Aug * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Aug_CH4 = round(Emissions_CH4_Aug.to_numpy().sum() / 10 ** 3, 2)

Emissions_CH4_Sep = (
    CH4_Emissions
    * (transported_LNG_3_Sep * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Sep_CH4 = round(Emissions_CH4_Sep.to_numpy().sum() / 10 ** 3, 2)

Emissions_CH4_Oct = (
    CH4_Emissions
    * (transported_LNG_3_Oct * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Oct_CH4 = round(Emissions_CH4_Oct.to_numpy().sum() / 10 ** 3, 2)

Emissions_CH4_Nov = (
    CH4_Emissions
    * (transported_LNG_3_Nov * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Nov_CH4 = round(Emissions_CH4_Nov.to_numpy().sum() / 10 ** 3, 2)

Emissions_CH4_Dec = (
    CH4_Emissions
    * (transported_LNG_3_Dec * 10 ** 9)
    / (
        0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas
        - LNG_Carrier.loc[0, "Capacity (m³)"]
        * LNG_to_Gas
        * LNG_Carrier.loc[0, "Boil off"]
        * Time
    )
)
Dec_CH4 = round(Emissions_CH4_Dec.to_numpy().sum() / 10 ** 3, 2)


Emi_2019_CH4 = [
    Jan_CH4,
    Feb_CH4,
    Mar_CH4,
    Apr_CH4,
    May_CH4,
    Jun_CH4,
    Jul_CH4,
    Aug_CH4,
    Sep_CH4,
    Oct_CH4,
    Nov_CH4,
    Dec_CH4,
]

Emissions_2019_CH4 = pd.DataFrame(
    Emi_2019_CH4,
    index=[
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ],  # "Import (MMBtu)"
    columns=["CH4 Emissions"],
)


ax = Emissions_2019_CH4.plot(figsize=(9, 6), kind="bar", color="grey", rot=0, width=0.7)
for container in ax.containers:
    ax.bar_label(container)

ax.set_ylabel("kilotonnes")
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()

Emissions_2019_CH4.to_numpy().sum()

CH4_2019 = (
    Emissions_CH4_Jan
    + Emissions_CH4_Feb
    + Emissions_CH4_Mar
    + Emissions_CH4_Apr
    + Emissions_CH4_May
    + Emissions_CH4_Jun
    + Emissions_CH4_Jul
    + Emissions_CH4_Aug
    + Emissions_CH4_Sep
    + Emissions_CH4_Oct
    + Emissions_CH4_Nov
    + Emissions_CH4_Dec
)
CH4_2019.to_numpy().sum()
# CH4_2019
CH4_per_mmBtu = Emissions_2019_CH4.to_numpy().sum() / (
    Transported_LNG_2019.to_numpy().sum() * MMBtu_Gas * 10 ** 3
)
CH4_per_mmBtu

###############################################################################
### 5 Shadow Prices
###############################################################################
### 5.1 Analysis by exporting nodes
###############################################################################
from utils import shadow_price_exp

Exporter_Shadow = shadow_price_exp(model_2019_Jan, SRC)
Exporter_Shadow = Exporter_Shadow.append(shadow_price_exp(model_2019_Feb, SRC))
Exporter_Shadow = Exporter_Shadow.append(shadow_price_exp(model_2019_Mar, SRC))
Exporter_Shadow = Exporter_Shadow.append(shadow_price_exp(model_2019_Apr, SRC))
Exporter_Shadow = Exporter_Shadow.append(shadow_price_exp(model_2019_May, SRC))
Exporter_Shadow = Exporter_Shadow.append(shadow_price_exp(model_2019_Jun, SRC))
Exporter_Shadow = Exporter_Shadow.append(shadow_price_exp(model_2019_Jul, SRC))
Exporter_Shadow = Exporter_Shadow.append(shadow_price_exp(model_2019_Aug, SRC))
Exporter_Shadow = Exporter_Shadow.append(shadow_price_exp(model_2019_Sep, SRC))
Exporter_Shadow = Exporter_Shadow.append(shadow_price_exp(model_2019_Oct, SRC))
Exporter_Shadow = Exporter_Shadow.append(shadow_price_exp(model_2019_Nov, SRC))
Exporter_Shadow = Exporter_Shadow.append(shadow_price_exp(model_2019_Dec, SRC))

Months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

idx = pd.Index(Months)
Exporter_Shadow = Exporter_Shadow.set_index(idx)

ax = Exporter_Shadow.plot(figsize=(9, 6), color=colours_exp)
plt.legend(bbox_to_anchor=(1.05, 0.875))
ax.set_ylabel("$/mmBtu", fontsize=11)
plt.show()

###############################################################################
### 5.2 Analysis by importing nodes
###############################################################################
from utils import shadow_price_imp

Importer_Shadow = shadow_price_imp(model_2019_Jan, CUS)
Importer_Shadow = Importer_Shadow.append(shadow_price_imp(model_2019_Feb, CUS))
Importer_Shadow = Importer_Shadow.append(shadow_price_imp(model_2019_Mar, CUS))
Importer_Shadow = Importer_Shadow.append(shadow_price_imp(model_2019_Apr, CUS))
Importer_Shadow = Importer_Shadow.append(shadow_price_imp(model_2019_May, CUS))
Importer_Shadow = Importer_Shadow.append(shadow_price_imp(model_2019_Jun, CUS))
Importer_Shadow = Importer_Shadow.append(shadow_price_imp(model_2019_Jul, CUS))
Importer_Shadow = Importer_Shadow.append(shadow_price_imp(model_2019_Aug, CUS))
Importer_Shadow = Importer_Shadow.append(shadow_price_imp(model_2019_Sep, CUS))
Importer_Shadow = Importer_Shadow.append(shadow_price_imp(model_2019_Oct, CUS))
Importer_Shadow = Importer_Shadow.append(shadow_price_imp(model_2019_Nov, CUS))
Importer_Shadow = Importer_Shadow.append(shadow_price_imp(model_2019_Dec, CUS))
Importer_Shadow = Importer_Shadow.set_index(idx)

ax = Importer_Shadow.plot(figsize=(9, 6), color=colours_imp)
plt.legend(bbox_to_anchor=(1.05, 0.875))
ax.set_ylabel("$/mmBtu", fontsize=11)
plt.show()
