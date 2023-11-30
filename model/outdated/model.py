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

###############################################################################
### Simple LNG Model
###############################################################################
geolocator = Nominatim(user_agent="Your_Name")

#pd.set_option('precision', 3)
MMBtu_LNG = 23.12 # 1m³ of LNG = 21.04MMBtu
MMBtu_Gas = 0.036 # 1m³ of Gas = 0.036MMBtu
LNG_to_Gas = 584 # 1m³ of LNG = 584m³ of gas (IGU LNG Annual Report 2019)
mt_LNG_BCM = 1.379 * 10**9 # mega tonne of LNG to bcm (https://www.enerdynamics.com/Energy-Currents_Blog/Understanding-Liquefied-Natural-Gas-LNG-Units.aspx)
mt_MMBtu = mt_LNG_BCM * MMBtu_Gas
t_oil_MMBtu = 39.6526 #  tonne of oil to mmbtu             https://unitjuggler.com/

###############################################################################
### 1 Data
###############################################################################
### 1.1 Importing nodes
###############################################################################
# Data for importing and exporting countries from "BP Stats Review (2020)"

# "Import (MMBtu)" column consists of imports in m³ multiplied with conversion factor

Imp_Nodes = pd.DataFrame({
    
    "Country" : ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan",
                 "France", "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific",
                 "Other Europe", "Total North America", "Total S. & C. America", "Total ME & Africa"],
    
    "Import Jan (MMBtu)" : [10.5651, 9.2547, 6.279, 2.83, 2.2386, 1.1288, 1.632, 1.42, 1.741, 1.074, 2.353, 0.585, 1.7, 1.9584, 0.911, 0.3536, 0.0952],
    
    "Import Feb (MMBtu)" : [10.30575, 5.93775, 4.095, 2.56, 1.46055, 0.9248, 1.83, 1.374, 1.17, 0.93, 1.782, 0.299, 1.768, 1.8496, 0.6528, 1.02, 0.3536],
    
    "Import Mar (MMBtu)" : [10.22385, 5.5419, 3.78105, 2.38, 2.0475, 1.2104, 2.335, 1.493, 1.78, 1.605, 1.4, 1.115, 2.1986, 1.6864, 0.9656, 0.9112, 0.1768],
    
    "Import Apr (MMBtu)" : [7.7532, 6.1971, 3.9585, 2.62, 2.0748, 1.1832, 2.572, 1.596, 2.244, 1.115, 0.707, 0.8074, 2.2168, 2.1624, 1.02, 1.0744, 0.748],
    
    "Import May (MMBtu)" : [7.7259, 6.04695, 4.05405, 2.75, 2.03385, 1.1152, 1.832, 1.656, 2.19, 1.115, 0.503, 0.7028, 2.9784, 2.4072, 0.9656, 1.1424, 1.4144],
    
    "Import Jun (MMBtu)" : [7.2345, 6.18345, 4.54545, 2.73, 1.89735, 1.0744, 1.739, 1.903, 0.76, 1.387, 0.68, 0.6528, 2.0264, 2.312, 1.2784, 1.904, 1.3192],
    
    "Import Jul (MMBtu)" : [7.2345, 6.6612, 4.54545, 2.79, 2.25225, 1.088, 1.046, 2.49, 0.3944, 1.265, 0.517, 0.8704, 2.6656, 1.8768, 0.8432, 1.972, 1.4688],
    
    "Import Aug (MMBtu)" : [8.463, 7.5075, 4.914, 2.82, 1.8837, 1.0064, 1.638, 2.144, 0.19, 1.265, 0.816, 0.9112, 2.4888, 1.9176, 1.088, 1.7408, 1.8496],
    
    "Import Sep (MMBtu)" : [8.94075, 6.92055, 3.4125, 2.79, 2.0475, 0.9928, 1.2745, 2.139, 1.3, 1.13, 0.558, 0.2856, 2.3256, 1.8088, 1.0064, 1.0472, 1.5776],
    
    "Import Oct (MMBtu)" : [8.85885, 5.6511, 4.368, 2.83, 2.00655, 1.0608, 1.7745, 1.95, 1.85, 1.35, 0.843, 0.7616, 2.1986, 2.0944, 0.9248, 0.8024, 1.1016],
    
    "Import Nov (MMBtu)" : [8.83155, 8.66775, 5.1597, 2.79, 1.51515, 0.6664, 2.84, 1.931, 2.4, 0.94, 1.115, 1.0336, 3.876, 2.2848, 0.5984, 0.9384, 0.476],
    
    "Import Dec (MMBtu)" : [9.4185, 10.30575, 6.51105, 2.83, 1.7745, 0.9792, 2.56, 1.81, 3.05, 1.1, 1.89, 0.9928, 4.148, 2.0808, 0.9656, 0.5576, 0.276],
    
    "Regasification Terminal" : ["Sodegaura", "Yancheng", "Incheon", "Dahej", "Kaohsiung",
                                 "Karachi", "Dunkirk",
                                 "Barcelona", "Isle of Grain", "Rovigo", "Marmara", "Zeebrugge",
                                 "Map Ta Phut, Thailand",
                                 "Świnoujście, Poland", "Ensenada, Mexico", "Rio de Janeiro, Brazil",
                                 "Al Ahmadi, Kuwait"],
    
    "Import (MMBtu)" : [105.6*10**9 * MMBtu_Gas, 84.9*10**9 * MMBtu_Gas, 55.6*10**9 * MMBtu_Gas,
                         32.9*10**9 * MMBtu_Gas, 23.2*10**9 * MMBtu_Gas, 12.4*10**9 * MMBtu_Gas,
                         23.1*10**9 * MMBtu_Gas, 21.9*10**9 * MMBtu_Gas, 19.1*10**9 * MMBtu_Gas,
                         14.3*10**9 * MMBtu_Gas, 13.2*10**9 * MMBtu_Gas, 9*10**9 * MMBtu_Gas,
                         30.6*10**9 * MMBtu_Gas, 24.4*10**9 * MMBtu_Gas, 11.2*10**9 * MMBtu_Gas,
                         13.5*10**9 * MMBtu_Gas, 10.9*10**9 * MMBtu_Gas],
    
    "Import 2030 (MMBtu)" : [86.287, 135, 58.6, 55, 28.75, 51.735, 30.944, 29.379,
                        
                             25.574, 19.146, 17.654, 12.093, 120, 40.776, 12.363,
                        
                             14.842, 47.14],

    "Import 2040 (MMBtu)" : [71.84, 167.676, 62.5, 75.72, 31.25, 70.5, 40.407,
                             38.363, 33.395, 25.001, 23.053, 15.791, 195.391,
                             44.799, 13.514, 16.217, 88],
    
    "Import Europe +33% (MMBtu)" : [105.6*10**9 * MMBtu_Gas, 84.9*10**9 * MMBtu_Gas, 55.6*10**9 * MMBtu_Gas,
                                     32.9*10**9 * MMBtu_Gas, 23.2*10**9 * MMBtu_Gas, 12.4*10**9 * MMBtu_Gas,
                                     (4/3)*23.1*10**9 * MMBtu_Gas, (4/3)*21.9*10**9 * MMBtu_Gas, (4/3)*19.1*10**9 * MMBtu_Gas,
                                     (4/3)*14.3*10**9 * MMBtu_Gas, (4/3)*13.2*10**9 * MMBtu_Gas, (4/3)*9*10**9 * MMBtu_Gas,
                                     30.6*10**9 * MMBtu_Gas, (4/3)*24.4*10**9 * MMBtu_Gas, 11.2*10**9 * MMBtu_Gas,
                                     13.5*10**9 * MMBtu_Gas, 10.9*10**9 * MMBtu_Gas],
    
    "Import Asia Pacific -20% (MMBtu)" : [(4/5)*105.6*10**9 * MMBtu_Gas, (4/5)*1.121*84.9*10**9 * MMBtu_Gas, (4/5)*1.121*55.6*10**9 * MMBtu_Gas,
                                     32.9*10**9 * MMBtu_Gas, (4/5)*23.2*10**9 * MMBtu_Gas, 12.4*10**9 * MMBtu_Gas,
                                     23.1*10**9 * MMBtu_Gas, 21.9*10**9 * MMBtu_Gas, 19.1*10**9 * MMBtu_Gas,
                                     14.3*10**9 * MMBtu_Gas, 13.2*10**9 * MMBtu_Gas, 9*10**9 * MMBtu_Gas,
                                     (4/5)*30.6*10**9 * MMBtu_Gas, 24.4*10**9 * MMBtu_Gas, 11.2*10**9 * MMBtu_Gas,
                                     13.5*10**9 * MMBtu_Gas, 10.9*10**9 * MMBtu_Gas],
    

})

#Imp_Countries["Import (MMBtu)"] = (Imp_Countries["Import (MMBtu)"].astype(float)/1000000000).astype(str)

Imp_Nodes["Location"] = Imp_Nodes["Regasification Terminal"].apply(geolocator.geocode)
Imp_Nodes["Point"]= Imp_Nodes["Location"].apply(lambda loc: tuple(loc.point) if loc else None)
Imp_Nodes[["Latitude", "Longitude", "Altitude"]] = pd.DataFrame(Imp_Nodes["Point"].to_list(), index=Imp_Nodes.index)

#del Imp_Nodes["Altitude"]
#del Imp_Nodes["Location"]
#del Imp_Nodes["Point"]


#center the columns, display() method doesn't work anymore, so not necessary for now
def pd_centered(df):
    return df.style.set_table_styles([
        {"selector": "th", "props": [("text-align", "center")]},
        {"selector": "td", "props": [("text-align", "center")]}])

Imp_Nodes["Import Jan (MMBtu)"] *= 10**9 * MMBtu_Gas
Imp_Nodes["Import Feb (MMBtu)"] *= 10**9 * MMBtu_Gas
Imp_Nodes["Import Mar (MMBtu)"] *= 10**9 * MMBtu_Gas
Imp_Nodes["Import Apr (MMBtu)"] *= 10**9 * MMBtu_Gas
Imp_Nodes["Import May (MMBtu)"] *= 10**9 * MMBtu_Gas
Imp_Nodes["Import Jun (MMBtu)"] *= 10**9 * MMBtu_Gas
Imp_Nodes["Import Jul (MMBtu)"] *= 10**9 * MMBtu_Gas
Imp_Nodes["Import Aug (MMBtu)"] *= 10**9 * MMBtu_Gas
Imp_Nodes["Import Sep (MMBtu)"] *= 10**9 * MMBtu_Gas
Imp_Nodes["Import Oct (MMBtu)"] *= 10**9 * MMBtu_Gas
Imp_Nodes["Import Nov (MMBtu)"] *= 10**9 * MMBtu_Gas
Imp_Nodes["Import Dec (MMBtu)"] *= 10**9 * MMBtu_Gas

Imp_Nodes["Import 2030 (MMBtu)"] *= 10**9 * MMBtu_Gas
Imp_Nodes["Import 2040 (MMBtu)"] *= 10**9 * MMBtu_Gas
#Imp_Nodes["Import (MMBtu)"] = Imp_Nodes["Import (MMBtu)"]/(10**9 * MMBtu_Gas)

#print(Imp_Nodes["Import (MMBtu)"].sum()/(10**9 * MMBtu_Gas))
print(Imp_Nodes["Import 2030 (MMBtu)"].sum())
print(Imp_Nodes["Import 2040 (MMBtu)"].sum())
print(Imp_Nodes["Import Europe +33% (MMBtu)"].sum()/(10**9 * MMBtu_Gas))
print(Imp_Nodes["Import Asia Pacific -20% (MMBtu)"].sum()/(10**9 * MMBtu_Gas))
Imp_Nodes

###############################################################################
### 1.2 Exporting nodes
###############################################################################
# define DF with data for exporting countries (BP 2020)

Exp_Nodes = pd.DataFrame({
    
    "Country" : ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                 "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific", "Other Europe",
                 "Other Americas", "Other ME", "Other Africa"],
    
    "Export (MMBtu)" : [107.1*10**9 * MMBtu_Gas, 104.7*10**9 * MMBtu_Gas, 47.5*10**9 * MMBtu_Gas,
                        39.4*10**9 * MMBtu_Gas, 35.1*10**9 * MMBtu_Gas, 28.8*10**9 * MMBtu_Gas,
                        17.0*10**9 * MMBtu_Gas, 16.6*10**9 * MMBtu_Gas, 16.5*10**9 * MMBtu_Gas,
                        14.1*10**9 * MMBtu_Gas, 20.9*10**9 * MMBtu_Gas, 8.6*10**9 * MMBtu_Gas, 
                        5.301*10**9 * MMBtu_Gas, 7.7*10**9 * MMBtu_Gas, 15.8*10**9 * MMBtu_Gas],
    
    "Export Jan (MMBtu)" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    
    "Export Feb (MMBtu)" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    
    "Export Mar (MMBtu)" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    
    "Export Apr (MMBtu)" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    
    "Export May (MMBtu)" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    
    "Export Jun (MMBtu)" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    
    "Export Jul (MMBtu)" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    
    "Export Aug (MMBtu)" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    
    "Export Sep (MMBtu)" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    
    "Export Oct (MMBtu)" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    
    "Export Nov (MMBtu)" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    
    "Export Dec (MMBtu)" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    
    "Export 2030 (MMBtu)" : [151.69, 124.4, 150.5, 60, 43, 39.28, 17, 20, 37.7, 15.86, 20.9, 8.6, 50, 7.7, 60],
                             
    "Export 2040 (MMBtu)" : [173.75, 140, 220, 85, 43, 70, 17, 20, 37.7, 15.86, 20.9, 8.6, 60, 7.7, 100],
        
    "Break Eeven Price ($/MMBtu)" : [2.36, 7.5, 5.95, 4.5, 6.0, 4.08,
                                     5.1, 4.93, 6.0, 3.7, 8.4, 5.0,
                                     6.0, 3.0, 4.5],
    
    "Break Eeven Price 2030 ($/MMBtu)" : [2.934, 9.325, 7.398, 5.595, 7.46, 5.0723, 6.341,
                                          6.13, 7.46, 4.6, 10.444, 6.217, 7.460, 3.73, 5.595],
    
    "Break Eeven Price 2040 ($/MMBtu)" : [3.577, 11.367, 9.018, 6.82, 9.094, 6.184, 7.73, 7.472,
                                          9.094, 5.608, 12.731, 7.578, 9.094, 4.547, 6.82],
    
    
    #"Feedstock ($/MMBtu)" : [1.5, 3.0, 3.0, 0.5, 3.0, 2.2, 3.0, 0.5, 2.0, 1.5],

    #"Liquefaction ($/MMBtu)" : [2.0, 3.5, 3.0, 4.0, 3.0, 1.88, 2.1, 2.0, 4.0, 2.0],
    
    "Liquefaction Terminal" : ["Ras Laffan", "Gladstone", "Sabine Pass",
                               "Sabetta", "Bintulu", "Bonny Island",
                               "Point Fortin", " Bethioua", "Bontang",
                               "Qalhat, Oman", "Port Moresby, Papua New Guinea",
                               "Hammerfest, Norway", "Callao, Peru",
                               "Abu Dhabi, UAE", "Soyo, Angola"],
    
    # data for capacity from IGU 2020
    
    "Nominal Liquefaction Capacity 2019 (MMBtu)" : [77.665*mt_MMBtu, 86*mt_MMBtu, 37.8*mt_MMBtu,
                                              26.6*1.07*mt_MMBtu, 30.5*mt_MMBtu, 22.2*mt_MMBtu,
                                              14.8*mt_MMBtu, 25.5*mt_MMBtu, 26.6*mt_MMBtu,
                                              10.4*mt_MMBtu, 14.1*mt_MMBtu, 4.2*mt_MMBtu,
                                              4.5*mt_MMBtu, 5.8*mt_MMBtu, 11.3*mt_MMBtu],
    
    "Nominal Liquefaction Capacity (MMBtu)" : [77.1*mt_MMBtu/12, 86*mt_MMBtu/12, 37.8*mt_MMBtu/12,
                                              26.6*1.07*mt_MMBtu/12, 30.5*mt_MMBtu/12, 22.2*mt_MMBtu/12,
                                              14.8*mt_MMBtu/12, 25.5*mt_MMBtu/12, 26.6*mt_MMBtu/12,
                                              10.4*mt_MMBtu/12, 14.1*mt_MMBtu/12, 4.2*mt_MMBtu/12,
                                              4.5*mt_MMBtu/12, 5.8*mt_MMBtu/12, 11.3*mt_MMBtu/12],
    
    
    "Nominal Liquefaction Capacity 2019 HC (MMBtu)" : [(2/3)*77.1*mt_MMBtu, 86*mt_MMBtu, 37.8*mt_MMBtu,
                                              26.6*1.07*mt_MMBtu, 30.5*mt_MMBtu, 22.2*mt_MMBtu,
                                              14.8*mt_MMBtu, 25.5*mt_MMBtu, 26.6*mt_MMBtu,
                                              (2/3)*10.4*mt_MMBtu, 14.1*mt_MMBtu, 4.2*mt_MMBtu,
                                              4.5*mt_MMBtu, (2/3)*5.8*mt_MMBtu, 11.3*mt_MMBtu],
    
        
})

# Price for US: https://www.macrotrends.net/2478/natural-gas-prices-historical-chart and 
# https://www.argusmedia.com/en/news/1431713-cheniere-longterm-lng-sales-data-excludes-some-fees
# Price for Qatar and Algeria: https://www.argusmedia.com/en/news/2098570-sonatrach-offers-spot-lng-cargoes-as-exports-slow
# Price for Papua NG: https://oilprice.com/Energy/Energy-General/Low-Gas-Prices-Could-Derail-Papua-New-Guineas-LNG-Ambitions.html
# Egypt Export 2019: https://www.mees.com/2020/4/10/oil-gas/egypt-2019-lng-exports/2aa75e10-7b34-11ea-9c97-c54251792df2
# Russia Export 2019: https://www.hellenicshippingnews.com/russian-lng-exports-a-year-in-review/

#Exp_Countries["Export (Bcm)"] = (Exp_Countries["Export (Bcm)"].astype(float)/1000000000).astype(str)

#"Nominal Liquefaction Capacity (MMBtu)" : [77*mt_MMBtu, 75.4*mt_MMBtu, 24.6*mt_MMBtu,
#                                              21.8*mt_MMBtu, 30.5*mt_MMBtu, 21.9*mt_MMBtu,
#                                              15.5*mt_MMBtu, 25.3*mt_MMBtu, 20.9*mt_MMBtu,
#                                              10.8*mt_MMBtu, 14.1*mt_MMBtu, 4.2*mt_MMBtu,
#                                              4.5*mt_MMBtu, 5.8*mt_MMBtu, 11.3*mt_MMBtu],


Exp_Nodes["Location"] = Exp_Nodes["Liquefaction Terminal"].apply(geolocator.geocode)
Exp_Nodes["Point"] = Exp_Nodes["Location"].apply(lambda loc: tuple(loc.point) if loc else None)
Exp_Nodes[["Latitude", "Longitude", "Altitude"]] = pd.DataFrame(Exp_Nodes["Point"].to_list(), index=Exp_Nodes.index)

# remove unnecessary columns
#del Exp_Nodes["Altitude"]
#del Exp_Nodes["Location"]
#del Exp_Nodes["Point"]

#display(pd_centered(Exp_Countries))
Exp_Nodes["Export Jan (MMBtu)"] = Exp_Nodes["Nominal Liquefaction Capacity (MMBtu)"] * 1.007
Exp_Nodes["Export Jun (MMBtu)"] = Exp_Nodes["Nominal Liquefaction Capacity (MMBtu)"] * 0.95
Exp_Nodes["Export Sep (MMBtu)"] = Exp_Nodes["Nominal Liquefaction Capacity (MMBtu)"] * 0.968
Exp_Nodes["Export Aug (MMBtu)"] = Exp_Nodes["Nominal Liquefaction Capacity (MMBtu)"] * 0.95
Exp_Nodes["Export Nov (MMBtu)"] = Exp_Nodes["Nominal Liquefaction Capacity (MMBtu)"] * 1.005
Exp_Nodes["Export Dec (MMBtu)"] = Exp_Nodes["Nominal Liquefaction Capacity (MMBtu)"] * 1.12

Exp_Nodes["Export 2030 (MMBtu)"] *= 10**9 * MMBtu_Gas
Exp_Nodes["Export 2040 (MMBtu)"] *= 10**9 * MMBtu_Gas
#Exp_Nodes["Nominal Liquefaction Capacity 2019 (MMBtu)"] = Exp_Nodes["Nominal Liquefaction Capacity 2019 (MMBtu)"]/(10**9 * MMBtu_Gas)

# Maps

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

###############################################################################
### 1.3 Sea distances among the importing and exporting nodes
###############################################################################
# Define DF with distances among largest liquefaction and regas terminals in nautical miles
# In case of lack of the route to the specific terminal, next largest port was taken
# sea-distances.org, searoutes.com

