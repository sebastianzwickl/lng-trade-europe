import utils
import numpy as np
import pyomo.environ as py


INPUT_DATA = [
    "delivered ex-ship price 2019.xlsx",
    "gasification capacity 2040.xlsx",
    "LNG demand between 2019 and 2040.xlsx",
]
# source 1 : BP Stats Review (2020)
# source 2 : https://www.bp.com/en/global/corporate/energy-economics/energy-outlook/natural-gas.html

TARGET_YEAR = 2040
INFLATION = 0.025


# 2019's VALUES
_data = utils.get_input_data_from_excel_sheets(INPUT_DATA)
_des = _data[0]
_gasification = _data[1]
_demand = _data[2]

des_dict = dict()
for _index, _row in _des.iterrows():
    des_dict[_row.Origin, _row.Destination] = np.around(
        (1 + INFLATION) ** (TARGET_YEAR - 2019) * _row["Costs in $/MMBtu"], 2
    )

_gas_dict = dict()
for _index, _row in _gasification.iterrows():
    _gas_dict[_row.Exporter] = _row["Gasification capacity in MMBtu"]

_SCENARIO = "Net Zero"
_demand_dict = dict()
_string = "Import 2040 (" + _SCENARIO + ") [MMBtu]"
for _index, _row in _demand.iterrows():
    if _row["Importer [Yes/No]"] == "Yes":
        _demand_dict[_row.Country] = _row[_string]

exporters = list(set(_des["Origin"]))
importers = list(set(_des["Destination"]))
_importers_europe = ["France", "Other Europe", "Spain", "Belgium", "UK", "Italy"]


model = py.ConcreteModel()
model.scenario = _SCENARIO
model.set_exporter = py.Set(initialize=exporters)
model.set_importer = py.Set(initialize=importers)
model.set_importer_europe = py.Set(initialize=_importers_europe)

model.par_des = py.Param(
    model.set_exporter,
    model.set_importer,
    initialize=des_dict,
    doc="Parameter: Delivered ex-ship price per exporter and importer in 2040 in $/MMBtu.",
)

model.par_gasification = py.Param(
    model.set_exporter,
    initialize=_gas_dict,
    doc="Parameter: Gasification capacity per exporter in 2040 in MMBtu/year.",
)

model.par_demand = py.Param(
    model.set_importer,
    initialize=_demand_dict,
    doc="Parameter: Demand per importer in 2040 in MMBtu/year.",
)

_formatted_number = "{:,}".format(model.par_gasification["Australia"])
print("Gasification capacity of Australia: ", _formatted_number)

_formatted_number = "{:,}".format(model.par_demand["China"])
print("LNG demand of China 2040 in MMBtu: ", _formatted_number)

# CCS (Carbon Capture and Storage)
#
#

"""
source: https://www.eia.gov/environment/emissions/co2_vol_mass.php
source: GLOBAL COSTS OF CARBON CAPTURE AND STORAGE

"""
_cost = 138  # in $/tCO2
_content = 0.053  # in tCO2/MMBtu
_value = _cost * _content
_ccs_cost = np.around((1 + INFLATION) ** (TARGET_YEAR - 2019) * _value, 2)

model.par_CCS_cost = py.Param(
    initialize=_ccs_cost,
    doc="Parameter: Cost of carbon capture and storage in Europe 2040 in $/MMBtu.",
)
print("CCS cost in $/MMBtu: ", model.par_CCS_cost())

# European domestic natural gas production
#
#
# source: https://ceenergynews.com/voices/the-myth-and-reality-behind-high-european-energy-prices/
# Russian piped gas: 0.7463 $/MMBtu

_production_cost = 1  # $/MMBtu
_value = np.around((1 + INFLATION) ** (TARGET_YEAR - 2019) * _production_cost, 2)

model.par_EDP_cost = py.Param(
    initialize=_value,
    doc="Parameter: Average European domestic natural gas production cost in 2040 in $/MMBtu.",
)
print("Europen domestic natural gas production cost in $/MMBtu: ", model.par_EDP_cost())

# source: https://www.statista.com/statistics/265345/natural-gas-production-in-the-european-union/#:~:text=In%202022%2C%20the%20natural%20gas,around%2041.1%20billion%20cubic%20meters.
# ==> 100 bcm (upper bound) ==> estimate based on BP Stats Review (2020) page 34
_value = 100 * 35315000
model.par_max_EDP = py.Param(
    initialize=_value,
    doc="Parameter: Maximum European domestic natural gas production with CCS in 2040 in MMBtu.",
)

_formatted_number = "{:,}".format(model.par_max_EDP())
print(
    "Max European domestic natural gas production 2040 substituting LNG in MMBtu: ",
    _formatted_number,
)

model.var_q = py.Var(
    model.set_exporter,
    model.set_importer,
    within=py.NonNegativeReals,
    doc="Variable: Quantity of LNG transported from exporter to importer in 2040 in MMBtu.",
)

