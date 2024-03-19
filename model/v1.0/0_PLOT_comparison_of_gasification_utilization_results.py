import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import os
from datetime import datetime
import numpy as np
import warnings
warnings.filterwarnings("ignore")

plt.rcParams['hatch.linewidth'] = 1.5

# TODO: y_lim ist die maximale gasification capacity(absolut)
# und einmal nur mit % machen

# It is necessary that the results are generated with the same time stamp (e.g., 20240102_0852_Net Zero)

_TIME = '20240102_0853'
_SCENARIO = 'New Momentum'

_CASES = ['', '+Diversification', '+HighPriceME', '+NoExpAfrica', '+PanCanClosed', '+RussianEmbargo']

_MAX = 7920000000  # gasification capacity of the largest exporter US

# get default gasification capacity dataframe in MMBtu per year
_gas = pd.read_excel('input data/gasification capacity 2040.xlsx')
_exporter = _gas.Exporter

for _exp in _exporter:
    _total = _gas.loc[_gas.Exporter == _exp]['Gasification capacity in MMBtu'].item()
    print('{}: {} MMBtu'.format(_exp, _total / 1000000000))
    _dict = dict()
    _dict['Total'] = _total
    for _c in _CASES:
        _data = pd.read_excel('result/'+_TIME+'_'+_SCENARIO+_c+'/1_primal solution.xlsx')
        _value = _data.loc[(_data.variable == 'LNG|Gasification|Utilization') & (_data.region == _exp)]['value'].item()
        if _c == '':
            _dict[_SCENARIO] = _value * _dict['Total'] / 100
        else:
            _dict[_c] = _value * _dict['Total'] / 100

    _labels = ['Total', _SCENARIO, 'DivImp', 'HighPriceME', 'NoExpAfr', 'PanCanClosed', 'Rus-Asia']
    _values = [_dict[_key] - _dict['Total'] for _key in _dict.keys()]
    _values[0] = _dict['Total']
    _offset = [_dict['Total'] for _key in _dict.keys()]
    _offset[0] = 0

    _new_values = [_dict[_key] for _key in _dict.keys()]
    _new_values[0] = 0

    # create figure
    _fig, _ax = plt.subplots(figsize=(6, 4))
    _bars = plt.bar(_labels, _values, width=0.8, bottom=_offset)

    _bars2 = plt.bar(_labels, _new_values, color='#11235A', zorder=3)

    plt.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=-1)
    plt.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=-1)

    for _index, bar in enumerate(_bars):
        if _index != 0:
            bar.set_color('#C6CF9B')
            # bar.set_edgecolor("black")
            bar.set_linewidth(0)

        if _index == 0:
            bar.set_color('#11235A')
            bar.set_alpha(1)
            bar.set_linewidth(1)
            bar.set_zorder(3)
            bar.set_hatch('//')
            bar.set_edgecolor('#C6CF9B')
            
            
    for _i, _value in enumerate(_new_values):
        if _i == 0:
            _percent = 100
        else:    
            _percent = int(np.around(_value / _dict['Total'] * 100, 1))
        _ax.text(_i, _dict['Total'] * 1.025, str(_percent) + '%', ha='center', color='#11235A')
            
            
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-3, 1))

    _ax.yaxis.set_major_formatter(formatter)

    _ax.set_ylim([0, _values[0]*1.3])

    _ax.set_ylabel("Export volumes [MMBtu]", fontsize=12)
    if _SCENARIO == 'Net Zero':
        _string = 'Net Zero'
    else:
        _string = 'Persisting\nFossil Demand'
    _ax.set_xticklabels(
        labels=['Liquefaction\ncapacity',
                _string,
                'Diversify\nimporters',
                'High price\nMiddle East',
                'No export\nfrom Africa',
                'Panama canal\nrestricted', 'Russia to\nAsia only'], rotation=45)

    _ax.set_title(_exp, fontsize=12)
    
    _patches = []
    _patches.append(mpatches.Patch(color='#11235A', label='Exported'))
    _patches.append(mpatches.Patch(color='#C6CF9B', label='Not exported'))

    _legend = _ax.legend(
        handles=_patches,
        loc="center",
        facecolor="white",
        fontsize=11,
        handlelength=1.5,
        handletextpad=0.5,
        ncol=2,
        borderpad=0.5,
        columnspacing=1,
        edgecolor="black",
        frameon=True,
        bbox_to_anchor=(0.5, 0.925),
        shadow=False,
        framealpha=0,
    )

    _legend.get_frame().set_linewidth(0.5)

    result_dir = os.path.join("result/comparison/"+_TIME+'_'+_SCENARIO)
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    plt.tight_layout()
    _fig.savefig(os.path.join(result_dir, _exp + '.pdf'), dpi=1000)




