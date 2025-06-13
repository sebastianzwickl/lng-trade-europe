import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scienceplots


"""
    
"""


plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "serif",
    }
)
plt.style.use(["science", "ieee"])

_fontsize = 14
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


def plot(model, dictionary):
    
    
    # ABSOLUTE QUANTITIES (SEPARATE)
    for year in [2030, 2040]:
        fig, ax = plt.subplots(figsize=(_factor * 2.5, _factor * 1.5))
        _dict = {}
        for exporter in model.set_exporter:
            _key = country_abbreviations.get(exporter)
            # value in bcm per year
            _dict[_key] = sum(model.var_q[exporter, importer, year]()
                                  for importer in model.set_importer) * 1000 / 35315
        _exp = list(_dict.keys())
        _quantities = list(_dict.values())
        
        ax.bar(_exp, _quantities, color='#0B192C', zorder=3)
        x_positions = np.arange(len(_exp))  # Define x positions
        ax.set_xticks(x_positions)  # Ensure fixed tick positions
        ax.set_xticklabels(_exp, rotation=45)  # Set labels
        ax.set_xlabel('Region', fontsize=_fontsize)
        ax.set_ylabel('Export volume (in bcm)', fontsize=_fontsize)
        ax.set_ylim([0, 250])
        plt.tight_layout()
        fig.savefig(dictionary + "/1_Exporters_quantity_"+ str(year)+".pdf", dpi=1000)
    
    # RELATIVE UTILISATION (SEPARATE)
    for year in [2030, 2040]:
        fig, ax = plt.subplots(figsize=(_factor * 3, _factor * 1.5))
        _dict = {}
        for exporter in model.set_exporter:
            _key = country_abbreviations.get(exporter)
            # value in bcm per year
            _dict[_key] = sum(model.var_q[exporter, importer, year]()
                                  for importer in model.set_importer) / model.par_liquification[exporter, year] * 100
        _exp = list(_dict.keys())
        _quantities = list(_dict.values())
        ax.bar(_exp, _quantities, color='#1E3E62', zorder=3)
        x_positions = np.arange(len(_exp))  # Define x positions
        ax.set_xticks(x_positions)  # Ensure fixed tick positions
        ax.set_xticklabels(_exp, rotation=45)  # Set labels
        ax.set_xlabel('Region', fontsize=_fontsize)
        ax.set_ylabel('Utilisation (in \%)', fontsize=_fontsize)
        plt.tight_layout()
        fig.savefig(dictionary + "/2_Exporters_utilisation_"+ str(year)+".pdf", dpi=1000)
      
###############################################################################
    
    exporters = list(model.set_exporter)
    importers = list(model.set_importer)
    all_countries = list(set(exporters + importers))  # Unique country list
    
    for year in [2030, 2040, 2050]: 
        size = len(all_countries)
        matrix = np.zeros((size, size))
        
        for exporter in exporters:
            for importer in importers:
                try:
                    flow_value = model.var_q[exporter, importer, year]()
                except:
                    flow_value = 0
                if flow_value > 0:
                    exp_idx = all_countries.index(exporter)
                    imp_idx = all_countries.index(importer)
                    matrix[exp_idx, imp_idx] = flow_value * 1000 / 35315
        
        df = pd.DataFrame(matrix, index=all_countries, columns=all_countries)
        df.to_excel(dictionary + '/BCM_Flows_Imp_to_Exp_' + str(year) + '.xlsx')


    # ABSOLUTE QUANTITIES (GROUPED)
    years = [2030, 2040]
    bar_width = 0.4
    _dicts = {}
    
    for year in years:
        _dict = {}
        for exporter in model.set_exporter:
            _key = country_abbreviations.get(exporter)
            _dict[_key] = sum(model.var_q[exporter, importer, year]() 
                              for importer in model.set_importer) * 1000 / 35315
        _dicts[year] = _dict
    
    _exporters = list(_dicts[2030].keys())
    x = np.arange(len(_exporters))
    
    fig, ax = plt.subplots(figsize=(_factor * 3, _factor * 1.5))
    
    
    for i, year in enumerate(years):
        if year == 2040:
            ax.bar(x + i * bar_width, _dicts[year].values(), bar_width, label=str(year), zorder=2, color='#0B192C', 
                   hatch='///', alpha=0.5, edgecolor='white', lw=0.25)
        else:
            ax.bar(x + i * bar_width, _dicts[year].values(), bar_width, label=str(year), zorder=2, 
                   color='#0B192C', lw=0.25, edgecolor='white')
            
            
    ax.set_xticks(x + bar_width / 2)
    ax.set_xticklabels(_exporters, rotation=45)
    ax.set_xlabel('Region', fontsize=_fontsize)
    ax.set_ylabel('Export volume (in bcm)', fontsize=_fontsize)
    ax.legend(title="Year")
    
    _legend = ax.legend(
        loc="upper right",
        facecolor="white",
        fontsize=12,
        handlelength=1.5,
        handletextpad=0.5,
        ncol=3,
        borderpad=0.35,
        columnspacing=0.75,
        edgecolor="black",
        frameon=True,
        bbox_to_anchor=(1, 1),
        shadow=False,
        framealpha=1,
        title='Year',
        title_fontsize=12
    )
    
    _legend.get_frame().set_linewidth(0.25)
    
    ax.grid(axis="y", linestyle="--", alpha=0.7, zorder=-2)
    
    plt.tight_layout()
    fig.savefig(dictionary + "/3_Exporter_quantity_2030+40.pdf", dpi=1000)
    