model.var_q_dom_europe = py.Var(
    model.set_importer_europe,
    within=py.NonNegativeReals,
    doc="Variable: Quantity of European domestic natural gas production with CCS in 2040 in MMBtu.",
)

model.var_demand_not_covered = py.Var(
    model.set_importer,
    within=py.NonNegativeReals,
    doc="Variable: Quantity of the demand that is not covered in MMBtu.",
)

###################################
# GASIFICATION CAPACITY OF EXPORTER


def restrict_export_by_gasification_capacity(model, exporter):
    _total_export = sum(
        model.var_q[exporter, _importer] for _importer in model.set_importer
    )
    return _total_export <= model.par_gasification[exporter]


model.con_restrict_export_by_gasification_capacity = py.Constraint(
    model.set_exporter,
    rule=restrict_export_by_gasification_capacity,
    doc="Constraint: Restrict export from each exporter by its gasification capacity.",
)


def demand_balance(m, i):
    if i in m.set_importer_europe:
        return (
            sum(m.var_q[exp, i] for exp in m.set_exporter)
            + m.var_q_dom_europe[i]
            + m.var_demand_not_covered[i]
            == m.par_demand[i]
        )
    else:
        return (
            sum(m.var_q[exp, i] for exp in m.set_exporter) + m.var_demand_not_covered[i]
            == m.par_demand[i]
        )


model.con_demand_balance = py.Constraint(
    model.set_importer,
    rule=demand_balance,
    doc="Constraint: Demand balance (including option for not supplying demand).",
)


def diversification(m, e, i):
    return m.var_q[e, i] <= (1 / 3) * m.par_demand[i]


model.con_diversification = py.Constraint(
    model.set_exporter,
    model.set_importer,
    rule=diversification,
    doc="Constraint: Diversification of exporters for each importer (max share of one-third%).",
)


def ccs_technology_utilization(m):
    return sum(m.var_q_dom_europe[i] for i in m.set_importer_europe) <= m.par_max_EDP


model.con_ccs_technology_utilization = py.Constraint(
    rule=ccs_technology_utilization,
    doc="Constraint: Restrict the utilization of European domestic natural gas production + CCS.",
)


# COST OF THE MARKET CLEARING
model.var_cost_market_clearing = py.Var(
    within=py.NonNegativeReals,
    doc="Variable: Cost of the market clearing per importer in $.",
)


def cost_of_market_clearing(m):
    return m.var_cost_market_clearing == sum(
        m.var_q[e, i] * m.par_des[e, i] for e in m.set_exporter for i in m.set_importer
    )


model.con_cost_of_market_clearing = py.Constraint(
    rule=cost_of_market_clearing,
    doc="Constraint: Cost of the market clearing (quantity times delivered ex-ship price) in $.",
)


# COST OF THE EUROPEAN DOMESTIC NATURAL GAS PRODUCTION
model.var_cost_edp = py.Var(
    within=py.NonNegativeReals,
    doc="Variable: Cost of the European domestic production in $.",
)


def cost_of_domestic_european_production(m):
    return m.var_cost_edp == sum(
        m.var_q_dom_europe[country] * m.par_EDP_cost
        for country in m.set_importer_europe
    )


model.con_cost_of_domestic_european_production = py.Constraint(
    rule=cost_of_domestic_european_production,
    doc="Constraint: Cost of the European domestic natural gas production in $.",
)


# COST OF CARBON CAPTURE AND STORAGE IN EUROPE
model.var_cost_ccs = py.Var(
    within=py.NonNegativeReals,
    doc="Variable: Cost of carbon capture and storage in Europe in $.",
)


def cost_of_carbon_capture_storage(m):
    return m.var_cost_ccs == sum(
        m.var_q_dom_europe[country] * m.par_CCS_cost
        for country in m.set_importer_europe
    )


model.con_cost_of_carbon_capture_storage = py.Constraint(
    rule=cost_of_carbon_capture_storage,
    doc="Constraint: Cost of capture capture & storage in Europe due to European domestic natural gas production in $.",
)

# COST OF LNG DEMAND NOT SUPPLIED
model.var_cost_not_supply = py.Var(
    within=py.NonNegativeReals,
    doc="Variable: Cost of not supplying LNG demand in $",
)


def cost_of_demand_not_covered(m):
    return m.var_cost_not_supply == sum(
        m.var_demand_not_covered[importer] for importer in m.set_importer
    )


model.con_cost_of_demand_not_covered = py.Constraint(
    rule=cost_of_demand_not_covered,
    doc="Constraint: Cost of LNG demand not covered in $.",
)


# OBJECTIVE FUNCTION
def objective_function(m):
    return (
        m.var_cost_market_clearing
        + m.var_cost_edp
        + m.var_cost_ccs
        + m.var_cost_not_supply
    )


model.objective = py.Objective(expr=objective_function, sense=py.minimize)


solver = py.SolverFactory("gurobi")
solution = solver.solve(model)

_formatted_number = "{:,}".format(int(model.objective()))
print("Objective function value: %s $" % _formatted_number)