# # get all possible exporters
# _exporters = list()

# for _k in data.keys():
#     _exporters = _exporters + list(data[_k].region)

# exporters = list(set(_exporters))

# _net_zero = []
# _new_momentum = []

# for _ex in exporters:
#     if _ex in list(data["Net_Zero"].region):
#         _data = data["Net_Zero"]
#         _value = _data.loc[_data.region == _ex].value.item()
#         _net_zero.append(_value)
#     else:
#         _net_zero.append(0)

#     if _ex in list(data["New_Momentum"].region):
#         _data = data["New_Momentum"]
#         _value = _data.loc[_data.region == _ex].value.item()
#         _new_momentum.append(_value)
#     else:
#         _new_momentum.append(0)

# _x = [0, 1]

# for index, ex in enumerate(exporters):
#     _values = [_net_zero[index], _new_momentum[index]]
#     _color = _colors[ex]
#     _ax1.plot(_x, _values, color=_color, marker="d", linewidth=3)

# _ax1.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
# _ax1.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)

# _ax1.set_ylabel("Import volumes from regions [MMBtu]", fontsize=12)

# formatter = ticker.ScalarFormatter(useMathText=True)
# formatter.set_scientific(True)
# formatter.set_powerlimits((-3, 1))

# _ax1.yaxis.set_major_formatter(formatter)

# _patches = []
# for _reg in sorted(exporters, reverse=True, key=len):
#     _patches.append(mpatches.Patch(color=_colors.get(_reg, "black"), label=_reg))

# _legend = _ax1.legend(
#     handles=_patches,
#     loc="upper left",
#     facecolor="white",
#     fontsize=12,
#     handlelength=1,
#     handletextpad=0.5,
#     ncol=1,
#     borderpad=0.5,
#     columnspacing=1,
#     edgecolor="black",
#     frameon=True,
#     bbox_to_anchor=(-0.005, 1 - 0.005),
#     shadow=False,
#     framealpha=0,
# )

# _legend.get_frame().set_linewidth(0.5)

# _ax1.set_xticks([0, 1])
# _ax1.set_xticklabels(labels=["Net", "New"], ha="center")
# _ax1.set_xlim([-0.15, 1.15])
# _aver = []

# _data = pd.read_excel(_names2[0])
# _data = _data.loc[_data.variable == "LNG|Cost|Average"].value.item()
# _aver.append(_data)
# _data = pd.read_excel(_names2[1])
# _data = _data.loc[_data.variable == "LNG|Cost|Average"].value.item()
# _aver.append(_data)

# _marg = []

# _data = pd.read_excel(_names2[0])
# _data = _data.loc[_data.variable == "LNG|Cost|Marginal"].value.item()
# _marg.append(_data)
# _data = pd.read_excel(_names2[1])
# _data = _data.loc[_data.variable == "LNG|Cost|Marginal"].value.item()
# _marg.append(_data)

# _ax2.plot(_x, _aver, color="#BCA37F", marker="d", linewidth=3)
# _ax2.plot(_x, _marg, color="#113946", marker="d", linewidth=3)
# _ax2.set_ylim(0, 15.5)

# _ax2.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
# _ax2.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
# _ax2.set_xticks([0, 1])
# _ax2.set_xticklabels(labels=["Net", "New"], ha="center")
# _ax2.set_xlim([-0.15, 1.15])
# _ax2.set_ylabel("Supply costs in Europe 2040 [$/MMBtu]", fontsize=12)


# _fig.tight_layout()

# _now = datetime.now().strftime("%Y%m%d_%H%M")
# result_dir = os.path.join("result/comparison")
# if not os.path.exists(result_dir):
#     os.makedirs(result_dir)

# _patches = []
# for _c in ["Average", "Marginal"]:
#     if _c == "Average":
#         _color = "#BCA37F"
#     else:
#         _color = "#113946"
#     _patches.append(mpatches.Patch(color=_color, label=_c))

# _legend = _ax2.legend(
#     handles=_patches,
#     loc="lower center",
#     facecolor="white",
#     fontsize=12,
#     handlelength=1,
#     handletextpad=0.5,
#     ncol=1,
#     borderpad=0.5,
#     columnspacing=1,
#     edgecolor="black",
#     frameon=True,
#     bbox_to_anchor=(0.5, 0),
#     shadow=False,
#     framealpha=0,
# )

# _fig.savefig(result_dir + "/"+ _INPUT_NET_ZERO + "+"+ _INPUT_NEW_MOMENTUM + " volumes and costs.pdf", dpi=1000)
