import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


# plt.style.use('seaborn-v0_8-paper')
plt.rcParams["xtick.labelsize"] = 12
plt.rcParams["ytick.labelsize"] = 12
plt.rcParams["hatch.linewidth"] = 0.5
plt.rcParams["axes.axisbelow"]


def run_me(data=None, dictionary=None):
    
    _x_axis = list(range(2030, 2041, 1))
    
    for _index, _datapoint in enumerate(data):
        
        fig, ax = plt.subplots(figsize=(5.5, 4))
        
        _nz, _nm = _datapoint[0], _datapoint[1]

        
        if _index == 0:
            _s = 'Average supply cost to Europe [$/MMBtu]'
            _c='#BCA37F'
            _o = '1_Average_Trend'
        else:
           _s = 'Marginal supply cost to Europe [$/MMBtu]'
           _c = '#113946'
           _o = '2_Marginal_Trend'
       
        ax.plot(_x_axis, _nz, label='Net Zero', color=_c, linestyle='solid', lw=2.25, marker='d', markersize=0)
        ax.plot(_x_axis, _nm, label='Persisting Fossil Demand', color=_c, linestyle='dashed', lw=2.25)
        
        ax.grid(which="major", axis="y", color="#B3C8CF", alpha=0.5, zorder=1)
        
        legend = plt.legend()
        handles, labels = plt.gca().get_legend_handles_labels()
        sorted_indices = sorted(range(len(labels)), key=lambda k: labels[k], reverse=True)
        sorted_handles = [handles[i] for i in sorted_indices]
        sorted_labels = [labels[i] for i in sorted_indices]
        legend = plt.legend(sorted_handles, sorted_labels, loc='upper left')
       
        ax.set_ylabel(_s, fontsize=12)
        ax.set_xlabel('Year', fontsize=12)
        minor_locator = MultipleLocator(1)
        ax.xaxis.set_minor_locator(minor_locator)
        ax.set_ylim([4.5, 15.5])
        
        fig.tight_layout()
        fig.savefig(dictionary + "/"+ _o +".pdf", dpi=1000)
       
    return
