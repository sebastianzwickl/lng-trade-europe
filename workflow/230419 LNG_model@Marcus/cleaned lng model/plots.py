import shutil
import sys
import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import chart_studio
import chart_studio.plotly as py
import seaborn as sns
import chart_studio.plotly as py
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import folium
from folium.plugins import MarkerCluster
import json

from IPython.display import display
from geopy.geocoders import Nominatim
from geopy import distance
from pyomo.environ import *

def plot_map(Imp_Nodes, Exp_Nodes):
    m = folium.Map(location=Exp_Nodes[["Latitude", "Longitude"]].mean().to_list(), zoom_start=1.5)
    #marker_cluster = MarkerCluster().add_to(m)

    for i,r in Exp_Nodes.iterrows():
        location = (r["Latitude"], r["Longitude"])
        folium.Marker(location=location,
                          popup = r['Country'],
                          tooltip=r['Country'],
                      icon = folium.Icon(color='orange')).add_to(m)
        
    for i,r in Imp_Nodes.iterrows():
        location = (r["Latitude"], r["Longitude"])
        folium.Marker(location=location,
                      popup = r['Country'],
                      tooltip=r['Country'],
                      icon = folium.Icon(color='blue')).add_to(m)
                                                            
    # display the map
    folium.Choropleth(
        geo_data=us_states,
        name='choropleth',
        data=Exp_Nodes,
        columns=['Country', "Nominal Liquefaction Capacity 2019 (MMBtu)"],
        key_on='feature.id',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        #legend_name='Unemployment Rate %'
    ).add_to(m)
    
    return