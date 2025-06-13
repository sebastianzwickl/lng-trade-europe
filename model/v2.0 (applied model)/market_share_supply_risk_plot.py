import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scienceplots
import os
import matplotlib.ticker as ticker


def get_all_folders(root_directory):
    folders = []
    for dirpath, dirnames, _ in os.walk(root_directory):
        for dirname in dirnames:
            folders.append(os.path.join(dirpath, dirname))
    return folders


plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "serif",
    }
)
plt.style.use(["science", "ieee"])

_fontsize = 12
_factor = 2.2

plt.rcParams["xtick.labelsize"] = _fontsize
plt.rcParams["ytick.labelsize"] = _fontsize

country_abbreviations = {
    "Qatar": "QA",
    "Australia": "AU",
    "USA": "US",
    "Russia": "RU",
    "Malaysia": "MY",
    "Nigeria": "NG",
    "Trinidad & Tobago": "TT",
    "Algeria": "DZ",
    "Indonesia": "ID",
    "Oman": "OM",
    "Other Asia Pacific": "OAP",
    "Other Europe": "OE",
    "Other Americas": "OA",
    "Other ME": "OME",
    "Other Africa": "OAF"
}

country_colors = {
    "QA": "#7886C7",  # Pastel Blue-Violet
    "AU": "#B5A8D5",  # Light Lavender
    "US": "#FFA725",  # Bright Orange
    "OA": "#C1CFA1",  # Sage
    "OAF": "#D2665A",  # Terracotta
    "RU": "#99CCFF",  # Light Sky Blue
    "MY": "#48A6A7",  # Teal
    "NG": "#FF9999",  # Light Coral
    "TT": "#FFB6C1",  # Light Pink
    "DZ": "#FFF599",  # Pale Yellow
    "ID": "#CC99FF",  # Light Purple
    
    
    
    
    "OM": "#0118D8",  # Peach
    "OAP": "#CFCFCF",  # Light Gray
    "OE": "#CCFFCC",  # Light Green
    
    "OME": "#D3CA79",  # Peach
    
    "JP": "#CFCFCF",  # Light Gray
    "CN": "#CFCFCF",  # Light Gray
    "KR": "#CFCFCF",  # Light Gray
    "IN": "#CFCFCF",  # Light Gray
    "TW": "#CFCFCF",  # Light Gray
    "PK": "#CFCFCF",  # Light Gray
    "ES": "#004494",  # Deep Blue
    "TNA": "#CFCFCF",  # Light Gray
    "SCA": "#CFCFCF",  # Light Gray
    "TMEA": "#CFCFCF",  # Light Gray
    "FR": "#004494",  # Deep Blue
    "GB": "#004494",  # Deep Blue
    "IT": "#004494",  # Deep Blue
    "BE": "#004494",  # Deep Blue
    "TR": "#CFCFCF"   # Light Gray
}

