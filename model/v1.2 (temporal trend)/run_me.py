import utils
import numpy as np
import pyomo.environ as py
from datetime import datetime
import pandas as pd
import os
import save_results_to_iamc_files as report
import plot_results_with_pyam as plot
import temporal_trend_plot as ttp
import average_increase as ai

# TODO: Add here something.


INPUT_DATA = [
    "delivered ex-ship price 2019.xlsx",
    "gasification capacity 2040.xlsx",
    "LNG demand between 2019 and 2040.xlsx",
]
# source 1 : BP Stats Review (2020)
# source 2 : https://www.bp.com/en/global/corporate/energy-economics/energy-outlook/natural-gas.html

_temporal_average_nz = []
_temporal_marginal_nz = []

_temporal_average_nm = []
_temporal_marginal_nm = []

# (0) ... Run either (i) Net Zero or (ii) New Momentum scenario

for _SCENARIO in ["Net Zero", 'New Momentum']:

    for TARGET_YEAR in list(range(2030, 2041, 1)):
        
        INFLATION = 0.025
    
        for _choice in [0]:
        
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
            
            if _choice == 3:
                for ex, im in des_dict.keys():
                    if ex in ["Qatar", "Oman", "Other ME"]:
                        des_dict[ex, im] *= 1.25
                    else:
                        pass
            else:
                pass
            
            
            if _choice == 5:
                _read_pan_routes = pd.read_excel("input data/panama routes.xlsx")
                for ex, im in des_dict.keys():
                    _flag = 0
                    for _index, _row in _read_pan_routes.iterrows():
                        if (ex == _row.Exporter) and (im == _row.Importer):
                            _flag = 1
                            des_dict[ex, im] *= 1.33
                        else:
                            pass
                    if _flag == 0:
                        des_dict[ex, im] *= 1.15
                    else:
                        pass
            else:
                pass
            
            
            _gas_dict = dict()
            for _index, _row in _gasification.iterrows():
                _gas_dict[_row.Exporter] = _row["Gasification capacity in MMBtu"]
            
            
            # TEMPORAL TREND OF THE LNG DEMAND BETWEEN 2030 and 2040
            _demand_dict = dict()
            _string = "Import 2040 (" + _SCENARIO + ") [MMBtu]"
            _string2 = "Import 2030 [bcm]"
            for _index, _row in _demand.iterrows():
                
                if _row["Importer [Yes/No]"] == "Yes":
                    
                    _val_2030 = _row[_string2] * 35315000
                    _val_2040 = _row[_string]
                    
                    _val = _val_2030 + ((_val_2040 - _val_2030)/10)*(TARGET_YEAR-2030)
                    
                    _demand_dict[_row.Country] = _val
                    
                else:
                    pass
                      
            exporters = list(set(_des["Origin"]))
            importers = list(set(_des["Destination"]))
            _importers_europe = ["France", "Spain", "Belgium", "UK", "Italy"]
            
            _embargo_set = {
                "France": ["Russia"],
                "Spain": ["Russia"],
                "Belgium": ["Russia"],
                "UK": ["Russia"],
                "Italy": ["Russia"],
            }
            
            model = py.ConcreteModel()
            model.scenario = _SCENARIO
            model.year = 2040
            model.set_exporter = py.Set(initialize=exporters)
            model.set_importer = py.Set(initialize=importers)
            model.set_importer_europe = py.Set(initialize=_importers_europe)
            model.embargo = _embargo_set
            
            model.dual = py.Suffix(direction=py.Suffix.IMPORT)
            
            
            model.par_des = py.Param(
                model.set_exporter,
                model.set_importer,
                initialize=des_dict,
                doc="Parameter: Delivered ex-ship price per exporter and importer in 2040 in $/MMBtu.",
                mutable=False,
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
            # print("__________________________")
            # print("CHECK OF INPUT PARAMETERS:")
            # print("")
            # _formatted_number = "{:,}".format(model.par_gasification["Australia"])
            # print("Gasification|Capacity|Australia (MMBtu): ", _formatted_number)
            
            # _formatted_number = "{:,}".format(model.par_demand["China"])
            # print("LNG|Demand|China|2040 (MMBtu): ", _formatted_number)
            
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
            # print("Cost|CCS ($/MMBtu): ", model.par_CCS_cost())
            
            # European domestic natural gas production
            #
            #
            # source: https://ceenergynews.com/voices/the-myth-and-reality-behind-high-european-energy-prices/
            # Russian piped gas: 0.7463 $/MMBtu
            
            _production_cost = 1.5  # $/MMBtu
            _value = np.around((1 + INFLATION) ** (TARGET_YEAR - 2019) * _production_cost, 2)
            
            model.par_EDP_cost = py.Param(
                initialize=_value,
                doc="Parameter: Average European domestic natural gas production cost in 2040 in $/MMBtu.",
            )
            # print("Cost|EDP ($/MMBtu): ", model.par_EDP_cost())
            
            # source: https://www.statista.com/statistics/265345/natural-gas-production-in-the-european-union/#:~:text=In%202022%2C%20the%20natural%20gas,around%2041.1%20billion%20cubic%20meters.
            # ==> 100 bcm (upper bound) ==> estimate based on BP Stats Review (2020) page 34
            _value = 35 * 35315000
            model.par_max_EDP = py.Param(
                initialize=_value,
                doc="Parameter: Maximum European domestic natural gas production with CCS in 2040 in MMBtu.",
            )
            
            _dem = sum(model.par_demand[i] for i in model.set_importer_europe)
            # _formatted_number = "{:,}".format(int(_dem))
            # print("LNG|Demand|Europe|2040 (MMBtu): ", _formatted_number)
            
            # _formatted_number = "{:,}".format(model.par_max_EDP())
            # print(
            #     "NG|Substitute|LNG|2040 (MMBtu): ",
            #     _formatted_number,
            # )
            
            # print("Share of European domestic production on the European total demand: {:.1f}%".format(model.par_max_EDP() / _dem * 100))
            # print("")
            # print("__________________________")
            
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
            
            
            def diversification_high(m, e, i):
                if i in m.set_importer_europe:
                    return m.var_q[e, i] <= (1 / 5) * m.par_demand[i]
                else:
                    return m.var_q[e, i] <= (1 / 3) * m.par_demand[i]
            
            
            def ccs_technology_utilization(m):
                return sum(m.var_q_dom_europe[i] for i in m.set_importer_europe) <= m.par_max_EDP
            
            
            model.con_ccs_technology_utilization = py.Constraint(
                rule=ccs_technology_utilization,
                doc="Constraint: Restrict the utilization of European domestic natural gas production + CCS.",
            )
            
            
            # COST OF THE MARKET CLEARING
            model.var_cost_market_clearing = py.Var(
                model.set_importer,
                within=py.NonNegativeReals,
                doc="Variable: Cost of the market clearing per importer in $.",
            )
            
            
            def cost_of_market_clearing(m, i):
                return m.var_cost_market_clearing[i] == sum(
                    m.var_q[e, i] * m.par_des[e, i] for e in m.set_exporter
                )
            
            
            model.con_cost_of_market_clearing = py.Constraint(
                model.set_importer,
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
                    m.var_demand_not_covered[importer] * 10e10 for importer in m.set_importer
                )
            
            
            model.con_cost_of_demand_not_covered = py.Constraint(
                rule=cost_of_demand_not_covered,
                doc="Constraint: Cost of LNG demand not covered in $.",
            )
            
            # EMBARGO
            
            
            def embargo_of_exporter_per_importer(model, importer, exporter):
                if importer in model.embargo.keys():
                    _list = model.embargo[importer]
                    if exporter in _list:
                        return model.var_q[exporter, importer] == 0
                    else:
                        return py.Constraint.Skip
                else:
                    return py.Constraint.Skip
            
            
            model.con_embargo = py.Constraint(
                model.set_importer, model.set_exporter, rule=embargo_of_exporter_per_importer
            )
            
            # OBJECTIVE FUNCTION
            def objective_function(m):
                _market = sum(m.var_cost_market_clearing[importer] for importer in m.set_importer)
                return _market + m.var_cost_edp + m.var_cost_ccs + m.var_cost_not_supply
            
            
            def no_export_from_african_regions(m, e, i):
                if e in ["Algeria", "Other Africa", "Nigeria"]:
                    return m.var_q[e, i] == 0
                else:
                    return py.Constraint.Skip
            
            
            def export_from_russia_only_to_asia(m, i):
                if i in ["China", "India", "Total ME & Africa"]:
                    return py.Constraint.Skip
                else:
                    return m.var_q['Russia', i] == 0
            
            
            """
                RESEARCH QUESTION 2 REGARDING POLITICAL TENSION
            """
            
            if _choice == 1:
                #  (1) ... Diverse (strong diversification of exporters in Europe)
                model.con_diversification.deactivate()
                model.con_diversification_high = py.Constraint(
                    model.set_exporter,
                    model.set_importer,
                    rule=diversification_high,
                    doc="Constraint: Diversification of exporters for each importer (max share of one-third)",
                )
                _sce = model.scenario
                model.scenario = _sce + "+Diversification"
            
            elif _choice == 2:
                #  (2) ... NoExpAfrica (no LNG export from Algeria, Other Africa, Nigeria)
                model.con_no_export_from_africa = py.Constraint(
                    model.set_exporter,
                    model.set_importer,
                    rule=no_export_from_african_regions,
                    doc="Constraint: No LNG export volumes from African regions.",
                )
                _sce = model.scenario
                model.scenario = _sce + "+NoExpAfrica"
            
            elif _choice == 3:
                #  (3) ... HighPriceME (+ 25% of LNG DES price of Qatar, Oman, Other ME)
                _sce = model.scenario
                model.scenario = _sce + "+HighPriceME"
            
            elif _choice == 4:
                #  (4) ... RussianEmbargo (Russian LNG exported to Asia only)
                model.con_export_from_russia_only_to_asia = py.Constraint(
                    model.set_importer,
                    rule=export_from_russia_only_to_asia,
                    doc="Constraint: LNG export from Russia towards China and India only.",
                )
                _sce = model.scenario
                model.scenario = _sce + "+RussianEmbargo"
        
            elif _choice == 5:
                # (5) ... PanCanClosed (Routes through Panama Canal + 33% in DES price and all others + 15%)
                _sce = model.scenario
                model.scenario = _sce + "+PanCanClosed"
        
            #
            #
            #
            #
            #
            #
            #
            #
            #
            #
            
            model.objective = py.Objective(expr=objective_function, sense=py.minimize)
        
            solver = py.SolverFactory("gurobi")
            solution = solver.solve(model)
            
            # print("OBJECTIVE VALUE: {:.0f} Mio. $".format(model.objective() / 1000000))
            
            # REPORT THE MODEL RESULTS TO OUTPUT FILES
            _now = datetime.now().strftime("%Y%m%d_%H")
            result_dir = os.path.join("result", "{}".format(_now))
            if (not os.path.exists(result_dir)) and (TARGET_YEAR == 2040):
                os.makedirs(result_dir)
            
            # _solution = report.write_results_to_ext_iamc_format(model, result_dir)
            # report.write_dual_variables_to_output_files(model, result_dir)
            
            _v_av, _v_mg = plot.run(model, result_dir)
            
            if _SCENARIO == 'Net Zero':
                _temporal_average_nz.append(_v_av)
                _temporal_marginal_nz.append(_v_mg)
            else:
                _temporal_average_nm.append(_v_av)
                _temporal_marginal_nm.append(_v_mg)

_data=[[_temporal_average_nz, _temporal_average_nm], [_temporal_marginal_nz, _temporal_marginal_nm]]

for _d in [_temporal_average_nz, _temporal_average_nm, _temporal_marginal_nz, _temporal_marginal_nm]:
    ai.calculate_average_increase(_d)

ttp.run_me(_data, result_dir)