Distances = pd.DataFrame([(6512, 5846, 6161, 1301, 5251, 881, 6240, 4650, 6260, 4380, 3460, 6270, 4374, 6840, 11406, 8154, 297),
                          
                          (3861, 4134, 4313, 5918, 3594, 6306, 11650, 10060, 11670, 9790, 8870, 11680, 4091, 12190, 6367, 8078, 7279),
                          
                          (9205, 10075, 10005, 9645, 10495, 9460, 4881, 5206, 4897, 6354, 6341, 4908, 12015, 5364, 4315, 5234, 9930),
                          
                          (4929, 5596, 5671, 8810, 6279, 8570, 2494, 4252, 2511, 5546, 5481, 2477, 7821, 2547, 9185, 7524, 9040),
    
                          (2276, 1656, 1998, 3231, 1262, 3466, 8980, 7390, 9000, 7120, 6200, 9010, 926, 9360, 7364, 9061, 4439),
                          
                          (10752, 10088, 10406, 6988, 9446, 7059, 4287, 3824, 4309, 4973, 4961, 4321, 8697, 4832, 8095, 3387, 7577),
                          
                          (8885, 9755, 9665, 8370, 10175, 8210, 3952, 3926, 3974, 5074, 5062, 3984, 11127, 4536, 4005, 3113, 8680),
                          
                          (9590, 8930, 9240, 4720, 8328, 4540, 1519, 343, 1541, 1432, 1417, 1552, 7450, 2129, 7445, 4464, 5000),
                          
                          (2651, 2181, 2487, 3517, 1448, 4014, 9260, 7670, 9280, 7390, 6470, 9290, 1651, 9910, 7203, 9212, 4987),
                          
                          (6046, 5379, 5694, 853, 4741, 446, 5760, 4180, 5790, 3900, 2980, 5800, 3864, 6310, 10896, 7623, 808),
                          
                          (3139, 3403, 3541, 5311, 2839, 5601, 10980, 9300, 10990, 9030, 8110, 10970, 3384, 11480, 6184, 8894, 6572),
                          
                          (12450, 11770, 12090, 7570, 11160, 7380, 1389, 3124, 1378, 4273, 4261, 1376, 10310, 1374, 8044, 6352, 7860),
                          
                          (8424, 9304, 9231, 10665, 9484, 10475, 6085, 6215, 6105, 7365, 7355, 6115, 11132, 6645, 3527, 5064, 10980),
                          
                          (6444, 5778, 6093, 1233, 5162, 803, 6180, 4590, 6200, 4310, 3390, 6210, 4284, 6950, 11328, 8091, 351),
                          
                          (10057, 9291, 9608, 6191, 8677, 6262, 4878, 4409, 4901, 5559, 5546, 4911, 8053, 5654, 8595, 3357, 6741)],

                  index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                           "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                           "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                  columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

#display(pd_centered(Distances))
Distances

# Define DF with distances among largest liquefaction and regas terminals in nautical miles
# In case of lack of the route to the specific terminal, next largest port was taken
# sea-distances.org, searoutes.com

# if route over canal: distance rounded on 0 for suez and on 5 for panama, needed for later calculations

Distances_Suez_Closed = pd.DataFrame([(6512, 5846, 6161, 1301, 5251, 881, 11044, 10587, 11084, 11811, 11849, 11009, 4374, 11753, 11406, 8154, 297),
                          
                          (3861, 4134, 4313, 5918, 3594, 6306, 12555, 12695, 12575, 13845, 13825, 12585, 4091, 13125, 6367, 8078, 7279),
                          
                          (9205, 10075, 10005, 9645, 10495, 12069, 4881, 5206, 4897, 6354, 6341, 4908, 12015, 5364, 4315, 5234, 12548),
                          
                          (4929, 5596, 5671, 10541, 6279, 10816, 2494, 4252, 2511, 5546, 5481, 2477, 7821, 2547, 9185, 7524, 11762),
                          
                          (2276, 1656, 1998, 3231, 1262, 3466, 12003, 11544, 12043, 12769, 12689, 12049, 926, 12612, 7364, 9061, 4439),
                          
                          (10752, 10088, 10406, 6988, 9446, 7059, 4287, 3824, 4309, 4973, 4961, 4321, 8697, 4832, 8095, 3387, 7577),
                          
                          (8885, 9755, 9665, 10054, 10175, 10009, 3952, 3926, 3974, 5074, 5062, 3984, 11127, 4536, 4005, 3113, 10534),
                          
                          (12425, 13038, 13424, 10101, 8328, 10056, 1519, 343, 1541, 1432, 1417, 1552, 7450, 2129, 7445, 4464, 10581),
                          
                          (2651, 2181, 2487, 3517, 1448, 4014, 12129, 11671, 12169, 12894, 12814, 12176, 1651, 12738, 7203, 9212, 4987),
                          
                          (6046, 5379, 5694, 853, 4741, 446, 10503, 10044, 10542, 11269, 11188, 10549, 3864, 11112, 10896, 7623, 808),
                          
                          (3139, 3403, 3541, 5311, 2839, 5601, 13279, 13319, 12821, 14044, 13964, 13324, 3384, 13888, 6184, 8894, 6572),
                          
                          (13075, 13995, 13915, 12114, 14494, 12069, 1389, 3124, 1378, 4273, 4261, 1376, 13714, 1374, 8044, 6352, 12594),
                          
                          (8424, 9304, 9231, 10665, 9484, 10475, 6085, 6215, 6105, 7365, 7355, 6115, 11132, 6645, 3527, 5064, 12349),
                          
                          (6444, 5778, 6093, 1233, 5162, 803, 10953, 10494, 10992, 11719, 11638, 10999, 4284, 11562, 11328, 8091, 351),
                          
                          (10057, 9291, 9608, 6191, 8677, 6262, 4878, 4409, 4901, 5559, 5546, 4911, 8053, 5654, 8595, 3357, 6741)],

                  index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                           "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                           "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                  columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

###############################################################################
### 1.4 LNG carrier
###############################################################################
# To keep the model simple it is assumed that there is only one type of the LNG carrier.

# define DF with lng carrier properties
#LNG_Carrier_Number = 530

LNG_Carrier = pd.DataFrame({"Capacity (m³)" : [160000], # average capacity in 2019 160000 (!!! GIIGNL p. 21; https://www.rivieramm.com/opinion/opinion/lng-shipping-by-numbers-36027)
                            "Spot Charter Rate ($/day)" : [69337], # average spot charter rate in 2019 (https://www.statista.com/statistics/1112660/lng-tanker-average-spot-charter-rate/)
                            "Speed (knots/h)" : [17], # Argus LNG daily (MT/Literature/Transport and Contracts)
                            "Bunker (mt/d)" : [99], #Almost half of tankers are ST, Outlook for competitive LNG supply Oxford
                            "Bunkers Price ($/mt)" : [670], # Outlook for competitive LNG supply Oxford
                            "Boil off" : [1/1000], # the daily guaranteed maximum boil-off or DGMB (0,1%)
                            "Boil Cost $/mmBtu" : [5],
                            "Heel" : [4/100]}) # 4% of the cargo is retained as the heel (LNG storage tanks need to be kept cool)

#print(LNG_Carrier_DF.loc[0, "Capacity (m³)"])
#display(pd_centered(LNG_Carrier))
LNG_Carrier.style
#LNG_Carrier.loc[0, "Capacity (m³)"]

###############################################################################
### 1.5 Additional costs
###############################################################################
# define DF containing additional costs
# Outlook for competitive LNG Supply OIES

Additional_Costs = pd.DataFrame({
    "Port Costs ($ for 3 days)" : [400000], 
    "Suez Canal Costs ($/Cargo)" : [1000000],  # 0.24 $/mmBtU
    "Panama Canal Costs ($/Cargo)" : [950000], # 0.21 $/mmBtu,                     
    "Insurance ($/day)" : [2600],
    "Fees (Percentage of Charter Costs)" : [2/100]})

#display(pd_centered(Additional_Costs))
Additional_Costs.style

###############################################################################
### 1.6 GHG
###############################################################################
# api-lng-ghg-emissions-guidelines-05-2015.pdf

CO2 = pd.DataFrame({
    "Bunker Fuel": [0.0845], #t/mmBtu
    "BOG": [0.0576]})

CH4 = pd.DataFrame({"Bunker Fuel": [0.0000046], #t/mmBtu
                    "BOG": [0.0000916]})



###############################################################################
### 2 Cost voyage times calculations
###############################################################################
### 2.1 (Return) voyage times
###############################################################################
# https://timera-energy.com/deconstructing-lng-shipping-costs/ and OIES articles!

Time = Distances / (LNG_Carrier.loc[0, "Speed (knots/h)"] * 12) # in days

# note to myself: it would be better to define a function which would compute the time!!!
#display(pd_centered(Time))
Time

Time_Suez_Closed = Distances_Suez_Closed / (LNG_Carrier.loc[0, "Speed (knots/h)"] * 12) # in days
Time

###############################################################################
### 2.2 Charter costs
###############################################################################
Charter_Costs = (Time + 3) * LNG_Carrier.loc[0, "Spot Charter Rate ($/day)"] # in $

Charter_Costs_Suez_Closed = (Time_Suez_Closed + 3) * LNG_Carrier.loc[0, "Spot Charter Rate ($/day)"] # in $

# display(pd_centered(Charter_Costs))
Charter_Costs_Suez_Closed

###############################################################################
### 2.3 Fuel costs
###############################################################################
# this is arbitrary cost 
lng_cost = 5 # $/MMBtu 

#Fuel_Costs = Time * LNG_Carrier.loc[0, "Boil off"] * 0.98 * LNG_Carrier.loc[0, "Capacity (m³)"] * lng_cost * MMBtu_LNG

#Fuel_Costs_Suez_Closed = Time_Suez_Closed * LNG_Carrier.loc[0, "Boil off"] * 0.98 * LNG_Carrier.loc[0, "Capacity (m³)"] * lng_cost * MMBtu_LNG

Fuel_Costs = Time * LNG_Carrier.loc[0, "Bunker (mt/d)"] * LNG_Carrier.loc[0, "Bunkers Price ($/mt)"] + 3 * 25 * LNG_Carrier.loc[0, "Bunkers Price ($/mt)"] 
                            
Fuel_Costs_Suez_Closed = Time_Suez_Closed * LNG_Carrier.loc[0, "Bunker (mt/d)"] * LNG_Carrier.loc[0, "Bunkers Price ($/mt)"] + 3 * 25 * LNG_Carrier.loc[0, "Bunkers Price ($/mt)"]
#display(pd_centered(Fuel_Costs))
Fuel_Costs

### Boiloff

BoilOff = Time * LNG_Carrier.loc[0,"Boil off"] * LNG_Carrier.loc[0, "Capacity (m³)"] *0.98 * MMBtu_LNG

BoilOff_Cost = BoilOff * LNG_Carrier.loc[0,"Boil Cost $/mmBtu"]

### Suez Closed
BoilOff_Suez_Closed = Time_Suez_Closed * LNG_Carrier.loc[0,"Boil off"] * LNG_Carrier.loc[0, "Capacity (m³)"] * MMBtu_LNG

BoilOff_Cost_Suez_Closed = BoilOff_Suez_Closed * LNG_Carrier.loc[0,"Boil Cost $/mmBtu"]


##### Emissions
Consumption_HOF = (Time * LNG_Carrier.loc[0, "Bunker (mt/d)"] + 3 * 25)

CO2_Emissions_Bunker = Consumption_HOF * t_oil_MMBtu * CO2.loc[0, "Bunker Fuel"]
CO2_Emissions_BoilOff = BoilOff * CO2.loc[0, "BOG"]

CO2_Emissions = CO2_Emissions_Bunker + CO2_Emissions_BoilOff

CH4_Emissions_Bunker = Consumption_HOF * t_oil_MMBtu * CH4.loc[0, "Bunker Fuel"]
CH4_Emissions_BoilOff = BoilOff * CH4.loc[0, "BOG"]

CH4_Emissions = CH4_Emissions_Bunker + CH4_Emissions_BoilOff
CO2_Emissions

###############################################################################
### 2.4 Agents and Broker Fees + Insurance
###############################################################################
Fees_and_Insurance = (Time + 3) * Additional_Costs.loc[0, "Insurance ($/day)"] + Charter_Costs * Additional_Costs.loc[0, "Fees (Percentage of Charter Costs)"]

Fees_and_Insurance_Suez_Closed = (Time_Suez_Closed + 3) * Additional_Costs.loc[0, "Insurance ($/day)"] + Charter_Costs_Suez_Closed * Additional_Costs.loc[0, "Fees (Percentage of Charter Costs)"]

#display(pd_centered(Fees_and_Insurance))
Fees_and_Insurance_Suez_Closed

###############################################################################
### 2.5 Suez/Panama Canal Fee
###############################################################################
Canal_Fees = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                   index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                           "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                           "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                  columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for index in Distances.index:
    for columns in Distances.columns:
        if (((Distances.loc[index, columns]) % 5 == 0) and ((Distances.loc[index, columns]) %10 != 0)):
            Canal_Fees.loc[index, columns] += Additional_Costs.loc[0, "Panama Canal Costs ($/Cargo)"]
        elif ((Distances.loc[index, columns]) % 10 == 0):
            Canal_Fees.loc[index, columns] += Additional_Costs.loc[0, "Suez Canal Costs ($/Cargo)"]
            
#display(pd_centered(Canal_Fees))
Canal_Fees

###############################################################################
### 2.6 Port Costs
###############################################################################
Port_Costs = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                           "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                           "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                  columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

Port_Costs += Additional_Costs.loc[0, "Port Costs ($ for 3 days)"]

#display(pd_centered(Port_Costs))
Port_Costs

###############################################################################
### 2.7 Total Costs of Transportation
###############################################################################
Transport_Costs =  Charter_Costs + Fuel_Costs + Fees_and_Insurance + Canal_Fees + Port_Costs + BoilOff_Cost

Transport_Costs_Suez_Closed =  Charter_Costs_Suez_Closed + Fuel_Costs_Suez_Closed + Fees_and_Insurance_Suez_Closed + Canal_Fees + Port_Costs + BoilOff_Cost_Suez_Closed

#######

Transport_Costs_MMBtu = Transport_Costs / ((0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] - LNG_Carrier.loc[0, "Capacity (m³)"]*LNG_Carrier.loc[0, "Boil off"] * Time) * MMBtu_LNG) # 1-heel-boil_off = 0.94

Transport_Costs_MMBtu_Suez_Closed = Transport_Costs_Suez_Closed / ((0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] - LNG_Carrier.loc[0, "Capacity (m³)"]*LNG_Carrier.loc[0, "Boil off"] * Time_Suez_Closed) * MMBtu_LNG) # 1-heel-boil_off = 0.94

#display(pd_centered(Transport_Costs_MMBtu))
Transport_Costs_MMBtu.style #in $/MMBtu
Transport_Costs_MMBtu

###############################################################################
### 2.8 Total Costs
###############################################################################
#taken from EXP_Countries df

Breakeven = pd.DataFrame([(2.36, 2.36, 2.36, 2.36, 2.36, 2.36, 2.36, 2.36, 2.36, 2.36, 2.36, 2.36, 2.36, 2.36, 2.36, 2.36, 2.36),
                          
                          (7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5),
                          
                          (5.95, 5.95, 5.95, 5.95, 5.95, 5.95, 5.95, 5.95, 5.95, 5.95, 5.95, 5.95, 5.95, 5.95, 5.95, 5.95, 5.95),
                          
                          (4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5),
                          
                          (6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0),
                          
                          (4.08, 4.08, 4.08, 4.08, 4.08, 4.08, 4.08, 4.08, 4.08, 4.08, 4.08, 4.08, 4.08, 4.08, 4.08, 4.08, 4.08),
                           
                          (5.1, 5.1, 5.1, 5.1, 5.1, 5.1, 5.1, 5.1, 5.1, 5.1, 5.1, 5.1, 5.1, 5.1, 5.1, 5.1, 5.1),
                          
                          (2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5),
                          
                          (6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0),
                          
                          (3.7, 3.7, 3.7, 3.7, 3.7, 3.7, 3.7, 3.7, 3.7, 3.7, 3.7, 3.7, 3.7, 3.7, 3.7, 3.7, 3.7),
                          
                          (7.7, 7.7, 7.7, 7.7, 7.7, 7.7, 7.7, 7.7, 7.7, 7.7, 7.7, 7.7, 7.7, 7.7, 7.7, 7.7, 7.7),
                          
                          (5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0),
                         
                          (6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0),
                          
                          (3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0),
                          
                          (4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5)

                       ],

                  index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                           "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                           "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                  columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

Total_Costs = Breakeven + Transport_Costs_MMBtu
Total_Costs_Suez_Closed = Breakeven + Transport_Costs_MMBtu_Suez_Closed


TotalCosts = Total_Costs

Total_Costs_2030 = Total_Costs*1.02**11
Total_Costs_2040 = Total_Costs*1.02**21

Total_Costs_Tr_05 = Breakeven + 0.5*Transport_Costs_MMBtu
Total_Costs_Tr_20 = Breakeven + 2*Transport_Costs_MMBtu

Total_Costs_Tr_05

###############################################################################
### 3 Model
###############################################################################
### 3.1 Data File and Functions
###############################################################################
Supply = Exp_Nodes.set_index("Country")["Nominal Liquefaction Capacity (MMBtu)"].to_dict()
Supply_Jan = Exp_Nodes.set_index("Country")["Export Jan (MMBtu)"].to_dict()
Supply_Jun = Exp_Nodes.set_index("Country")["Export Jun (MMBtu)"].to_dict()
Supply_Aug = Exp_Nodes.set_index("Country")["Export Aug (MMBtu)"].to_dict()
Supply_Sep = Exp_Nodes.set_index("Country")["Export Sep (MMBtu)"].to_dict()
Supply_Nov = Exp_Nodes.set_index("Country")["Export Nov (MMBtu)"].to_dict()
Supply_Dec = Exp_Nodes.set_index("Country")["Export Dec (MMBtu)"].to_dict()
Supply_2019 = Exp_Nodes.set_index("Country")["Nominal Liquefaction Capacity 2019 (MMBtu)"].to_dict()
Supply_2030 = Exp_Nodes.set_index("Country")["Export 2030 (MMBtu)"].to_dict()
Supply_2040 = Exp_Nodes.set_index("Country")["Export 2040 (MMBtu)"].to_dict()
Supply_HC = Exp_Nodes.set_index("Country")["Nominal Liquefaction Capacity 2019 HC (MMBtu)"].to_dict()

#print(Supply)

Demand_Jan = Imp_Nodes.set_index("Country")["Import Jan (MMBtu)"].to_dict()
Demand_Feb = Imp_Nodes.set_index("Country")["Import Feb (MMBtu)"].to_dict()
Demand_Mar = Imp_Nodes.set_index("Country")["Import Mar (MMBtu)"].to_dict()
Demand_Apr = Imp_Nodes.set_index("Country")["Import Apr (MMBtu)"].to_dict()
Demand_May = Imp_Nodes.set_index("Country")["Import May (MMBtu)"].to_dict()
Demand_Jun = Imp_Nodes.set_index("Country")["Import Jun (MMBtu)"].to_dict()
Demand_Jul = Imp_Nodes.set_index("Country")["Import Jul (MMBtu)"].to_dict()
Demand_Aug = Imp_Nodes.set_index("Country")["Import Aug (MMBtu)"].to_dict()
Demand_Sep = Imp_Nodes.set_index("Country")["Import Sep (MMBtu)"].to_dict()
Demand_Oct = Imp_Nodes.set_index("Country")["Import Oct (MMBtu)"].to_dict()
Demand_Nov = Imp_Nodes.set_index("Country")["Import Nov (MMBtu)"].to_dict()
Demand_Dec = Imp_Nodes.set_index("Country")["Import Dec (MMBtu)"].to_dict()
Demand_2019 = Imp_Nodes.set_index("Country")["Import (MMBtu)"].to_dict()
Demand_2030 = Imp_Nodes.set_index("Country")["Import 2030 (MMBtu)"].to_dict()
Demand_2040 = Imp_Nodes.set_index("Country")["Import 2040 (MMBtu)"].to_dict()
Demand_2019_EU = Imp_Nodes.set_index("Country")["Import Europe +33% (MMBtu)"].to_dict()
Demand_2019_Asia = Imp_Nodes.set_index("Country")["Import Asia Pacific -20% (MMBtu)"].to_dict()

#print(Demand)

Cost = {}

for index in Total_Costs.index:
    for column in Total_Costs.columns:
        Cost[column, index] = Total_Costs.loc[index,column]
        
Cost_Suez_Closed = {}
        
for index in Total_Costs_Suez_Closed.index:
    for column in Total_Costs_Suez_Closed.columns:
        Cost_Suez_Closed[column, index] = Total_Costs_Suez_Closed.loc[index,column]
        
        
Cost_Tr_05 = {}
        
for index in Total_Costs_Tr_05.index:
    for column in Total_Costs_Tr_05.columns:
        Cost_Tr_05[column, index] = Total_Costs_Tr_05.loc[index,column]
        
Cost_Tr_20 = {}
        
for index in Total_Costs_Tr_20.index:
    for column in Total_Costs_Tr_20.columns:
        Cost_Tr_20[column, index] = Total_Costs_Tr_20.loc[index,column]
        
#Cost
#print(len(Cost))
#Demand_Dec
#Cost_Suez_Closed

CUS = list(Demand_2019.keys()) # Customer
SRC = list(Supply_2019.keys()) # Source
Supply_2019
Cost_Tr_05

def LNG_Model_3(Demand, Supply):
    
    model = ConcreteModel()
    model.dual = Suffix(direction=Suffix.IMPORT)
    
    CUS = list(Demand.keys()) 
    SRC = list(Supply.keys()) 

    model.x = Var(CUS, SRC, domain = NonNegativeReals)

    
    model.Cost = Objective(expr = sum([Cost[c,s]*model.x[c,s] for c in CUS for s in SRC]), sense = minimize)

    
    model.src = ConstraintList()
    for s in SRC:
        model.src.add(sum([model.x[c,s] for c in CUS]) <= Supply[s])
        
    model.dmd = ConstraintList()
    for c in CUS:
        model.dmd.add(sum([model.x[c,s] for s in SRC]) == Demand[c])
    
    model.div = ConstraintList()
    for c in CUS:
        for s in SRC:
            model.div.add(model.x[c,s] <= (1/3) * Demand[c])
            
    
    return model

if __name__ == "__main__":
    
    model_2019_Jan = LNG_Model_3(Demand_Jan, Supply_Jan)
    results_2019_Jan = SolverFactory('gurobi').solve(model_2019_Jan)
    
    model_2019_Feb = LNG_Model_3(Demand_Feb, Supply)
    results_2019_Feb = SolverFactory('gurobi').solve(model_2019_Feb)
    
    model_2019_Mar = LNG_Model_3(Demand_Mar, Supply)
    results_2019_Mar = SolverFactory('gurobi').solve(model_2019_Mar)
    
    model_2019_Apr = LNG_Model_3(Demand_Apr, Supply)
    results_2019_Apr = SolverFactory('gurobi').solve(model_2019_Apr)
    
    model_2019_May = LNG_Model_3(Demand_May, Supply)
    results_2019_May = SolverFactory('gurobi').solve(model_2019_May)
    
    model_2019_Jun = LNG_Model_3(Demand_Jun, Supply_Jun)
    results_2019_Jun = SolverFactory('gurobi').solve(model_2019_Jun)
    
    model_2019_Jul = LNG_Model_3(Demand_Jul, Supply)
    results_2019_Jul = SolverFactory('gurobi').solve(model_2019_Jul)
    
    model_2019_Aug = LNG_Model_3(Demand_Aug, Supply_Aug)
    results_2019_Aug = SolverFactory('gurobi').solve(model_2019_Aug)
    
    model_2019_Sep = LNG_Model_3(Demand_Sep, Supply_Sep)
    results_2019_Sep = SolverFactory('gurobi').solve(model_2019_Sep)
    
    model_2019_Oct = LNG_Model_3(Demand_Oct, Supply)
    results_2019_Oct = SolverFactory('gurobi').solve(model_2019_Oct)
    
    model_2019_Nov = LNG_Model_3(Demand_Nov, Supply_Nov)
    results_2019_Nov = SolverFactory('gurobi').solve(model_2019_Nov)
    
    model_2019_Dec = LNG_Model_3(Demand_Dec, Supply_Dec)
    results_2019_Dec = SolverFactory('gurobi').solve(model_2019_Dec)
    
    results_2019_Feb.write()

###############################################################################
### 3.1 January
###############################################################################
transported_LNG_3_Jan = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

Emissions_Jan = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_Jan.index:
    for importer in transported_LNG_3_Jan.columns:
        transported_LNG_3_Jan.loc[exporter, importer] = model_2019_Jan.x[importer, exporter]() / MMBtu_Gas / 1000000000
        
        
Merit_Order_3_Jan = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))


