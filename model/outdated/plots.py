# import shutil
# import sys
# import os.path
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import chart_studio
# import chart_studio.plotly as py
# import seaborn as sns
# import chart_studio.plotly as py
# from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
# import folium
# from folium.plugins import MarkerCluster
# import json
# from IPython.display import display
# from geopy.geocoders import Nominatim
# from geopy import distance
# from pyomo.environ import *

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import geopandas


def plot_map(Imp_Nodes, Exp_Nodes):
    
    """
        FIGURE ENVIRONMENT
    """
    
    fig = plt.figure(figsize=(6.5, 3), constrained_layout=False)
    _gs = GridSpec(1, 1, figure=fig)
    ax = fig.add_subplot(_gs[0, 0])
    
    world = gpd.read_file('data/world_shapefile/world_boundaries.shp')
    world.boundary.plot(ax=ax, linewidth=0.15, color='gray')
    world.to_excel('data/world_shapefile/world_boundaries.xlsx', index=False)
    
    _import_nodes = ['Japan', 'China', 'South Korea', 'India', 'Taiwan', 'Pakistan',
                         'France', 'Spain', 'U.K. of Great Britain and Northern Ireland',
                         'Italy', 'Turkey', 'Belgium', 'Other Asia Pacific', 'Other Europe', 'Total North America', 'Total S. & C. America']
    

    _imp_reg_dict = {
        'Other Asia Pacific' : 'Vietnam',
        'Other Europe' : 'Germany',
        'Total North America' : 'United States of America',
        'Total S. & C. America' : 'Chile'
        }
    
    for imp_n in _import_nodes:
        if imp_n in _imp_reg_dict.keys():
            _country = _imp_reg_dict[imp_n]
        else:
            _country = imp_n
        
        world.loc[world.name == _country].plot(ax=ax, color='red')
        

    
    
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    
    plt.tight_layout()
    plt.show()
    fig.savefig('LNG_Import_Export_Countries.pdf', format='pdf')
    
    
    
    
    
    
    
    
    # m = folium.Map(location=Exp_Nodes[["Latitude", "Longitude"]].mean().to_list(), zoom_start=1.5)
    # #marker_cluster = MarkerCluster().add_to(m)

    # for i,r in Exp_Nodes.iterrows():
    #     location = (r["Latitude"], r["Longitude"])
    #     folium.Marker(location=location,
    #                       popup = r['Country'],
    #                       tooltip=r['Country'],
    #                   icon = folium.Icon(color='orange')).add_to(m)
        
    # for i,r in Imp_Nodes.iterrows():
    #     location = (r["Latitude"], r["Longitude"])
    #     folium.Marker(location=location,
    #                   popup = r['Country'],
    #                   tooltip=r['Country'],
    #                   icon = folium.Icon(color='blue')).add_to(m)
                                                            
    # # display the map
    # folium.Choropleth(
    #     geo_data=us_states,
    #     name='choropleth',
    #     data=Exp_Nodes,
    #     columns=['Country', "Nominal Liquefaction Capacity 2019 (MMBtu)"],
    #     key_on='feature.id',
    #     fill_color='YlGn',
    #     fill_opacity=0.7,
    #     line_opacity=0.2,
    #     #legend_name='Unemployment Rate %'
    # ).add_to(m)
    
    return