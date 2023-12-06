import pyam as py
import matplotlib.pyplot as plt
import os
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import pandas as pd


_colors = {
    'Algeria': "#FFEAD2",
    'Qatar': "#DBDFEA",
    'Nigeria': "#ACB1D6",
    'Other Europe': "#FF90BC",
    'Other Africa': '#EE7214',
    'Trinidad & Tobago': '#F7B787',
    'USA': '#527853',
    'Other Americas': '#9BB8CD'
    }


def run(model, folder):
    plt.style.use("default")
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12

    # for Europe
    fig, ax = plt.subplots()

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

    ax.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=1)
    ax.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=1)
    _bars = ax.bar(_x_pos, height=_prices, width=_quantities, fill=True, color=[_colors.get(_reg, 'black') for _reg in _regions], zorder=2, alpha=1)
    for bar in _bars:
        bar.set_edgecolor("black")
        bar.set_linewidth(0.5)

    plt.xlim(0, _cumulated)
    plt.ylim(0, 20)

    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-3, 1))

    ax.xaxis.set_major_formatter(formatter)

    _patches = []
    for _reg in _regions:
        _patches.append(mpatches.Patch(color=_colors.get(_reg, 'black'), label=_reg))

    _legend = ax.legend(handles=_patches, loc='upper left', facecolor='white', fontsize=12,
                        handlelength=1.5,
                        handletextpad=0.5, ncol=1, borderpad=0.5, columnspacing=1, edgecolor="black", frameon=True,
                        bbox_to_anchor=(0.015, 1-0.015),
                        shadow=False,
                        framealpha=1
                        )

    _legend.get_frame().set_linewidth(0.5)

    ax.set_xlabel("Import volumes from regions [MMBtu]", fontsize=12)
    ax.set_ylabel("Supply cost [$/MMBtu]", fontsize=12)

    plt.title("LNG supply in Europe 2040 and associated supply cost", fontsize=14)
    plt.tight_layout()
    fig.savefig(os.path.join(folder, "import volumes europe.pdf"), dpi=1000)

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

    _df.to_excel(os.path.join(folder, 'european values.xlsx'), index=False)

    return


def plot_results(res_dir):

    # Plot Day-Ahead, Future (Base) and CO2 Price

    fig, ax = plt.subplots()
    df = py.IamDataFrame("IAMC_inputs.xlsx")
    df.plot(
        color="variable",
        title="Electricity prices in EUR/MWh, $CO_2$ price in EUR/t",
        marker="d",
        markersize=5,
        ax=ax,
    )
    plt.xlabel("Time in h")
    plt.ylabel("")
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    legend = plt.legend(fontsize=12)
    legend.get_texts()[0].set_text("$CO_2$")
    legend.get_texts()[1].set_text("Day-Ahead (EPEX)")
    legend.get_texts()[2].set_text("Future contract (EEX)")

    plt.tight_layout()
    fig.savefig(os.path.join(res_dir, "Prices.png"), dpi=500)

    # Plot Results
    fig, ax = plt.subplots()
    df = py.IamDataFrame(os.path.join(res_dir, "IAMC_hourly.xlsx"))
    df.plot(
        color="variable",
        title="Hydropower plant resource allocation in MWh",
        marker="d",
        markersize=5,
        ax=ax,
        cmap="Dark2",
    )
    plt.xlabel("Time in h")
    plt.ylabel("")
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=12)
    plt.title("Hydropower plant resource allocation in MWh", fontsize=14)
    plt.tight_layout()
    fig.savefig(os.path.join(res_dir, "Ressource allocation.png"), dpi=500)

    # Plot supply/generation
    fig = plt.figure(constrained_layout=False)
    plt.style.use("ggplot")
    gs = fig.add_gridspec(2, 1)
    fig_leader = fig.add_subplot(gs[0, :])
    fig_follower = fig.add_subplot(gs[1, :])

    df = py.IamDataFrame(os.path.join(res_dir, "IAMC_supply.xlsx"))
    data_leader = df.filter(variable=["Future contract", "Day-Ahead"])
    data_leader.plot.stack(
        stack="variable",
        title="Hydropower electricty production",
        total=True,
        ax=fig_leader,
        cmap="Set3",
    )
    fig_leader.set_xlabel("Time in h")
    lines = fig_leader.get_lines()
    lines[0].set_linewidth(2)
    fig_leader.set_title("Hydropower electricty production", fontsize=12)

    data_leader = df.filter(variable=["Conventional"])
    data_leader.plot.stack(
        stack="variable",
        title="Energy demand provision\n(transportation firm)",
        total=True,
        ax=fig_follower,
        cmap="PiYG",
    )
    fig_follower.set_xlabel("Time in h")
    lines = fig_follower.get_lines()
    lines[0].set_linewidth(2)
    fig_follower.set_title(
        "Energy demand provision\n(transportation firm)", fontsize=12
    )

    plt.tight_layout()
    fig.savefig(os.path.join(res_dir, "Energy service provision.png"), dpi=500)