for i in transported_LNG_3_Jan.index:
    for j in transported_LNG_3_Jan.columns:
        if transported_LNG_3_Jan.loc[i,j] > 0:
            Merit_Order_3_Jan.loc[i,j] = TotalCosts.loc[i,j]

# print(transported_LNG_3_Jan)

Merit_Order_3_Jan

Sum_3_Jan = Merit_Order_3_Jan * transported_LNG_3_Jan * MMBtu_Gas * 1000000000

DES_Pr_3_Jan = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Jan.columns))),
                   
                   index = ["Jan"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Jan = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Jan.columns))),
                   
                   index = ["Jan"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Jan.loc["Jan"] = [10.5651, 9.2547, 6.279, 2.83, 2.2386, 1.1288, 1.632, 1.42, 1.741, 1.074, 2.353, 0.585, 1.7, 1.9584, 0.911, 0.3536, 0.0952]

Imp_3_Jan *= 10**9 * MMBtu_Gas
Imp_3_Jan

for column in Sum_3_Jan.columns:
    DES_Pr_3_Jan.loc["Jan", column] = Sum_3_Jan[column].sum()


DES_Pri_3_Jan = DES_Pr_3_Jan / Imp_3_Jan
DES_Price_3_Jan = DES_Pri_3_Jan.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_Jan.sort_values(by="Jan", ascending=False, inplace = True)

plt.rcParams['figure.dpi'] = 200
DES_Price_3_Jan.plot(kind = 'bar', color = 'orange', figsize=(9,6))
#transported_LNG_3_Jan
plt.savefig("Jan.svg")

###############################################################################
### 3.3 February
###############################################################################
transported_LNG_3_Feb = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

Emissions_Feb = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_Feb.index:
    for importer in transported_LNG_3_Feb.columns:
        transported_LNG_3_Feb.loc[exporter, importer] = model_2019_Feb.x[importer, exporter]() / MMBtu_Gas / 1000000000
        
        
Merit_Order_3_Feb = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))


for i in transported_LNG_3_Feb.index:
    for j in transported_LNG_3_Feb.columns:
        if transported_LNG_3_Feb.loc[i,j] > 0:
            Merit_Order_3_Feb.loc[i,j] = TotalCosts.loc[i,j]

# print(transported_LNG_3_Feb)

Sum_3_Feb = Merit_Order_3_Feb * transported_LNG_3_Feb * MMBtu_Gas * 1000000000

