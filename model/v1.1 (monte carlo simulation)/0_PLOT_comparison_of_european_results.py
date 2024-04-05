import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import os
from datetime import datetime

########
#######
######
#####
####
###
##
#
_INPUT_NET_ZERO = '20240102_0852'
_INPUT_NEW_MOMENTUM = '20240102_0853'
#
##
###
####
#####
######
#######
########


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

_names1 = "result/"+_INPUT_NET_ZERO+"_Net Zero/"+"3_european supply.xlsx"
_names2 = "result/"+_INPUT_NEW_MOMENTUM+"_New Momentum/"+"3_european supply.xlsx"
_names = [_names1,_names2]


_names2 = [
    "result/"+_INPUT_NET_ZERO+"_Net Zero/"+"3_european costs.xlsx",
    "result/"+_INPUT_NEW_MOMENTUM+"_New Momentum/"+"3_european costs.xlsx",
]

data = dict()

for _name in _names:
    if "Net Zero" in _name:
        _key = "Net_Zero"
    else:
        _key = "New_Momentum"

    data[_key] = pd.read_excel(_name)

_fig, (_ax1, _ax2) = plt.subplots(
    nrows=1, ncols=2, gridspec_kw={"width_ratios": [2 / 3, 1 / 3]}
)

# get all possible exporters
_exporters = list()

for _k in data.keys():
    _exporters = _exporters + list(data[_k].region)

exporters = list(set(_exporters))

_net_zero = []
_new_momentum = []

for _ex in exporters:
    if _ex in list(data["Net_Zero"].region):
        _data = data["Net_Zero"]
        _value = _data.loc[_data.region == _ex].value.item()
        _net_zero.append(_value)
    else:
        _net_zero.append(0)

    if _ex in list(data["New_Momentum"].region):
        _data = data["New_Momentum"]
        _value = _data.loc[_data.region == _ex].value.item()
        _new_momentum.append(_value)
    else:
        _new_momentum.append(0)

_x = [0, 1]

for index, ex in enumerate(exporters):
    _values = [_net_zero[index], _new_momentum[index]]
    _color = _colors[ex]
    _ax1.plot(_x, _values, color=_color, marker="d", linewidth=3)

_ax1.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
_ax1.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)

_ax1.set_ylabel("Import volumes from regions [MMBtu]", fontsize=12)

formatter = ticker.ScalarFormatter(useMathText=True)
formatter.set_scientific(True)
formatter.set_powerlimits((-3, 1))

_ax1.yaxis.set_major_formatter(formatter)

_patches = []
for _reg in sorted(exporters, reverse=True, key=len):
    _patches.append(mpatches.Patch(color=_colors.get(_reg, "black"), label=_reg))

_legend = _ax1.legend(
    handles=_patches,
    loc="upper left",
    facecolor="white",
    fontsize=10,
    handlelength=1,
    handletextpad=0.5,
    ncol=1,
    borderpad=0.5,
    columnspacing=1,
    edgecolor="black",
    frameon=True,
    bbox_to_anchor=(-0.005, 1.015),
    shadow=False,
    framealpha=0,
)

_legend.get_frame().set_linewidth(0.5)

_ax1.set_xticks([0, 1])
_ax1.set_xticklabels(labels=["Zero", "Persisting"], ha="center")
_ax1.set_xlim([-0.15, 1.15])
_aver = []

_data = pd.read_excel(_names2[0])
_data = _data.loc[_data.variable == "LNG|Cost|Average"].value.item()
_aver.append(_data)
_data = pd.read_excel(_names2[1])
_data = _data.loc[_data.variable == "LNG|Cost|Average"].value.item()
_aver.append(_data)

_marg = []

_data = pd.read_excel(_names2[0])
_data = _data.loc[_data.variable == "LNG|Cost|Marginal"].value.item()
_marg.append(_data)
_data = pd.read_excel(_names2[1])
_data = _data.loc[_data.variable == "LNG|Cost|Marginal"].value.item()
_marg.append(_data)

_ax2.plot(_x, _aver, color="#BCA37F", marker="d", linewidth=3)
_ax2.plot(_x, _marg, color="#113946", marker="d", linewidth=3)
_ax2.set_ylim(0, 15.5)

_ax2.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
_ax2.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
_ax2.set_xticks([0, 1])
_ax2.set_xticklabels(labels=["Zero", "Persisting"], ha="center")
_ax2.set_xlim([-0.15, 1.15])
_ax2.set_ylabel("Supply cost in Europe 2040 [$/MMBtu]", fontsize=12)


_fig.tight_layout()

_now = datetime.now().strftime("%Y%m%d_%H%M")
result_dir = os.path.join("result/comparison")
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

_patches = []
for _c in ["Average", "Marginal"]:
    if _c == "Average":
        _color = "#BCA37F"
    else:
        _color = "#113946"
    _patches.append(mpatches.Patch(color=_color, label=_c))

_legend = _ax2.legend(
    handles=_patches,
    loc="lower center",
    facecolor="white",
    fontsize=10,
    handlelength=1,
    handletextpad=0.5,
    ncol=1,
    borderpad=0.5,
    columnspacing=1,
    edgecolor="black",
    frameon=True,
    bbox_to_anchor=(0.5, -0.025),
    shadow=False,
    framealpha=0,
)

_fig.savefig(result_dir + "/"+ _INPUT_NET_ZERO + "+"+ _INPUT_NEW_MOMENTUM + " volumes and costs.pdf", dpi=1000)
