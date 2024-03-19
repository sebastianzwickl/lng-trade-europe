import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import os
from datetime import datetime
import numpy as np
import warnings
from matplotlib.lines import Line2D

warnings.filterwarnings("ignore")

plt.rcParams["hatch.linewidth"] = 1.5

data = pd.read_excel("marginal and average costs.xlsx")

_color_average = "#BCA37F"
_color_marginal = "#113946"

# create figure
_fig, _ax = plt.subplots(figsize=(6, 4))
_x_values = list(range(0, 6, 1))

# AVERAGE
_average_net = data.loc[(data.Szenario == "Net Zero")]["Average"].values
_average_per = data.loc[(data.Szenario == "Persisting")]["Average"].values

L_NET_AV = _ax.plot(_x_values, _average_net, color=_color_average, linestyle="solid", marker='d', markersize='4', label='Net Zero')
L_NET_AV[0].set_label('Net Zero')
L_PER_AV = _ax.plot(
    _x_values, _average_per, color=_color_average, linestyle="dotted", linewidth=2, marker='d', markersize='4', label='Persisting Fossil Demand'
)
L_PER_AV[0].set_label('Persisting Fossil Demand')

_ax.fill_between(_x_values, _average_per, _average_net, color=_color_average, alpha=0.25)

plt.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=-1)
plt.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=-1)

for _x_val, _val in enumerate(_average_net):
    _ax.text(_x_val, _val - 0.1 * _ax.get_ylim()[1], s= str(_val), ha='center', color=_color_average, fontsize=10)

for _x_val, _val in enumerate(_average_per):
    _ax.text(_x_val, _val + 0.05 * _ax.get_ylim()[1], s= str(_val), ha='center', color=_color_average, fontsize=10)

_ax.set_ylim([0, 17])


_ax.set_xticklabels(
    labels=[
        "",
        "Main\nscenario",
        "Diversify\nimporters",
        "High price\nMiddle East",
        "No export\nfrom Africa",
        "Panama canal\nrestricted",
        "Russia to\nAsia only",
    ],
    rotation=45,
)

_ax.set_ylabel("Average supply cost [$/MMBtu]", fontsize=12, y=0.45, ha='center')
# _ax.text(x=0.975, y=0.925, s='Europe 2040', ha='right', transform=_ax.transAxes)
lines = [L_NET_AV[0], L_PER_AV[0]]
line_handles = [l for l in lines]
line_labels = [l.get_label() for l in lines]

_legend = _ax.legend(
    handles=line_handles,
    labels=line_labels,
    loc="lower right",
    facecolor="white",
    fontsize=12,
    handlelength=1.5,
    handletextpad=0.5,
    ncol=2,
    borderpad=0.5,
    columnspacing=1,
    edgecolor="black",
    frameon=True,
    bbox_to_anchor=(1, 0),
    shadow=False,
    framealpha=0,
)

_legend.get_frame().set_linewidth(0.5)

_now = datetime.now().strftime("%Y%m%d_%H")

result_dir = os.path.join("results")
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

plt.tight_layout()
_fig.savefig(os.path.join(result_dir, "Average" + _now + "_.pdf"), dpi=1000)
#
#
#
#
#
#
#
#
# create figure
_fig, _ax = plt.subplots(figsize=(6, 4))
_x_values = list(range(0, 6, 1))

# AVERAGE
_average_net = data.loc[(data.Szenario == "Net Zero")]["Marginal"].values
_average_per = data.loc[(data.Szenario == "Persisting")]["Marginal"].values

L_NET_AV = _ax.plot(_x_values, _average_net, color=_color_marginal, linestyle="solid", marker='d', markersize='4', label='Net Zero')
L_NET_AV[0].set_label('Net Zero')
L_PER_AV = _ax.plot(
    _x_values, _average_per, color=_color_marginal, linestyle="dotted", linewidth=2, marker='d', markersize='4', label='Persisting Fossil Demand'
)
L_PER_AV[0].set_label('Persisting Fossil Demand')

_ax.fill_between(_x_values, _average_per, _average_net, color=_color_marginal, alpha=0.25)

plt.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=-1)
plt.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=-1)

for _x_val, _val in enumerate(_average_net):
    _ax.text(_x_val, _val - 0.1 * _ax.get_ylim()[1], s= str(_val), ha='center', color=_color_marginal, fontsize=10)

for _x_val, _val in enumerate(_average_per):
    _ax.text(_x_val, _val + 0.05 * _ax.get_ylim()[1], s= str(_val), ha='center', color=_color_marginal, fontsize=10)

_ax.set_ylim([0, 17])


_ax.set_xticklabels(
    labels=[
        "",
        "Main\nscenario",
        "Diversify\nimporters",
        "High price\nMiddle East",
        "No export\nfrom Africa",
        "Panama canal\nconstricted",
        "Russia to\nAsia only",
    ],
    rotation=45,
)

_ax.set_ylabel("Marginal supply cost [$/MMBtu]", fontsize=12, y=0.45, ha='center')

lines = [L_NET_AV[0], L_PER_AV[0]]
line_handles = [l for l in lines]
line_labels = [l.get_label() for l in lines]

_legend = _ax.legend(
    handles=line_handles,
    labels=line_labels,
    loc="lower right",
    facecolor="white",
    fontsize=12,
    handlelength=1.5,
    handletextpad=0.5,
    ncol=2,
    borderpad=0.5,
    columnspacing=1,
    edgecolor="black",
    frameon=True,
    bbox_to_anchor=(1, 0),
    shadow=False,
    framealpha=0,
)

_legend.get_frame().set_linewidth(0.5)

_now = datetime.now().strftime("%Y%m%d_%H")

result_dir = os.path.join("results")
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

plt.tight_layout()
_fig.savefig(os.path.join(result_dir, "Marginal" + _now + "_.pdf"), dpi=1000)








# # NET ZERO

# _marginal_net = data.loc[(data.Szenario == "Net Zero")]["Marginal"].values

# L_NET_MG = _ax.plot(_x_values, _marginal_net, linestyle="solid", color=_color_marginal, marker='d', markersize='4')

# # PERSISTING

# _marginal_per = data.loc[(data.Szenario == "Persisting")]["Marginal"].values

# L_PER_MG = _ax.plot(
#     _x_values, _marginal_per, linestyle="dotted", linewidth=2, color=_color_marginal, marker='d', markersize='4'
# )



# # PERSISTING values below
# for _x_val, _val in enumerate(_average_per):
#     _ax.text(_x_val, _val + 0.05 * _ax.get_ylim()[1], s= str(_val), ha='center', color=_color_average, fontsize=10)
# for _x_val, _val in enumerate(_marginal_per):
#     _ax.text(_x_val, _val + 0.05 * _ax.get_ylim()[1], s= str(_val), ha='center', color=_color_marginal, fontsize=10)



# Legende machen