DES_Pr_3_Feb = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Feb.columns))),
                   
                   index = ["Feb"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Feb = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Feb.columns))),
                   
                   index = ["Feb"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Feb.loc["Feb"] = [10.30575, 5.93775, 4.095, 2.56, 1.46055, 0.9248, 1.83, 1.374, 1.17, 0.93, 1.782, 0.299, 1.768, 1.8496, 0.6528, 1.02, 0.3536]

Imp_3_Feb *= 10**9 * MMBtu_Gas
Imp_3_Feb

for column in Sum_3_Feb.columns:
    DES_Pr_3_Feb.loc["Feb", column] = Sum_3_Feb[column].sum()


DES_Pri_3_Feb = DES_Pr_3_Feb / Imp_3_Feb
DES_Price_3_Feb = DES_Pri_3_Feb.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_Feb.sort_values(by="Feb", ascending=False, inplace = True)

DES_Price_3_Feb.plot(kind = 'barh', color = 'orange', figsize=(10,6))

###############################################################################
### 3.4 March
###############################################################################
transported_LNG_3_Mar = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_Mar.index:
    for importer in transported_LNG_3_Mar.columns:
        transported_LNG_3_Mar.loc[exporter, importer] = model_2019_Mar.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_3_Mar = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for i in transported_LNG_3_Mar.index:
    for j in transported_LNG_3_Mar.columns:
        if transported_LNG_3_Mar.loc[i,j] > 0:
            Merit_Order_3_Mar.loc[i,j] = TotalCosts.loc[i,j]

Sum_3_Mar = Merit_Order_3_Mar * transported_LNG_3_Mar * MMBtu_Gas * 1000000000

DES_Pr_3_Mar = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Mar.columns))),
                   
                   index = ["Mar"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Mar = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Mar.columns))),
                   
                   index = ["Mar"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Mar.loc["Mar"] = [10.22385, 5.5419, 3.78105, 2.38, 2.0475, 1.2104, 2.335, 1.493, 1.78, 1.605, 1.4, 1.115, 2.1986, 1.6864, 0.9656, 0.9112, 0.1768]

Imp_3_Mar *= 10**9 * MMBtu_Gas
Imp_3_Mar

for column in Sum_3_Mar.columns:
    DES_Pr_3_Mar.loc["Mar", column] = Sum_3_Mar[column].sum()


DES_Pri_3_Mar = DES_Pr_3_Mar / Imp_3_Mar
DES_Price_3_Mar = DES_Pri_3_Mar.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_Mar.sort_values(by="Mar", ascending=False, inplace = True)

DES_Price_3_Mar.plot(kind = 'barh', color = 'orange', figsize=(10,6))

###############################################################################
### 3.5 April
###############################################################################
transported_LNG_3_Apr = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_Apr.index:
    for importer in transported_LNG_3_Apr.columns:
        transported_LNG_3_Apr.loc[exporter, importer] = model_2019_Apr.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_3_Apr = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for i in transported_LNG_3_Apr.index:
    for j in transported_LNG_3_Apr.columns:
        if transported_LNG_3_Apr.loc[i,j] > 0:
            Merit_Order_3_Apr.loc[i,j] = TotalCosts.loc[i,j]
            
Sum_3_Apr = Merit_Order_3_Apr * transported_LNG_3_Apr * MMBtu_Gas * 1000000000

DES_Pr_3_Apr = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Apr.columns))),
                   
                   index = ["Apr"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Apr = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Apr.columns))),
                   
                   index = ["Apr"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Apr.loc["Apr"] = [7.7532, 6.1971, 3.9585, 2.62, 2.0748, 1.1832, 2.572, 1.596, 2.244, 1.115, 0.707, 0.8074, 2.2168, 2.1624, 1.02, 1.0744, 0.748]

Imp_3_Apr *= 10**9 * MMBtu_Gas
Imp_3_Apr

for column in Sum_3_Apr.columns:
    DES_Pr_3_Apr.loc["Apr", column] = Sum_3_Apr[column].sum()


DES_Pri_3_Apr = DES_Pr_3_Apr / Imp_3_Apr
DES_Price_3_Apr = DES_Pri_3_Apr.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_Apr.sort_values(by="Apr", ascending=False, inplace = True)

DES_Price_3_Apr.plot(kind = 'barh', color = 'orange', figsize=(10,6))

###############################################################################
### 3.6 May
###############################################################################
transported_LNG_3_May = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_May.index:
    for importer in transported_LNG_3_May.columns:
        transported_LNG_3_May.loc[exporter, importer] = model_2019_May.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_3_May = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for i in transported_LNG_3_May.index:
    for j in transported_LNG_3_May.columns:
        if transported_LNG_3_May.loc[i,j] > 0:
            Merit_Order_3_May.loc[i,j] = TotalCosts.loc[i,j]

Sum_3_May = Merit_Order_3_May * transported_LNG_3_May * MMBtu_Gas * 1000000000

DES_Pr_3_May = pd.DataFrame(np.zeros((1,len(Merit_Order_3_May.columns))),
                   
                   index = ["May"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_May = pd.DataFrame(np.zeros((1,len(Merit_Order_3_May.columns))),
                   
                   index = ["May"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_May.loc["May"] = [7.7259, 6.04695, 4.05405, 2.75, 2.03385, 1.1152, 1.832, 1.656, 2.19, 1.115, 0.503, 0.7028, 2.9784, 2.4072, 0.9656, 1.1424, 1.4144]

Imp_3_May *= 10**9 * MMBtu_Gas
Imp_3_May

for column in Sum_3_May.columns:
    DES_Pr_3_May.loc["May", column] = Sum_3_May[column].sum()


DES_Pri_3_May = DES_Pr_3_May / Imp_3_May
DES_Price_3_May = DES_Pri_3_May.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_May.sort_values(by="May", ascending=False, inplace = True)

DES_Price_3_May.plot(kind = 'barh', color = 'orange', figsize=(10,6))

###############################################################################
### 3.7 June
###############################################################################
transported_LNG_3_Jun = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_Jun.index:
    for importer in transported_LNG_3_Jun.columns:
        transported_LNG_3_Jun.loc[exporter, importer] = model_2019_Jun.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_3_Jun = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for i in transported_LNG_3_Jun.index:
    for j in transported_LNG_3_Jun.columns:
        if transported_LNG_3_Jun.loc[i,j] > 0:
            Merit_Order_3_Jun.loc[i,j] = TotalCosts.loc[i,j]

Sum_3_Jun = Merit_Order_3_Jun * transported_LNG_3_Jun * MMBtu_Gas * 1000000000

DES_Pr_3_Jun = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Jun.columns))),
                   
                   index = ["Jun"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Jun = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Jun.columns))),
                   
                   index = ["Jun"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Jun.loc["Jun"] = [7.7259, 6.04695, 4.05405, 2.75, 2.03385, 1.1152, 1.832, 1.656, 2.19, 1.115, 0.503, 0.7028, 2.9784, 2.4072, 0.9656, 1.1424, 1.4144]

Imp_3_Jun *= 10**9 * MMBtu_Gas
Imp_3_Jun

for column in Sum_3_Jun.columns:
    DES_Pr_3_Jun.loc["Jun", column] = Sum_3_Jun[column].sum()


DES_Pri_3_Jun = DES_Pr_3_Jun / Imp_3_Jun
DES_Price_3_Jun = DES_Pri_3_Jun.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_Jun.sort_values(by="Jun", ascending=False, inplace = True)

DES_Price_3_Jun.plot(kind = 'barh', color = 'orange', figsize=(9,6))

###############################################################################
### 3.8 July
###############################################################################
transported_LNG_3_Jul = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_Jul.index:
    for importer in transported_LNG_3_Jul.columns:
        transported_LNG_3_Jul.loc[exporter, importer] = model_2019_Jul.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_3_Jul = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for i in transported_LNG_3_Jul.index:
    for j in transported_LNG_3_Jul.columns:
        if transported_LNG_3_Jul.loc[i,j] > 0:
            Merit_Order_3_Jul.loc[i,j] = TotalCosts.loc[i,j]

Sum_3_Jul = Merit_Order_3_Jul * transported_LNG_3_Jul * MMBtu_Gas * 1000000000

DES_Pr_3_Jul = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Jul.columns))),
                   
                   index = ["Jul"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Jul = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Jul.columns))),
                   
                   index = ["Jul"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Jul.loc["Jul"] = [7.2345, 6.18345, 4.54545, 2.73, 1.89735, 1.0744, 1.739, 1.903, 0.76, 1.387, 0.68, 0.6528, 2.0264, 2.312, 1.2784, 1.904, 1.3192]

Imp_3_Jul *= 10**9 * MMBtu_Gas
Imp_3_Jul

for column in Sum_3_Jul.columns:
    DES_Pr_3_Jul.loc["Jul", column] = Sum_3_Jul[column].sum()


DES_Pri_3_Jul = DES_Pr_3_Jul / Imp_3_Jul
DES_Price_3_Jul = DES_Pri_3_Jul.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_Jul.sort_values(by="Jul", ascending=False, inplace = True)

DES_Price_3_Jul.plot(kind = 'barh', color = 'orange', figsize=(9,6))

###############################################################################
### 3.9 August
###############################################################################
transported_LNG_3_Aug = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_Aug.index:
    for importer in transported_LNG_3_Aug.columns:
        transported_LNG_3_Aug.loc[exporter, importer] = model_2019_Aug.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_3_Aug = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for i in transported_LNG_3_Aug.index:
    for j in transported_LNG_3_Aug.columns:
        if transported_LNG_3_Aug.loc[i,j] > 0:
            Merit_Order_3_Aug.loc[i,j] = TotalCosts.loc[i,j]

Sum_3_Aug = Merit_Order_3_Aug * transported_LNG_3_Aug * MMBtu_Gas * 1000000000

DES_Pr_3_Aug = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Aug.columns))),
                   
                   index = ["Aug"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Aug = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Aug.columns))),
                   
                   index = ["Aug"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Aug.loc["Aug"] = [8.463, 7.5075, 4.914, 2.82, 1.8837, 1.0064, 1.638, 2.144, 0.19, 1.265, 0.816, 0.9112, 2.4888, 1.9176, 1.088, 1.7408, 1.8496]

Imp_3_Aug *= 10**9 * MMBtu_Gas
Imp_3_Aug

for column in Sum_3_Aug.columns:
    DES_Pr_3_Aug.loc["Aug", column] = Sum_3_Aug[column].sum()


DES_Pri_3_Aug = DES_Pr_3_Aug / Imp_3_Aug
DES_Price_3_Aug = DES_Pri_3_Aug.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_Aug.sort_values(by="Aug", ascending=False, inplace = True)

DES_Price_3_Aug.plot(kind = 'barh', color = 'orange', figsize=(10,6))

###############################################################################
### 3.10 September
###############################################################################
transported_LNG_3_Sep = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_Sep.index:
    for importer in transported_LNG_3_Sep.columns:
        transported_LNG_3_Sep.loc[exporter, importer] = model_2019_Sep.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_3_Sep = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for i in transported_LNG_3_Sep.index:
    for j in transported_LNG_3_Sep.columns:
        if transported_LNG_3_Sep.loc[i,j] > 0:
            Merit_Order_3_Sep.loc[i,j] = TotalCosts.loc[i,j]

Sum_3_Sep = Merit_Order_3_Sep * transported_LNG_3_Sep * MMBtu_Gas * 1000000000

DES_Pr_3_Sep = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Sep.columns))),
                   
                   index = ["Sep"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Sep = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Sep.columns))),
                   
                   index = ["Sep"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Sep.loc["Sep"] = [8.94075, 6.92055, 3.4125, 2.79, 2.0475, 0.9928, 1.2745, 2.139, 1.3, 1.13, 0.558, 0.2856, 2.3256, 1.8088, 1.0064, 1.0472, 1.5776]

Imp_3_Sep *= 10**9 * MMBtu_Gas
Imp_3_Sep

for column in Sum_3_Sep.columns:
    DES_Pr_3_Sep.loc["Sep", column] = Sum_3_Sep[column].sum()


DES_Pri_3_Sep = DES_Pr_3_Sep / Imp_3_Sep
DES_Price_3_Sep = DES_Pri_3_Sep.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_Sep.sort_values(by="Sep", ascending=False, inplace = True)

DES_Price_3_Sep.plot(kind = 'barh', color = 'orange', figsize=(10,6))

###############################################################################
### 3.11 October
###############################################################################
transported_LNG_3_Oct = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_Oct.index:
    for importer in transported_LNG_3_Oct.columns:
        transported_LNG_3_Oct.loc[exporter, importer] = model_2019_Oct.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_3_Oct = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for i in transported_LNG_3_Oct.index:
    for j in transported_LNG_3_Oct.columns:
        if transported_LNG_3_Oct.loc[i,j] > 0:
            Merit_Order_3_Oct.loc[i,j] = TotalCosts.loc[i,j]

Sum_3_Oct = Merit_Order_3_Oct * transported_LNG_3_Oct * MMBtu_Gas * 1000000000

DES_Pr_3_Oct = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Oct.columns))),
                   
                   index = ["Oct"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Oct = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Oct.columns))),
                   
                   index = ["Oct"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Oct.loc["Oct"] = [8.85885, 5.6511, 4.368, 2.83, 2.00655, 1.0608, 1.7745, 1.95, 1.85, 1.35, 0.843, 0.7616, 2.1986, 2.0944, 0.9248, 0.8024, 1.1016]

Imp_3_Oct *= 10**9 * MMBtu_Gas
Imp_3_Oct

for column in Sum_3_Oct.columns:
    DES_Pr_3_Oct.loc["Oct", column] = Sum_3_Oct[column].sum()


DES_Pri_3_Oct = DES_Pr_3_Oct / Imp_3_Oct
DES_Price_3_Oct = DES_Pri_3_Oct.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_Oct.sort_values(by="Oct", ascending=False, inplace = True)

DES_Price_3_Oct.plot(kind = 'barh', color = 'orange', figsize=(9,6))

###############################################################################
### 3.12 November
###############################################################################
transported_LNG_3_Nov = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_Nov.index:
    for importer in transported_LNG_3_Nov.columns:
        transported_LNG_3_Nov.loc[exporter, importer] = model_2019_Nov.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_3_Nov = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for i in transported_LNG_3_Nov.index:
    for j in transported_LNG_3_Nov.columns:
        if transported_LNG_3_Nov.loc[i,j] > 0:
            Merit_Order_3_Nov.loc[i,j] = TotalCosts.loc[i,j]

Sum_3_Nov = Merit_Order_3_Nov * transported_LNG_3_Nov * MMBtu_Gas * 1000000000

DES_Pr_3_Nov = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Nov.columns))),
                   
                   index = ["Nov"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Nov = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Nov.columns))),
                   
                   index = ["Nov"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Nov.loc["Nov"] = [8.83155, 8.66775, 5.1597, 2.79, 1.51515, 0.6664, 2.84, 1.931, 2.4, 0.94, 1.115, 1.0336, 3.876, 2.2848, 0.5984, 0.9384, 0.476]

Imp_3_Nov *= 10**9 * MMBtu_Gas
Imp_3_Nov

for column in Sum_3_Nov.columns:
    DES_Pr_3_Nov.loc["Nov", column] = Sum_3_Nov[column].sum()


DES_Pri_3_Nov = DES_Pr_3_Nov / Imp_3_Nov
DES_Price_3_Nov = DES_Pri_3_Nov.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_Nov.sort_values(by="Nov", ascending=False, inplace = True)

DES_Price_3_Nov.plot(kind = 'barh', color = 'orange', figsize=(10,6))

###############################################################################
### 3.13 December
###############################################################################
transported_LNG_3_Dec = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_Dec.index:
    for importer in transported_LNG_3_Dec.columns:
        transported_LNG_3_Dec.loc[exporter, importer] = model_2019_Dec.x[importer, exporter]() / MMBtu_Gas / 10**9


Merit_Order_3_Dec = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for i in transported_LNG_3_Dec.index:
    for j in transported_LNG_3_Dec.columns:
        if transported_LNG_3_Dec.loc[i,j] > 0:
            Merit_Order_3_Dec.loc[i,j] = TotalCosts.loc[i,j]
            
Sum_3_Dec = Merit_Order_3_Dec * transported_LNG_3_Dec * MMBtu_Gas * 1000000000

DES_Pr_3_Dec = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Dec.columns))),
                   
                   index = ["Dec"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Dec = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Dec.columns))),
                   
                   index = ["Dec"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_Dec.loc["Dec"] = [9.4185, 10.30575, 6.51105, 2.83, 1.7745, 0.9792, 2.56, 1.81, 3.05, 1.1, 1.89, 0.9928, 4.148, 2.0808, 0.9656, 0.5576, 0.276]

Imp_3_Dec *= 10**9 * MMBtu_Gas
Imp_3_Dec

for column in Sum_3_Dec.columns:
    DES_Pr_3_Dec.loc["Dec", column] = Sum_3_Dec[column].sum()


DES_Pri_3_Dec = DES_Pr_3_Dec / Imp_3_Dec
DES_Price_3_Dec = DES_Pri_3_Dec.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_Dec.sort_values(by="Dec", ascending=False, inplace = True)

DES_Price_3_Dec.plot(kind = 'barh', color = 'orange', figsize=(10,6))
transported_LNG_3_Dec

# ###############################################################################
# ### 4 Baseline (2019)
# ###############################################################################
# ### 4.1 Monthly DES Prices
# ###############################################################################
# Des_2019 = DES_Price_Jan
# Des_2019 = Des_2019.append(DES_Pri_3_Feb)
# Des_2019 = Des_2019.append(DES_Pri_3_Mar)
# Des_2019 = Des_2019.append(DES_Pri_3_Apr)
# Des_2019 = Des_2019.append(DES_Pri_3_May)
# Des_2019 = Des_2019.append(DES_Pri_3_Jun)
# Des_2019 = Des_2019.append(DES_Pri_3_Jul)
# Des_2019 = Des_2019.append(DES_Pri_3_Aug)
# Des_2019 = Des_2019.append(DES_Pri_3_Sep)
# Des_2019 = Des_2019.append(DES_Pri_3_Oct)
# Des_2019 = Des_2019.append(DES_Pri_3_Nov)
# Des_2019 = Des_2019.append(DES_Pri_3_Dec)

# Des_2019

# ax_monthly_DES = plt.gca()

# Des_2019.plot(kind='line', y='Japan', color = 'darkred', ax=ax_monthly_DES, figsize = (9, 6))
# Des_2019.plot(kind='line',y='China', ax=ax_monthly_DES, color = 'red')
# Des_2019.plot(kind='line',y='France', ax=ax_monthly_DES, color = 'dodgerblue')
# Des_2019.plot(kind='line',y='Other Europe', ax=ax_monthly_DES, color = 'green')
# Des_2019.plot(kind='line',y='UK', ax=ax_monthly_DES, color = 'orange')
# Des_2019.plot(kind='line',y='South Korea', ax=ax_monthly_DES, color = 'purple')
# #Des_2019.plot(kind='line',y='Pakistan', ax=ax_monthly_DES, color = 'grey')


# #ax.set_xlabel(fontsize = 12)
# ax_monthly_DES.set_ylabel("$/mmBtu", fontsize = 12)
# plt.legend(bbox_to_anchor=(1, 0.5))
# plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)
# plt.show()
# plt.savefig("Monthly_DES_Prices_2019.svg")
# #Des_2019

# ###############################################################################
# ### 4.2 Monthly costs
# ###############################################################################
# Monthly_Costs = pd.DataFrame([(round(model_2019_Jan.Cost() / 10**9, 2),
#                round(model_2019_Feb.Cost() / 10**9, 2),
#                round(model_2019_Mar.Cost() / 10**9, 2),
#                round(model_2019_Apr.Cost() / 10**9, 2),
#                round(model_2019_May.Cost() / 10**9, 2),
#                round(model_2019_Jun.Cost() / 10**9, 2),
#                round(model_2019_Jul.Cost() / 10**9, 2),
#                round(model_2019_Aug.Cost() / 10**9, 2),
#                round(model_2019_Sep.Cost() / 10**9, 2),
#                round(model_2019_Oct.Cost() / 10**9, 2),
#                round(model_2019_Nov.Cost() / 10**9, 2),
#                round(model_2019_Dec.Cost() / 10**9, 2))],
                   
#                    index = ["Monthly Costs for Imported LNG"], #"Import (MMBtu)"
    
#                    columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
#                               "Jul", "Aug","Sep", "Oct", "Nov", "Dec"]).T


# ax_monthly_costs = Monthly_Costs.plot(figsize = (9, 6), kind="bar", color="lightcoral", rot=0, width=0.7)
# for container in ax_monthly_costs.containers:
#     ax_monthly_costs.bar_label(container)

# ax_monthly_costs.set_ylabel("Billions of $")    
# plt.legend(bbox_to_anchor=(1.0, 1.0))
# ax_monthly_costs.get_legend().remove()
# plt.show()
# plt.savefig("Monthly_Costs_for_Imported_LNG.svg")

# ###############################################################################
# ### 4.3 Transported Volumes
# ###############################################################################
# Transported_LNG_2019 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
#                     index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"],

#                     columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"))

# Transported_LNG_2019 = transported_LNG_3_Jan + transported_LNG_3_Feb + transported_LNG_3_Mar + transported_LNG_3_Apr + transported_LNG_3_May + transported_LNG_3_Jun + transported_LNG_3_Jul + transported_LNG_3_Aug + transported_LNG_3_Sep + transported_LNG_3_Oct + transported_LNG_3_Nov + transported_LNG_3_Dec
# Transported_LNG_2019

# ###############################################################################
# ### 4.4 LNG Shippments Table and Sankey Diagram
# ###############################################################################
# colours_exp = ["steelblue", "orange", "mediumseagreen", "lightcoral", "purple", "peru",
#            "deeppink", "gray", "gold", "turquoise", "cornflowerblue", "lime",
#            "teal",  "darksalmon", "slateblue"]

# colours_imp = ["crimson", "red", "lightskyblue", "saddlebrown", "lightsalmon", "seagreen",
#                    "dodgerblue", "darkorange", "mediumblue", "limegreen", "darkred", "indigo",
#                    "yellow", "purple", "steelblue", "seagreen", "springgreen"]

# # Generate a colour pallet to let us colour in each line
# palette = sns.color_palette("pastel", len(Transported_LNG_2019.index))
# colours = palette.as_hex()

# colours_exp = ["steelblue", "orange", "mediumseagreen", "lightcoral", "purple", "peru",
#            "deeppink", "gray", "gold", "turquoise", "cornflowerblue", "lime",
#            "teal",  "darksalmon", "slateblue"]

# colours_imp = ["crimson", "red", "lightskyblue", "saddlebrown", "lightsalmon", "seagreen",
#                    "dodgerblue", "darkorange", "mediumblue", "limegreen", "darkred", "indigo",
#                    "yellow", "purple", "steelblue", "seagreen", "springgreen"]
# # Nodes & links

# nodes = [['ID', 'Label', 'Color'],
#          [0,'Qatar','steelblue'],
#         [1,'Australia','darkorange'],
#         [2,'USA','mediumseagreen'],
#         [3,'Russia','lightcoral'],
#         [4,'Malaysia','purple'],
#         [5,'Nigeria','peru'],
#         [6,'Trinidad & Tobago','deeppink'],
#         [7,'Algeria','gray'],
#         [8,'Indonesia','gold'],
#         [9,'Oman','turquoise'],
#          [10,"Other Asia Pacific",'cornflowerblue'],
#          [11,"Other Europe",'sandybrown'],
#          [12,'Other Americas','teal'],
#          [13,'Other Middle East','darksalmon'],
#          [14,'Other Africa','slateblue'], 
#          [15,'Japan','crimson'], 
#          [16,'China','red'],
#          [17,'South Korea','lightskyblue'],
#          [18,'India','saddlebrown'],
#          [19,'Taiwan','lightsalmon'],
#          [20,'Pakistan','seagreen'],
#          [21,'France','dodgerblue'],
#          [22,'Spain','darkorange'],
#          [23,'UK','mediumblue'],
#          [24,'Italy','limegreen'],
#          [25,'Turkey','darkred'],
#          [26,'Belgium','indigo'],
#          [27,'Other Asia Pacific','yellow'],
#          [28,'Other Europe','purple'],
#          [29,'Total North America','steelblue'],
#          [30,'Total S. & C. America','seagreen'],
#          [31,'Total ME & Africa','springgreen'],
#         ]



# # links with your data
# links = [['Source','Target','Value','Link Color']]

# c_count = 0 #colour counter
# i = 0 
# j = 14

# for index in Transported_LNG_2019.index:
#     for column in Transported_LNG_2019.columns:
#         j += 1
#         if Transported_LNG_2019.loc[index, column] != 0:
#             links.append([i, j, Transported_LNG_2019.loc[index, column], colours[c_count]])
#             #print(i+1,",", j+1, ",", Transported_LNG_3.loc[index, column])
#     i += 1
#     j = 14
#     c_count += 1

# #links

# # Retrieve headers and build dataframes
# nodes_headers = nodes.pop(0)
# links_headers = links.pop(0)
# df_nodes = pd.DataFrame(nodes, columns = nodes_headers)
# df_links = pd.DataFrame(links, columns = links_headers)

# # Sankey plot setup
# data_trace = dict(
#     type='sankey',
#     domain = dict(
#       x =  [0,1],
#       y =  [0,1]
#     ),
#     orientation = "h",
#     valueformat = ".0f",
#     node = dict(
#       pad = 14,
#      thickness = 45,
#       line = dict(
#         color = "black",
#         width = 0
#       ),
#       label =  df_nodes['Label'].dropna(axis=0, how='any'),
#       color = df_nodes['Color']
#     ),
#     link = dict(
#       source = df_links['Source'].dropna(axis=0, how='any'),
#       target = df_links['Target'].dropna(axis=0, how='any'),
#       value = df_links['Value'].dropna(axis=0, how='any'),
#       color = df_links['Link Color'].dropna(axis=0, how='any'),
#   )
# )

# layout = dict(
#               width=1000, height=1000,
#               paper_bgcolor = "white",
#               #title = "LNG Shipments",
#               font = dict(size = 15)
#              )

# fig_LNG_shipment = dict(data=[data_trace], layout=layout)
# iplot(fig_LNG_shipment, validate=False)
# #plt.rcParams['figure.dpi'] = 200

# ###############################################################################
# ### 4.5 Number of Carriers
# ###############################################################################
# LNG_Carrier_Number_Jan = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
#                     index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"],

#                     columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"))

# LNG_Carrier_Number_Feb = LNG_Carrier_Number_Mar = LNG_Carrier_Number_Apr = LNG_Carrier_Number_May = LNG_Carrier_Number_Jun = LNG_Carrier_Number_Jul = LNG_Carrier_Number_Aug = LNG_Carrier_Number_Sep = LNG_Carrier_Number_Oct = LNG_Carrier_Number_Nov = LNG_Carrier_Number_Dec = LNG_Carrier_Number_Jan

# LNG_Carrier_Number_Jan = (transported_LNG_3_Jan*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/31
# JanC = round(LNG_Carrier_Number_Jan.to_numpy().sum())

# LNG_Carrier_Number_Feb = (transported_LNG_3_Feb*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/28
# FebC = round(LNG_Carrier_Number_Feb.to_numpy().sum())

# LNG_Carrier_Number_Mar = (transported_LNG_3_Mar*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/31
# MarC = round(LNG_Carrier_Number_Mar.to_numpy().sum())

# LNG_Carrier_Number_Apr = (transported_LNG_3_Apr*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/30
# AprC = round(LNG_Carrier_Number_Apr.to_numpy().sum())

# LNG_Carrier_Number_May = (transported_LNG_3_May*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/31
# MayC = round(LNG_Carrier_Number_May.to_numpy().sum())

# LNG_Carrier_Number_Jun = (transported_LNG_3_Jun*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/30
# JunC = round(LNG_Carrier_Number_Jun.to_numpy().sum())

# LNG_Carrier_Number_Jul = (transported_LNG_3_Jul*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/31
# JulC = round(LNG_Carrier_Number_Jul.to_numpy().sum())

# LNG_Carrier_Number_Aug = (transported_LNG_3_Aug*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/31
# AugC = round(LNG_Carrier_Number_Aug.to_numpy().sum())

# LNG_Carrier_Number_Sep = (transported_LNG_3_Sep*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/30
# SepC = round(LNG_Carrier_Number_Sep.to_numpy().sum())

# LNG_Carrier_Number_Oct = (transported_LNG_3_Oct*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/31
# OctC = round(LNG_Carrier_Number_Oct.to_numpy().sum())

# LNG_Carrier_Number_Nov = (transported_LNG_3_Nov*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/30
# NovC = round(LNG_Carrier_Number_Nov.to_numpy().sum())

# LNG_Carrier_Number_Dec = (transported_LNG_3_Dec*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/31
# DecC = round(LNG_Carrier_Number_Dec.to_numpy().sum())

# LNG_Carr_2019 = [JanC, FebC, MarC, AprC, MayC, JunC, JulC, AugC, SepC, OctC, NovC, DecC]


# LNG_Carriers_2019 = pd.DataFrame(LNG_Carr_2019,
                   
#                    index = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
#                             "Jul", "Aug","Sep", "Oct", "Nov", "Dec"], #"Import (MMBtu)"
    
#                    columns = ["Number of LNG Carriers"])


# ax_LNG_carriers = LNG_Carriers_2019.plot(figsize = (9, 6), kind="bar", color = "orange", rot=0, width=0.7)
# for container in ax_LNG_carriers.containers:
#     ax_LNG_carriers.bar_label(container)
    
# plt.legend(bbox_to_anchor=(1.0, 1.0))
# ax_LNG_carriers.get_legend().remove()
# plt.show()
# #LNG_Carrier_Number_Jan
# #plt.savefig("Number of LNG Carriers.svg")

# ###############################################################################
# ### 4.6 Monthly Transport Emissions 2019
# ###############################################################################
# Emissions_CO2_Jan_ = (transported_LNG_3_Jan*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)#* CO2_Emissions
# Emissions_CO2_Jan_

# Emissions_CO2_Jan = (transported_LNG_3_Jan*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time) * CO2_Emissions
# Jan_CO2 = round(Emissions_CO2_Jan.to_numpy().sum()/10**6,2)

# Emissions_CO2_Feb = CO2_Emissions * (transported_LNG_3_Feb*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Feb_CO2 = round(Emissions_CO2_Feb.to_numpy().sum()/10**6,2)

# Emissions_CO2_Mar = CO2_Emissions * (transported_LNG_3_Mar*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Mar_CO2 = round(Emissions_CO2_Mar.to_numpy().sum()/10**6,2)

# Emissions_CO2_Apr = CO2_Emissions * (transported_LNG_3_Apr*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Apr_CO2 = round(Emissions_CO2_Apr.to_numpy().sum()/10**6,2)

# Emissions_CO2_May = CO2_Emissions * (transported_LNG_3_May*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# May_CO2 = round(Emissions_CO2_May.to_numpy().sum()/10**6,2)

# Emissions_CO2_Jun = CO2_Emissions * (transported_LNG_3_Jun*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Jun_CO2 = round(Emissions_CO2_Jun.to_numpy().sum()/10**6,2)

# Emissions_CO2_Jul = CO2_Emissions * (transported_LNG_3_Jul*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Jul_CO2 = round(Emissions_CO2_Jul.to_numpy().sum()/10**6,2)

# Emissions_CO2_Aug = CO2_Emissions * (transported_LNG_3_Aug*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Aug_CO2 = round(Emissions_CO2_Aug.to_numpy().sum()/10**6,2)

# Emissions_CO2_Sep = CO2_Emissions * (transported_LNG_3_Sep*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Sep_CO2 = round(Emissions_CO2_Sep.to_numpy().sum()/10**6,2)

# Emissions_CO2_Oct = CO2_Emissions * (transported_LNG_3_Oct*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Oct_CO2 = round(Emissions_CO2_Oct.to_numpy().sum()/10**6,2)

# Emissions_CO2_Nov = CO2_Emissions * (transported_LNG_3_Nov*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Nov_CO2 = round(Emissions_CO2_Nov.to_numpy().sum()/10**6,2)

# Emissions_CO2_Dec = CO2_Emissions * (transported_LNG_3_Dec*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Dec_CO2 = round(Emissions_CO2_Dec.to_numpy().sum()/10**6,2)


# Emi_2019_CO2 = [Jan_CO2, Feb_CO2, Mar_CO2, Apr_CO2, May_CO2, Jun_CO2,
#             Jul_CO2, Aug_CO2, Sep_CO2, Oct_CO2, Nov_CO2, Dec_CO2]

# Emissions_2019_CO2 = pd.DataFrame(Emi_2019_CO2,
                   
#                    index = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
#                             "Jul", "Aug","Sep", "Oct", "Nov", "Dec"], #"Import (MMBtu)"
    
#                    columns = ["CO2 Emissions"])


# ax = Emissions_2019_CO2.plot(figsize = (9, 6), kind="bar", color = "lightgray", rot=0, width=0.7)
# for container in ax.containers:
#     ax.bar_label(container)

# ax.set_ylabel("megatonnes")    
    
# plt.legend(bbox_to_anchor=(1.0, 1.0))
# ax.get_legend().remove()
# plt.show()
                                           
# CO2_per_mmBtu = Emissions_2019_CO2.to_numpy().sum()#/(Transported_LNG_2019.to_numpy().sum() * MMBtu_Gas * 10**3)
# CO2_per_mmBtu

# #Emissions_CO2_Jan

# CO2_2019 = Emissions_CO2_Jan + Emissions_CO2_Feb + Emissions_CO2_Mar + Emissions_CO2_Apr + Emissions_CO2_May + Emissions_CO2_Jun + Emissions_CO2_Jul + Emissions_CO2_Aug + Emissions_CO2_Sep + Emissions_CO2_Oct + Emissions_CO2_Nov + Emissions_CO2_Dec
# #CO2_2019.to_numpy().sum()
# CO2_2019

# Emissions_CH4_Jan = CH4_Emissions * (transported_LNG_3_Jan*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Jan_CH4 = round(Emissions_CH4_Jan.to_numpy().sum()/10**3,2)

# Emissions_CH4_Feb = CH4_Emissions * (transported_LNG_3_Feb*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Feb_CH4 = round(Emissions_CH4_Feb.to_numpy().sum()/10**3,2)

# Emissions_CH4_Mar = CH4_Emissions * (transported_LNG_3_Mar*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Mar_CH4 = round(Emissions_CH4_Mar.to_numpy().sum()/10**3,2)

# Emissions_CH4_Apr = CH4_Emissions * (transported_LNG_3_Apr*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Apr_CH4 = round(Emissions_CH4_Apr.to_numpy().sum()/10**3,2)

# Emissions_CH4_May = CH4_Emissions * (transported_LNG_3_May*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# May_CH4 = round(Emissions_CH4_May.to_numpy().sum()/10**3,2)

# Emissions_CH4_Jun = CH4_Emissions * (transported_LNG_3_Jun*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Jun_CH4 = round(Emissions_CH4_Jun.to_numpy().sum()/10**3,2)

# Emissions_CH4_Jul = CH4_Emissions * (transported_LNG_3_Jul*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Jul_CH4 = round(Emissions_CH4_Jul.to_numpy().sum()/10**3,2)

# Emissions_CH4_Aug = CH4_Emissions * (transported_LNG_3_Aug*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Aug_CH4 = round(Emissions_CH4_Aug.to_numpy().sum()/10**3,2)

# Emissions_CH4_Sep = CH4_Emissions * (transported_LNG_3_Sep*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Sep_CH4 = round(Emissions_CH4_Sep.to_numpy().sum()/10**3,2)

# Emissions_CH4_Oct = CH4_Emissions * (transported_LNG_3_Oct*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Oct_CH4 = round(Emissions_CH4_Oct.to_numpy().sum()/10**3,2)

# Emissions_CH4_Nov = CH4_Emissions * (transported_LNG_3_Nov*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Nov_CH4 = round(Emissions_CH4_Nov.to_numpy().sum()/10**3,2)

# Emissions_CH4_Dec = CH4_Emissions * (transported_LNG_3_Dec*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
# Dec_CH4 = round(Emissions_CH4_Dec.to_numpy().sum()/10**3,2)


# Emi_2019_CH4 = [Jan_CH4, Feb_CH4, Mar_CH4, Apr_CH4, May_CH4, Jun_CH4,
#                 Jul_CH4, Aug_CH4, Sep_CH4, Oct_CH4, Nov_CH4, Dec_CH4]

# Emissions_2019_CH4 = pd.DataFrame(Emi_2019_CH4,
                   
#                    index = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
#                             "Jul", "Aug","Sep", "Oct", "Nov", "Dec"], #"Import (MMBtu)"
    
#                    columns = ["CH4 Emissions"])


# ax = Emissions_2019_CH4.plot(figsize = (9, 6), kind="bar", color = "grey", rot=0, width=0.7)
# for container in ax.containers:
#     ax.bar_label(container)

# ax.set_ylabel("kilotonnes")    
# plt.legend(bbox_to_anchor=(1.0, 1.0))
# ax.get_legend().remove()
# plt.show()

# Emissions_2019_CH4.to_numpy().sum()

# CH4_2019 = Emissions_CH4_Jan + Emissions_CH4_Feb + Emissions_CH4_Mar + Emissions_CH4_Apr + Emissions_CH4_May + Emissions_CH4_Jun + Emissions_CH4_Jul + Emissions_CH4_Aug + Emissions_CH4_Sep + Emissions_CH4_Oct + Emissions_CH4_Nov + Emissions_CH4_Dec
# CH4_2019.to_numpy().sum()
# #CH4_2019
# CH4_per_mmBtu = Emissions_2019_CH4.to_numpy().sum()/(Transported_LNG_2019.to_numpy().sum() * MMBtu_Gas * 10**3)
# CH4_per_mmBtu

# ###############################################################################
# ### 5 Shadow Prices
# ###############################################################################
# ### 5.1 Analysis by exporting nodes
# ###############################################################################
# dual_export_Jan = pd.DataFrame(np.zeros((1, len(export_countries))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])


# for m in model_2019_Jan.src.keys():
#     s = SRC[m-1]
#     dual_export_Jan.loc["Shadow Price ($/MMBtu)", s] = model_2019_Jan.dual[model_2019_Jan.src[m]]
#     print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_Jan[s]/MMBtu_Gas/10**9,model_2019_Jan.src[m]()/MMBtu_Gas/10**9,model_2019_Jan.dual[model_2019_Jan.src[m]]))

# Dual_Export_Jan = dual_export_Jan.T
# #Dual_Export

# Dual_Export_Jan.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_Jan.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_export_Feb = pd.DataFrame(np.zeros((1, len(Merit_Order_3_Feb.index))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])


# for m in model_2019_Feb.src.keys():
#     s = SRC[m-1]
#     dual_export_Feb.loc["Shadow Price ($/MMBtu)", s] = model_2019_Feb.dual[model_2019_Feb.src[m]]
#     print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply[s]/MMBtu_Gas/10**9,model_2019_Feb.src[m]()/MMBtu_Gas/10**9,model_2019_Feb.dual[model_2019_Feb.src[m]]))

# Dual_Export_Feb = dual_export_Feb.T
# #Dual_Export

# Dual_Export_Feb.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_Feb.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_export_Mar = pd.DataFrame(np.zeros((1, len(Merit_Order_3_Mar.index))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])


# for m in model_2019_Mar.src.keys():
#         s = SRC[m-1]
#         dual_export_Mar.loc["Shadow Price ($/MMBtu)", s] = model_2019_Mar.dual[model_2019_Mar.src[m]]
#         print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply[s]/MMBtu_Gas/10**9,model_2019_Mar.src[m]()/MMBtu_Gas/10**9,model_2019_Mar.dual[model_2019_Mar.src[m]]))

# Dual_Export_Mar = dual_export_Mar.T
# #Dual_Export

# Dual_Export_Mar.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_Mar.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_export_Apr = pd.DataFrame(np.zeros((1, len(Merit_Order_3_Apr.index))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])


# for m in model_2019_Apr.src.keys():
#         s = SRC[m-1]
#         dual_export_Apr.loc["Shadow Price ($/MMBtu)", s] = model_2019_Apr.dual[model_2019_Apr.src[m]]
#         print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply[s]/MMBtu_Gas/10**9,model_2019_Apr.src[m]()/MMBtu_Gas/10**9,model_2019_Apr.dual[model_2019_Apr.src[m]]))


# Dual_Export_Apr = dual_export_Apr.T
# #Dual_Export

# Dual_Export_Apr.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_Apr.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_export_May = pd.DataFrame(np.zeros((1, len(Merit_Order_3_May.index))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])


# for m in model_2019_May.src.keys():
#         s = SRC[m-1]
#         dual_export_May.loc["Shadow Price ($/MMBtu)", s] = model_2019_May.dual[model_2019_May.src[m]]
#         print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply[s]/MMBtu_Gas/10**9,model_2019_May.src[m]()/MMBtu_Gas/10**9,model_2019_May.dual[model_2019_May.src[m]]))


# Dual_Export_May = dual_export_May.T
# #Dual_Export

# Dual_Export_May.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_May.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_export_Jun = pd.DataFrame(np.zeros((1, len(Merit_Order_3_Jun.index))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])


# for m in model_2019_Jun.src.keys():
#         s = SRC[m-1]
#         dual_export_Jun.loc["Shadow Price ($/MMBtu)", s] = model_2019_Jun.dual[model_2019_Jun.src[m]]
#         print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_Jun[s]/MMBtu_Gas/10**9,model_2019_Jun.src[m]()/MMBtu_Gas/10**9,model_2019_Jun.dual[model_2019_Jun.src[m]]))


# Dual_Export_Jun = dual_export_Jun.T
# #Dual_Export

# Dual_Export_Jun.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_Jun.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_export_Jul = pd.DataFrame(np.zeros((1, len(Merit_Order_3_Jul.index))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])


# for m in model_2019_Jul.src.keys():
#         s = SRC[m-1]
#         dual_export_Jul.loc["Shadow Price ($/MMBtu)", s] = model_2019_Jul.dual[model_2019_Jul.src[m]]
#         print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply[s]/MMBtu_Gas/10**9,model_2019_Jul.src[m]()/MMBtu_Gas/10**9,model_2019_Jul.dual[model_2019_Jul.src[m]]))


# Dual_Export_Jul = dual_export_Jul.T
# #Dual_Export

# Dual_Export_Jul.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_Jul.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_export_Aug = pd.DataFrame(np.zeros((1, len(Merit_Order_3_Aug.index))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])


# for m in model_2019_Aug.src.keys():
#         s = SRC[m-1]
#         dual_export_Aug.loc["Shadow Price ($/MMBtu)", s] = model_2019_Aug.dual[model_2019_Aug.src[m]]
#         print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_Aug[s]/MMBtu_Gas/10**9,model_2019_Aug.src[m]()/MMBtu_Gas/10**9,model_2019_Aug.dual[model_2019_Aug.src[m]]))

# Dual_Export_Aug = dual_export_Aug.T
# #Dual_Export

# Dual_Export_Aug.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_Aug.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_export_Sep = pd.DataFrame(np.zeros((1, len(Merit_Order_3_Sep.index))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])

# for m in model_2019_Sep.src.keys():
#         s = SRC[m-1]
#         dual_export_Sep.loc["Shadow Price ($/MMBtu)", s] = model_2019_Sep.dual[model_2019_Sep.src[m]]
#         print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_Sep[s]/MMBtu_Gas/10**9,model_2019_Sep.src[m]()/MMBtu_Gas/10**9,model_2019_Sep.dual[model_2019_Sep.src[m]]))

# Dual_Export_Sep = dual_export_Sep.T
# #Dual_Export

# Dual_Export_Sep.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_Sep.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_export_Oct = pd.DataFrame(np.zeros((1, len(Merit_Order_3_Oct.index))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])

# for m in model_2019_Oct.src.keys():
#         s = SRC[m-1]
#         dual_export_Oct.loc["Shadow Price ($/MMBtu)", s] = model_2019_Oct.dual[model_2019_Oct.src[m]]
#         print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply[s]/MMBtu_Gas/10**9,model_2019_Oct.src[m]()/MMBtu_Gas/10**9,model_2019_Oct.dual[model_2019_Oct.src[m]]))

# Dual_Export_Oct = dual_export_Oct.T
# #Dual_Export

# Dual_Export_Oct.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_Oct.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_export_Nov = pd.DataFrame(np.zeros((1, len(Merit_Order_3_Nov.index))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])

# for m in model_2019_Nov.src.keys():
#         s = SRC[m-1]
#         dual_export_Nov.loc["Shadow Price ($/MMBtu)", s] = model_2019_Nov.dual[model_2019_Nov.src[m]]
#         print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_Nov[s]/MMBtu_Gas/10**9,model_2019_Nov.src[m]()/MMBtu_Gas/10**9,model_2019_Nov.dual[model_2019_Nov.src[m]]))

# Dual_Export_Nov = dual_export_Nov.T
# #Dual_Export

# Dual_Export_Nov.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_Nov.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_export_Dec = pd.DataFrame(np.zeros((1, len(Merit_Order_3_Dec.index))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
#                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
#                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])

# for m in model_2019_Dec.src.keys():
#         s = SRC[m-1]
#         dual_export_Dec.loc["Shadow Price ($/MMBtu)", s] = model_2019_Dec.dual[model_2019_Dec.src[m]]
#         print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_Dec[s]/MMBtu_Gas/10**9,model_2019_Dec.src[m]()/MMBtu_Gas/10**9,model_2019_Dec.dual[model_2019_Dec.src[m]]))

# Dual_Export_Dec = dual_export_Dec.T
# #Dual_Export

# Dual_Export_Dec.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_Dec.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# Exporter_Shadow = dual_export_Jan
# Exporter_Shadow = Exporter_Shadow.append(dual_export_Feb)
# Exporter_Shadow = Exporter_Shadow.append(dual_export_Mar)
# Exporter_Shadow = Exporter_Shadow.append(dual_export_Apr)
# Exporter_Shadow = Exporter_Shadow.append(dual_export_May)
# Exporter_Shadow = Exporter_Shadow.append(dual_export_Jun)
# Exporter_Shadow = Exporter_Shadow.append(dual_export_Jul)
# Exporter_Shadow = Exporter_Shadow.append(dual_export_Aug)
# Exporter_Shadow = Exporter_Shadow.append(dual_export_Sep)
# Exporter_Shadow = Exporter_Shadow.append(dual_export_Oct)
# Exporter_Shadow = Exporter_Shadow.append(dual_export_Nov)
# Exporter_Shadow = Exporter_Shadow.append(dual_export_Dec)

# Months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
#           "Oct", "Nov", "Dec"]

# idx = pd.Index(Months)
# Exporter_Shadow = Exporter_Shadow.set_index(idx)

# ax = Exporter_Shadow.plot(figsize = (9, 6), color = colours_exp)
# plt.legend(bbox_to_anchor=(1.05, 0.875))
# ax.set_ylabel("$/mmBtu", fontsize = 11)
# plt.show()

# #Exporter_Shadow.T

# ###############################################################################
# ### 5.2 Analysis by importing nodes
# ###############################################################################
# dual_import_Jan = pd.DataFrame(np.zeros((1,len(import_countries))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"])



# for n in model_2019_Jan.dmd.keys():
#         c = CUS[n-1]
#         dual_import_Jan.loc["Shadow Price ($/MMBtu)", c] = model_2019_Jan.dual[model_2019_Jan.dmd[n]]
#         print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_Jan[c]/MMBtu_Gas/10**9,model_2019_Jan.dmd[n]()/MMBtu_Gas/10**9,model_2019_Jan.dual[model_2019_Jan.dmd[n]]))

# Dual_Import_Jan = dual_import_Jan.T
# Dual_Import_Jan

# Dual_Import_Jan.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
# ax = Dual_Import_Jan.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="blue")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_import_Feb = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Feb.columns))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"])


# for n in model_2019_Feb.dmd.keys():
#         c = CUS[n-1]
#         dual_import_Feb.loc["Shadow Price ($/MMBtu)", c] = model_2019_Feb.dual[model_2019_Feb.dmd[n]]
#         print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_Feb[c]/MMBtu_Gas/10**9,model_2019_Feb.dmd[n]()/MMBtu_Gas/10**9,model_2019_Feb.dual[model_2019_Feb.dmd[n]]))

# Dual_Import_Feb = dual_import_Feb.T
# Dual_Import_Feb

# Dual_Import_Feb.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
# ax = Dual_Import_Feb.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="blue")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_import_Mar = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Mar.columns))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"])


# for n in model_2019_Mar.dmd.keys():
#         c = CUS[n-1]
#         dual_import_Mar.loc["Shadow Price ($/MMBtu)", c] = model_2019_Mar.dual[model_2019_Mar.dmd[n]]
#         print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_Mar[c]/MMBtu_Gas/10**9,model_2019_Mar.dmd[n]()/MMBtu_Gas/10**9,model_2019_Mar.dual[model_2019_Mar.dmd[n]]))

# Dual_Import_Mar = dual_import_Mar.T
# Dual_Import_Mar

# Dual_Import_Mar.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
# ax = Dual_Import_Mar.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="blue")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_import_Apr = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Apr.columns))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"])


# for n in model_2019_Apr.dmd.keys():
#         c = CUS[n-1]
#         dual_import_Apr.loc["Shadow Price ($/MMBtu)", c] = model_2019_Apr.dual[model_2019_Apr.dmd[n]]
#         print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_Apr[c]/MMBtu_Gas/10**9,model_2019_Apr.dmd[n]()/MMBtu_Gas/10**9,model_2019_Apr.dual[model_2019_Apr.dmd[n]]))

# Dual_Import_Apr = dual_import_Apr.T
# Dual_Import_Apr

# Dual_Import_Apr.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
# ax = Dual_Import_Apr.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="blue")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_import_May = pd.DataFrame(np.zeros((1,len(Merit_Order_3_May.columns))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"])


# for n in model_2019_May.dmd.keys():
#         c = CUS[n-1]
#         dual_import_May.loc["Shadow Price ($/MMBtu)", c] = model_2019_May.dual[model_2019_May.dmd[n]]
#         print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_May[c]/MMBtu_Gas/10**9,model_2019_May.dmd[n]()/MMBtu_Gas/10**9,model_2019_May.dual[model_2019_May.dmd[n]]))

# Dual_Import_May = dual_import_May.T
# Dual_Import_May

# Dual_Import_May.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
# ax = Dual_Import_May.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="blue")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_import_Jun = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Jun.columns))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"])


# for n in model_2019_Jun.dmd.keys():
#         c = CUS[n-1]
#         dual_import_Jun.loc["Shadow Price ($/MMBtu)", c] = model_2019_Jun.dual[model_2019_Jun.dmd[n]]
#         print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_Jun[c]/MMBtu_Gas/10**9,model_2019_Jun.dmd[n]()/MMBtu_Gas/10**9,model_2019_Jun.dual[model_2019_Jun.dmd[n]]))

# Dual_Import_Jun = dual_import_Jun.T
# Dual_Import_Jun

# Dual_Import_Jun.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
# ax = Dual_Import_Jun.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="blue")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_import_Jul = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Jul.columns))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"])


# for n in model_2019_Jul.dmd.keys():
#         c = CUS[n-1]
#         dual_import_Jul.loc["Shadow Price ($/MMBtu)", c] = model_2019_Jul.dual[model_2019_Jul.dmd[n]]
#         print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_Jul[c]/MMBtu_Gas/10**9,model_2019_Jul.dmd[n]()/MMBtu_Gas/10**9,model_2019_Jul.dual[model_2019_Jul.dmd[n]]))

# Dual_Import_Jul = dual_import_Jul.T
# Dual_Import_Jul

# Dual_Import_Jul.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
# ax = Dual_Import_Jul.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="blue")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_import_Aug = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Aug.columns))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"])



# for n in model_2019_Aug.dmd.keys():
#         c = CUS[n-1]
#         dual_import_Aug.loc["Shadow Price ($/MMBtu)", c] = model_2019_Aug.dual[model_2019_Aug.dmd[n]]
#         print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_Aug[c]/MMBtu_Gas/10**9,model_2019_Aug.dmd[n]()/MMBtu_Gas/10**9,model_2019_Aug.dual[model_2019_Aug.dmd[n]]))

# Dual_Import_Aug = dual_import_Aug.T
# Dual_Import_Aug

# Dual_Import_Aug.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
# ax = Dual_Import_Aug.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="blue")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_import_Sep = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Sep.columns))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"])


# for n in model_2019_Sep.dmd.keys():
#         c = CUS[n-1]
#         dual_import_Sep.loc["Shadow Price ($/MMBtu)", c] = model_2019_Sep.dual[model_2019_Sep.dmd[n]]
#         print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_Sep[c]/MMBtu_Gas/10**9,model_2019_Sep.dmd[n]()/MMBtu_Gas/10**9,model_2019_Sep.dual[model_2019_Sep.dmd[n]]))

# Dual_Import_Sep = dual_import_Sep.T
# Dual_Import_Sep

# Dual_Import_Sep.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
# ax = Dual_Import_Sep.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="blue")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_import_Oct = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Oct.columns))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"])


# for n in model_2019_Oct.dmd.keys():
#         c = CUS[n-1]
#         dual_import_Oct.loc["Shadow Price ($/MMBtu)", c] = model_2019_Oct.dual[model_2019_Oct.dmd[n]]
#         print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_Oct[c]/MMBtu_Gas/10**9,model_2019_Oct.dmd[n]()/MMBtu_Gas/10**9,model_2019_Oct.dual[model_2019_Oct.dmd[n]]))

# Dual_Import_Oct = dual_import_Oct.T
# Dual_Import_Oct

# Dual_Import_Oct.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
# ax = Dual_Import_Oct.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="blue")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_import_Nov = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Nov.columns))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"])


# for n in model_2019_Nov.dmd.keys():
#         c = CUS[n-1]
#         dual_import_Nov.loc["Shadow Price ($/MMBtu)", c] = model_2019_Nov.dual[model_2019_Nov.dmd[n]]
#         print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_Nov[c]/MMBtu_Gas/10**9,model_2019_Nov.dmd[n]()/MMBtu_Gas/10**9,model_2019_Nov.dual[model_2019_Nov.dmd[n]]))

# Dual_Import_Nov = dual_import_Nov.T
# Dual_Import_Nov

# Dual_Import_Nov.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
# ax = Dual_Import_Nov.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="blue")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# dual_import_Dec = pd.DataFrame(np.zeros((1,len(Merit_Order_3_Dec.columns))),
                   
#                    index = ["Shadow Price ($/MMBtu)"],
    
#                    columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
#                              "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
#                              "Total North America", "Total S. & C. America", "Total ME & Africa"])


# for n in model_2019_Dec.dmd.keys():
#         c = CUS[n-1]
#         dual_import_Dec.loc["Shadow Price ($/MMBtu)", c] = model_2019_Dec.dual[model_2019_Dec.dmd[n]]
#         print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_Dec[c]/MMBtu_Gas/10**9,model_2019_Dec.dmd[n]()/MMBtu_Gas/10**9,model_2019_Dec.dual[model_2019_Dec.dmd[n]]))

# Dual_Import_Dec = dual_import_Dec.T
# Dual_Import_Dec

# Dual_Import_Dec.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
# ax = Dual_Import_Dec.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="blue")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

# Importer_Shadow = dual_import_Jan

# Importer_Shadow = Importer_Shadow.append(dual_import_Feb)
# Importer_Shadow = Importer_Shadow.append(dual_import_Mar)
# Importer_Shadow = Importer_Shadow.append(dual_import_Apr)
# Importer_Shadow = Importer_Shadow.append(dual_import_May)
# Importer_Shadow = Importer_Shadow.append(dual_import_Jun)
# Importer_Shadow = Importer_Shadow.append(dual_import_Jul)
# Importer_Shadow = Importer_Shadow.append(dual_import_Aug)
# Importer_Shadow = Importer_Shadow.append(dual_import_Sep)
# Importer_Shadow = Importer_Shadow.append(dual_import_Oct)
# Importer_Shadow = Importer_Shadow.append(dual_import_Nov)
# Importer_Shadow = Importer_Shadow.append(dual_import_Dec)


# Importer_Shadow = Importer_Shadow.set_index(idx)

# ax = plt.gca()

# Importer_Shadow.plot(kind='line', y='Japan', ylim=(7.32,9.2), ax=ax, color = 'crimson', figsize = (9, 6))
# Importer_Shadow.plot(kind='line',y='China', ax=ax, color = 'red')
# Importer_Shadow.plot(kind='line',y='South Korea', ax=ax, color = 'lightskyblue')
# Importer_Shadow.plot(kind='line',y='Taiwan', ax=ax, color = 'lightsalmon')
# Importer_Shadow.plot(kind='line',y='India', ax=ax, color = 'purple')
# Importer_Shadow.plot(kind='line',y='France', ax=ax, color = 'dodgerblue')
# Importer_Shadow.plot(kind='line',y='Spain', ax=ax, color = 'darkorange')
# Importer_Shadow.plot(kind='line',y='Other Europe', ax=ax, color = 'paleturquoise')
# Importer_Shadow.plot(kind='line',y='UK', ax=ax, color = 'mediumblue')
# Importer_Shadow.plot(kind='line',y='Italy', ax=ax, color = 'limegreen')
# Importer_Shadow.plot(kind='line',y='Turkey', ax=ax, color = 'darkred')
# Importer_Shadow.plot(kind='line',y='Belgium', ax=ax, color = 'indigo')
# Importer_Shadow.plot(kind='line',y='Other Asia Pacific', ax=ax, color = 'yellow')
# Importer_Shadow.plot(kind='line',y='Total S. & C. America', ax=ax, color = 'springgreen')


# # colours_exp_imp = ["crimson", "red", "lightskyblue", "saddlebrown", "lightsalmon", "seagreen",
# #                    "dodgerblue", "darkorange", "mediumblue", "limegreen", "darkred", "indigo",
# #                    "yellow", "paleturquoise", "steelblue", "seagreen", "springgreen"]

# #ax = Importer_Shadow.plot(figsize = (9, 6), ylim=(7.32,9.7))
# ax.set_ylabel("$/mmBtu")
# plt.legend(bbox_to_anchor=(1, 0.83))
# plt.show()
# #Importer_Shadow.T

###############################################################################
### 6 Outlook
###############################################################################
### 6.1 2019
###############################################################################
model_2019 = LNG_Model_3(Demand_2019, Supply_2019)
results_2019 = SolverFactory('gurobi').solve(model_2019)
results_2019.write()
Demand_2019

model_3_2019 = ConcreteModel()
model_3_2019.dual = Suffix(direction=Suffix.IMPORT)

CUS_2019 = list(Demand_2019.keys()) 
SRC_2019 = list(Supply_2019.keys())

model_3_2019.x = Var(CUS_2019, SRC_2019, domain = NonNegativeReals)

model_3_2019.Cost = Objective(
    expr = sum([Cost[c,s]*model_3_2019.x[c,s] for c in CUS_2019 for s in SRC_2019]),
    sense = minimize)

model_3_2019.src = ConstraintList()
for s in SRC_2019:
    model_3_2019.src.add(sum([model_3_2019.x[c,s] for c in CUS_2019]) <= Supply_2019[s])
        
model_3_2019.dmd = ConstraintList()
for c in CUS_2019:
    model_3_2019.dmd.add(sum([model_3_2019.x[c,s] for s in SRC_2019]) == Demand_2019[c])

model_3_2019.div = ConstraintList()
for c in CUS_2019:
    for s in SRC_2019:
        model_3_2019.div.add(model_3_2019.x[c,s] <= (1/3) * Demand_2019[c])
    
results_3_2019 = SolverFactory('gurobi').solve(model_3_2019)
results_3_2019.write()

transported_LNG_3_2019 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_2019.index:
    for importer in transported_LNG_3_2019.columns:
        transported_LNG_3_2019.loc[exporter, importer] = model_3_2019.x[importer, exporter]() / MMBtu_Gas / 1000000000


#Merit_Order_3_2019

Merit_Order_3_2019 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))