###############################################################################

    data = {'Year': model.set_years}

    # Collect data in the dictionary before creating the DataFrame
    for importer in model.set_importer_eu:
        data[f'Demand|{importer}'] = [
            model.par_importer_demand[importer, year] * 1000 / 35315 
            for year in model.set_years
        ]
        
        for exporter in model.set_exporter:
            if sum(model.var_q[exporter, importer, y]() for y in model.set_years) != 0:
                data[f'Q|{importer}|{exporter}'] = [
                    model.var_q[exporter, importer, year]() * 1000 / 35315 
                    for year in model.set_years
                ]
        
        if importer in model.set_importer_eu:
            if sum(model.var_q_edp[importer, year]() for year in model.set_years) != 0:
                data[f'Q|{importer}|Domestic'] = [
                    model.var_q_edp[importer, year]() * 1000 / 35315 
                    for year in model.set_years
                ]

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(data)

    # Write to Excel
    df.to_excel(dictionary + '/EU_Importers_Supply_Details_bcm.xlsx', index=False)
    
    
    data = {'Year': model.set_years}

    # Collect data in the dictionary before creating the DataFrame
    for importer in model.set_importer:
        data[f'Demand|{importer}'] = [
            model.par_importer_demand[importer, year] * 1000 / 35315 
            for year in model.set_years
        ]
        
        for exporter in model.set_exporter:
            if sum(model.var_q[exporter, importer, y]() for y in model.set_years) != 0:
                data[f'Q|{importer}|{exporter}'] = [
                    model.var_q[exporter, importer, year]() * 1000 / 35315 
                    for year in model.set_years
                ]
        
        if importer in model.set_importer_eu:
            if sum(model.var_q_edp[importer, year]() for year in model.set_years) != 0:
                data[f'Q|{importer}|Domestic'] = [
                    model.var_q_edp[importer, year]() * 1000 / 35315 
                    for year in model.set_years
                ]

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(data)

    # Write to Excel
    df.to_excel(dictionary + '/All_Importers_Supply_Details_bcm.xlsx', index=False)

    
###############################################################################

    # Initialize dictionary for all data
    data_dict = {'Year': model.set_years}

    for exporter in model.set_exporter:
        # Total export volume (converted)
        data_dict[f'Total|{exporter} (in bcm)'] = [
            sum(model.var_q[exporter, importer, year]() * 1000 / 35315
                for importer in model.set_importer)
            for year in model.set_years
        ]

        # Specific emissions
        data_dict[f'Specific emissions|{exporter}'] = [
            model.var_rho[exporter, year]() for year in model.set_years
        ]

        # Initial specific emissions (constant across years)
        data_dict[f'Initial specific emissions|{exporter}'] = [
            model.par_rho[exporter] for _ in model.set_years
        ]

        # Specific emission reduction
        data_dict[f'Specific emission reduction|{exporter}'] = [
            model.var_rho_plus[exporter, year]() for year in model.set_years
        ]

        # Flows to EU importers
        for importer in model.set_importer_eu:
            q_values = [model.var_q[exporter, importer, year]() for year in model.set_years]
            if sum(q_values) != 0:
                data_dict[f'q |{exporter}|{importer}'] = q_values

            psi_values = [model.var_psi[exporter, importer, year]() for year in model.set_years]
            if sum(psi_values) != 0:
                data_dict[f'q x rho |{exporter}|{importer}'] = psi_values

    # Create DataFrame in one go
    _df = pd.DataFrame(data_dict)
    _df.to_excel(dictionary + '/Exporters_Overview_Quantity.xlsx', index=False)

    
###############################################################################

    """
        SUPPLY CONCENTRATION OF EUROPEAN LNG IMPORTERS OVER TIME
    """

    # Create a dictionary to hold all columns
    data_dict = {'Year': model.set_years}

    # Add individual importer concentration values
    for importer in model.set_importer_eu:
        _str = 'c|' + importer
        _values = [model.var_c[importer, year]() for year in model.set_years]
        data_dict[_str] = _values

    # Add EU average concentration
    data_dict['EU+'] = [
        np.mean([model.var_c[imp, year]() for imp in model.set_importer_eu])
        for year in model.set_years
    ]

    # Build the DataFrame in one step
    _df = pd.DataFrame(data_dict)
    _df.to_excel(dictionary + '/EU_Importers_Supply_Concentration.xlsx', index=False)

    