def run():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    relative_root_directory = 'result'
    root_directory = os.path.join(script_directory, relative_root_directory)
    all_folders = get_all_folders(root_directory)
    
    
    for folder in all_folders:
        for year in [str(2030), str(2040)]:
            file_path = os.path.join(folder, f'BCM_Flows_Imp_to_Exp_{year}.xlsx')
    
            if os.path.exists(file_path):
                _data = pd.read_excel(file_path)
                _total = 0
                for c in country_abbreviations.keys():
                    # Convert the first column to strings for comparison
                    filtered_data = _data[_data.iloc[:, 0].astype(str) == c]
                    f_new = filtered_data.drop('Unnamed: 0', axis=1)
                    _total += f_new.values.sum()
                
                _countries = []
                _values = []
                _rest_of_exporters = 0
                for c in country_abbreviations.keys():
                    filtered_data = _data[_data.iloc[:, 0].astype(str) == c]
                    f_new = filtered_data.drop('Unnamed: 0', axis=1).values.sum()
                    _share = (f_new / _total) * 100
                    
                    if _share >= 5:
                        _countries.append(country_abbreviations[c])
                        _values.append(_share)
                    else:
                        _rest_of_exporters += _share
                    
                if _rest_of_exporters != 0:
                    _countries.append('FRN')
                    _values.append(_rest_of_exporters)
                
                merged_dict = dict(zip(_countries, _values))
                
                _colors = [country_colors.get(_c, '#F6DC43') for _c in _countries]
                
                fig, ax = plt.subplots(figsize=(_factor * 1.5, _factor * 1.5))
                explode = len(_values) * [0.025]
                ax.pie(
                    _values,
                    labels=_countries,
                    autopct='{:.1f}\%'.format,  # also corrected: \% -> %
                    colors=_colors,
                    startangle=140,
                    explode=explode,
                    textprops=dict(fontsize=11, va='center', ha='center')  # fixed dict syntax and removed quotes around number
                    )
                
                ax.axis('equal')
                plt.tight_layout()
                fig.savefig(folder + "/PLOT_Market_Shares_"+ year+".pdf", dpi=1000)
                plt.close()
                
                
        # EXPORTER'S SPECIFIC SUPPLY CHAIN EMISSION PLOT        
        
        file_path = os.path.join(folder, 'Exporters_Overview_Quantity.xlsx')
        if os.path.exists(file_path):
            _data = pd.read_excel(file_path)
        
            fig, ax = plt.subplots(figsize=(_factor * 3, _factor * 1.5), nrows=1, ncols=2, gridspec_kw={'width_ratios':[5,1], 'height_ratios':[1]})
            
            years = list(_data.Year[0:16])
            years.insert(0, 2029)
            
            for c in country_abbreviations:
                _values_by_2045 = list(_data['Specific emissions|'+c][0:16]*1000*53)
                _values_by_2045.insert(0, _data['Initial specific emissions|'+c][0]*1000*53)
                
                _values_reduced = sum(list(_data['Specific emission reduction|'+c][0:11]))
                
                if _values_reduced == 0:
                    _lw=1.
                    _ls='dashed'
                else:
                    _lw=2
                    _ls = 'solid'
                
                ax[0].plot(years, _values_by_2045, label=country_abbreviations[c], 
                           color=country_colors.get(country_abbreviations[c], 'black'),
                           ls=_ls,
                           lw=_lw)
            
            handles, labels = ax[0].get_legend_handles_labels()
            
            # Add legend to ax[1]
            _leg = ax[1].legend(
                handles, labels,
                loc="center",
                facecolor="white",
                fontsize=12,
                handlelength=1.25,
                handletextpad=0.5,
                ncol=2,
                borderpad=0.35,
                columnspacing=0.75,
                edgecolor="black",
                frameon=True,
                bbox_to_anchor=(0.5, 0.5),
                shadow=False,
                framealpha=1,
                title='Exporters',
                title_fontsize=12
            )
            
            ax[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
            
            ax[0].set_ylabel('Emissions (gCO2/kgLNG)', fontsize=_fontsize)
            ax[0].set_xlim([2029, 2041])
            ax[0].set_xticks([2030, 2035, 2040])           # Set the positions
            ax[0].set_xticklabels([2030, 2035, 2040])      # Set the labels
    
    
            ax[1].axis('off')  # Hide grid/axis lines if you want only the legend
            
            _leg.get_frame().set_linewidth(0.5)
            
            plt.tight_layout()
            fig.savefig(folder + "/PLOT_Supply_Chain_Emissions.pdf", dpi=1000)
            
        # EU IMPORTER'S SUPPLY RISK
        file_path = os.path.join(folder, 'EU_Importers_Supply_Risks.xlsx')
        if os.path.exists(file_path):
            _data = pd.read_excel(file_path)
            fig, ax = plt.subplots(figsize=(_factor * 2, _factor * 1.5))
            _x_values = _data.Year
            _y_values = [sum(list(row.values)[1:]) for index, row in _data.iterrows()]
            _y_values = [_val + (1-_y_values[0]) for _val in _y_values]
            
            ax.plot(_x_values, _y_values, ls='dotted', marker='d')
            ax.set_xlim([2030, 2041])
            ax.set_xticks([2030, 2035, 2040])           # Set the positions
            ax.set_xticklabels([2030, 2035, 2040])      # Set the labels
            
            val = ax.get_ylim()
            ax.set_ylim([0, val[1]])
            
            ax.set_ylabel('Supply risk', fontsize=_fontsize)
            plt.tight_layout()
            fig.savefig(folder + "/PLOT_Supply_Risk.pdf", dpi=1000)
        
        
    
    
        # CBAM REVENUES - EMISSION REDUCTION (UNTIL 2040)
        file_path = os.path.join(folder, 'Exporters_CBAM_Emissions.xlsx')
        if os.path.exists(file_path):
            _data = pd.read_excel(file_path)
            
            fig, ax = plt.subplots(figsize=(_factor * 2, _factor * 1.5))
            
            for index, row in _data.iterrows():
                country = row.Exporters
                label = country_abbreviations[country]
                x_val = row['CBAM revenues (by 2040)']
                y_val = (row['Emissions 2030 (in tCO2/MMBtu)'] - row['Emissions 2040 (in tCO2/MMBtu)']) * 1_000 * 53
                color = country_colors.get(label, 'black')
                
                ax.scatter(x_val, y_val, color=color, alpha=.75, label=label, lw=.5, edgecolors='black')
            
            # Remove duplicate labels in legend
            handles, labels = ax.get_legend_handles_labels()
            unique = dict(zip(labels, handles))
            _leg = ax.legend(
                unique.values(),
                unique.keys(),
                loc="upper right",
                facecolor="white",
                fontsize=12,
                handlelength=1.25,
                handletextpad=0.5,
                ncol=2,
                borderpad=0.35,
                columnspacing=0.75,
                edgecolor="black",
                frameon=True,
                bbox_to_anchor=(1, 1),
                shadow=False,
                framealpha=1,
                title='Exporters',
                title_fontsize=12
            )
            
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
            ax.set_ylabel('Emission reduction (gCO2/kgLNG)', fontsize=_fontsize)
            ax.set_xlabel('CBAM revenues (million \$)', fontsize=_fontsize)
            
            _leg.get_frame().set_linewidth(0.5)
            
            plt.tight_layout()
            fig.savefig(os.path.join(folder, "PLOT_CBAM_Emissions.pdf"), dpi=1000)
            plt.close()
        
        
        
        
        # EU LNG IMPORTS BY 2040
        file_path = os.path.join(folder, 'EU_Importers_Supply_Details_bcm.xlsx')
        if os.path.exists(file_path):
            _data = pd.read_excel(file_path)
            
            fig, ax = plt.subplots(figsize=(_factor * 3*0.85, _factor * 1.5*0.85))

            pattern = '|'.join(list(country_abbreviations.keys()))
            filtered = _data.filter(regex=rf'^Q\|.*\|({pattern})$').copy()
            filtered['Year'] = _data['Year']
            
            # Melt to long format
            long_df = filtered.melt(id_vars='Year', var_name='Flow', value_name='Volume')
            
            # Extract exporter name
            long_df['Exporter'] = long_df['Flow'].str.extract(r'\|(.*?)$')
            
            # Group by Year and Exporter
            grouped = long_df.groupby(['Year', 'Exporter'])['Volume'].sum().unstack().fillna(0)
            
            result = pd.DataFrame({'Year': _data['Year']})
            
            for exporter in list(country_abbreviations.keys()):
                exporter_cols = _data.filter(regex=rf'\|{exporter}$')
                nonzero_cols = exporter_cols.loc[:, (exporter_cols != 0).any()]
                result[exporter] = nonzero_cols.sum(axis=1)


            result = result.loc[:, (result != 0).any()]
            
            result.rename(columns={k: v for k, v in country_abbreviations.items() if k in result.columns}, inplace=True)

            result.set_index('Year').plot.area(ax=ax, alpha=0.8, lw=0.0001,
                                               color=[country_colors[col] for col in result.columns if col != 'Year'])
                
            ax.set_ylabel('EC import volumes (bcm)', fontsize=_fontsize)
            ax.set_xlabel('')
            _leg = ax.legend(loc='upper right', bbox_to_anchor=(1, 1), ncol=5,
                      facecolor="white",
                      fontsize=12,
                      handlelength=1.25,
                      handletextpad=0.5,
                      borderpad=0.35,
                      columnspacing=0.75,
                      edgecolor="black",
                      frameon=True,
                      shadow=False,
                      framealpha=1,
                      title_fontsize=11)
            _leg.get_frame().set_linewidth(0.5)
            
            ax.set_xlim([2030, 2040])
            ax.set_xticks([2030, 2035, 2040])           # Set the positions
            ax.set_xticklabels([2030, 2035, 2040], fontsize=_fontsize)      # Set the labels

            plt.tight_layout()
            fig.savefig(os.path.join(folder, "PLOT_EU_Imports_Cumulative.pdf"), dpi=1000)
            plt.close()
            
            
        
        
                
                
                
        
            

        

        

        
    
    

    
    
    