for i in transported_LNG_3_2019.index:
    for j in transported_LNG_3_2019.columns:
        if transported_LNG_3_2019.loc[i,j] > 0:
            Merit_Order_3_2019.loc[i,j] = Total_Costs.loc[i,j]


Sum_3_2019 = Merit_Order_3_2019 * transported_LNG_3_2019 * MMBtu_Gas * 1000000000

DES_Pr_3_2019 = pd.DataFrame(np.zeros((1,len(Merit_Order_3_2019.columns))),
                   
                   index = ["Base Year"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_2019 = pd.DataFrame(np.zeros((1,len(Merit_Order_3_2019.columns))),
                   
                   index = ["Base Year"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_2019.loc["Base Year"] = [105.6*10**9 * MMBtu_Gas, 84.9*10**9 * MMBtu_Gas, 55.6*10**9 * MMBtu_Gas,
                         32.9*10**9 * MMBtu_Gas, 23.2*10**9 * MMBtu_Gas, 12.4*10**9 * MMBtu_Gas,
                         23.1*10**9 * MMBtu_Gas, 21.9*10**9 * MMBtu_Gas, 19.1*10**9 * MMBtu_Gas,
                         14.3*10**9 * MMBtu_Gas, 13.2*10**9 * MMBtu_Gas, 9*10**9 * MMBtu_Gas,
                         30.6*10**9 * MMBtu_Gas, 24.4*10**9 * MMBtu_Gas, 11.2*10**9 * MMBtu_Gas,
                         13.5*10**9 * MMBtu_Gas, 10.9*10**9 * MMBtu_Gas]


for column in Sum_3_2019.columns:
    DES_Pr_3_2019.loc["Base Year", column] = Sum_3_2019[column].sum()


DES_Pri_3_2019 = DES_Pr_3_2019 / Imp_3_2019
DES_Price_3_2019 = DES_Pri_3_2019.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_2019.sort_values(by="Base Year", ascending=False, inplace = True)

DES_Price_3_2019.plot(kind = 'barh', color = 'orange', figsize=(9,6))
transported_LNG_3_2019

dual_export_2019 = pd.DataFrame(np.zeros((1, len(transported_LNG_3_2019.index))),
                   
                   index = ["Shadow Price 2019 ($/MMBtu)"],
    
                   columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"])


for m in model_3_2019.src.keys():
        s = SRC_2019[m-1]
        dual_export_2019.loc["Shadow Price 2019 ($/MMBtu)", s] = model_3_2019.dual[model_3_2019.src[m]]
        print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_2019[s]/MMBtu_Gas/10**9,model_3_2019.src[m]()/MMBtu_Gas/10**9,model_3_2019.dual[model_3_2019.src[m]]))

Dual_Export_2019 = dual_export_2019.T
#Dual_Export

Dual_Export_2019.sort_values("Shadow Price 2019 ($/MMBtu)", ascending=True, inplace = True)
ax = Dual_Export_2019.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="red")
ax.set_xlabel("$/MMBtu", fontsize=14)
ax.set_ylabel("", fontsize=14)
plt.show()

dual_import_2019 = pd.DataFrame(np.zeros((1,len(transported_LNG_3_2019.columns))),
                   
                   index = ["Shadow Price 2019 ($/MMBtu)"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])


for n in model_3_2019.dmd.keys():
        c = CUS_2019[n-1]
        dual_import_2019.loc["Shadow Price 2019 ($/MMBtu)", c] = model_3_2019.dual[model_3_2019.dmd[n]]
        print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_2019[c]/MMBtu_Gas/10**9,model_3_2019.dmd[n]()/MMBtu_Gas/10**9,model_3_2019.dual[model_3_2019.dmd[n]]))

