import numpy as np
import pyomo.environ as py
from datetime import datetime
import pandas as pd
import os
import create_figures
import market_share_supply_risk_plot



"""
    TODOS:
        - Review model and its code (until row 895)
        - check: par_theta (how does supply risk changes when emissions change)
"""

###############################################################################


def get_input_data_from_excel_sheets(name=None):
    # this function takes the name of an .xlsx file as argument
    # and returns a pandas dataframe
    _to_return = []
    for item in name:
        _get = pd.read_excel("input/" + item)
        _to_return.append(_get)
    return _to_return




###############################################################################

# inputs from Anna and Brendan
# restrict EU internal supply to 15 bcm (Anna, 14 March)
# one with and one without new EU internal supply (Brendan, 17 March)
# scenarios: (1) New Momentum, (2) Net-Zero, and
# (3) EU goes Net-Zero, remaning for New Momentum
# the role of US LNG ("who is going to fill the gap?")

###############################################################################

for v1, v2, v3, v4, w1, w2, w3 in [
        # ['Net Zero', "Net Zero", 1, 150, 5/10, 25/100, 25/100],
        #
        # ['New Momentum', "New Momentum", 1, 150, 5/10, 25/100, 25/100],
        #
        #['New Momentum', "Net Zero", 1, 150, 5/10, 25/100, 25/100],
        #['New Momentum', "Net Zero", 1, 150, 1/3, 1/3, 1/3],
        ['New Momentum', "Net Zero", 1, 150, 5/10, 1/10, 4/10],
        ['New Momentum', "New Momentum", 1, 150, 5/10, 1/10, 4/10],
        ['Net Zero', "Net Zero", 1, 150, 5/10, 1/10, 4/10],
]:

# - The Future of LNG Trade: Inflexible, Inefficient, and Polarized?
# Trade between Chinese buyers and US LNG
# EU wants to ban Russian LNG 
# Maximum methane intensity values


    # the list below includes the names of the .xlsx files that serve as input
    INPUT_DATA = [
        "0_delivered ex-ship costs in 2019.xlsx",
        "1_liquification capacity from 2030.xlsx",
        "2_demand 2019 to 2040.xlsx",
        "3_eu's carbon price.xlsx",
        "4_2030 supply chain emissions reduction budget for the exporter.xlsx",
        "5_specific supply chain emissions of the exporter in 2030.xlsx",
        "6_worldwide governance indicators in 2023.xlsx",
    ]
   
    _MAIN_SCENARIO_GLOBAL = v1  # Net Zero
    # _MAIN_SCENARIO_GLOBAL = "Net Zero"
    _MAIN_SCENARIO_EU = v2  # New Momentum
    # _MAIN_SCENARIO_EU = "New Momentum"
    
    
    _EU_INTERNAL_SUPPLY = "Depleted"  # 'Restocked'
    
    _Share_t = v3  # redistribution share of CBAM's revenues (between 0 and 1)
    _target_year = 2050
    _CBAM_IMPLEMENTATION_STRICT = False  # how CBAM's revenues can be redistributed
    _INFLATION = 0.025  # cost increase over time due to inflation
    
    ###############################################################################
    
    empirical_data = get_input_data_from_excel_sheets(INPUT_DATA)
    _weighting_factors = {
        "Supply Cost": w1,
        "Supply Concentration": w2,
        "Supply Risk": w3,
    }
    
    ###############################################################################
    
    DES = empirical_data[0]
    LIQUIFICATION = empirical_data[1]
    DEMAND = empirical_data[2]
    CO2 = empirical_data[3]
    BUDGET = empirical_data[4]
    RHO = empirical_data[5]
    RISK_FACTORS = empirical_data[6]
    
    ###############################################################################
    
    dict_des = {}
    for index, row in DES.iterrows():
        for year in range(2030, 2051, 1):
            dict_des[row.Origin, row.Destination, year] = np.around(
                (1 + _INFLATION) ** (year - 2019) * row["Costs in $/MMBtu"], 2
            )
    
    dict_liquification = {}
    
    if _MAIN_SCENARIO_GLOBAL == _MAIN_SCENARIO_EU == 'New Momentum':
        _factor = 1.1
    else: 
        _factor = 1.0
    
    for index, row in LIQUIFICATION.iterrows():
        for year in range(2030, 2051, 1):
            if year <= 2040:
                dict_liquification[row.Exporter, year] = row["Liquification capacity in MMBtu"] / 1000000
            else:
                dict_liquification[row.Exporter, year] = row["Liquification capacity in MMBtu"] / 1000000 * _factor
    
    dict_demand_global = {}
    _string = "Import 2040 (" + _MAIN_SCENARIO_GLOBAL + ") [MMBtu]"
    _string2 = "Import 2030 [bcm]"
    for index, row in DEMAND.iterrows():
        if row["Importer [Yes/No]"] == "Yes":
            _val_2030 = row[_string2] * 35315000
            _val_2040 = row[_string]
            for TARGET_YEAR in list(range(2030, _target_year + 1, 1)):
                if TARGET_YEAR <= 2040:
                    _val = _val_2030 + ((_val_2040 - _val_2030) / 10) * (TARGET_YEAR - 2030)
                else:
                    _val = (
                        _val_2040
                        + ((_val_2040 - _val_2030) / 10) * (TARGET_YEAR - 2040) * 0.5
                    )
                # LNG demand per importer and year in million MMBtu
                dict_demand_global[row.Country, TARGET_YEAR] = _val / 1000000
    
    dict_demand_eu = {}
    _string = "Import 2040 (" + _MAIN_SCENARIO_EU + ") [MMBtu]"
    _string2 = "Import 2030 [bcm]"
    for index, row in DEMAND.iterrows():
        if row["Importer [Yes/No]"] == "Yes":
            _val_2030 = row[_string2] * 35315000
            _val_2040 = row[_string]
            for TARGET_YEAR in list(range(2030, _target_year + 1, 1)):
                if TARGET_YEAR <= 2040:
                    _val = _val_2030 + ((_val_2040 - _val_2030) / 10) * (TARGET_YEAR - 2030)
                else:
                    _val = (
                        _val_2040
                        + ((_val_2040 - _val_2030) / 10) * (TARGET_YEAR - 2040) * 0.5
                    )
                dict_demand_eu[row.Country, TARGET_YEAR] = _val / 1000000
    
    ###############################################################################
    
    # Europen Domestic Production (EDP) --- COSTS
    # https://ceenergynews.com/voices/the-myth-and-reality-behind-high-european-energy-prices/
    # Russian Piped Gas: 0.7463 $/MMBtu
    _production_cost = 2 * 0.7463  # Approximately 2.0 x Russian Piped Gas (in $/MMBtu)
    dict_EDP = dict()
    for year in range(2030, _target_year + 1, 1):
        dict_EDP[year] = np.around((1 + _INFLATION) ** (year - 2019) * _production_cost, 2)
    
    # Europen Domestic Production (EDP) --- Production Limits
    # More precisely in the European Union (EU)
    # https://www.statista.com/statistics/265345/natural-gas-production-in-the-european-union/#:~:text=In%202022%2C%20the%20natural%20gas,around%2041.1%20billion%20cubic%20meters.
    # Upper limit is 100 bcm according to BP's Stats Review from 2020 (p. 34)
    
    if _EU_INTERNAL_SUPPLY == "Depleted":
        # the value of 15 is given in bcm
        _value = 15 * 35315000
    elif _EU_INTERNAL_SUPPLY == "Restocked":
        # the value of 45 is given in bcm
        _value = 45 * 35315000
    
    dict_EDP_limit = dict()
    for year in range(2030, _target_year + 1, 1):
        if year < 2040:
            dict_EDP_limit[year] = _value / 1000000
        elif year == 2040:
            if _EU_INTERNAL_SUPPLY == "Restocked":
                dict_EDP_limit[year] = 30 * 35315000 / 1000000
            else:
                dict_EDP_limit[year] = 10 * 35315000 / 1000000
        else:
            dict_EDP_limit[year] = 5 * 35315000 / 1000000
    
    ###############################################################################
    
    # Carbon Price and Carbon Capture and Storage (CCS)
    # https://www.eia.gov/environment/emissions/co2_vol_mass.php
    # "GLOBAL COSTS OF CARBON CAPTURE AND STORAGE"
    _cost = 138  # (in $/tCO2)
    # _content = 0.053  # (in tCO2/MMBtu) ==> This are direct emissions
    # Natural Gas: 52.91 kg/MMBtu ==>
    _content = 0.00003043392  # value is taken from Norway (in tCO2/MMBtu)
    _value = _cost * _content  # (in million $ / million MMBtu)
    dict_CCS = dict()
    for year in range(2030, _target_year + 1, 1):
        dict_CCS[year] = np.around((1 + _INFLATION) ** (year - 2019) * _value, 5)
    
    print("_______________________________________________________________________")
    print(
        "EU internal production costs in 2035 (equipped with CCS) {:.4f} $/MMBtu".format(
            dict_CCS[2030] + _production_cost
        )
    )
    print("")
    
    print("__________________________________________________________________")
    print(
        "2030's delived ex-ship costs vary between {:.3f} and {:.3f} $/MMBtu".format(
            min(DES["Costs in $/MMBtu"]), max(DES["Costs in $/MMBtu"])
        )
    )
    print("")
    
    
    ###############################################################################
    
    dict_carbon_price = dict()
    # EUR/tCO2 in million $ / million tCO2
    for index, row in CO2.iterrows():
        dict_carbon_price[row.Year] = row.Value / 0.96122
    
    ###############################################################################
    
    # Exporter's budget for supply chain mitigation measures in 2030
    dict_budget = dict()
    for index, row in BUDGET.iterrows():
        dict_budget[row.Exporter] = row["2030's budget in $"] / 1000000
    
    ###############################################################################
    
    # Exporter's specific supply chain emissions in 2030 (in tCO2/MMBtu)
    # Source:
    # "Call of duties: how emission taxes on imports could transform the global LNG market" (Fig. 1)
    # "The greenhouse gas footprint of liquefied natural gas (LNG) exported from the United States)
    # https://doi.org/10.1002/ese3.1934
    # Fig. 1's values x 1.53
    # 1 kg LNG equals to approximately 53 MMBtu
    # https://www.enerdynamics.com/Energy-Currents_Blog/Understanding-Liquefied-Natural-Gas-LNG-Units.aspx
    
    dict_rho = dict()  # (in tCO2/MMBtu)
    for index, row in RHO.iterrows():
        # dict_rho[row.Exporter] = row["2023's emissions in tCO2/MMBtu (NEW)"]
        dict_rho[row.Exporter] = row["Emissions (corrected)"]
    
    ###############################################################################
    
    # EFF : Specific investment costs in the LNG supply chain
    # https://www.globalccsinstitute.com/wp-content/uploads/2021/03/Technology-Readiness-and-Costs-for-CCS-2021-1.pdf
    # Footnote 4 on page 29
    
    # For industrial processes with high concentration CO2/inherent CO2 capture
    # process, e.g., natural gas processing, fertiliser, bioethanol,
    # ethylene oxidation production,
    # a cost range of $0 – 10 per tonne of CO2 captured is assumed
    # for CO2 conditioning. The cost is adjusted according to
    # the prices of feedstock in the United States,
    # e.g., $2.11 per GJ coal and $4.19
    # per GJ natural gas prices (James et al. 2019),
    # as well as $8.8 per GJ wood pellets biomass (Canadian Biomass Magazine 2020).
    
    # Unit of "EFF" is tCO2/MMBtu/$
    # https://think.ing.com/articles/the-issue-of-lng-emissions/
    # "How industry players are reducing emissions"
    
    # CHOSE (A) EXPORTER SPECIFIC
    # 1/(10$/tCO2)/Liquification/10
    # 10...years
    
    _dollar_per_tCO2 = 47.3
    # _dollar_per_tCO2 = v4
    
    dict_eff = dict()
    for index, row in LIQUIFICATION.iterrows():
        for _y in list(range(2030, _target_year + 1, 1)):
            # in million tCO2 / million MMBtu per million $
            dict_eff[row.Exporter, _y] = (
                1
                / (
                    row["Liquification capacity in MMBtu"] / 1000000
                    * (_target_year + 1 - _y)
                    * _dollar_per_tCO2
                )
            )
            # if _y == 2035:
            #     print('{}:{}'.format(row.Exporter, dict_eff[row.Exporter, _y]))
    
    # # OR (B) AVERAGE VALUE
    # dict_eff = dict()
    # for index, row in LIQUIFICATION.iterrows():
    #     dict_eff[row.Exporter] = np.mean(LIQUIFICATION['Eff'])
    
    
    ###############################################################################
    
    # Supply Risk Indicator (\bar{v}_{e,i})
    dict_supply_risk = dict()
    for index, row in RISK_FACTORS.iterrows():
        if row.Region in dict_budget.keys():
            if row.Region == 'USA':
                dict_supply_risk[row.Region] = RISK_FACTORS.loc[RISK_FACTORS.Region == 'USA']['Refined'].item()
            else:
                dict_supply_risk[row.Region] = row.Refined
        else:
            pass
    
    print("______________________________________________________")
    print(
        "Supply Risk Indicator Values range between {:.5f} and {:.5f}".format(
            min(dict_supply_risk.values()), max(dict_supply_risk.values())
        )
    )
    print("")
    
    _exporters = list(LIQUIFICATION.Exporter)
    
    ###############################################################################
    
    del [
        DEMAND,
        DES,
        year,
        TARGET_YEAR,
        row,
        INPUT_DATA,
        index,
        empirical_data,
        CO2,
        LIQUIFICATION,
        BUDGET,
        RHO,
        RISK_FACTORS,
    ]
    
    ###############################################################################
    
    _importers = sorted(set(list(k[0] for k in dict_demand_eu.keys())))
    _importers_europe = ["France", "Spain", "Belgium", "UK", "Italy"]
    
    dict_demand_global = {
        key: value
        for key, value in dict_demand_global.items()
        if key[0] not in _importers_europe
    }
    dict_demand_eu = {
        key: value for key, value in dict_demand_eu.items() if key[0] in _importers_europe
    }
    
    dict_demand = dict_demand_global | dict_demand_eu
    
    model = py.ConcreteModel()
    
    
    def create_scenario_name(_global=None, european_demand=None, european_supply=None):
        if _global == "New Momentum":
            _str1 = "GL_NM"
        elif _global == "Net Zero":
            _str1 = "GL_NZ"
        else:
            pass
    
        if european_demand == "New Momentum":
            _str2 = "EU_NM"
        elif european_demand == "Net Zero":
            _str2 = "EU_NZ"
        else:
            pass
    
        if european_supply == "Depleted":
            _str3 = "EUxSUP_Dep"
        elif european_supply == "Restocked":
            _str3 = "EUxSUP_RES"
        else:
            pass
    
        _str = _str1 + "__" + _str2 + "__" + _str3
        return _str
    
    ###############################################################################
    
    input_dict = {
        'Global LNG Demand': _MAIN_SCENARIO_GLOBAL,
        'EU LNG Demand': _MAIN_SCENARIO_EU,
        'EU Internal Gas Production': _EU_INTERNAL_SUPPLY,
        'Share of CBAM Revenies Redistributed': str(_Share_t * 100) + '%',
        'Upstream Emission Reduction Costs (in $/tCO2)': _dollar_per_tCO2,
        'Weighting|Costs': str(_weighting_factors["Supply Cost"] * 100) + '%',
        'Weighting|Concentration': str(_weighting_factors["Supply Concentration"] * 100) + '%',
        'Weighting|Risk': str(_weighting_factors["Supply Risk"] * 100) + '%'
    }
    
    input_df = pd.DataFrame([input_dict])  # Wrap dict in list
    
    
    ###############################################################################
    
    model.scenario = create_scenario_name(
        _MAIN_SCENARIO_GLOBAL, _MAIN_SCENARIO_EU, _EU_INTERNAL_SUPPLY
    )
    model.set_years = py.Set(initialize=range(2030, _target_year + 1, 1))
    model.set_exporter = py.Set(initialize=_exporters)
    model.set_importer = py.Set(initialize=_importers)
    model.set_importer_eu = py.Set(initialize=_importers_europe)
    
    model.set_non_eu_imp = py.Set(
        initialize=_importers, filter=lambda model, i: i not in _importers_europe
    )
    
    model.dual = py.Suffix(direction=py.Suffix.IMPORT)
    
    ###############################################################################
    
    model.par_des = py.Param(
        model.set_exporter,
        model.set_importer,
        model.set_years,
        initialize=dict_des,
        mutable=False,
        doc="Delivered ex-ship costs (in million $/ million MMBtu).",
    )
    print(
        "   - DES|Nigeria|Spain|2030 in million $ / million MMBtu: ",
        model.par_des["Nigeria", "Spain", 2030],
    )
    
    ###############################################################################
    
    model.par_liquification = py.Param(
        model.set_exporter,
        model.set_years,
        initialize=dict_liquification,
        doc="Liquefication capacity per exporter e (in million MMBtu/year).",
    )
    _formatted_number = "{:,}".format(model.par_liquification["Algeria", 2040])
    print("   - LIQ|Algeria in million MMTbtu/yr: ", _formatted_number)
    
    ###############################################################################
    
    model.par_importer_demand = py.Param(
        model.set_importer,
        model.set_years,
        initialize=dict_demand,
        doc="LNG demand per importer i and year y (in million MMBtu/year).",
    )
    _formatted_number = "{:,}".format(int(model.par_importer_demand["Spain", 2040]))
    print("   - DEM|Spain in million MMTbtu/yr: ", _formatted_number)
    
    _formatted_number = "{:,}".format(int(model.par_importer_demand["Spain", 2041]))
    print("   - DEM|Spain in million MMTbtu/yr: ", _formatted_number)
    
    ###############################################################################
    
    model.par_exporter_budget = py.Param(
        model.set_exporter,
        initialize=dict_budget,
        doc="Financial resource in 2030 of an exporter e for supply chain emission mitigation measures (in million $).",
    )
    print("   - Budget|Algeria in million $: ", model.par_exporter_budget["Algeria"])
    
    ###############################################################################
    
    # SOURCE: https://www.enerdata.net/publications/executive-briefing/carbon-price-forecast-under-eu-ets.pdf
    # between 75 (2030) and 138 (2040)
    
    model.par_carbon_tax = py.Param(
        model.set_years,
        initialize=dict_carbon_price,
        doc="Carbon price/tax for importing LNG in EU importers i (in million $ / million tCO2)",
    )
    print(
        "   - Carbon price|EU|2035 in million $ / million tCO2: {:.1f}".format(
            model.par_carbon_tax[2035]
        )
    )
    
    ###############################################################################
    
    model.par_CCS_cost = py.Param(
        model.set_years,
        initialize=dict_CCS,
        doc="Cost for CCS for the EU-based natural gas production per year y (in million $ / million tCO2).",
    )
    print(
        "   - Cost for CCS for the EU-based natural gas production in million $ / million tCO2: {:.5f}".format(
            model.par_CCS_cost[2035]
        )
    )
    
    ###############################################################################
    
    model.par_EDP_cost = py.Param(
        model.set_years,
        initialize=dict_EDP,
        doc="Cost for EU-based natural gas production per year t (in million $ / million MMBtu).",
    )
    print(
        "   - Cost for EU-based natural gas production per year t (in million $ / million MMBtu): {:.1f}".format(
            model.par_EDP_cost[2035]
        )
    )
    
    ###############################################################################
    
    model.par_EDP_production_limit = py.Param(
        model.set_years,
        initialize=dict_EDP_limit,
        doc="Maximum EU-based natural gas production per year t (in million MMBtu/year).",
    )
    print(
        "   - Maximum EU-based natural gas production per year t (in million MMBtu/year): {:,}".format(
            model.par_EDP_production_limit[2035]
        )
    )
    
    ###############################################################################
    
    model.par_eff = py.Param(
        model.set_exporter,
        model.set_years,
        initialize=dict_eff,
        doc="Specific investment costs for reducing supply chain emissions per exporter e (in million tCO2 / million MMBtu / million $).",
    )
    print(
        "   - Investment costs for supply chain mitigation (million tCO2 / million MMBtu / million $): {}".format(
            model.par_eff["Algeria", 2030]
        )
    )
    
    ###############################################################################
    
    model.par_rho = py.Param(
        model.set_exporter,
        initialize=dict_rho,
        doc="Specific supply chain emissions per exporter e (in million tCO2 / million MMBtu).",
    )
    
    print(
        "   - Algeria's specific supply chain emissions (in million tCO2 / million MMBtu): {}".format(
            model.par_rho["Algeria"]
        )
    )
    
    ###############################################################################
    
    _number_of_binary_steps = 4
    _dict_steps = {
        i: 2 ** (i - (_number_of_binary_steps - 1)) for i in range(_number_of_binary_steps)
    }
    
    max_val = sum(_dict_steps.values())  # Gesamtwert der Stützstellen
    _dict_steps = {k: v / max_val for k, v in _dict_steps.items()}
    
    # print(_dict_steps)
    
    ###############################################################################
    
    model.set_n = py.Set(initialize=range(0, _number_of_binary_steps, 1))
    
    model.par_n = py.Param(model.set_n, initialize=_dict_steps)
    
    ###############################################################################
    
    
    model.par_supply_risk = py.Param(
        model.set_exporter,
        initialize=dict_supply_risk,
        doc="Supply Risk associated with supply from exporter e in importer",
    )
    # print("   - Supply Risk: {}".format(model.par_supply_risk["Algeria"]))
    
    ###############################################################################
    
    
    # def init_par_theata(model, exporter):
    #     return model.par_supply_risk[exporter] / model.par_rho[exporter]
    
    
    # model.par_theta = py.Param(model.set_exporter, rule=init_par_theata, doc="theta_{e}")
    
    del [
        dict_des,
        dict_liquification,
        dict_demand_eu,
        dict_demand_global,
        dict_budget,
        dict_carbon_price,
        dict_CCS,
        dict_EDP,
        dict_EDP_limit,
        dict_eff,
        dict_rho,
        dict_supply_risk,
    ]
    
    ###############################################################################
    
    model.var_q = py.Var(
        model.set_exporter,
        model.set_importer,
        model.set_years,
        within=py.NonNegativeReals,
        doc="CHECKED: q_{e,i,t}",
    )
    
    ###############################################################################
    
    model.var_q_edp = py.Var(
        model.set_importer_eu,
        model.set_years,
        within=py.NonNegativeReals,
        #    bounds=(0, 3531.5),
        doc="CHECKED: q^{EDP}_{i',t}",
    )
    
    ###############################################################################
    
    model.var_r = py.Var(
        model.set_exporter,
        model.set_importer,
        model.set_years,
        within=py.NonNegativeReals,
        doc="CHECKED: r_{e,i',t}",
    )
    
    ###############################################################################
    
    model.var_supply_cost = py.Var(within=py.NonNegativeReals, doc="CHECKED: SupplyCost")
    
    ###############################################################################
    
    model.var_psi = py.Var(
        model.set_exporter,
        model.set_importer_eu,
        model.set_years,
        within=py.NonNegativeReals,
        doc="CHECKED: PSI_{e,i',t}",
    )
    
    ###############################################################################
    
    model.var_d = py.Var(
        model.set_exporter,
        model.set_importer_eu,
        model.set_years,
        within=py.NonNegativeReals,
        doc="CHECKED: d^{EU}_{e,i',t}",
    )
    
    ###############################################################################
    
    model.var_beta = py.Var(
        model.set_exporter,
        model.set_years,
        within=py.NonNegativeReals,
        doc="CHECKED: beta_{e,t}",
    )
    
    ###############################################################################
    
    model.var_earnings = py.Var(
        model.set_exporter,
        model.set_years,
        within=py.NonNegativeReals,
        doc="CHECKED: e_{e,t}",
    )
    
    ###############################################################################
    
    model.var_s = py.Var(
        model.set_exporter,
        model.set_years,
        within=py.NonNegativeReals,
        doc="CHECKED: s_{e,t}",
    )
    
    ###############################################################################
    
    model.var_rho = py.Var(
        model.set_exporter,
        model.set_years,
        within=py.NonNegativeReals,
        doc="CHECKED: rho_{e,t}",
    )
    
    ###############################################################################
    
    model.var_rho_plus = py.Var(
        model.set_exporter,
        model.set_years,
        within=py.NonNegativeReals,
        doc="CHECKED: rho^{CO2,LNG+}_{e,t}",
    )
    
    ###############################################################################
    
    model.var_supply_con = py.Var(
        within=py.NonNegativeReals, doc="CHECKED: SupplyConcentration"
    )
    
    ###############################################################################
    
    model.var_c = py.Var(
        model.set_importer_eu,
        model.set_years,
        within=py.NonNegativeReals,
        doc="CHECKED: SupplyConcentration",
    )
    
    ###############################################################################
    
    model.var_supply_risk = py.Var(doc="CHECKED: SupplyRisk")
    
    ###############################################################################
    
    model.var_sigma_bin = py.Var(
        model.set_exporter,
        model.set_years,
        model.set_n,
        within=py.Binary,
        doc="CHECKED: sigma_{e,i',t,n}",
    )
    
    # print(model.var_sigma_bin.pprint())
    
    ###############################################################################
    
    model.var_z = py.Var(
        model.set_exporter,
        model.set_importer_eu,
        model.set_years,
        model.set_n,
        within=py.NonNegativeReals,
        doc="z_{e,i',t,n}",
    )
    
    # print(model.var_z.pprint())
    
    ###############################################################################
    
    
    def supply_cost(model):
        delivered = sum(
            model.par_des[e, i, t] * model.var_q[e, i, t]
            for e in model.set_exporter
            for i in model.set_importer
            for t in model.set_years
        )
        european = sum(
            model.var_q_edp[i, t] * (model.par_EDP_cost[t] + model.par_CCS_cost[t])
            for i in model.set_importer_eu
            for t in model.set_years
        )
        cbam = sum(
            model.var_r[e, i, t]
            for e in model.set_exporter
            for i in model.set_importer_eu
            for t in model.set_years
        )
        return model.var_supply_cost == delivered + european + cbam
    
    
    model.con_supply_cost = py.Constraint(
        rule=supply_cost,
        doc="CHECKED: Eq. (4): Supply Cost = Sum_t [Delivered ex-ship + EDP + CBAM]",
    )
    
    ###############################################################################
    
    
    def cbam_cost(m, e, i, t):
        # m.var_psi[e, i, t] --- specific emissions rho X LNG delivered 
        # see equation / function "psi_z_constraint" below
        if e == 'USA':
            return m.var_r[e, i, t] == m.par_carbon_tax[t] * m.var_psi[e, i, t]
        else:
            return m.var_r[e, i, t] == m.par_carbon_tax[t] * m.var_psi[e, i, t]
    
    
    model.con_cbam_cost = py.Constraint(
        model.set_exporter,
        model.set_importer_eu,
        model.set_years,
        rule=cbam_cost,
        doc="CHECKED: Eq. (5): r^{EU}_{e,i'',t} = CO2^{tax}_{t} x PSI_{e,i',t}",
    )
    
    ###############################################################################
    
    
    def cbam_distribution(m, e, i, t):
        return m.var_d[e, i, t] == _Share_t * m.var_r[e, i, t]
    
    
    model.con_cbam_distribution = py.Constraint(
        model.set_exporter,
        model.set_importer_eu,
        model.set_years,
        rule=cbam_distribution,
        doc="CHECKED: Eq. (6): d^{EU}_{e,i',t} = Share_t x r^{EU}_{e,i',t}",
    )
    
    ###############################################################################
    
    
    def cbam_exporter_flexible(m, t):
        return sum(m.var_beta[e, t] for e in m.set_exporter) <= sum(
            m.var_d[e, i, t] for e in m.set_exporter for i in m.set_importer_eu
        )
    
    
    model.con_cbam_exporter_flexible = py.Constraint(
        model.set_years,
        rule=cbam_exporter_flexible,
        doc="CHECKED: Eq. (7): Sum_e beta_{e,t} = Sum_e,i' d^{EU}_{e,i',t}",
    )
    
    ###############################################################################
    
    
    def cbam_exporter_strict(m, e, t):
        return m.var_beta[e, t] <= sum(m.var_d[e, i, t] for i in model.set_importer_eu)
    
    
    model.con_cbam_exporter_strict = py.Constraint(
        model.set_exporter,
        model.set_years,
        rule=cbam_exporter_strict,
        doc="Eq. (9): beta_{e,t} = Sum_i' d^{EU}_{e,i',t}",
    )
    
    if _CBAM_IMPLEMENTATION_STRICT == False:
        model.con_cbam_exporter_strict.deactivate()
    else:
        model.con_cbam_exporter_flexible.deactivate()
    
    ###############################################################################
    
    
    def earnings_per_exporter(m, e, t):
        if t == m.set_years.first():
            return (
                m.var_earnings[e, t]
                == m.par_exporter_budget[e] - m.var_s[e, t]
            )
        else:
            return (
                m.var_earnings[e, t]
                == m.var_earnings[e, t - 1] + m.var_beta[e, t - 1] - m.var_s[e, t]
            )
    
    
    model.con_earnings_per_exporter = py.Constraint(
        model.set_exporter,
        model.set_years,
        rule=earnings_per_exporter,
        doc="CHECKED: Eq. (10+11): e_{e,t} = e_{e,t-1} + beta_{e,t} - s_{e,t}",
    )
    
    
    def earnings_per_exporter_empty(m, e):
        _t_end = m.set_years.last()
        return m.var_earnings[e, _t_end] == 0
    
    
    model.con_earnings_per_exporter_empty = py.Constraint(
        model.set_exporter,
        rule=earnings_per_exporter_empty,
        doc='CHECKED'
    )
    
    
    ###############################################################################
    
    
    def specific_supply_chain_emissions(m, e, t):
        if t == m.set_years.first():
            return m.var_rho[e, t] == m.par_rho[e] - m.var_rho_plus[e, t]
        else:
            return m.var_rho[e, t] == m.var_rho[e, t - 1] - m.var_rho_plus[e, t]
    
    
    model.con_specific_supply_chain_emissions = py.Constraint(
        model.set_exporter,
        model.set_years,
        rule=specific_supply_chain_emissions,
        doc="CHECKED: Eq. (12+13): rho^{CO2,LNG}_{e,t} = rho^{CO2,LNG}_{e,t-1} - rho^{CO2,LNG+}_{e,t}",
    )
    
    
    # def define_last_var_rho_plus(m, e, t):
    #     if t == m.set_years.last():
    #         return m.var_rho_plus[e, t] == 0
    #     else:
    #         return py.Constraint.Skip
    # model.con_define_last_var_rho_plus = py.Constraint(model.set_exporter, model.set_years, rule=define_last_var_rho_plus)
    
    
    ###############################################################################
    
    
    def supply_chain_emission_measures_economics(m, e, t):
        return m.var_rho_plus[e, t] == m.par_eff[e, t] * m.var_s[e, t]
    
    
    model.con_supply_chain_emission_measures_economics = py.Constraint(
        model.set_exporter,
        model.set_years,
        rule=supply_chain_emission_measures_economics,
        doc="CHECKED: Eq. (14): rho^{CO2,LNG+}_{e,t} = Eff x s_{e,t}",
    )
    
    ###############################################################################
    
    
    def supply_concentration(m):
        return m.var_supply_con == sum(
            m.var_c[i, t] for i in m.set_importer_eu for t in m.set_years
        )
    
    
    model.con_supply_concentration = py.Constraint(
        rule=supply_concentration, doc="CHECKED: SupplyConcentration = sum_{t,i'} c_{i',t}"
    )
    
    ###############################################################################
    
    
    def supply_concentration_per_importer(m, e, i, t):
        return m.var_q[e, i, t] <= m.var_c[i, t] * m.par_importer_demand[i, t]
    
    
    model.con_supply_concentration_per_importer = py.Constraint(
        model.set_exporter,
        model.set_importer_eu,
        model.set_years,
        rule=supply_concentration_per_importer,
        doc="CHECKED: Eq. (16): \frac{q_{e,i',t}}{d_{i',t} <= c_{i',t}",
    )
    
    ###############################################################################
    
    
    def supply_risk(m):
        _first_term = sum(
            m.par_supply_risk[e] * m.var_q[e, i, t]
            for t in model.set_years
            for e in model.set_exporter
            for i in model.set_importer
        )
        
        _second_term = sum(
            m.var_q[e, i, t] * m.par_rho[e] * 0.0263
            for t in model.set_years
            for e in model.set_exporter
            for i in model.set_importer_eu
        )
        
        _third_term = sum(
            m.var_psi[e, i, t] * 0.0263
            for t in model.set_years
            for e in model.set_exporter
            for i in model.set_importer_eu
        )
        
        return _first_term - _second_term + _third_term == m.var_supply_risk
    
    
    # def supply_risk(m):
        # _european_importers = sum(
            # m.par_supply_risk[e] / m.par_rho[e] * m.var_psi[e, i, t]
            # for t in m.set_years
            # for e in m.set_exporter
            # for i in m.set_importer_eu
        # )
        # _other_importers = sum(
            # m.par_supply_risk[e] * m.var_q[e, i, t]
            # for t in m.set_years
            # for e in m.set_exporter
            # for i in m.set_non_eu_imp
        # )
    
        # return m.var_supply_risk == _european_importers + _other_importers
    
    
    model.con_supply_risk = py.Constraint(
        rule=supply_risk, 
        doc="CHECKED: Eq. (19): Supply Risk"
        )
    
    ###############################################################################
    
    
    def psi_z_constraint(m, e, i, t):
        return m.var_psi[e, i, t] == sum(
            m.par_n[n] * model.par_rho[e] * m.var_z[e, i, t, n]
            for n in model.set_n
        )
    
    
    model.con_psi_z_constraint = py.Constraint(
        model.set_exporter, model.set_importer_eu, model.set_years, 
        rule=psi_z_constraint,
        doc='CHECKED'
    )
    
    
    # def z_q_constraint1(m, e, i, t, n):
    #     return m.var_z[e, i, t, n] <= m.par_liquification[e] * model.par_rho[e] * m.var_sigma_bin[e, i, t, n]
    def z_q_constraint1(m, e, i, t, n):
        return m.var_z[e, i, t, n] <= m.var_sigma_bin[e, t, n] * m.par_liquification[e, t]
    
    
    model.con_z_q_constraint1 = py.Constraint(
        model.set_exporter,
        model.set_importer_eu,
        model.set_years,
        model.set_n,
        rule=z_q_constraint1,
        doc='CHECKED'
    )
    
    
    # def z_q_constraint2(m, e, i, t, n):
    #     return m.var_z[e, i, t, n] <= m.var_q[e, i, t]
    def z_q_constraint2(m, e, i, t, n):
        return m.var_z[e, i, t, n] <= m.var_q[e, i, t]
    
    
    model.con_z_q_constraint2 = py.Constraint(
        model.set_exporter,
        model.set_importer_eu,
        model.set_years,
        model.set_n,
        rule=z_q_constraint2,
        doc='CHECKED'
    )
    
    
    # def z_q_constraint3(m, e, i, t, n):
    #     return (
    #         m.var_z[e, i, t, n]
    #         >= m.var_q[e, i, t] - (1 - m.var_sigma_bin[e, i, t, n]) * m.par_liquification[e]
    #     )
    def z_q_constraint3(m, e, i, t, n):
        return (
            m.var_q[e, i, t] - m.var_z[e, i, t, n]
            <= (1 - m.var_sigma_bin[e, t, n]) * m.par_liquification[e, t]
        )
    
    
    model.con_z_q_constraint3 = py.Constraint(
        model.set_exporter,
        model.set_importer_eu,
        model.set_years,
        model.set_n,
        rule=z_q_constraint3,
        doc='CHECKED'
    )
    
    ###############################################################################
    
    
    def define_specific_emissions(m, e, t):
        return m.var_rho[e, t] == sum(
            m.var_sigma_bin[e, t, n] * m.par_n[n] * model.par_rho[e] for n in model.set_n
        )
    
    
    model.con_define_specific_emissions = py.Constraint(
        model.set_exporter,
        model.set_years,
        rule=define_specific_emissions,
        doc="CHECKED: rho[e,t] = sum(sigma[e,t,n] * par[n] * RHO[e])",
    )
    
    ###############################################################################
    
    
    def reduce_binary_size(m, e, t, n):
        # Only apply constraint for years beyond the start of the planning horizon
        if t in m.set_years:
            # Find the starting year of the current 5-year block
            block_start = 2030 + 5 * ((t - 2030) // 5)
            if t != block_start:
                return m.var_sigma_bin[e, t, n] == m.var_sigma_bin[e, block_start, n]
            else:
                return py.Constraint.Skip  # No constraint needed on the first year of the block
        else:
            return py.Constraint.Skip

        
    model.con_reduce_binary_size = py.Constraint(model.set_exporter, 
                                                 model.set_years, 
                                                 model.set_n, 
                                                 rule=reduce_binary_size, 
                                                 doc='CHECKED'
                                                 )
     
    def reduce_binary_2(m, e, n):
        return m.var_sigma_bin[e, m.set_years.last(), n] == m.var_sigma_bin[e, m.set_years.last()-5, n]
    
    model.con_reduce_binary_2 = py.Constraint(model.set_exporter, model.set_n, rule=reduce_binary_2)
    
    ###############################################################################
    
    
    def demand_balance(m, i, t):
        if i in m.set_importer_eu:
            return (
                m.par_importer_demand[i, t]
                == sum(m.var_q[e, i, t] for e in m.set_exporter) + m.var_q_edp[i, t]
            )
        else:
            return m.par_importer_demand[i, t] == sum(
                m.var_q[e, i, t] for e in m.set_exporter
            )
    
    
    model.con_demand_balance = py.Constraint(
        model.set_importer, model.set_years, rule=demand_balance,
        doc='CHECKED'
    )
    
    ###############################################################################
    
    
    def european_domestic_production_annual(m, t):
        return (
            sum(m.var_q_edp[i, t] for i in m.set_importer_eu)
            <= m.par_EDP_production_limit[t]
        )
    
    
    model.con_european_domestic_production_annual = py.Constraint(
        model.set_years, rule=european_domestic_production_annual,
        doc='CHECKED'
    )
    
    ###############################################################################
    
    
    def liquification_limits_per_exporter(m, e, t):
        return sum(m.var_q[e, i, t] for i in m.set_importer) <= m.par_liquification[e, t]
    
    
    model.con_liquification_limits_per_exporter = py.Constraint(
        model.set_exporter, model.set_years, rule=liquification_limits_per_exporter,
        doc='CHECKED'
    )
    
    ###############################################################################
    
    """
        UTOPIA OPTIMIZATION
    """
    utopia_dict = {}
    
    
    # SUPPLY COST
    def objective_cost(m):
        return m.var_supply_cost
    
    
    model.objective = py.Objective(expr=objective_cost, sense=py.minimize)
    solver = py.SolverFactory("gurobi")
    solution = solver.solve(model)
    
    print("")
    print("____Cost____")
    print("Objective function: {:.2f}".format(model.objective()))
    print("    Cost: {:.2f}".format(model.var_supply_cost()))
    print("    Concentration: {:.2f}".format(model.var_supply_con()))
    print("    Risk: {:.2f}".format(model.var_supply_risk()))
    print("")
    
    utopia_dict["Obj: Supply Cost", "Supply Cost"] = model.var_supply_cost()
    utopia_dict["Obj: Supply Cost", "Supply Concentration"] = model.var_supply_con()
    utopia_dict["Obj: Supply Cost", "Supply Risk"] = model.var_supply_risk()
    
    model.del_component(model.objective)
    
    
    # SUPPLY CONCENTRATION
    def objective_concentration(m):
        return m.var_supply_con
    
    
    model.objective = py.Objective(expr=objective_concentration, sense=py.minimize)
    solver = py.SolverFactory("gurobi")
    solution = solver.solve(model)
    print("____Supply Concentration____")
    print("Objective function: {:.2f}".format(model.objective()))
    print("    Cost: {:.2f}".format(model.var_supply_cost()))
    print("    Concentration: {:.2f}".format(model.var_supply_con()))
    print("    Risk: {:.2f}".format(model.var_supply_risk()))
    print("")
    
    utopia_dict["Obj: Supply Concentration", "Supply Cost"] = model.var_supply_cost()
    utopia_dict[
        "Obj: Supply Concentration", "Supply Concentration"
    ] = model.var_supply_con()
    utopia_dict["Obj: Supply Concentration", "Supply Risk"] = model.var_supply_risk()
    
    model.del_component(model.objective)
    
    
    # SUPPLY RISK
    def objective_risk(m):
        return m.var_supply_risk
    
    
    model.objective = py.Objective(expr=objective_risk, sense=py.minimize)
    solver = py.SolverFactory("gurobi")
    solution = solver.solve(model)
    print("____Supply risk____")
    print("Objective function: {:.2f}".format(model.objective()))
    print("    Cost: {:.2f}".format(model.var_supply_cost()))
    print("    Concentration: {:.2f}".format(model.var_supply_con()))
    print("    Risk: {:.2f}".format(model.var_supply_risk()))
    print("")
    
    utopia_dict["Obj: Supply Risk", "Supply Cost"] = model.var_supply_cost()
    utopia_dict["Obj: Supply Risk", "Supply Concentration"] = model.var_supply_con()
    utopia_dict["Obj: Supply Risk", "Supply Risk"] = model.var_supply_risk()
    model.del_component(model.objective)
    
    w_supply_cost = (
        _weighting_factors["Supply Cost"]
        * 1
        / (
            max(
                utopia_dict["Obj: Supply Cost", "Supply Cost"],
                utopia_dict["Obj: Supply Concentration", "Supply Cost"],
                utopia_dict["Obj: Supply Risk", "Supply Cost"],
            )
            - min(
                utopia_dict["Obj: Supply Cost", "Supply Cost"],
                utopia_dict["Obj: Supply Concentration", "Supply Cost"],
                utopia_dict["Obj: Supply Risk", "Supply Cost"],
            )
        )
    )
    
    w_supply_concentration = (
        _weighting_factors["Supply Concentration"]
        * 1
        / (
            max(
                utopia_dict["Obj: Supply Cost", "Supply Concentration"],
                utopia_dict["Obj: Supply Concentration", "Supply Concentration"],
                utopia_dict["Obj: Supply Risk", "Supply Concentration"],
            )
            - min(
                utopia_dict["Obj: Supply Cost", "Supply Concentration"],
                utopia_dict["Obj: Supply Concentration", "Supply Concentration"],
                utopia_dict["Obj: Supply Risk", "Supply Concentration"],
            )
        )
    )
    
    w_supply_risk = (
        _weighting_factors["Supply Risk"]
        * 1
        / (
            max(
                utopia_dict["Obj: Supply Cost", "Supply Risk"],
                utopia_dict["Obj: Supply Concentration", "Supply Risk"],
                utopia_dict["Obj: Supply Risk", "Supply Risk"],
            )
            - min(
                utopia_dict["Obj: Supply Cost", "Supply Risk"],
                utopia_dict["Obj: Supply Concentration", "Supply Risk"],
                utopia_dict["Obj: Supply Risk", "Supply Risk"],
            )
        )
    )
    
    """
        MULTI-OBJECTIVE OPTIMIZATION
    """
    print("MULTI-OBJECTIVE OPTIMIZATION")
    print(w_supply_cost)
    print(w_supply_concentration)
    print(w_supply_risk)
    print("")
    
    
    def objective(m):
        return (
            w_supply_cost * m.var_supply_cost
            + w_supply_concentration * m.var_supply_con
            + w_supply_risk * m.var_supply_risk
        )
    
    
    model.objective = py.Objective(expr=objective, sense=py.minimize)
    model.name = "Cross border adjustment mechanism - LNG implementation"
    model.write("cbam_trade_model.lp", io_options={"symbolic_solver_labels": True})
    
    
    ###############################################################################
    
    solver = py.SolverFactory("gurobi")
    
    # solver.options["NumericFocus"] = 3  # Improve numerical stability
    # solver.options["Heuristics"] = 0.0  # Turn off heuristics
    solver.options["Threads"] = 0  # Use all available CPU cores
    
    # solver.options["BarConvTol"] = 1e-8  # Improves barrier solver accuracy
    # solver.options["Method"] = -1  # Auto-select best solution method (default)
    # solver.options["AggFill"] = 0  # Avoid aggressive matrix aggregation
    
    solver.options["MIPFocus"] = 0  # Focus on optimality
    # solver.options['MIPGap'] = 1e-4
    solver.options["TimeLimit"] = 3*3600  # Set a generous time limit (e.g., 1 hour)
    
    solver.options["LogFile"] = "gurobi.log"  # Log solving process
    
    solution = solver.solve(model, tee=True)
    print("OBJECTIVE VALUE: {:.1f}".format(model.objective()))
    # print(model.var_supply_cost() / 1000000)
    
    # REPORT THE MODEL RESULTS TO OUTPUT FILES
    _now = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = os.path.join("result", "{}__{}".format(model.scenario, _now))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    _create_figures = create_figures.plot(model, result_dir)
    input_df.to_excel(result_dir + '/READ_ME_TO_UNDERSTAND_MAIN_INPUTS.xlsx', index=False)
    
    
    
    script_dir = os.path.dirname(__file__)  # directory of plotting.py
    r_script_path = os.path.join(script_dir, "chord_diagram_plot.R")

market_share_supply_risk_plot.run()

# print('NO US TAX REVENUE REDISTRIBUTION')
