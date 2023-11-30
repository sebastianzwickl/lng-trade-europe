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
### create and solve model for every month
###############################################################################
def create_and_solve_model(Demand, Supply, Cost):
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
            
    results = SolverFactory('gurobi').solve(model)
    
    return model

###############################################################################
### init parameters
###############################################################################
geolocator = Nominatim(user_agent="Your_Name")

#pd.set_option('precision', 3)
MMBtu_LNG = 23.12 # 1m³ of LNG = 21.04MMBtu
MMBtu_Gas = 0.036 # 1m³ of Gas = 0.036MMBtu
LNG_to_Gas = 584 # 1m³ of LNG = 584m³ of gas (IGU LNG Annual Report 2019)
mt_LNG_BCM = 1.379 * 10**9 # mega tonne of LNG to bcm (https://www.enerdynamics.com/Energy-Currents_Blog/Understanding-Liquefied-Natural-Gas-LNG-Units.aspx)
mt_MMBtu = mt_LNG_BCM * MMBtu_Gas
t_oil_MMBtu = 39.6526 #  tonne of oil to mmbtu             https://unitjuggler.com/

import_countries = ["Japan", "China", "South Korea", "India", "Taiwan", 
                    "Pakistan", "France", "Spain","UK", "Italy", "Turkey", 
                    "Belgium", "Other Asia Pacific", "Other Europe",
                    "Total North America", "Total S. & C. America", 
                    "Total ME & Africa"
                    ]

export_countries = ["Qatar", "Australia", "USA", "Russia", "Malaysia", 
                    "Nigeria", "Trinidad & Tobago", "Algeria", "Indonesia", 
                    "Oman", "Other Asia Pacific", "Other Europe", 
                    "Other Americas", "Other ME", "Other Africa"
                    ]

###############################################################################
### calculate monthly values from model results
###############################################################################
def calculate_model_month(model, TotalCosts, Distances, month, Import):
    transported_LNG = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),
                        index = export_countries,
                        columns = import_countries)

    for exporter in transported_LNG.index:
        for importer in transported_LNG.columns:
            transported_LNG.loc[exporter, importer] = model.x[importer, exporter]() / MMBtu_Gas / 1000000000
            
    Merit_Order = pd.DataFrame(np.zeros((len(Distances.index),len(Distances.columns))),                     
                        index = export_countries,
                        columns = import_countries)

    for i in transported_LNG.index:
        for j in transported_LNG.columns:
            if transported_LNG.loc[i,j] > 0:
                Merit_Order.loc[i,j] = TotalCosts.loc[i,j]

    Sum = Merit_Order * transported_LNG * MMBtu_Gas * 1000000000

    DES = pd.DataFrame(np.zeros((1,len(Merit_Order.columns))),
                       index = [month],
                       columns = import_countries)

    Imp = pd.DataFrame(np.zeros((1,len(Merit_Order.columns))),         
                       index = [month],
                       columns = import_countries)
    Imp.loc[month] = Import
    Imp *= 10**9 * MMBtu_Gas
    
    for column in Sum.columns:
        DES.loc[month, column] = Sum[column].sum()

    DES_price = DES / Imp
    DES_priceT = DES_price.T

    DES_priceT.sort_values(by=month, ascending=False, inplace = True)

    # plt.rcParams['figure.dpi'] = 200
    # DES_priceT.plot(kind = 'bar', color = 'orange', figsize=(9,6))
    
    return transported_LNG, DES_price

def shadow_price_exp(model, SRC):
    dual_exp = pd.DataFrame(np.zeros((1, len(export_countries))),
                       index = ["Shadow Price ($/MMBtu)"],
                       columns = export_countries)

    for m in model.src.keys():
        s = SRC[m-1]
        dual_exp.loc["Shadow Price ($/MMBtu)", s] = model.dual[model.src[m]]
        
    dual_T = dual_exp.T
    dual_T.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
    # ax = dual_T.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
    # ax.set_xlabel("$/MMBtu", fontsize=14)
    # ax.set_ylabel("", fontsize=14)
    # plt.show()
    
    return dual_exp

def shadow_price_imp(model, CUS):
    dual_imp = pd.DataFrame(np.zeros((1, len(import_countries))),
                       index = ["Shadow Price ($/MMBtu)"],
                       columns = import_countries)

    for n in model.dmd.keys():
        c = CUS[n-1]
        dual_imp.loc["Shadow Price ($/MMBtu)", c] = model.dual[model.dmd[n]]
        
    dual_T = dual_imp.T
    dual_T.sort_values("Shadow Price ($/MMBtu)", ascending=True, inplace = True)
    # ax = dual_T.plot(kind = 'barh', figsize = (10, 7), legend = True, fontsize = 14, color="red")
    # ax.set_xlabel("$/MMBtu", fontsize=14)
    # ax.set_ylabel("", fontsize=14)
    # plt.show()
    
    return dual_imp  

