Dual_Import_2019 = dual_import_2019.T
Dual_Import_2019

Dual_Import_2019.sort_values("Shadow Price 2019 ($/MMBtu)", inplace = True, ascending=False)
ax = Dual_Import_2019.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="blue")
ax.set_xlabel("$/MMBtu", fontsize=14)
ax.set_ylabel("", fontsize=14)
plt.show()

###############################################################################
### 6.2 2030
###############################################################################
Supply_2030 = Exp_Nodes.set_index("Country")["Export 2030 (MMBtu)"].to_dict()

Demand_2030 = Imp_Nodes.set_index("Country")["Import 2030 (MMBtu)"].to_dict()

Cost_2030 = {}

for index in Total_Costs_2030.index:
    for column in Total_Costs_2030.columns:
        Cost_2030[column, index] = Total_Costs_2030.loc[index,column]

model_3_2030 = ConcreteModel()
model_3_2030.dual = Suffix(direction=Suffix.IMPORT)

CUS_2030 = list(Demand_2030.keys()) # Customer
SRC_2030 = list(Supply_2030.keys()) # Source

model_3_2030.x = Var(CUS_2030, SRC_2030, domain = NonNegativeReals)

model_3_2030.Cost = Objective(
    expr = sum([Cost_2030[c,s]*model_3_2030.x[c,s] for c in CUS_2030 for s in SRC_2030]),
    sense = minimize)




model_3_2030.src = ConstraintList()
for s in SRC_2030:
    model_3_2030.src.add(sum([model_3_2030.x[c,s] for c in CUS_2030]) <= Supply_2030[s])
    


model_3_2030.dmd = ConstraintList()
for c in CUS_2030:
    model_3_2030.dmd.add(sum([model_3_2030.x[c,s] for s in SRC_2030]) == Demand_2030[c])
    


model_3_2030.div = ConstraintList()
for c in CUS_2030:
    for s in SRC_2030:
        model_3_2030.div.add(model_3_2030.x[c,s] <= (1/3) * Demand_2030[c])
        

results_3_2030 = SolverFactory('gurobi').solve(model_3_2030)
results_3_2030.write()

transported_LNG_3_2030 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_2030.index:
    for importer in transported_LNG_3_2030.columns:
        transported_LNG_3_2030.loc[exporter, importer] = model_3_2030.x[importer, exporter]() / MMBtu_Gas / 1000000000

        
        
Merit_Order_3_2030 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))


for i in transported_LNG_3_2030.index:
    for j in transported_LNG_3_2030.columns:
        if transported_LNG_3_2030.loc[i,j] > 0:
            Merit_Order_3_2030.loc[i,j] = Total_Costs_2030.loc[i,j]

#Merit_Order_3_2030

Sum_3_2030 = Merit_Order_3_2030 * transported_LNG_3_2030 * MMBtu_Gas * 1000000000

DES_Pr_3_2030 = pd.DataFrame(np.zeros((1,len(Merit_Order_3_2030.columns))),
                   
                   index = ["2030"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_2030 = pd.DataFrame(np.zeros((1,len(Merit_Order_3_2030.columns))),
                   
                   index = ["2030"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_2030.loc["2030"] = [86.287, 135, 58.6, 55, 28.75, 51.735, 30.944, 29.379,
                        
                             25.574, 19.146, 17.654, 12.093, 120, 40.776, 12.363,
                        
                             14.842, 47.14]

Imp_3_2030 *= 10**9 * MMBtu_Gas
Imp_3_2030

for column in Sum_3_2030.columns:
    DES_Pr_3_2030.loc["2030", column] = Sum_3_2030[column].sum()


DES_Pri_3_2030 = DES_Pr_3_2030 / Imp_3_2030
DES_Price_3_2030 = DES_Pri_3_2030.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_2030.sort_values(by="2030", ascending=False, inplace = True)

DES_Price_3_2030.plot(kind = 'barh', color = 'orange', figsize=(9,6))

dual_export_2030 = pd.DataFrame(np.zeros((1, len(Merit_Order_3_2030.index))),
                   
                   index = ["Shadow Price 2030 ($/MMBtu)"],
    
                   columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"])

for m in model_3_2030.src.keys():
        s = SRC_2030[m-1]
        dual_export_2030.loc["Shadow Price 2030 ($/MMBtu)", s] = model_3_2030.dual[model_3_2030.src[m]]
        print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_2030[s]/MMBtu_Gas/10**9,model_3_2030.src[m]()/MMBtu_Gas/10**9,model_3_2030.dual[model_3_2030.src[m]]))

Dual_Export_2030 = dual_export_2030.T
#Dual_Export

#Dual_Export_2030.sort_values("Shadow Price 2030 ($/MMBtu)", ascending=True, inplace = True)
ax = Dual_Export_2030.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="red")
ax.set_xlabel("$/MMBtu", fontsize=14)
ax.set_ylabel("", fontsize=14)
plt.show()

dual_import_2030 = pd.DataFrame(np.zeros((1,len(Merit_Order_3_2030.columns))),
                   
                   index = ["Shadow Price 2030 ($/MMBtu)"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])


for n in model_3_2030.dmd.keys():
        c = CUS_2030[n-1]
        dual_import_2030.loc["Shadow Price 2030 ($/MMBtu)", c] = model_3_2030.dual[model_3_2030.dmd[n]]
        print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_2030[c]/MMBtu_Gas/10**9,model_3_2030.dmd[n]()/MMBtu_Gas/10**9,model_3_2030.dual[model_3_2030.dmd[n]]))

Dual_Import_2030 = dual_import_2030.T
Dual_Import_2030

#Dual_Import_2030.sort_values("Shadow Price 2030 ($/MMBtu)", ascending=False, inplace = True)
ax = Dual_Import_2030.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="blue")
ax.set_xlabel("$/MMBtu", fontsize=14)
ax.set_ylabel("", fontsize=14)
plt.show()




















###############################################################################
### 6.3 2040
###############################################################################

# IMPORT & EXPORT
Supply_2040 = Exp_Nodes.set_index("Country")["Export 2040 (MMBtu)"].to_dict()  # EXPORT VALUES (Gasification)
_gasification_2040 = pd.DataFrame(list(Supply_2040.items()), columns=['Exporter', 'Gasification capacity in MMBtu'])
_gasification_2040.to_excel('gasification capacity 2040.xlsx', index=False)

Demand_2040 = Imp_Nodes.set_index("Country")["Import 2040 (MMBtu)"].to_dict() # IMPORT VALUES (Re-Gasification)
_regasification_2040 = pd.DataFrame(list(Demand_2040.items()), columns=['Importer', 'Re-Gasification capacity in MMBtu'])
_regasification_2040.to_excel('regasification capacity 2040.xlsx', index=False)

# COST
Cost_2040 = {}
for index in Total_Costs_2040.index:
    # for index / exporter
    for column in Total_Costs_2040.columns:
        # for column / importer
        Cost_2040[column, index] = Total_Costs_2040.loc[index, column]
        # Cost_2040[Import country, Export country]

# CREATE MODEL
# Primal
model_3_2040 = ConcreteModel()
# Dual
model_3_2040.dual = Suffix(direction=Suffix.IMPORT)

# Sets
CUS_2040 = list(Demand_2040.keys())  # Import countries / customers
SRC_2040 = list(Supply_2040.keys())  # Export countries / sources

model_3_2040.x = Var(CUS_2040, SRC_2040, domain=NonNegativeReals, doc='Quantities from the source to the customer.')

model_3_2040.Cost = Objective(
    expr=sum([Cost_2040[c,s]*model_3_2040.x[c,s] for c in CUS_2040 for s in SRC_2040]),
    sense=minimize,
    doc='Objective function.')



model_3_2040.src = ConstraintList()
for s in SRC_2040:
    model_3_2040.src.add(sum([model_3_2040.x[c,s] for c in CUS_2040]) <= Supply_2040[s])
    

model_3_2040.dmd = ConstraintList()
for c in CUS_2040:
    model_3_2040.dmd.add(sum([model_3_2040.x[c,s] for s in SRC_2040]) == Demand_2040[c])
    

model_3_2040.div = ConstraintList()
for c in CUS_2040:
    for s in SRC_2040:
        model_3_2040.div.add(model_3_2040.x[c,s] <= (1/3) * Demand_2040[c])
        

results_3_2040 = SolverFactory('gurobi').solve(model_3_2040)
results_3_2040.write()

transported_LNG_3_2040 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_3_2040.index:
    for importer in transported_LNG_3_2040.columns:
        transported_LNG_3_2040.loc[exporter, importer] = model_3_2040.x[importer, exporter]() / MMBtu_Gas / 1000000000

        
        
Merit_Order_3_2040 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))


for i in transported_LNG_3_2040.index:
    for j in transported_LNG_3_2040.columns:
        if transported_LNG_3_2040.loc[i,j] > 0:
            Merit_Order_3_2040.loc[i,j] = Total_Costs_2040.loc[i,j]

#Merit_Order_3_2030

Sum_3_2040 = Merit_Order_3_2040 * transported_LNG_3_2040 * MMBtu_Gas * 1000000000

DES_Pr_3_2040 = pd.DataFrame(np.zeros((1,len(Merit_Order_3_2040.columns))),
                   
                   index = ["2040"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_2040 = pd.DataFrame(np.zeros((1,len(Merit_Order_3_2040.columns))),
                   
                   index = ["2040"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_3_2040.loc["2040"] = [71.84, 167.676, 62.5, 75.72, 31.25, 70.5, 40.407,
                             38.363, 33.395, 25.001, 23.053, 15.791, 185.391,
                             44.799, 13.514, 16.217, 85]

Imp_3_2040 *= 10**9 * MMBtu_Gas
Imp_3_2040

for column in Sum_3_2040.columns:
    DES_Pr_3_2040.loc["2040", column] = Sum_3_2040[column].sum()


DES_Pri_3_2040 = DES_Pr_3_2040 / Imp_3_2040
DES_Price_3_2040 = DES_Pri_3_2040.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_2040.sort_values(by="2040", ascending=False, inplace = True)

DES_Price_3_2040.plot(kind = 'barh', color = 'orange', figsize=(9,6))
transported_LNG_3_2040

Merit_Order_3_2040

dual_export_2040 = pd.DataFrame(np.zeros((1, len(Merit_Order_3_2040.index))),
                   
                   index = ["Shadow Price 2040 ($/MMBtu)"],
    
                   columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"])

for m in model_3_2040.src.keys():
        s = SRC_2040[m-1]
        dual_export_2040.loc["Shadow Price 2040 ($/MMBtu)", s] = model_3_2040.dual[model_3_2040.src[m]]
        print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_2040[s]/MMBtu_Gas/10**9,model_3_2040.src[m]()/MMBtu_Gas/10**9,model_3_2040.dual[model_3_2040.src[m]]))

Dual_Export_2040 = dual_export_2040.T
#Dual_Export

#Dual_Export_2040.sort_values("Shadow Price 2040 ($/MMBtu)", ascending=True, inplace = True)
ax = Dual_Export_2040.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="red")
ax.set_xlabel("$/MMBtu", fontsize=14)
ax.set_ylabel("", fontsize=14)
plt.show()

dual_import_2040 = pd.DataFrame(np.zeros((1,len(Merit_Order_3_2040.columns))),
                   
                   index = ["Shadow Price 2040 ($/MMBtu)"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])


for n in model_3_2040.dmd.keys():
        c = CUS_2040[n-1]
        dual_import_2040.loc["Shadow Price 2040 ($/MMBtu)", c] = model_3_2040.dual[model_3_2040.dmd[n]]
        print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_2040[c]/MMBtu_Gas/10**9,model_3_2040.dmd[n]()/MMBtu_Gas/10**9,model_3_2040.dual[model_3_2040.dmd[n]]))

Dual_Import_2040 = dual_import_2040.T
Dual_Import_2040

#Dual_Import_2040.sort_values("Shadow Price 2040 ($/MMBtu)", ascending=False, inplace = True)
ax = Dual_Import_2040.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="blue")
ax.set_xlabel("$/MMBtu", fontsize=14)
ax.set_ylabel("", fontsize=14)
plt.show()

Outlook_DES = DES_Price_3_2019.T

Outlook_DES = Outlook_DES.append(DES_Price_3_2030.T)
Outlook_DES = Outlook_DES.append(DES_Price_3_2040.T)

Years = ["Base Year", "2030", "2040"]

Outlook_DES.T.plot(figsize = (9, 6), kind="bar")
plt.legend(bbox_to_anchor=(1.0, 1.0))
plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)

