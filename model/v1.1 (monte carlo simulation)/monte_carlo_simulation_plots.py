import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from matplotlib.ticker import FuncFormatter


plt.style.use('seaborn-v0_8-paper')
plt.rcParams["xtick.labelsize"] = 12
plt.rcParams["ytick.labelsize"] = 12
plt.rcParams["hatch.linewidth"] = 0.5
plt.rcParams["axes.axisbelow"]
 
# def percent_formatter(x, pos):
#     return '{:.0f}%'.format(x)



def run_me(data=None, dictionary=None):
    
    n_bins = int(len(data[0])/10)
    
    for _index, _dp in enumerate(data):
        _x0=0.025
        if _index == 0:
            _c='#BCA37F'
            _s = 'Average supply cost in Europe 2040 [$/MMBtu]'
            _o = '1_Average'
            _ha='left'
        elif _index == 1:
            _c = '#113946'
            _s = 'Marginal supply cost in Europe 2040 [$/MMBtu]'
            _o = '2_Marginal'
            _ha='left'
        else:
            _c = '#ED7D31'
            _s = 'Supply share of European domestic production [%]'
            _o = '3_CCS'
            _ha='left'
            _x0=0.025
            
        
        fig, ax = plt.subplots(figsize=(5.5, 4))
        if _index == 2:
            _update = [x * 100 for x in _dp]
            counts, bins, _ = ax.hist(_update, bins=n_bins, zorder=0, density=True, alpha=0.45, color=_c)
            mu, std = norm.fit(_update)
        else:
          counts, bins, _ = ax.hist(_dp, bins=n_bins, zorder=0, density=True, alpha=0.45, color=_c)  
          mu, std = norm.fit(_dp)
            
        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        p = norm.pdf(x, mu, std)
        ax.plot(x, p, linewidth=1.5, color=_c, zorder=2)
        ax.plot(x, p, linewidth=2.5, color='black', zorder=1)
        
        ax.text(
            x=_x0, 
            y=0.935, 
            s=fr'$\mu={mu:.2f}$, $\sigma={std:.2f}$',
            transform=plt.gca().transAxes, 
            ha=_ha, 
            fontsize=12
        )
        
        if _index == 0:
            ax.set_xlim([0, 15])
        elif _index == 1:
            ax.set_xlim([0, 30])
        else:
            ax.set_xlim([0, 35])
            
        ax.set_ylabel('Probability density', fontsize=12)
        ax.set_xlabel(_s, fontsize=12)
        fig.tight_layout()
        fig.savefig(dictionary + "/"+ _o +".pdf", dpi=1000)
    
    return
