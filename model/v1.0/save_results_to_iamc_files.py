import pandas as pd
import numpy as np
import pyomo.environ as py
import os


def write_iamc(output_df, model, scenario, region, variable, unit, time, values):

    if isinstance(values, list):
        _df = pd.DataFrame(
            {
                "model": model,
                "scenario": scenario,
                "region": region,
                "variable": variable,
                "unit": unit,
                "year": time,
                "value": values,
            }
        )
    else:
        _df = pd.DataFrame(
            {
                "model": model,
                "scenario": scenario,
                "region": region,
                "variable": variable,
                "unit": unit,
                "year": time,
                "value": values,
            },
            index=[0],
        )

    output_df = output_df.append(_df)
    return output_df


def write_results_to_ext_iamc_format(m, res_dir):
    """
        (1) SAVE INPUT DATA TO ENSURE RESULTS CAN BE REPRODUCED ==> '0_input.xlsx'
            (A) delivered ex-ship price (par_des)
            (B) maximum gasification / export capacity (par_gasification)
            (C) lng demand (par_demand)
            (D) cost of carbon capture and storage (par_CCS_cost)
            (E) cost of european domestic production (par_EDP_cost)
            (F) maximum european domestic production (par_max_EDP)
    """

    input_iamc = pd.DataFrame()
    _scenario = m.scenario
    _model = 'LNG model'
    _time = m.year

    # (1A)
    for e in m.set_exporter:
        for i in m.set_importer:
            input_iamc = write_iamc(
                input_iamc, _model, _scenario, e+'>'+i, "Delivered ex-ship price", "$/MMBtu", m.year, m.par_des[e,i]
            )

    # (1B)
    for e in m.set_exporter:
        input_iamc = write_iamc(
            input_iamc, _model, _scenario, e, "Gasification capacity", "MMBtu/year", m.year, m.par_gasification[e]
        )

    # (1C)
    for i in m.set_importer:
        input_iamc = write_iamc(
            input_iamc, _model, _scenario, i, "LNG demand", "MMBtu/year", m.year, m.par_demand[i]
        )

    # (1D)
    input_iamc = write_iamc(
        input_iamc, _model, _scenario, 'Europe', "CCS|Cost", "$/MMBtu", m.year, m.par_CCS_cost()
    )

    # (1E)
    input_iamc = write_iamc(
        input_iamc, _model, _scenario, 'Europe', "EDP|Cost", "$/MMBtu", m.year, m.par_EDP_cost()
    )

    # (1F)
    input_iamc = write_iamc(
        input_iamc, _model, _scenario, 'Europe', "EDP|Maximum", "MMBtu/year", m.year, m.par_max_EDP()
    )

    input_iamc.to_excel(
            os.path.join(res_dir, "0_inputs.xlsx"), index=False
        )

    """
        (2) SAVE RESULTS '1_optimal solution.xlsx'
            (2A) var_q
            (2B) var_q_dom_europe
            (2C) var_demand_not_covered
            
            (2D) var_cost_market_clearing
            (2E) var_cost_edp
            (2F) var_cost_ccs
            (2G) var_cost_not_supply
            (2H) objective
    """

    output_iamc = pd.DataFrame()

    # (2A)
    for e in m.set_exporter:
        for i in m.set_importer:
            _value = m.var_q[e, i]()
            if _value > 0:
                output_iamc = write_iamc(
                    output_iamc, _model, _scenario, e+'>'+i, "LNG|Trade", "MMBtu", m.year, _value
                )
            else:
                pass

    # (2B)
    for c in m.set_importer_europe:
        _value = m.var_q_dom_europe[c]()
        if _value > 0:
            output_iamc = write_iamc(
                    output_iamc, _model, _scenario, c, "EDP|NG", "MMBtu", m.year, _value
                )
        else:
            pass

    # (2C)
    for i in m.set_importer:
        _v = m.var_demand_not_covered[i]()
        if _v > 0:
            output_iamc = write_iamc(
                output_iamc, _model, _scenario, c, "LNG|Unsupplied", "MMBtu", m.year, _v
            )
        else:
            pass

    output_iamc.to_excel(
            os.path.join(res_dir, "1_optimal solution.xlsx"), index=False
        )



    return





















    #
    # DUAL VARIABLEN SPEICHERN











    # # Spot markt revenues
    # _value = np.around(py.value(m.revenues_spot), 0)
    # output_iamc = write_IAMC(
    #     output_iamc, _model, _scenario, _region, "Day-Ahead", _unit, _time, _value
    # )
    # # Base future revenues
    # _value = np.around(py.value(m.revenues_future), 0)
    # output_iamc = write_IAMC(
    #     output_iamc, _model, _scenario, _region, "Future contract", _unit, _time, _value
    # )
    # # Hydrogen revenues
    # _value = np.around(py.value(m.revenues_H2), 0)
    # output_iamc = write_IAMC(
    #     output_iamc, _model, _scenario, _region, "Hydrogen", _unit, _time, _value
    # )
    #
    # output_iamc.to_excel(os.path.join(res_dir, "IAMC_annual.xlsx"), index=False)
    #
    # _unit = "MWh"
    # _time = [_t for _t in m.set_time]
    # output_iamc = pd.DataFrame()
    #
    # # Quantity future
    # _value = []
    # for _t in m.set_time:
    #     _value.append(np.around(py.value(m.v_q_future[_t]), 0))
    # output_iamc = write_IAMC(
    #     output_iamc, _model, _scenario, _region, "Future contract", _unit, _time, _value
    # )
    # # Quantity day-ahead
    # _value = []
    # for _t in m.set_time:
    #     _value.append(np.around(py.value(m.v_q_spot[_t]), 0))
    # output_iamc = write_IAMC(
    #     output_iamc, _model, _scenario, _region, "Day-Ahead", _unit, _time, _value
    # )
    # # Quantity hydrogen
    # _value = []
    # for _t in m.set_time:
    #     _value.append(np.around(py.value(m.v_q_H2[_t]), 0))
    # output_iamc = write_IAMC(
    #     output_iamc, _model, _scenario, _region, "Hydrogen", _unit, _time, _value
    # )
    #
    # output_iamc.to_excel(os.path.join(res_dir, "IAMC_hourly.xlsx"), index=False)
    #
    # _value = []
    # for _t in m.set_time:
    #     _value.append(np.around(py.value(m.v_q_fossil[_t]), 0))
    # output_iamc = write_IAMC(
    #     output_iamc, _model, _scenario, _region, "Conventional", _unit, _time, _value
    # )
    #
    # output_iamc.to_excel(os.path.join(res_dir, "IAMC_supply.xlsx"), index=False)
    #
    # plot_IAMC.plot_results(res_dir)
    #
    # # Write shadow price and projecte shadow price to result file
    # output_iamc = pd.DataFrame()
    # _value = []
    # for _t in m.set_time:
    #     _value.append(np.around(-py.value(m.dual_lambda_load[_t]), 2))
    # output_iamc = write_IAMC(
    #     output_iamc, _model, _scenario, _region, "Shadow price", _unit, _time, _value
    # )

