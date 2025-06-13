import pyam as py
import matplotlib.pyplot as plt
import os
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import pandas as pd


_colors = {
    "Algeria": "#FFEAD2",
    "Qatar": "#89B9AD",
    "Nigeria": "#ACB1D6",
    "Other Europe": "#FF90BC",
    "Other Africa": "#EE7214",
    "Trinidad & Tobago": "#F7B787",
    "USA": "#748E63",
    "Other Americas": "#9BB8CD",
    }


def run(model, folder):
    plt.style.use("default")
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12

    # for Europe
    # fig, ax = plt.subplots()

    _dict_europe = {}
    for european_country in model.set_importer_europe:
        for exporter in model.set_exporter:
            if model.var_q[exporter, european_country]() > 0:
                if exporter in _dict_europe.keys():
                    _quantity = (
                        _dict_europe[exporter][0]
                        + model.var_q[exporter, european_country]()
                    )
                    _price = (
                        _dict_europe[exporter][0] * _dict_europe[exporter][1]
                        + model.var_q[exporter, european_country]()
                        * model.par_des[exporter, european_country]
                    ) / _quantity
                    del _dict_europe[exporter]
                    _dict_europe[exporter] = tuple([_quantity, _price])
                else:
                    _dict_europe[exporter] = tuple(
                        [
                            model.var_q[exporter, european_country](),
                            model.par_des[exporter, european_country],
                        ]
                    )
            else:
                pass

    _regions = []
    _quantities = []
    _prices = []

    for _r, _t in sorted(_dict_europe.items(), key=lambda x: x[1][1]):
        _regions.append(_r)
        _quantities.append(_t[0])
        _prices.append(_t[1])

    _x_pos = []
    _cumulated = 0
    for _index, _qua in enumerate(_quantities):
        if _index == 0:
            _x_pos.append(_qua / 2)
        else:
            _x_pos.append(_qua / 2 + _cumulated)
        _cumulated = _cumulated + _qua

    # ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
    # ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
    # _bars = ax.bar(_x_pos, height=_prices, width=_quantities, fill=True, color=[_colors.get(_reg, 'black') for _reg in _regions], zorder=2, alpha=1)
    # for bar in _bars:
    #     bar.set_edgecolor("black")
    #     bar.set_linewidth(0.5)

    # plt.xlim(0, _cumulated)
    # plt.ylim(0, 15.5)

    # formatter = ticker.ScalarFormatter(useMathText=True)
    # formatter.set_scientific(True)
    # formatter.set_powerlimits((-3, 1))

    # ax.xaxis.set_major_formatter(formatter)

    # _patches = []
    # for _reg in sorted(_regions):
    #     _patches.append(mpatches.Patch(color=_colors.get(_reg, 'black'), label=_reg))
        
    # if len(_patches) == 4:
    #     _ncol = 4
    # else:
    #     _ncol = 3
    
    # _legend = ax.legend(handles=_patches, loc='upper left', facecolor='white', fontsize=12,
    #                     handlelength=1,
    #                     handletextpad=0.5, ncol=_ncol, borderpad=0.5, columnspacing=1, edgecolor="black", frameon=True,
    #                     bbox_to_anchor=(0.005, 1-0.005),
    #                     shadow=False,
    #                     framealpha=0
    #                     )

    # _legend.get_frame().set_linewidth(0.5)

    # ax.set_xlabel("Import volumes from regions [MMBtu]", fontsize=12)
    # ax.set_ylabel("Supply cost [$/MMBtu]", fontsize=12)

    # #  plt.title("LNG supply in Europe 2040 and associated supply cost", fontsize=14)
    # plt.tight_layout()
    # fig.savefig(os.path.join(folder, "import volumes europe.pdf"), dpi=1000)

    # save average and marginal cost
    _regions  # regions
    _quantities  # supply quantities
    _prices  # supply cost

    _average = 0
    _marginal = 0
    _total = 0

    for index, item in enumerate(_regions):
        _total = _total + _quantities[index] * _prices[index]

    _average = _total / sum(_quantities)
    _marginal = _prices[-1]

    _df = pd.DataFrame(
        {
            "model": 'LNG model',
            "scenario": model.scenario,
            "region": 'Europe',
            "variable": ['LNG|Cost|Average', 'LNG|Cost|Marginal'],
            "unit": ['$/MMBtu', 'MMBtu'],
            "year": '2040',
            "value": [_average, _marginal],
        }
    )

    # _df.to_excel(os.path.join(folder, '3_european costs.xlsx'), index=False)
    
    _df = pd.DataFrame(
        {
            "model": 'LNG model',
            "scenario": model.scenario,
            "region": _regions,
            "variable": 'LNG|Export|Europe',
            "unit": 'MMBtu',
            "year": '2040',
            "value": _quantities,
        }
    )

    # _df.to_excel(os.path.join(folder, '3_european supply.xlsx'), index=False)
    
    #  plot European marginal and average supply cost
    
    _labels = ['Average','Marginal']
    _values = [_average, _marginal]
    
    # _fig = plt.figure(figsize=(6,3))
    # _hbars = plt.barh(_labels, _values, color=['#BCA37F', '#113946'], zorder=2, alpha=1)
    # plt.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
    # plt.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
    
    # plt.xlim([0, 15.5])
    
    # for bar in _hbars:
    #     bar.set_edgecolor("black")
    #     bar.set_linewidth(0.5)
    
    # for bar, cost in zip(_hbars, _values):
    #     plt.text(bar.get_width() - 0.25, bar.get_y() + bar.get_height()/2, f'{cost:.1f}', 
    #          va='center', ha='right', color='white', fontsize=12)
    
    # plt.xlabel("Supply cost in Europe 2040 [$/MMBtu]", fontsize=12)

    # plt.tight_layout()
    # _fig.savefig(os.path.join(folder, "supply costs europe.pdf"), dpi=1000)

    return _average, _marginal