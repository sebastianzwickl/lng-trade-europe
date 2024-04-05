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

# TODO: Add something here.

_color_dark = '#6C5F5B'
_color_bride = '#ED7D31'

# It is necessary that the results are generated with the same time stamp (e.g., 20240102_0852_Net Zero)

_TIME = '20240102_0853'
_SCENARIO = 'New Momentum'

_CASES = ['', '+Diversification', '+HighPriceME', '+NoExpAfrica', '+PanCanClosed', '+RussianEmbargo']

_demand = pd.read_excel('input data/LNG demand between 2019 and 2040.xlsx')
_importers_europe = ["France", "Spain", "Belgium", "UK", "Italy"]

_column = 'Import 2040 (' + _SCENARIO + ') [MMBtu]' 
total_european_lng_demand = np.around(sum(_demand.loc[_demand.Country.isin(_importers_europe)][_column]), 1)

EDP_CCS_COSTS = 12.28 + 2.52 # CCS + Production Cost
EDP = 2.52
CCS = 12.28

_total = pd.read_excel('result/'+_TIME+'_'+_SCENARIO+'/0_input.xlsx')
_total = _total.loc[_total.variable == 'EDP|Maximum']['value'].item()
_dict = dict()
_dict['Total demand'] = total_european_lng_demand
_dict['Max. Production'] = _total

for _c in _CASES:
    _data = pd.read_excel('result/'+_TIME+'_'+_SCENARIO+_c+'/1_primal solution.xlsx')
    _value = _data.loc[(_data.variable == 'LNG|Cost|EDP') & (_data.region == 'Europe')]['value'].item()
    if _c == '':
        _dict[_SCENARIO] = _value / EDP
    else:
        _dict[_c] = _value / EDP


_labels = ['Total demand', 'Max. Production', _SCENARIO, 'DivImp', 'HighPriceME', 'NoExpAfr', 'PanCanClosed', 'Rus-Asia']
_values = [_dict[_key] for _key in _dict.keys()]


# create figure
_fig, _ax = plt.subplots(figsize=(6, 4))
_bars = plt.bar(_labels, _values, width=0.8, zorder=2)

_new_values = [_dict[_key] - _dict['Max. Production'] for _key in _dict.keys()]
_offset = [_dict['Max. Production'] for _key in _dict.keys()]
_offset[0] = 0
_new_values[0] = 0
# _bars2 = plt.bar(_labels, _new_values, color='#11235A', zorder=3, bottom=_offset)

plt.grid(which="major", axis="both", color="#758D99", alpha=0.2, zorder=-2)
plt.grid(which="minor", axis="both", color="#758D99", alpha=0.2, zorder=-1)

for _index, bar in enumerate(_bars):
    if (_index != 0) and (_index != 1):
        bar.set_color(_color_bride)
        bar.set_linewidth(1)
        bar.set_edgecolor(_color_dark)

    if _index == 0:
        bar.set_color(_color_dark)
        # bar.set_alpha(0.65)
        bar.set_linewidth(0)
    
    if _index == 1:
        bar.set_color(_color_dark)
        # bar.set_alpha(0.75)
        bar.set_linewidth(0.1)
        bar.set_zorder(3)
        bar.set_hatch('//')
        bar.set_edgecolor(_color_bride)
            
    if _SCENARIO == 'Net Zero':
        _ax.set_ylim([0, 1.1*_dict['Total demand']])
        _scale = 0.025
    else:
        _scale = 0.075
    
    
    
    for _i, _value in enumerate(_values):
        if _i != 0:       
            _percent = int(np.around(_value / _dict['Total demand'] * 100, 1))
            _ax.text(_i, _value + _dict['Max. Production'] * _scale, str(_percent) + '%', ha='center', color='#092635')
            
            
formatter = ticker.ScalarFormatter(useMathText=True)
formatter.set_scientific(True)
formatter.set_powerlimits((-3, 1))

_ax.yaxis.set_major_formatter(formatter)

_ax.set_ylabel("European domestic production\n(incl. CCS) [MMBtu]", fontsize=12)
if _SCENARIO == 'Net Zero':
    _string = 'Net Zero'
else:
    _string = 'New\nMomentum'
_ax.set_xticklabels(
    labels=['Total\ndemand',
            'Production\ncapacity',
            _string,
            'Diversify\nimporters',
            'High price\nMiddle East',
            'No export\nfrom Africa',
            'Panama canal\nrestricted', 'Russia to\nAsia only'], rotation=45)

result_dir = os.path.join("result/comparison/"+_TIME+'_'+_SCENARIO)
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

plt.tight_layout()
_fig.savefig(os.path.join(result_dir, 'Europe.pdf'), dpi=1000)