###############################################################################
    
    del [data, _str, _df, _values]
    """
        CBAM REVENUES AND DISTRIBUTION OVER TIME
    """
    data = {
        'Year': model.set_years
    }
    _df = pd.DataFrame(data)
    
    # Add CBAM revenues for each importer
    for importer in model.set_importer_eu:
        _str = 'rev|' + importer
        _values = [sum(model.var_r[ex, importer, year]() for ex in model.set_exporter) for year in model.set_years]
        if any(_values):  # Add column only if at least one value is nonzero
            _df[_str] = _values
    
    # Add total CBAM revenue for the EU+
    _str = 'rev|EU+'
    _values = [sum(model.var_r[e, i, y]() for e in model.set_exporter for i in model.set_importer_eu) for y in model.set_years]
    if any(_values):
        _df[_str] = _values
    
    # Add re-revenues, earnings, and spendings for each exporter
    for exporter in model.set_exporter:
        _str = 're-rev|' + exporter
        _values = [model.var_beta[exporter, t]() for t in model.set_years]
        if any(_values):
            _df[_str] = _values
    
        _str = 'earnings|' + exporter
        _values = [model.var_earnings[exporter, t]() for t in model.set_years]
        if any(_values):
            _df[_str] = _values
    
        _str = 'spendings|' + exporter
        _values = [model.var_s[exporter, t]() for t in model.set_years]
        if any(_values):
            _df[_str] = _values
    
    # Export DataFrame to Excel
    _df.to_excel(dictionary + '/EU_Importers_to_Exporters_Cashflows.xlsx', index=False)

###############################################################################

    """
        SUPPLY RISK DATA 1
    """

    # Create a dictionary to hold all columns
    data_dict = {'Year': model.set_years}

    for importer in model.set_importer_eu:
        _str = f'Supply Risk|{importer}'
        _values = [
            sum(model.par_supply_risk[e] / model.par_rho[e] * model.var_psi[e, importer, t]() 
                for e in model.set_exporter)
            for t in model.set_years
        ]
        data_dict[_str] = _values

    # Create DataFrame at once
    _df = pd.DataFrame(data_dict)
    _df.to_excel(dictionary + '/EU_Importers_Supply_Risks.xlsx', index=False)

    """
        SUPPLY RISK DATA 2
    """

    # Create another dictionary to hold all columns
    data_dict = {'Year': model.set_years}

    for importer in model.set_importer_eu:
        for e in model.set_exporter:
            _str = f'Supply Risk|{importer}|{e}'
            _values = [
                model.par_supply_risk[e] / model.par_rho[e] * model.var_psi[e, importer, t]() 
                for t in model.set_years
            ]
            data_dict[_str] = _values

    # Create DataFrame at once
    _df = pd.DataFrame(data_dict)
    _df.to_excel(dictionary + '/EU_Importers_Supply_Risks_Detailed.xlsx', index=False)
    
    
    """
        CBAM REVENUES AND SUPPLY CHAIN EMISSIONS
    """

    # Create the data dictionary
    data_dict = {'Exporters': list(model.set_exporter)}

    # Compute CBAM revenues by 2040
    values = [
        sum(model.var_r[exp, i, t]() for i in model.set_importer_eu for t in range(model.set_years.first(), 2041))
        for exp in model.set_exporter
    ]
    data_dict['CBAM revenues (by 2040)'] = values  # Fixed from _values to values
    
    values = [
        sum(model.var_s[exp, t]() for t in range(model.set_years.first(), 2041))
        for exp in model.set_exporter
    ]
    data_dict['Spendings (by 2040)'] = values  # Fixed from _values to values

    # Get emissions in 2040
    values2 = [model.var_rho[e, 2040]() for e in model.set_exporter]
    data_dict['Emissions 2040 (in tCO2/MMBtu)'] = values2

    # Get emissions in 2030
    values3 = [model.par_rho[e] for e in model.set_exporter]
    data_dict['Emissions 2030 (in tCO2/MMBtu)'] = values3

    # Convert to DataFrame and export to Excel
    _df = pd.DataFrame(data_dict)
    _df.to_excel(dictionary + '/Exporters_CBAM_Emissions.xlsx', index=False)
    
    
    """
        MONITOR SPENDINGS IN SUPPLY CHAIN EMISSION REDUCTION MEASURES
    """
    
    del [data, _str, _df, _values]
    data = {
        'Year': model.set_years
    }
    _df = pd.DataFrame(data)
    for exporter in model.set_exporter:
        _str = 'spendings|' + exporter
        _values = [model.var_s[exporter, t]() for t in model.set_years]
        if any(_values):
            _df[_str] = _values
        _str = 'Emissions|' + exporter
        _values = [model.var_rho[exporter, t]() for t in model.set_years]
        if any(_values):
            _df[_str] = _values
    # Export DataFrame to Excel
    _df.to_excel(dictionary + '/EXPORTERS_Emission_Investments.xlsx', index=False)
    
    
    """
        LNG DEMAND VALUES (IN million MMBtu)
    """
    data = {
        'Year': model.set_years
    }
    _df = pd.DataFrame(data)
    for imp in model.set_importer:
        _values = [model.par_importer_demand[imp, t] for t in model.set_years]
        _df[imp] = _values
    _df.to_excel(dictionary + '/IMPORTERS_demand_millionMMBtu.xlsx', index=False)
    
    return