Outlook_Exp = pd.DataFrame([[77.1, 86, 37.8, 26.6*1.07, 30.5, 22.2, 14.8, 25.5, 26.6, 10.4, 14.1, 4.2, 4.5, 5.8, 11.3],
                            [151.69, 124.4, 150.5, 60, 43, 39.28, 17, 20, 37.7, 15.86, 20.9, 8.6, 50, 7.7, 60],
                            [173.75, 140, 220, 85, 43, 70, 17, 20, 37.7, 15.86, 20.9, 8.6, 60, 12, 100],],
                   
                    index = ["2019", "2030", "2040"],
    
                    columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                              "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                              "Other Europe", "Other Americas", "Other ME", "Other Africa"])

Outlook_Exp.loc["2030"] = Outlook_Exp.loc["2030"] * 10**9/mt_LNG_BCM
Outlook_Exp.loc["2040"] = Outlook_Exp.loc["2040"] * 10**9/mt_LNG_BCM
Outlook_Exp.plot.area(figsize = (9, 6), color = colours_exp, ylabel="mtpa", ylim=(0,800))
plt.legend(bbox_to_anchor=(1.0, 0.875))
print(Outlook_Exp.loc["2040"].sum())



































###############################################################################
### 6.4 DES Prices Plot
###############################################################################
Outlook_Imp = Imp_3_2019/MMBtu_Gas/mt_LNG_BCM
Outlook_Imp = Outlook_Imp.append(Imp_3_2030/MMBtu_Gas/mt_LNG_BCM)
Outlook_Imp = Outlook_Imp.append(Imp_3_2040/MMBtu_Gas/mt_LNG_BCM)
Outlook_Imp
Outlook_Imp.plot.area(figsize = (9, 6), color = colours_imp, ylabel="mtpa", ylim=(0,800))
plt.legend(bbox_to_anchor=(1.0, 0.915))

###############################################################################
### 6.5 Importers Shadowprices Outlook
###############################################################################
Outlook_Importer_Shadow = Dual_Import_2019.T

Outlook_Importer_Shadow = Outlook_Importer_Shadow.append(Dual_Import_2030.T)
Outlook_Importer_Shadow = Outlook_Importer_Shadow.append(Dual_Import_2040.T)


id_y = pd.Index(Years)
Outlook_Importer_Shadow = Outlook_Importer_Shadow.set_index(id_y)

#Outlook_Importer_Shadow.plot(figsize = (12, 6.5))
#plt.legend(bbox_to_anchor=(1.0, 1.0))
#plt.show()
#Importer_Shadow.T

Outlook_Importer_Shadow.T.plot(figsize = (9, 6), kind="bar")
plt.legend(bbox_to_anchor=(1.0, 1.0))

#Outlook_Importer_Shadow

###############################################################################
### 6.6 Exporters Shadowprices Outlook
###############################################################################
Outlook_Exporter_Shadow = Dual_Export_2019.T

Outlook_Exporter_Shadow = Outlook_Exporter_Shadow.append(Dual_Export_2030.T)
Outlook_Exporter_Shadow = Outlook_Exporter_Shadow.append(Dual_Export_2040.T)

Outlook_Exporter_Shadow = Outlook_Exporter_Shadow.set_index(id_y)

#Outlook_Importer_Shadow.plot(figsize = (12, 6.5))
#plt.legend(bbox_to_anchor=(1.0, 1.0))
#plt.show()
#Importer_Shadow.T

Outlook_Exporter_Shadow.T.plot(figsize = (9, 6), kind="bar")
plt.legend(bbox_to_anchor=(1.0, 0.2))

Outlook_Exporter_Shadow

Dual_Import_2040.sort_values("Shadow Price 2040 ($/MMBtu)", ascending=True, inplace = True)
Dual_Import_2030.sort_values("Shadow Price 2030 ($/MMBtu)", ascending=True, inplace = True)
Dual_Import_2019.sort_values("Shadow Price 2019 ($/MMBtu)", ascending=True, inplace = True)

Dual_Import_2040.plot(figsize = (9, 6), kind="barh", color = "blue")

Dual_Export_2040.sort_values("Shadow Price 2040 ($/MMBtu)", ascending=True, inplace = True)
Dual_Export_2030.sort_values("Shadow Price 2030 ($/MMBtu)", ascending=True, inplace = True)
Dual_Export_2019.sort_values("Shadow Price 2019 ($/MMBtu)", ascending=True, inplace = True)

Dual_Export_2040.plot(figsize = (9, 6), kind="barh", color = "red")

###############################################################################
### 6.7 Costs Outlook
###############################################################################
Total_Costs_2019 = model_2019_Jan.Cost() + model_2019_Feb.Cost() + model_2019_Mar.Cost() + model_2019_Apr.Cost() + model_2019_May.Cost() + model_2019_Jun.Cost() + model_2019_Jul.Cost() + model_2019_Aug.Cost() + model_2019_Sep.Cost() + model_2019_Oct.Cost() + model_2019_Nov.Cost() + model_2019_Dec.Cost()


Imports_Outlook = [round(Imp_Nodes["Import (MMBtu)"].sum() / 10**9 / MMBtu_Gas,0),
                   round(Imp_Nodes["Import 2030 (MMBtu)"].sum() / 10**9 / MMBtu_Gas,0),
                   round(Imp_Nodes["Import 2040 (MMBtu)"].sum() / 10**9 / MMBtu_Gas,0)]


Total_Costs = [round(Total_Costs_2019  / 10**9, 0),
               round(model_3_2030.Cost() / 10**9, 0),
               round(model_3_2040.Cost() / 10**9, 0)]

Total_Costs_Outlook = pd.DataFrame({#"Import Volumes": Imports_Outlook, 
                                    "Total Costs": Total_Costs}, 
                                   index = ["2019", "2030", "2040"])

ax = Total_Costs_Outlook.plot(figsize = (9, 6), kind="bar", color = [#"lightblue",
                                                                     "lightcoral"], rot=0)

for container in ax.containers:
    ax.bar_label(container)
ax.set_ylabel("Billions of $")    
        
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
#ax.set_xlabel("Minimal number of different importing routes")
plt.show()

###############################################################################
### 6.8 Number of Carriers Outlook
###############################################################################
LNG_Carrier_Number_2030 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

LNG_Carrier_Number_2040 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

LNG_Carrier_Number_2019 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

LNG_Carrier_Number_2030 = (transported_LNG_3_2030*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/365
Carriers_2030 = round(LNG_Carrier_Number_2030.to_numpy().sum())

LNG_Carrier_Number_2019 = (transported_LNG_3_2019*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/365
Carriers_2019 = round(LNG_Carrier_Number_2019.to_numpy().sum())

LNG_Carrier_Number_2040 = (transported_LNG_3_2040*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/366
Carriers_2040 = round(LNG_Carrier_Number_2040.to_numpy().sum())


LNG_Carr_Outlook = [Carriers_2019, Carriers_2030, Carriers_2040]


LNG_Carriers_ = pd.DataFrame({"Number of LNG Carriers": LNG_Carr_Outlook, 
                              }, index = ["2019", "2030", "2040"])


ax = LNG_Carriers_.plot(figsize = (9, 6), kind="bar", color = ["orange", "coral"], rot=0)

for container in ax.containers:
    ax.bar_label(container)
    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()

###############################################################################
### 6.9 Emissions Outlook
###############################################################################
Emissions_2019_ = CO2_Emissions * (transported_LNG_3_2019*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Outlook_2019_CO2 = round(Emissions_2019_.to_numpy().sum()/10**6,2)

Emissions_2030_ = CO2_Emissions * (transported_LNG_3_2030*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Outlook_2030_CO2 = round(Emissions_2030_.to_numpy().sum()/10**6,2)

Emissions_2040_ = CO2_Emissions * (transported_LNG_3_2040*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Outlook_2040_CO2 = round(Emissions_2040_.to_numpy().sum()/10**6,2)

Emi_Outlook_CO2 = [Outlook_2019_CO2, Outlook_2030_CO2, Outlook_2040_CO2]

Emissions_Outlook_CO2 = pd.DataFrame(Emi_Outlook_CO2,
                   
                   index = ["2019", "2030", "2040"],
    
                   columns = ["CO2 Emissions"])


ax = Emissions_Outlook_CO2.plot(figsize = (9, 6), kind="bar", color = "lightgray", rot=0)
for container in ax.containers:
    ax.bar_label(container)

ax.set_ylabel("megatonnes")    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()
CO2_per_mmBtu_2040 = Emissions_2040_.to_numpy().sum()/(transported_LNG_3_2040.to_numpy().sum() * MMBtu_Gas * 10**9)
Outlook_2019_CO2

Emissions_2019__ = CH4_Emissions * (transported_LNG_3_2019*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Outlook_2019_CH4 = round(Emissions_2019__.to_numpy().sum()/10**3,2)

Emissions_2030__ = CH4_Emissions * (transported_LNG_3_2030*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Outlook_2030_CH4 = round(Emissions_2030__.to_numpy().sum()/10**3,2)

Emissions_2040__ = CH4_Emissions * (transported_LNG_3_2040*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Outlook_2040_CH4 = round(Emissions_2040__.to_numpy().sum()/10**3,2)

Emi_Outlook_CH4 = [Outlook_2019_CH4, Outlook_2030_CH4, Outlook_2040_CH4]

Emissions_Outlook_CH4 = pd.DataFrame(Emi_Outlook_CH4,
                   
                   index = ["2019", "2030", "2040"],
    
                   columns = ["CH4 Emissions"])


ax = Emissions_Outlook_CH4.plot(figsize = (9, 6), kind="bar", color = "grey", rot=0)
for container in ax.containers:
    ax.bar_label(container)

ax.set_ylabel("kilotonnes")    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()
"""
###############################################################################
### 7 Diversification of importing routes
###############################################################################
### 7.1 4 Suppliers
###############################################################################
def LNG_Model_4(Demand, Supply):
    
    
    model = ConcreteModel()
    model.dual = Suffix(direction=Suffix.IMPORT)
    
    
    CUS = list(Demand.keys()) 
    SRC = list(Supply.keys()) 

     
    model.x = Var(CUS, SRC, domain = NonNegativeReals)

    
    model.Cost = Objective(expr = sum([Cost[c,s]*model.x[c,s] for c in CUS for s in SRC]), sense = minimize)

    
    model.src = ConstraintList()
    for s in SRC:
        model.src.add(sum([model.x[c,s] for c in CUS]) <= Supply[s])
        
    model.dmd = ConstraintList()
    for c in CUS:
        model.dmd.add(sum([model.x[c,s] for s in SRC]) == Demand[c])
            
    model.div = ConstraintList()
    for c in CUS:
        for s in SRC:
            model.div.add(model.x[c,s] <= 0.25 * Demand[c])
    
    return model

if __name__ == "__main__":
    
    model_2019_4_Suppliers = LNG_Model_4(Demand_2019, Supply_2019)
    results_2019_4_Suppliers = SolverFactory('gurobi').solve(model_2019_4_Suppliers)
    
    results_2019_4_Suppliers.write()
    
transported_LNG_2019_4_Suppliers = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_2019_4_Suppliers.index:
    for importer in transported_LNG_2019_4_Suppliers.columns:
        transported_LNG_2019_4_Suppliers.loc[exporter, importer] = model_2019_4_Suppliers.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_4_2019 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

print(Total_Costs)
for i in transported_LNG_2019_4_Suppliers.index:
    for j in transported_LNG_2019_4_Suppliers.columns:
        if transported_LNG_2019_4_Suppliers.loc[i,j] > 0:
            Merit_Order_4_2019.loc[i,j] = Total_Costs.loc[i,j]


Sum_4_2019 = Merit_Order_4_2019 * transported_LNG_2019_4_Suppliers * MMBtu_Gas * 1000000000

DES_Pr_4_2019 = pd.DataFrame(np.zeros((1,len(Merit_Order_4_2019.columns))),
                   
                   index = ["Base Year"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])


for column in Sum_4_2019.columns:
    DES_Pr_4_2019.loc["Base Year", column] = Sum_4_2019[column].sum()


DES_Pri_4_2019 = DES_Pr_4_2019 / Imp_3_2019
DES_Price_4_2019 = DES_Pri_4_2019.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

#DES_Price_3_2019.sort_values(by="2019", ascending=False, inplace = True)

DES_Price_4_2019.plot(kind = 'barh', color = 'orange', figsize=(9,6))
#DES_Price_3_2019
transported_LNG_2019_4_Suppliers.round(3)

###############################################################################
### 7.3 5 Suppliers
###############################################################################
def LNG_Model_5(Demand, Supply):
    
    
    model = ConcreteModel()
    model.dual = Suffix(direction=Suffix.IMPORT)
    
    
    CUS = list(Demand.keys()) 
    SRC = list(Supply.keys()) 

    
    model.x = Var(CUS, SRC, domain = NonNegativeReals)

    
    model.Cost = Objective(expr = sum([Cost[c,s]*model.x[c,s] for c in CUS for s in SRC]), sense = minimize)

    
    model.src = ConstraintList()
    for s in SRC:
        model.src.add(sum([model.x[c,s] for c in CUS]) <= Supply[s])
        
    model.dmd = ConstraintList()
    for c in CUS:
        model.dmd.add(sum([model.x[c,s] for s in SRC]) == Demand[c])
    
    model.div = ConstraintList()
    for c in CUS:
        for s in SRC:
            model.div.add(model.x[c,s] <= 0.221 * Demand[c])
    
    return model


if __name__ == "__main__":
    
    model_2019_5_Suppliers = LNG_Model_5(Demand_2019, Supply_2019)
    results_2019_5_Suppliers = SolverFactory('gurobi').solve(model_2019_5_Suppliers)
    
    results_2019_5_Suppliers.write()


transported_LNG_2019_5_Suppliers = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_2019_5_Suppliers.index:
    for importer in transported_LNG_2019_5_Suppliers.columns:
        transported_LNG_2019_5_Suppliers.loc[exporter, importer] = model_2019_5_Suppliers.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_5_2019 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))


for i in transported_LNG_2019_5_Suppliers.index:
    for j in transported_LNG_2019_5_Suppliers.columns:
        if transported_LNG_2019_5_Suppliers.loc[i,j] > 0:
            Merit_Order_5_2019.loc[i,j] = Total_Costs.loc[i,j]
            

Sum_5_2019 = Merit_Order_5_2019 * transported_LNG_2019_5_Suppliers * MMBtu_Gas * 1000000000

DES_Pr_5_2019 = pd.DataFrame(np.zeros((1,len(Merit_Order_5_2019.columns))),
                   
                   index = ["Base Year"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])


for column in Sum_5_2019.columns:
    DES_Pr_5_2019.loc["Base Year", column] = Sum_5_2019[column].sum()


DES_Pri_5_2019 = DES_Pr_5_2019 / Imp_3_2019
DES_Price_5_2019 = DES_Pri_5_2019.T

#DES_Price_5_2019.sort_values(by="2019", ascending=False, inplace = True)

DES_Price_5_2019.plot(kind = 'barh', color = 'orange', figsize=(9,6))
#Merit_Order_5_2019
transported_LNG_2019_5_Suppliers

###############################################################################
### 7.4 DES Prices Plot
###############################################################################
Diver_DES = DES_Price_3_2019.T

Diver_DES = Diver_DES.append(DES_Price_4_2019.T)
Diver_DES = Diver_DES.append(DES_Price_5_2019.T)

Diver_DESv_Num = ["3 Exporters", "4 Exporters", "5 Exporters"]

id_y = pd.Index(Diver_DESv_Num)
Diver_DES = Diver_DES.set_index(id_y)

Diver_DES.T.plot(figsize = (9, 6), kind="bar")
#plt.legend(bbox_to_anchor=(1.0, 1.0))
plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)
Diver_DES

###############################################################################
### 7.5 Tankers Number
###############################################################################
num_carrier_3 = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

num_carrier_3 = (Transported_LNG_2019*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/365
num_carrier_3.to_numpy().sum()

num_carrier_2019_4_Suppliers = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

num_carrier_2019_4_Suppliers = (transported_LNG_2019_4_Suppliers*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/365
num_carrier_2019_4_Suppliers.to_numpy().sum()

num_carrier_2019_5_Suppliers = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

num_carrier_2019_5_Suppliers = (transported_LNG_2019_5_Suppliers*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/365
num_carrier_2019_5_Suppliers.to_numpy().sum()

Num_of_Carriers = [round(num_carrier_3.to_numpy().sum()),
                   round(num_carrier_2019_4_Suppliers.to_numpy().sum()),
                   round(num_carrier_2019_5_Suppliers.to_numpy().sum())]

Carriers_2019_Diversification  = pd.DataFrame(Num_of_Carriers,
                   
                   index = ["3", "4", "5"],
    
                   columns = ["Average Number of Carriers"])

plt.rc('font', size=16)
plt.rc('axes', labelsize=16)
plt.rc('xtick', labelsize=16)
plt.rc('ytick', labelsize=16)

ax = Carriers_2019_Diversification.plot(figsize = (9, 6), kind="bar", color = "orange", rot=0, ylim=(0,410))
for container in ax.containers:
    ax.bar_label(container)

    
ax.set_xlabel("Minimal number of different LNG suppliers")
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()

###############################################################################
### 7.6 Total Costs
###############################################################################
Div_Total_Costs = [round(model_3_2019.Cost() / 10**9, 0),
               round(model_2019_4_Suppliers.Cost() / 10**9, 0),
               round(model_2019_5_Suppliers.Cost() / 10**9, 0)]

Diversification_Total_Costs = pd.DataFrame({#"Import Volumes": Imports_Outlook, 
                                    "Total Costs": Div_Total_Costs}, 
                                   index = ["3", "4", "5"])

ax = Diversification_Total_Costs.plot(figsize = (9, 6), kind="bar", color = [#"lightblue",
                                                                     "lightcoral"], rot=0, ylim=(0,120))

for container in ax.containers:
    ax.bar_label(container)
ax.set_ylabel("Billions of $")

plt.rc('font', size=16)
plt.rc('axes', labelsize=16)
        
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
ax.set_xlabel("Minimal number of different LNG suppliers")
#ax.set_xlabel("Minimal number of different importing routes")
plt.show()

###############################################################################
### 7.7 Shadow prices
###############################################################################
dual_export_2019_4 = pd.DataFrame(np.zeros((1, len(transported_LNG_3_2019.index))),
                   
                   index = ["Shadow Price 2019 ($/MMBtu)"],
    
                   columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"])

dual_export_2019_5 = pd.DataFrame(np.zeros((1, len(transported_LNG_3_2019.index))),
                   
                   index = ["Shadow Price 2019 ($/MMBtu)"],
    
                   columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"])

for m in model_2019_4_Suppliers.src.keys():
        s = SRC_2019[m-1]
        dual_export_2019_4.loc["Shadow Price 2019 ($/MMBtu)", s] = model_2019_4_Suppliers.dual[model_2019_4_Suppliers.src[m]]
        #print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_2019[s]/MMBtu_Gas/10**9,model_2019_4_Suppliers.src[m]()/MMBtu_Gas/10**9,model_2019_4_Suppliers.dual[model_2019_4_Suppliers.src[m]]))
        dual_export_2019_5.loc["Shadow Price 2019 ($/MMBtu)", s] = model_2019_5_Suppliers.dual[model_2019_5_Suppliers.src[m]]
        #print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_2019[s]/MMBtu_Gas/10**9,model_2019_5_Suppliers.src[m]()/MMBtu_Gas/10**9,model_2019_5_Suppliers.dual[model_2019_5_Suppliers.src[m]]))
    
Dual_Export_2019.sort_values("Shadow Price 2019 ($/MMBtu)", ascending=True, inplace = True)
# ax = Dual_Export_2019_5.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="red")
# ax.set_xlabel("$/MMBtu", fontsize=14)
# ax.set_ylabel("", fontsize=14)
# plt.show()

Dual_Export_2019_4 = dual_export_2019_4.T
Dual_Export_2019_5 = dual_export_2019_5.T

Diver_Exporter_Shadow = Dual_Export_2019.T

Diver_Exporter_Shadow = Diver_Exporter_Shadow.append(Dual_Export_2019_4.T)
Diver_Exporter_Shadow = Diver_Exporter_Shadow.append(Dual_Export_2019_5.T)

Diver_Exporter_Shadow = Diver_Exporter_Shadow.set_index(id_y)

Diver_Exporter_Shadow.T.plot(figsize = (9, 6), kind="bar")
#plt.legend(bbox_to_anchor=(1.0, 0.2))
#plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)
Diver_Exporter_Shadow

dual_import_2019_4 = pd.DataFrame(np.zeros((1, len(transported_LNG_3_2019.columns))),
                   
                   index = ["Shadow Price 2019 ($/MMBtu)"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

dual_import_2019_5 = pd.DataFrame(np.zeros((1, len(transported_LNG_3_2019.columns))),
                   
                   index = ["Shadow Price 2019 ($/MMBtu)"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])


for n in model_3_2019.dmd.keys():
        c = CUS_2019[n-1]
        dual_import_2019_4.loc["Shadow Price 2019 ($/MMBtu)", c] = model_2019_4_Suppliers.dual[model_2019_4_Suppliers.dmd[n]]
        dual_import_2019_5.loc["Shadow Price 2019 ($/MMBtu)", c] = model_2019_5_Suppliers.dual[model_2019_5_Suppliers.dmd[n]]
        


Dual_Import_2019_4 = dual_import_2019_4.T
Dual_Import_2019_5 = dual_import_2019_5.T

Diver_Importer_Shadow = Dual_Import_2019.T

Diver_Importer_Shadow = Diver_Importer_Shadow.append(Dual_Import_2019_4.T)
Diver_Importer_Shadow = Diver_Importer_Shadow.append(Dual_Import_2019_5.T)

Diver_Importer_Shadow = Diver_Importer_Shadow.set_index(id_y)

Diver_Importer_Shadow.T.plot(figsize = (9, 6), kind="bar", ylim=(0,12))
#plt.legend(bbox_to_anchor=(0.999, 1.011))
#plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)

Diver_Importer_Shadow

###############################################################################
### 7.8 Emissions
###############################################################################
#Emissions_2019_ = CO2_Emissions * (transported_LNG_3_2019*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
#Outlook_2019_CO2 = round(Emissions_2019_.to_numpy().sum()/10**6,2)

Emissions_2019_4 = CO2_Emissions * (transported_LNG_2019_4_Suppliers*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Emissions_CO2_4 = round(Emissions_2019_4.to_numpy().sum()/10**6,2)

Emissions_2019_5 = CO2_Emissions * (transported_LNG_2019_5_Suppliers*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Emissions_CO2_5 = round(Emissions_2019_5.to_numpy().sum()/10**6,2)

Emi_Diver_CO2 = [Outlook_2019_CO2, Emissions_CO2_4, Emissions_CO2_5]

Emissions_Diver_CO2 = pd.DataFrame(Emi_Diver_CO2,
                   
                   index = ["3", "4", "5"],
    
                   columns = ["CO2 Emissions"])

plt.rc('font', size=16)
plt.rc('axes', labelsize=16)
ax = Emissions_Diver_CO2.plot(figsize = (9, 6), kind="bar", color = "lightgray", rot=0, ylim=(0,75))
for container in ax.containers:
    ax.bar_label(container)

ax.set_ylabel("megatonnes")    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
ax.set_xlabel("Minimal number of different LNG suppliers")
plt.show()
#CO2_per_mmBtu_2019_4 = Emissions_2040_.to_numpy().sum()/(transported_LNG_3_2040.to_numpy().sum() * MMBtu_Gas * 10**9)
#CO2_per_mmBtu_2040

#Emissions_2019_ = CO2_Emissions * (transported_LNG_3_2019*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
#Outlook_2019_CO2 = round(Emissions_2019_.to_numpy().sum()/10**6,2)

Emissions_2019_4_CH4 = CH4_Emissions * (transported_LNG_2019_4_Suppliers*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Emissions_CH4_4 = round(Emissions_2019_4_CH4.to_numpy().sum()/10**3,2)

Emissions_2019_5_CH4 = CH4_Emissions * (transported_LNG_2019_5_Suppliers*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Emissions_CH4_5 = round(Emissions_2019_5_CH4.to_numpy().sum()/10**3,2)

Emi_Diver_CH4 = [Outlook_2019_CH4, Emissions_CH4_4, Emissions_CH4_5]

Emissions_Diver_CH4 = pd.DataFrame(Emi_Diver_CH4,
                   
                   index = ["3", "4", "5"],
    
                   columns = ["CH4 Emissions"])


ax = Emissions_Diver_CH4.plot(figsize = (9, 6), kind="bar", color = "grey", rot=0, ylim=(0,47))
for container in ax.containers:
    ax.bar_label(container)

ax.set_ylabel("kilotonnes")    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
ax.set_xlabel("Minimal number of different LNG suppliers")
plt.show()
#CO2_per_mmBtu_2019_4 = Emissions_2040_.to_numpy().sum()/(transported_LNG_3_2040.to_numpy().sum() * MMBtu_Gas * 10**9)
#CO2_per_mmBtu_2040

###############################################################################
### 8 Strait of Hormuz at 2/3
###############################################################################
### 8.1 Prices
###############################################################################
model_2019_HC = LNG_Model_3(Demand_2019, Supply_HC)
results_2019_HC = SolverFactory('glpk').solve(model_2019_HC)
results_2019_HC.write()

transported_2019_HC = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_2019_HC.index:
    for importer in transported_2019_HC.columns:
        transported_2019_HC.loc[exporter, importer] = model_2019_HC.x[importer, exporter]() / MMBtu_Gas / 1000000000
    

Merit_Order_2019_HC = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))


for i in Merit_Order_2019_HC.index:
    for j in Merit_Order_2019_HC.columns:
        if transported_2019_HC.loc[i,j] > 0:
            Merit_Order_2019_HC.loc[i,j] = TotalCosts.loc[i,j]


Sum_2019_HC = Merit_Order_2019_HC * transported_2019_HC * MMBtu_Gas * 1000000000


DES_Pr_2019_HC = pd.DataFrame(np.zeros((1,len(Merit_Order_2019_HC.columns))),
                   
                   index = ["2019"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_2019_HC = pd.DataFrame(np.zeros((1,len(Merit_Order_2019_HC.columns))),
                   
                   index = ["2019"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])



Imp_2019_HC.loc["2019"] = [105.6*10**9 * MMBtu_Gas, 84.9*10**9 * MMBtu_Gas, 55.6*10**9 * MMBtu_Gas,
                         32.9*10**9 * MMBtu_Gas, 23.2*10**9 * MMBtu_Gas, 12.4*10**9 * MMBtu_Gas,
                         23.1*10**9 * MMBtu_Gas, 21.9*10**9 * MMBtu_Gas, 19.1*10**9 * MMBtu_Gas,
                         14.3*10**9 * MMBtu_Gas, 13.2*10**9 * MMBtu_Gas, 9*10**9 * MMBtu_Gas,
                         30.6*10**9 * MMBtu_Gas, 24.4*10**9 * MMBtu_Gas, 11.2*10**9 * MMBtu_Gas,
                         13.5*10**9 * MMBtu_Gas, 10.9*10**9 * MMBtu_Gas]



for column in Imp_2019_HC.columns:
    DES_Pr_2019_HC.loc["2019", column] = Sum_2019_HC[column].sum()


DES_Pri_2019_HC = DES_Pr_2019_HC / Imp_2019_HC
DES_Price_2019_HC = DES_Pri_2019_HC.T

#DES_Prices_1 = DESp.sort_values("DES Price ($/MMBtu)", ascending=False, inplace = True)

DES_Price_3_2019.sort_values(by="Base Year", ascending=False, inplace = True)

#DES_Price_3_Oct_Q.plot(kind = 'barh', color = 'orange', figsize=(9,6))
DES_Price_HC = DES_Price_3_2019.T
DES_Price_HC = DES_Price_HC.append(DES_Price_2019_HC.T)

HC_ = ["Baseline", "ME Output reduced by 33%"]

id_y = pd.Index(HC_)
DES_Price_HC = DES_Price_HC.set_index(id_y)

DES_Price_HC.T.plot(figsize = (9, 6), kind="bar")
#plt.legend(bbox_to_anchor=(1.0, 1.0))
plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)
plt.legend(fontsize=12.4)

###############################################################################
### 8.2 Costs
###############################################################################
Costs_HC = [round(Total_Costs_2019 / 10**9, 2),
            round(model_2019_HC.Cost() / 10**9, 2)]


Costs_HC_ = pd.DataFrame({"Total costs": Costs_HC, 
                              }, index = ["Baseline", "ME Output reduced by 33%"])


ax = Costs_HC_.plot(figsize = (9, 6), kind="bar", color = ["coral"], rot=0, ylim=(0,125))

for container in ax.containers:
    ax.bar_label(container)
    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.set_ylabel("Billions of $")
ax.get_legend().remove()
plt.show()

###############################################################################
### 8.3 Number of LNG Carriers
###############################################################################
LNG_Carrier_Number_HC = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))



LNG_Carrier_Number_HC = (transported_2019_HC*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/365


Num_of_Carriers_HC = [round(Carriers_2019),
                      round(LNG_Carrier_Number_HC.to_numpy().sum())]

Carriers_2019_HC = pd.DataFrame(Num_of_Carriers_HC,
                   
                   index = ["Normal", "ME Output -33%"],
    
                   columns = ["Average Number of Carriers"])


ax = Carriers_2019_HC.plot(figsize = (9, 6), kind="bar", color = "orange", rot=0, ylim=(0,385))
for container in ax.containers:
    ax.bar_label(container)

#ax.set_xlabel("Minimal number of different LNG suppliers")
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()

###############################################################################
### 8.4 Shadow Prices
###############################################################################
dual_export_2019_HC = pd.DataFrame(np.zeros((1, len(Merit_Order_2019_HC.index))),
                   
                   index = ["Shadow Price ($/MMBtu)"],
    
                   columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"])


for m in model_2019_HC.src.keys():
        s = SRC[m-1]
        dual_export_2019_HC.loc["Shadow Price ($/MMBtu)", s] = model_2019_HC.dual[model_2019_HC.src[m]]
        print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_HC[s]/MMBtu_Gas/10**9,model_2019_HC.src[m]()/MMBtu_Gas/10**9,model_2019_HC.dual[model_2019_HC.src[m]]))

Dual_Export_HC = dual_export_2019_HC.T
#Dual_Export

#Dual_Export_Jun_SA.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
ax = Dual_Export_HC.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="red")
ax.set_xlabel("$/MMBtu", fontsize=14)
ax.set_ylabel("", fontsize=14)
plt.show()

dual_import_2019_HC = pd.DataFrame(np.zeros((1,len(Merit_Order_2019_HC.columns))),
                   
                   index = ["Shadow Price Mar_SA ($/MMBtu)"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])



for n in model_2019_HC.dmd.keys():
        c = CUS[n-1]
        dual_import_2019_HC.loc["Shadow Price Mar_SA ($/MMBtu)", c] = model_2019_HC.dual[model_2019_HC.dmd[n]]
        print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_2019[c]/MMBtu_Gas/10**9,model_2019_HC.dmd[n]()/MMBtu_Gas/10**9,model_2019_HC.dual[model_2019_HC.dmd[n]]))

Dual_Import_HC = dual_import_2019_HC.T
#Dual_Import_Jun_Q

#Dual_Import_Jun_SA.sort_values("Shadow Price Mar_SA ($/MMBtu)", ascending=False, inplace = True)
ax = Dual_Import_HC.plot(kind = 'barh', figsize = (9, 6), legend = True, fontsize = 14, color="blue")
ax.set_xlabel("$/MMBtu", fontsize=14)
ax.set_ylabel("", fontsize=14)
plt.show()

#Dual_Import_2019_4.sort_values("Shadow Price 2019 ($/MMBtu)", ascending=False, inplace = True)
Importer_Shadow_HC = Dual_Import_2019.T
Importer_Shadow_HC = Importer_Shadow_HC.append(Dual_Import_HC.T)

HC_y = ["Baseline", "ME Output reduced by 33%"]

id_y = pd.Index(HC_y) 
Importer_Shadow_HC = Importer_Shadow_HC.set_index(id_y)
Importer_Shadow_HC.T.plot(figsize = (9, 6), kind="bar", ylim=(0,15))
#plt.legend(bbox_to_anchor=(1.0, 1.0))
#plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)
Importer_Shadow_HC

#Dual_Export_2019_4.sort_values("Shadow Price 2019 ($/MMBtu)", ascending=True, inplace = True)

Exporter_Shadow_HC = Dual_Export_2019.T
Exporter_Shadow_HC = Exporter_Shadow_HC.append(Dual_Export_HC.T)

Exporter_Shadow_HC = Exporter_Shadow_HC.set_index(id_y)
#Dual_Import_2019.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
Exporter_Shadow_HC.T.plot(figsize = (9, 6), kind="bar")
#plt.legend(bbox_to_anchor=(1.0, 0.18))
#plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)
Exporter_Shadow_HC

###############################################################################
### 8.5 Emissions
###############################################################################
Emissions_2019_HC_ = CO2_Emissions * (transported_2019_HC*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Emissions_2019_HC_CO2 = round(Emissions_2019_HC_.to_numpy().sum()/10**6,2)


Emi_HC_CO2 = [Outlook_2019_CO2, Emissions_2019_HC_CO2]

Emissions_HC_CO2 = pd.DataFrame(Emi_HC_CO2,
                   
                   index = ["Baseline", "ME Output reduced by 33%"],
    
                   columns = ["CO2 Emissions"])


ax = Emissions_HC_CO2.plot(figsize = (9, 6), kind="bar", color = "lightgray", rot=0, ylim=(0,70))

for container in ax.containers:
    ax.bar_label(container)

ax.set_ylabel("megatonnes")    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()

Emissions_2019_HC_CH4_ = CH4_Emissions * (transported_2019_HC*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Emissions_2019_HC_CH4 = round(Emissions_2019_HC_CH4_.to_numpy().sum()/10**3,2)


Emi_HC_CH4 = [Outlook_2019_CH4, Emissions_2019_HC_CH4]

Emissions_HC_CH4 = pd.DataFrame(Emi_HC_CH4,
                   
                   index = ["Baseline", "ME Output reduced by 33%"],
    
                   columns = ["CH4 Emissions"])


ax = Emissions_HC_CH4.plot(figsize = (9, 6), kind="bar", color = "grey", rot=0, ylim=(0,43))
for container in ax.containers:
    ax.bar_label(container)

ax.set_ylabel("kilotonnes")    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()
Emissions_2019_HC_CH4

###############################################################################
### 9 Europe +33%
###############################################################################
### 9.1 DES Price
###############################################################################
model_2019_EU = LNG_Model_4(Demand_2019_EU, Supply_2019)
results_2019_EU = SolverFactory('gurobi').solve(model_2019_EU)
results_2019_EU.write()

transported_LNG_2019_EU = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_2019_EU.index:
    for importer in transported_LNG_2019_EU.columns:
        transported_LNG_2019_EU.loc[exporter, importer] = model_2019_EU.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_2019_EU = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))


for i in transported_LNG_2019_EU.index:
    for j in transported_LNG_2019_EU.columns:
        if transported_LNG_2019_EU.loc[i,j] > 0:
            Merit_Order_2019_EU.loc[i,j] = Total_Costs.loc[i,j]


Sum_2019_EU = Merit_Order_2019_EU * transported_LNG_2019_EU * MMBtu_Gas * 1000000000

DES_Pr_2019_EU = pd.DataFrame(np.zeros((1,len(Merit_Order_2019_EU.columns))),
                   
                   index = ["2019"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_2019_EU = pd.DataFrame(np.zeros((1,len(Merit_Order_3_2019.columns))),
                   
                   index = ["2019"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_2019_EU.loc["2019"] = [105.6*10**9 * MMBtu_Gas, 84.9*10**9 * MMBtu_Gas, 55.6*10**9 * MMBtu_Gas,
                           32.9*10**9 * MMBtu_Gas, 23.2*10**9 * MMBtu_Gas, 12.4*10**9 * MMBtu_Gas,
                           (4/3)*23.1*10**9 * MMBtu_Gas, (4/3)*21.9*10**9 * MMBtu_Gas, (4/3)*19.1*10**9 * MMBtu_Gas,
                           (4/3)*14.3*10**9 * MMBtu_Gas, (4/3)*13.2*10**9 * MMBtu_Gas, (4/3)*9*10**9 * MMBtu_Gas,
                           30.6*10**9 * MMBtu_Gas, (4/3)*24.4*10**9 * MMBtu_Gas, 11.2*10**9 * MMBtu_Gas,
                           13.5*10**9 * MMBtu_Gas, 10.9*10**9 * MMBtu_Gas]


for column in Sum_2019_EU.columns:
    DES_Pr_2019_EU.loc["2019", column] = Sum_2019_EU[column].sum()


DES_Pri_2019_EU = DES_Pr_2019_EU / Imp_2019_EU
DES_Price_2019_EU = DES_Pri_2019_EU.T

DES_Price_4_2019.sort_values(by="Base Year", ascending=False, inplace = True)

#DES_Price_2019_EU.plot(kind = 'barh', color = 'orange', figsize=(9,6))
#DES_Price_2019_EU

DES_Price_EU = DES_Price_4_2019.T
DES_Price_EU = DES_Price_EU.append(DES_Price_2019_EU.T)

EU_ = ["Baseline", "33% LNG demand increase in Europe"]

id_y = pd.Index(EU_)
DES_Price_EU = DES_Price_EU.set_index(id_y)

DES_Price_EU.T.plot(figsize = (9, 6), kind="bar", ylim=(0,9))
#plt.legend(bbox_to_anchor=(1.0, 1.0))
plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)
transported_LNG_2019_EU.round(3)

###############################################################################
### 9.2 Carriers
###############################################################################
LNG_Carrier_Number_2019_EU = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

LNG_Carrier_Number_EU = (transported_LNG_2019_EU*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/365
Carriers_EU = round(LNG_Carrier_Number_EU.to_numpy().sum())

LNG_Carr_EU_ = [round(num_carrier_2019_4_Suppliers.to_numpy().sum()), Carriers_EU]


LNG_Carriers_EU = pd.DataFrame({"Number of LNG Carriers": LNG_Carr_EU_, 
                              }, index = ["Normal", "Europe +33% demand increase"])


ax = LNG_Carriers_EU.plot(figsize = (9, 6), kind="bar", color = ["orange"], rot=0, ylim=(0,438))

for container in ax.containers:
    ax.bar_label(container)
    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()

###############################################################################
### 9.3 Costs
###############################################################################
Costs_EU = [round(model_2019_4_Suppliers.Cost() / 10**9, 2),
            round(model_2019_EU.Cost() / 10**9, 2)]


Costs_EU_ = pd.DataFrame({"Total costs": Costs_EU, 
                              }, index = ["Normal", "Europe +33% demand increase"])


ax = Costs_EU_.plot(figsize = (9, 6), kind="bar", color = ["coral"], rot=0, ylim=(0,130))

for container in ax.containers:
    ax.bar_label(container)
    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.set_ylabel("Billions of $")
ax.get_legend().remove()
plt.show()

###############################################################################
### 9.4 Shadow Exporters
###############################################################################
dual_export_2019_EU = pd.DataFrame(np.zeros((1, len(Merit_Order_2019_EU.index))),
                   
                   index = ["Shadow Price ($/MMBtu)"],
    
                   columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"])


for m in model_2019_EU.src.keys():
        s = SRC[m-1]
        dual_export_2019_EU.loc["Shadow Price ($/MMBtu)", s] = model_2019_EU.dual[model_2019_EU.src[m]]
        print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_2019[s]/MMBtu_Gas/10**9,model_2019_EU.src[m]()/MMBtu_Gas/10**9,model_2019_EU.dual[model_2019_EU.src[m]]))

Dual_Export_EU = dual_export_2019_EU.T
Dual_Export_2019_4.sort_values("Shadow Price 2019 ($/MMBtu)", ascending=True, inplace = True)

Exporter_Shadow_EU = Dual_Export_2019_4.T
Exporter_Shadow_EU = Exporter_Shadow_EU.append(Dual_Export_EU.T)
EU_ = ["Baseline", "33% LNG demand increase in Europe"]

id_y = pd.Index(EU_)
Exporter_Shadow_EU = Exporter_Shadow_EU.set_index(id_y)
#Dual_Import_2019.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
Exporter_Shadow_EU.T.plot(figsize = (9, 6), kind="bar")
plt.legend(bbox_to_anchor=(1.0, 0.2))
#plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)
Exporter_Shadow_EU

###############################################################################
### 9.5 Shadow Importers
###############################################################################
dual_import_2019_EU = pd.DataFrame(np.zeros((1,len(Merit_Order_2019_EU.columns))),
                   
                   index = ["Shadow Price Mar_SA ($/MMBtu)"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])


for n in model_2019_EU.dmd.keys():
        c = CUS[n-1]
        dual_import_2019_EU.loc["Shadow Price Mar_SA ($/MMBtu)", c] = model_2019_EU.dual[model_2019_EU.dmd[n]]
        print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_2019_EU[c]/MMBtu_Gas/10**9,model_2019_EU.dmd[n]()/MMBtu_Gas/10**9,model_2019_EU.dual[model_2019_EU.dmd[n]]))

Dual_Import_EU = dual_import_2019_EU.T
#Dual_Import_Jun_Q

Dual_Import_2019_4.sort_values("Shadow Price 2019 ($/MMBtu)", ascending=False, inplace = True)
# ax.set_xlabel("$/MMBtu", fontsize=12)
# ax.set_ylabel("", fontsize=12)
# plt.show()

Importer_Shadow_EU = Dual_Import_2019_4.T
Importer_Shadow_EU = Importer_Shadow_EU.append(Dual_Import_EU.T)

EU_y = ["Baseline", "33% LNG demand increase in Europe"]

id_y = pd.Index(EU_y) 
Importer_Shadow_EU = Importer_Shadow_EU.set_index(id_y)
Importer_Shadow_EU.T.plot(figsize = (9, 6), kind="bar", ylim=(0,14.5))
#plt.legend(bbox_to_anchor=(1.0, 1.0))
#plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)
#Dual_Import_2019_4

###############################################################################
### 9.6 CO2
###############################################################################
Emissions_2019_EU_ = CO2_Emissions * (transported_LNG_2019_EU*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Emissions_2019_EU_CO2 = round(Emissions_2019_EU_.to_numpy().sum()/10**6,2)


Emi_EU_CO2 = [Emissions_CO2_4, Emissions_2019_EU_CO2]

Emissions_EU_CO2 = pd.DataFrame(Emi_EU_CO2,
                   
                   index = ["Normal", "Europe +33% demand increase"],
    
                   columns = ["CO2 Emissions"])


ax = Emissions_EU_CO2.plot(figsize = (9, 6), kind="bar", color = "lightgray", rot=0, ylim=(0,79))

for container in ax.containers:
    ax.bar_label(container)

ax.set_ylabel("megatonnes")    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()

###############################################################################
### 9.7 CH4
###############################################################################
Emissions_2019_EU_CH4_ = CH4_Emissions * (transported_LNG_2019_EU*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Emissions_2019_EU_CH4 = round(Emissions_2019_EU_CH4_.to_numpy().sum()/10**3,2)


Emi_EU_CH4 = [Emissions_CH4_4, Emissions_2019_EU_CH4]

Emissions_EU_CH4 = pd.DataFrame(Emi_EU_CH4,
                   
                   index = ["Normal", "Europe +33% demand increase"],
    
                   columns = ["CH4 Emissions"])


ax = Emissions_EU_CH4.plot(figsize = (9, 6), kind="bar", color = "grey", rot=0, ylim=(0,51))
for container in ax.containers:
    ax.bar_label(container)

ax.set_ylabel("kilotonnes")    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()
#Emissions_EU_CH4

###############################################################################
### 10 Asia Pacific -20%
###############################################################################
### 10.1 DES Price
###############################################################################
model_2019_Asia = LNG_Model_4(Demand_2019_Asia, Supply_2019)
results_2019_Asia = SolverFactory('gurobi').solve(model_2019_Asia)
results_2019_Asia.write()

transported_LNG_2019_AS = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

for exporter in transported_LNG_2019_AS.index:
    for importer in transported_LNG_2019_AS.columns:
        transported_LNG_2019_AS.loc[exporter, importer] = model_2019_Asia.x[importer, exporter]() / MMBtu_Gas / 1000000000


Merit_Order_2019_AS = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))


for i in transported_LNG_2019_AS.index:
    for j in transported_LNG_2019_AS.columns:
        if transported_LNG_2019_AS.loc[i,j] > 0:
            Merit_Order_2019_AS.loc[i,j] = Total_Costs.loc[i,j]


Sum_2019_AS = Merit_Order_2019_AS * transported_LNG_2019_AS * MMBtu_Gas * 1000000000

DES_Pr_2019_AS = pd.DataFrame(np.zeros((1,len(Merit_Order_2019_AS.columns))),
                   
                   index = ["2019"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_2019_AS = pd.DataFrame(np.zeros((1,len(Merit_Order_3_2019.columns))),
                   
                   index = ["2019"], #"Import (MMBtu)"
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])

Imp_2019_AS.loc["2019"] = [1.121*105.6*10**9 * MMBtu_Gas, 1.121*84.9*10**9 * MMBtu_Gas, 1.121*55.6*10**9 * MMBtu_Gas,
                           1.121*32.9*10**9 * MMBtu_Gas, 1.121*23.2*10**9 * MMBtu_Gas, 1.121*12.4*10**9 * MMBtu_Gas,
                           23.1*10**9 * MMBtu_Gas, 21.9*10**9 * MMBtu_Gas, 19.1*10**9 * MMBtu_Gas,
                           14.3*10**9 * MMBtu_Gas, 13.2*10**9 * MMBtu_Gas, 9*10**9 * MMBtu_Gas,
                           1.121*30.6*10**9 * MMBtu_Gas, 24.4*10**9 * MMBtu_Gas, 11.2*10**9 * MMBtu_Gas,
                           13.5*10**9 * MMBtu_Gas, 10.9*10**9 * MMBtu_Gas]


for column in Sum_2019_AS.columns:
    DES_Pr_2019_AS.loc["2019", column] = Sum_2019_AS[column].sum()


DES_Pri_2019_AS = DES_Pr_2019_AS / Imp_2019_AS
DES_Price_2019_AS = DES_Pri_2019_AS.T

DES_Price_4_2019.sort_values(by="Base Year", ascending=True, inplace = True)

# DES_Price_2019_EU.plot(kind = 'barh', color = 'orange', figsize=(9,6))
#DES_Price_2019_EU

DES_Price_AS = DES_Price_4_2019.T
DES_Price_AS = DES_Price_AS.append(DES_Price_2019_AS.T)

AS_ = ["Baseline", "20% LNG demand decrease in Asia Pacific"]

id_y = pd.Index(AS_)
DES_Price_AS = DES_Price_AS.set_index(id_y)

DES_Price_AS.T.plot(figsize = (9, 6), kind="bar", ylim=(0,8))
#plt.legend(bbox_to_anchor=(1.0, 1.0))
plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)
DES_Price_AS

###############################################################################
### 10.2 Carriers
###############################################################################
LNG_Carrier_Number_2019_AS = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                   
                    index = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"],

                    columns = ("Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"))

LNG_Carrier_Number_AS = (transported_LNG_2019_AS*10**9)/(0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)*(Time+3)/365
Carriers_AS = round(LNG_Carrier_Number_AS.to_numpy().sum())

LNG_Carr_AS_ = [round(num_carrier_2019_4_Suppliers.to_numpy().sum()), Carriers_AS]


LNG_Carriers_AS = pd.DataFrame({"Number of LNG Carriers": LNG_Carr_AS_, 
                              }, index = ["Normal", "Asia Pacific 20% demand decrease"])


bx = LNG_Carriers_AS.plot(figsize = (9, 6), kind="bar", color = ["orange"], rot=0, ylim=(0,400))

for container in bx.containers:
    bx.bar_label(container)
    
plt.legend(bbox_to_anchor=(1.0, 1.0))
bx.get_legend().remove()
plt.show()
Carriers_AS

###############################################################################
### 10.3 Costs
###############################################################################
Costs_AS = [round(model_2019_4_Suppliers.Cost() / 10**9, 2),
            round(model_2019_Asia.Cost() / 10**9, 2)]


Costs_AS_ = pd.DataFrame({"Total costs": Costs_AS, 
                              }, index = ["Normal", "Asia Pacific 20% demand decrease%"])


ax = Costs_AS_.plot(figsize = (9, 6), kind="bar", color = ["coral"], rot=0, ylim=(0,120))

for container in ax.containers:
    ax.bar_label(container)
    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.set_ylabel("Billions of $")
ax.get_legend().remove()
plt.show()

###############################################################################
### 10.4 Shadow Exporters
###############################################################################
dual_export_2019_AS = pd.DataFrame(np.zeros((1, len(Merit_Order_2019_AS.index))),
                   
                   index = ["Shadow Price ($/MMBtu)"],
    
                   columns = ["Qatar", "Australia", "USA", "Russia", "Malaysia", "Nigeria",
                             "Trinidad & Tobago", "Algeria", "Indonesia", "Oman", "Other Asia Pacific",
                             "Other Europe", "Other Americas", "Other ME", "Other Africa"])

for m in model_2019_Asia.src.keys():
        s = SRC[m-1]
        dual_export_2019_AS.loc["Shadow Price ($/MMBtu)", s] = model_2019_Asia.dual[model_2019_Asia.src[m]]
        print("{0:18s}{1:15.1f}{2:14.1f}{3:14.4f}".format(s,Supply_2019[s]/MMBtu_Gas/10**9,model_2019_Asia.src[m]()/MMBtu_Gas/10**9,model_2019_Asia.dual[model_2019_Asia.src[m]]))

Dual_Export_AS = dual_export_2019_AS.T
Dual_Export_2019_4.sort_values("Shadow Price 2019 ($/MMBtu)", ascending=True, inplace = True)

Exporter_Shadow_AS = Dual_Export_2019_4.T
Exporter_Shadow_AS = Exporter_Shadow_AS.append(Dual_Export_AS.T)

id_y = pd.Index(AS_)
Exporter_Shadow_AS = Exporter_Shadow_AS.set_index(id_y)
#Dual_Import_2019.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
Exporter_Shadow_AS.T.plot(figsize = (9, 6), kind="bar")
#plt.legend(bbox_to_anchor=(1.0, 0.18))
#plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)
Exporter_Shadow_AS

###############################################################################
### 10.5 Shadow Importers
###############################################################################
dual_import_2019_AS = pd.DataFrame(np.zeros((1,len(Merit_Order_2019_AS.columns))),
                   
                   index = ["Shadow Price Mar_SA ($/MMBtu)"],
    
                   columns = ["Japan", "China", "South Korea", "India", "Taiwan", "Pakistan", "France",
                             "Spain","UK", "Italy", "Turkey", "Belgium", "Other Asia Pacific", "Other Europe",
                             "Total North America", "Total S. & C. America", "Total ME & Africa"])


for n in model_2019_Asia.dmd.keys():
        c = CUS[n-1]
        dual_import_2019_AS.loc["Shadow Price Mar_SA ($/MMBtu)", c] = model_2019_Asia.dual[model_2019_Asia.dmd[n]]
        print("{0:26s}{1:15.1f}{2:10.1f}{3:12.4f}".format(c,Demand_2019_Asia[c]/MMBtu_Gas/10**9,model_2019_Asia.dmd[n]()/MMBtu_Gas/10**9,model_2019_Asia.dual[model_2019_Asia.dmd[n]]))

Dual_Import_AS = dual_import_2019_AS.T
#Dual_Import_Jun_Q

Dual_Import_2019_4.sort_values("Shadow Price 2019 ($/MMBtu)", ascending=False, inplace = True)
# ax.set_xlabel("$/MMBtu", fontsize=12)
# ax.set_ylabel("", fontsize=12)
# plt.show()

Importer_Shadow_AS = Dual_Import_2019_4.T
Importer_Shadow_AS = Importer_Shadow_AS.append(Dual_Import_AS.T)

id_y = pd.Index(AS_) 
Importer_Shadow_AS = Importer_Shadow_AS.set_index(id_y)
#Dual_Import_2019.sort_values("Shadow Price ($/MMBtu)", ascending=False, inplace = True)
Importer_Shadow_AS.T.plot(figsize = (9, 6), kind="bar", ylim=(0,11))
#plt.legend(bbox_to_anchor=(1.0, 1.0))
#plt.grid(axis = 'y', linestyle = '--', linewidth = 0.25)

###############################################################################
### 10.6 CO2
###############################################################################
Emissions_2019_AS_ = CO2_Emissions * (transported_LNG_2019_AS*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Emissions_2019_AS_CO2 = round(Emissions_2019_AS_.to_numpy().sum()/10**6,2)


Emi_AS_CO2 = [Emissions_CO2_4, Emissions_2019_AS_CO2]

Emissions_AS_CO2 = pd.DataFrame(Emi_AS_CO2,
                   
                   index = ["Normal", "Asia Pacific 20% demand decrease"],
    
                   columns = ["CO2 Emissions"])


ax = Emissions_AS_CO2.plot(figsize = (9, 6), kind="bar", color = "lightgray", rot=0, ylim=(0,69))

for container in ax.containers:
    ax.bar_label(container)

ax.set_ylabel("megatonnes")    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()

###############################################################################
### 10.7 CH4
###############################################################################
Emissions_2019_AS_CH4_ = CH4_Emissions * (transported_LNG_2019_AS*10**9) / (0.94 * LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas - LNG_Carrier.loc[0, "Capacity (m³)"] * LNG_to_Gas * LNG_Carrier.loc[0, "Boil off"] * Time)
Emissions_2019_AS_CH4 = round(Emissions_2019_AS_CH4_.to_numpy().sum()/10**3,2)


Emi_AS_CH4 = [Emissions_CH4_4, Emissions_2019_AS_CH4]

Emissions_AS_CH4 = pd.DataFrame(Emi_AS_CH4,
                   
                   index = ["Normal", "Asia Pacific 20% demand decrease"],
    
                   columns = ["CH4 Emissions"])


ax = Emissions_AS_CH4.plot(figsize = (9, 6), kind="bar", color = "grey", rot=0, ylim=(0,44))
for container in ax.containers:
    ax.bar_label(container)

ax.set_ylabel("kilotonnes")    
plt.legend(bbox_to_anchor=(1.0, 1.0))
ax.get_legend().remove()
plt.show()

"""