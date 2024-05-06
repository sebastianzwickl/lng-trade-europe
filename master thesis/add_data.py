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

geolocator = Nominatim(user_agent="Your_Name")
# list of import and export countries
import_countries = pd.read_excel("data/import_nodes.xlsx").Country
export_countries = pd.read_excel("data/export_nodes.xlsx").Country

# get all the constants required (for further information see in 'constants.py')
import constants

(
    MMBtu_LNG,
    MMBtu_Gas,
    mt_LNG_BCM,
    mt_MMBtu,
    t_oil_MMBtu,
    LNG_to_Gas,
) = constants.get_values()

#
#
#
#
#


def add_dataframes():

    """

    LNG IMPORTS ARE DEFINED HERE!

    """

    # lng imports 2019 per country from bp stats report 2019 (page 41)
    var_import_mmbtu_2019 = pd.read_excel(
        "data/input/lng_import_from_bp_2020_report.xlsx", sheet_name="LNG IMPORTS 2019"
    )["Value [bcm]"].values
    var_import_mmbtu_2030 = pd.read_excel(
        "data/input/lng_import_from_bp_2020_report.xlsx", sheet_name="LNG IMPORTS 2030"
    )["Value [bcm]"].values
    var_import_mmbtu_2040 = pd.read_excel(
        "data/input/lng_import_from_bp_2020_report.xlsx", sheet_name="LNG IMPORTS 2040"
    )["Value [bcm]"].values

    for year, values in [
        [2019, var_import_mmbtu_2019],
        [2030, var_import_mmbtu_2030],
        [2040, var_import_mmbtu_2040],
    ]:
        print(
            "Global LNG demand in {0} : {1} bcm".format(
                str(year), np.around(sum(values), 0)
            )
        )

    """
    
        SCENARIOS: 'Import Europe +33% (MMBtu)' and 'Import Asia Pacific -20% (MMBtu)'
        
    """

    # for scenario 'Import Europe +33% (MMBtu)' ==> 2030's values
    # Index list contains all regions in Europe (e.g., index 6 corresponds to France)
    var_import_mmbtu_2030_copy = var_import_mmbtu_2030
    for _index in [6, 7, 8, 9, 10, 11, 13]:
        var_import_mmbtu_2030_copy[_index] *= 4 / 3

    # for scenario 'Import Asia Pacific -20% (MMBtu)' ==> 2030's values and 2040's values of China
    # Index list contains all regions in Europe (e.g., index 6 corresponds to France)
    var_import_mmbtu_2040_copy = var_import_mmbtu_2040
    for _index in [1]:
        var_import_mmbtu_2040_copy[_index] *= 0.8

    Imp_Nodes = pd.DataFrame(
        {
            "Country": import_countries,
            "Import Jan (MMBtu)": [
                10.5651,
                9.2547,
                6.279,
                2.83,
                2.2386,
                1.1288,
                1.632,
                1.42,
                1.741,
                1.074,
                2.353,
                0.585,
                1.7,
                1.9584,
                0.911,
                0.3536,
                0.0952,
            ],
            "Import Feb (MMBtu)": [
                10.30575,
                5.93775,
                4.095,
                2.56,
                1.46055,
                0.9248,
                1.83,
                1.374,
                1.17,
                0.93,
                1.782,
                0.299,
                1.768,
                1.8496,
                0.6528,
                1.02,
                0.3536,
            ],
            "Import Mar (MMBtu)": [
                10.22385,
                5.5419,
                3.78105,
                2.38,
                2.0475,
                1.2104,
                2.335,
                1.493,
                1.78,
                1.605,
                1.4,
                1.115,
                2.1986,
                1.6864,
                0.9656,
                0.9112,
                0.1768,
            ],
            "Import Apr (MMBtu)": [
                7.7532,
                6.1971,
                3.9585,
                2.62,
                2.0748,
                1.1832,
                2.572,
                1.596,
                2.244,
                1.115,
                0.707,
                0.8074,
                2.2168,
                2.1624,
                1.02,
                1.0744,
                0.748,
            ],
            "Import May (MMBtu)": [
                7.7259,
                6.04695,
                4.05405,
                2.75,
                2.03385,
                1.1152,
                1.832,
                1.656,
                2.19,
                1.115,
                0.503,
                0.7028,
                2.9784,
                2.4072,
                0.9656,
                1.1424,
                1.4144,
            ],
            "Import Jun (MMBtu)": [
                7.2345,
                6.18345,
                4.54545,
                2.73,
                1.89735,
                1.0744,
                1.739,
                1.903,
                0.76,
                1.387,
                0.68,
                0.6528,
                2.0264,
                2.312,
                1.2784,
                1.904,
                1.3192,
            ],
            "Import Jul (MMBtu)": [
                7.2345,
                6.6612,
                4.54545,
                2.79,
                2.25225,
                1.088,
                1.046,
                2.49,
                0.3944,
                1.265,
                0.517,
                0.8704,
                2.6656,
                1.8768,
                0.8432,
                1.972,
                1.4688,
            ],
            "Import Aug (MMBtu)": [
                8.463,
                7.5075,
                4.914,
                2.82,
                1.8837,
                1.0064,
                1.638,
                2.144,
                0.19,
                1.265,
                0.816,
                0.9112,
                2.4888,
                1.9176,
                1.088,
                1.7408,
                1.8496,
            ],
            "Import Sep (MMBtu)": [
                8.94075,
                6.92055,
                3.4125,
                2.79,
                2.0475,
                0.9928,
                1.2745,
                2.139,
                1.3,
                1.13,
                0.558,
                0.2856,
                2.3256,
                1.8088,
                1.0064,
                1.0472,
                1.5776,
            ],
            "Import Oct (MMBtu)": [
                8.85885,
                5.6511,
                4.368,
                2.83,
                2.00655,
                1.0608,
                1.7745,
                1.95,
                1.85,
                1.35,
                0.843,
                0.7616,
                2.1986,
                2.0944,
                0.9248,
                0.8024,
                1.1016,
            ],
            "Import Nov (MMBtu)": [
                8.83155,
                8.66775,
                5.1597,
                2.79,
                1.51515,
                0.6664,
                2.84,
                1.931,
                2.4,
                0.94,
                1.115,
                1.0336,
                3.876,
                2.2848,
                0.5984,
                0.9384,
                0.476,
            ],
            "Import Dec (MMBtu)": [
                9.4185,
                10.30575,
                6.51105,
                2.83,
                1.7745,
                0.9792,
                2.56,
                1.81,
                3.05,
                1.1,
                1.89,
                0.9928,
                4.148,
                2.0808,
                0.9656,
                0.5576,
                0.276,
            ],
            "Regasification Terminal": [
                "Sodegaura",
                "Yancheng",
                "Incheon",
                "Dahej",
                "Kaohsiung",
                "Karachi",
                "Dunkirk",
                "Barcelona",
                "Isle of Grain",
                "Rovigo",
                "Marmara",
                "Zeebrugge",
                "Map Ta Phut, Thailand",
                "Świnoujście, Poland",
                "Ensenada, Mexico",
                "Rio de Janeiro, Brazil",
                "Al Ahmadi, Kuwait",
            ],
            "Import (MMBtu)": var_import_mmbtu_2019 * 10 ** 9 * MMBtu_Gas,
            "Import 2030 (MMBtu)": var_import_mmbtu_2030 * 10 ** 9 * MMBtu_Gas,
            "Import 2040 (MMBtu)": var_import_mmbtu_2040 * 10 ** 9 * MMBtu_Gas,
            "Import Europe +33% (MMBtu)": var_import_mmbtu_2030_copy
            * 10 ** 9
            * MMBtu_Gas,
            "Import Asia Pacific -20% (MMBtu)": var_import_mmbtu_2040_copy
            * 10 ** 9
            * MMBtu_Gas,
        }
    )

    Imp_Nodes["Location"] = Imp_Nodes["Regasification Terminal"].apply(
        geolocator.geocode
    )
    Imp_Nodes["Point"] = Imp_Nodes["Location"].apply(
        lambda loc: tuple(loc.point) if loc else None
    )
    Imp_Nodes[["Latitude", "Longitude", "Altitude"]] = pd.DataFrame(
        Imp_Nodes["Point"].to_list(), index=Imp_Nodes.index
    )

    # center the columns, display() method doesn't work anymore, so not necessary for now
    def pd_centered(df):
        return df.style.set_table_styles(
            [
                {"selector": "th", "props": [("text-align", "center")]},
                {"selector": "td", "props": [("text-align", "center")]},
            ]
        )

    # NOTE: THE SCALING FACTOR OF '0.959617719634954' MATCHES THE MONTHYL IMPORT VOLUMES IN 2019 WITH THE ANNUAL IMPORT VOLUMES, TAKEN FROM THE
    # FOLLOWING SOURCE: https://www.bp.com/en/global/corporate/energy-economics/energy-outlook/natural-gas.html
    Imp_Nodes["Import Jan (MMBtu)"] *= 10 ** 9 * MMBtu_Gas * 0.959617719634954
    Imp_Nodes["Import Feb (MMBtu)"] *= 10 ** 9 * MMBtu_Gas * 0.959617719634954
    Imp_Nodes["Import Mar (MMBtu)"] *= 10 ** 9 * MMBtu_Gas * 0.959617719634954
    Imp_Nodes["Import Apr (MMBtu)"] *= 10 ** 9 * MMBtu_Gas * 0.959617719634954
    Imp_Nodes["Import May (MMBtu)"] *= 10 ** 9 * MMBtu_Gas * 0.959617719634954
    Imp_Nodes["Import Jun (MMBtu)"] *= 10 ** 9 * MMBtu_Gas * 0.959617719634954
    Imp_Nodes["Import Jul (MMBtu)"] *= 10 ** 9 * MMBtu_Gas * 0.959617719634954
    Imp_Nodes["Import Aug (MMBtu)"] *= 10 ** 9 * MMBtu_Gas * 0.959617719634954
    Imp_Nodes["Import Sep (MMBtu)"] *= 10 ** 9 * MMBtu_Gas * 0.959617719634954
    Imp_Nodes["Import Oct (MMBtu)"] *= 10 ** 9 * MMBtu_Gas * 0.959617719634954
    Imp_Nodes["Import Nov (MMBtu)"] *= 10 ** 9 * MMBtu_Gas * 0.959617719634954
    Imp_Nodes["Import Dec (MMBtu)"] *= 10 ** 9 * MMBtu_Gas * 0.959617719634954

    ###########################################################################
    ###########################################################################
    ###########################################################################

    """
    
        LNG EXPORTS ARE DEFINED HERE!
        
    """

    var_export_mmbtu_2019 = pd.read_excel(
        "data/input/lng_export_from_bp_2020_report.xlsx", sheet_name="LNG EXPORTS 2019"
    )["Value [bcm]"].values

    Exp_Nodes = pd.DataFrame(
        {
            "Country": export_countries,
            "Export (MMBtu)": var_export_mmbtu_2019 * 10 ** 9 * MMBtu_Gas,
            "Export Jan (MMBtu)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Export Feb (MMBtu)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Export Mar (MMBtu)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Export Apr (MMBtu)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Export May (MMBtu)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Export Jun (MMBtu)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Export Jul (MMBtu)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Export Aug (MMBtu)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Export Sep (MMBtu)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Export Oct (MMBtu)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Export Nov (MMBtu)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Export Dec (MMBtu)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Export 2030 (MMBtu)": [
                151.69,
                124.4,
                150.5,
                60,
                43,
                39.28,
                17,
                20,
                37.7,
                15.86,
                20.9,
                8.6,
                50,
                7.7,
                60,
            ],
            "Export 2040 (MMBtu)": [
                173.75,
                140,
                220,
                85,
                43,
                70,
                17,
                20,
                37.7,
                15.86,
                20.9,
                8.6,
                60,
                7.7,
                100,
            ],
            "Break Eeven Price ($/MMBtu)": [
                2.36,
                7.5,
                5.95,
                4.5,
                6.0,
                4.08,
                5.1,
                4.93,
                6.0,
                3.7,
                8.4,
                5.0,
                6.0,
                3.0,
                4.5,
            ],
            "Break Eeven Price 2030 ($/MMBtu)": [
                2.934,
                9.325,
                7.398,
                5.595,
                7.46,
                5.0723,
                6.341,
                6.13,
                7.46,
                4.6,
                10.444,
                6.217,
                7.460,
                3.73,
                5.595,
            ],
            "Break Eeven Price 2040 ($/MMBtu)": [
                3.577,
                11.367,
                9.018,
                6.82,
                9.094,
                6.184,
                7.73,
                7.472,
                9.094,
                5.608,
                12.731,
                7.578,
                9.094,
                4.547,
                6.82,
            ],
            "Liquefaction Terminal": [
                "Ras Laffan",
                "Gladstone",
                "Sabine Pass",
                "Sabetta",
                "Bintulu",
                "Bonny Island",
                "Point Fortin",
                " Bethioua",
                "Bontang",
                "Qalhat, Oman",
                "Port Moresby, Papua New Guinea",
                "Hammerfest, Norway",
                "Callao, Peru",
                "Abu Dhabi, UAE",
                "Soyo, Angola",
            ],
            # data for capacity from IGU 2020
            "Nominal Liquefaction Capacity 2019 (MMBtu)": [
                77.665 * mt_MMBtu,
                86 * mt_MMBtu,
                37.8 * mt_MMBtu,
                26.6 * 1.07 * mt_MMBtu,
                30.5 * mt_MMBtu,
                22.2 * mt_MMBtu,
                14.8 * mt_MMBtu,
                25.5 * mt_MMBtu,
                26.6 * mt_MMBtu,
                10.4 * mt_MMBtu,
                14.1 * mt_MMBtu,
                4.2 * mt_MMBtu,
                4.5 * mt_MMBtu,
                5.8 * mt_MMBtu,
                11.3 * mt_MMBtu,
            ],
            "Nominal Liquefaction Capacity (MMBtu)": [
                77.1 * mt_MMBtu / 12,
                86 * mt_MMBtu / 12,
                37.8 * mt_MMBtu / 12,
                26.6 * 1.07 * mt_MMBtu / 12,
                30.5 * mt_MMBtu / 12,
                22.2 * mt_MMBtu / 12,
                14.8 * mt_MMBtu / 12,
                25.5 * mt_MMBtu / 12,
                26.6 * mt_MMBtu / 12,
                10.4 * mt_MMBtu / 12,
                14.1 * mt_MMBtu / 12,
                4.2 * mt_MMBtu / 12,
                4.5 * mt_MMBtu / 12,
                5.8 * mt_MMBtu / 12,
                11.3 * mt_MMBtu / 12,
            ],
            "Nominal Liquefaction Capacity 2019 HC (MMBtu)": [
                (2 / 3) * 77.1 * mt_MMBtu,
                86 * mt_MMBtu,
                37.8 * mt_MMBtu,
                26.6 * 1.07 * mt_MMBtu,
                30.5 * mt_MMBtu,
                22.2 * mt_MMBtu,
                14.8 * mt_MMBtu,
                25.5 * mt_MMBtu,
                26.6 * mt_MMBtu,
                (2 / 3) * 10.4 * mt_MMBtu,
                14.1 * mt_MMBtu,
                4.2 * mt_MMBtu,
                4.5 * mt_MMBtu,
                (2 / 3) * 5.8 * mt_MMBtu,
                11.3 * mt_MMBtu,
            ],
        }
    )

    # Price for US: https://www.macrotrends.net/2478/natural-gas-prices-historical-chart and
    # https://www.argusmedia.com/en/news/1431713-cheniere-longterm-lng-sales-data-excludes-some-fees
    # Price for Qatar and Algeria: https://www.argusmedia.com/en/news/2098570-sonatrach-offers-spot-lng-cargoes-as-exports-slow
    # Price for Papua NG: https://oilprice.com/Energy/Energy-General/Low-Gas-Prices-Could-Derail-Papua-New-Guineas-LNG-Ambitions.html
    # Egypt Export 2019: https://www.mees.com/2020/4/10/oil-gas/egypt-2019-lng-exports/2aa75e10-7b34-11ea-9c97-c54251792df2
    # Russia Export 2019: https://www.hellenicshippingnews.com/russian-lng-exports-a-year-in-review/

    # Exp_Countries["Export (Bcm)"] = (Exp_Countries["Export (Bcm)"].astype(float)/1000000000).astype(str)

    Exp_Nodes["Location"] = Exp_Nodes["Liquefaction Terminal"].apply(geolocator.geocode)
    Exp_Nodes["Point"] = Exp_Nodes["Location"].apply(
        lambda loc: tuple(loc.point) if loc else None
    )
    Exp_Nodes[["Latitude", "Longitude", "Altitude"]] = pd.DataFrame(
        Exp_Nodes["Point"].to_list(), index=Exp_Nodes.index
    )

    Exp_Nodes["Export Jan (MMBtu)"] = (
        Exp_Nodes["Nominal Liquefaction Capacity (MMBtu)"] * 1.007
    )
    Exp_Nodes["Export Jun (MMBtu)"] = (
        Exp_Nodes["Nominal Liquefaction Capacity (MMBtu)"] * 0.95
    )
    Exp_Nodes["Export Sep (MMBtu)"] = (
        Exp_Nodes["Nominal Liquefaction Capacity (MMBtu)"] * 0.968
    )
    Exp_Nodes["Export Aug (MMBtu)"] = (
        Exp_Nodes["Nominal Liquefaction Capacity (MMBtu)"] * 0.95
    )
    Exp_Nodes["Export Nov (MMBtu)"] = (
        Exp_Nodes["Nominal Liquefaction Capacity (MMBtu)"] * 1.005
    )
    Exp_Nodes["Export Dec (MMBtu)"] = (
        Exp_Nodes["Nominal Liquefaction Capacity (MMBtu)"] * 1.12
    )

    Exp_Nodes["Export 2030 (MMBtu)"] *= 10 ** 9 * MMBtu_Gas
    Exp_Nodes["Export 2040 (MMBtu)"] *= 10 ** 9 * MMBtu_Gas

    ###########################################################################
    ###########################################################################
    ###########################################################################

    Distances = pd.DataFrame(
        [
            (
                6512,
                5846,
                6161,
                1301,
                5251,
                881,
                6240,
                4650,
                6260,
                4380,
                3460,
                6270,
                4374,
                6840,
                11406,
                8154,
                297,
            ),
            (
                3861,
                4134,
                4313,
                5918,
                3594,
                6306,
                11650,
                10060,
                11670,
                9790,
                8870,
                11680,
                4091,
                12190,
                6367,
                8078,
                7279,
            ),
            (
                9205,
                10075,
                10005,
                9645,
                10495,
                9460,
                4881,
                5206,
                4897,
                6354,
                6341,
                4908,
                12015,
                5364,
                4315,
                5234,
                9930,
            ),
            (
                4929,
                5596,
                5671,
                8810,
                6279,
                8570,
                2494,
                4252,
                2511,
                5546,
                5481,
                2477,
                7821,
                2547,
                9185,
                7524,
                9040,
            ),
            (
                2276,
                1656,
                1998,
                3231,
                1262,
                3466,
                8980,
                7390,
                9000,
                7120,
                6200,
                9010,
                926,
                9360,
                7364,
                9061,
                4439,
            ),
            (
                10752,
                10088,
                10406,
                6988,
                9446,
                7059,
                4287,
                3824,
                4309,
                4973,
                4961,
                4321,
                8697,
                4832,
                8095,
                3387,
                7577,
            ),
            (
                8885,
                9755,
                9665,
                8370,
                10175,
                8210,
                3952,
                3926,
                3974,
                5074,
                5062,
                3984,
                11127,
                4536,
                4005,
                3113,
                8680,
            ),
            (
                9590,
                8930,
                9240,
                4720,
                8328,
                4540,
                1519,
                343,
                1541,
                1432,
                1417,
                1552,
                7450,
                2129,
                7445,
                4464,
                5000,
            ),
            (
                2651,
                2181,
                2487,
                3517,
                1448,
                4014,
                9260,
                7670,
                9280,
                7390,
                6470,
                9290,
                1651,
                9910,
                7203,
                9212,
                4987,
            ),
            (
                6046,
                5379,
                5694,
                853,
                4741,
                446,
                5760,
                4180,
                5790,
                3900,
                2980,
                5800,
                3864,
                6310,
                10896,
                7623,
                808,
            ),
            (
                3139,
                3403,
                3541,
                5311,
                2839,
                5601,
                10980,
                9300,
                10990,
                9030,
                8110,
                10970,
                3384,
                11480,
                6184,
                8894,
                6572,
            ),
            (
                12450,
                11770,
                12090,
                7570,
                11160,
                7380,
                1389,
                3124,
                1378,
                4273,
                4261,
                1376,
                10310,
                1374,
                8044,
                6352,
                7860,
            ),
            (
                8424,
                9304,
                9231,
                10665,
                9484,
                10475,
                6085,
                6215,
                6105,
                7365,
                7355,
                6115,
                11132,
                6645,
                3527,
                5064,
                10980,
            ),
            (
                6444,
                5778,
                6093,
                1233,
                5162,
                803,
                6180,
                4590,
                6200,
                4310,
                3390,
                6210,
                4284,
                6950,
                11328,
                8091,
                351,
            ),
            (
                10057,
                9291,
                9608,
                6191,
                8677,
                6262,
                4878,
                4409,
                4901,
                5559,
                5546,
                4911,
                8053,
                5654,
                8595,
                3357,
                6741,
            ),
        ],
        index=export_countries,
        columns=import_countries,
    )

    # Define DF with distances among largest liquefaction and regas terminals in nautical miles
    # In case of lack of the route to the specific terminal, next largest port was taken
    # sea-distances.org, searoutes.com

    # if route over canal: distance rounded on 0 for suez and on 5 for panama, needed for later calculations

    Distances_Suez_Closed = pd.DataFrame(
        [
            (
                6512,
                5846,
                6161,
                1301,
                5251,
                881,
                11044,
                10587,
                11084,
                11811,
                11849,
                11009,
                4374,
                11753,
                11406,
                8154,
                297,
            ),
            (
                3861,
                4134,
                4313,
                5918,
                3594,
                6306,
                12555,
                12695,
                12575,
                13845,
                13825,
                12585,
                4091,
                13125,
                6367,
                8078,
                7279,
            ),
            (
                9205,
                10075,
                10005,
                9645,
                10495,
                12069,
                4881,
                5206,
                4897,
                6354,
                6341,
                4908,
                12015,
                5364,
                4315,
                5234,
                12548,
            ),
            (
                4929,
                5596,
                5671,
                10541,
                6279,
                10816,
                2494,
                4252,
                2511,
                5546,
                5481,
                2477,
                7821,
                2547,
                9185,
                7524,
                11762,
            ),
            (
                2276,
                1656,
                1998,
                3231,
                1262,
                3466,
                12003,
                11544,
                12043,
                12769,
                12689,
                12049,
                926,
                12612,
                7364,
                9061,
                4439,
            ),
            (
                10752,
                10088,
                10406,
                6988,
                9446,
                7059,
                4287,
                3824,
                4309,
                4973,
                4961,
                4321,
                8697,
                4832,
                8095,
                3387,
                7577,
            ),
            (
                8885,
                9755,
                9665,
                10054,
                10175,
                10009,
                3952,
                3926,
                3974,
                5074,
                5062,
                3984,
                11127,
                4536,
                4005,
                3113,
                10534,
            ),
            (
                12425,
                13038,
                13424,
                10101,
                8328,
                10056,
                1519,
                343,
                1541,
                1432,
                1417,
                1552,
                7450,
                2129,
                7445,
                4464,
                10581,
            ),
            (
                2651,
                2181,
                2487,
                3517,
                1448,
                4014,
                12129,
                11671,
                12169,
                12894,
                12814,
                12176,
                1651,
                12738,
                7203,
                9212,
                4987,
            ),
            (
                6046,
                5379,
                5694,
                853,
                4741,
                446,
                10503,
                10044,
                10542,
                11269,
                11188,
                10549,
                3864,
                11112,
                10896,
                7623,
                808,
            ),
            (
                3139,
                3403,
                3541,
                5311,
                2839,
                5601,
                13279,
                13319,
                12821,
                14044,
                13964,
                13324,
                3384,
                13888,
                6184,
                8894,
                6572,
            ),
            (
                13075,
                13995,
                13915,
                12114,
                14494,
                12069,
                1389,
                3124,
                1378,
                4273,
                4261,
                1376,
                13714,
                1374,
                8044,
                6352,
                12594,
            ),
            (
                8424,
                9304,
                9231,
                10665,
                9484,
                10475,
                6085,
                6215,
                6105,
                7365,
                7355,
                6115,
                11132,
                6645,
                3527,
                5064,
                12349,
            ),
            (
                6444,
                5778,
                6093,
                1233,
                5162,
                803,
                10953,
                10494,
                10992,
                11719,
                11638,
                10999,
                4284,
                11562,
                11328,
                8091,
                351,
            ),
            (
                10057,
                9291,
                9608,
                6191,
                8677,
                6262,
                4878,
                4409,
                4901,
                5559,
                5546,
                4911,
                8053,
                5654,
                8595,
                3357,
                6741,
            ),
        ],
        index=export_countries,
        columns=import_countries,
    )

    ###########################################################################
    ###########################################################################
    ###########################################################################

    LNG_Carrier = pd.DataFrame(
        {
            "Capacity (m³)": [
                160000
            ],  # average capacity in 2019 160000 (!!! GIIGNL p. 21; https://www.rivieramm.com/opinion/opinion/lng-shipping-by-numbers-36027)
            "Spot Charter Rate ($/day)": [
                69337
            ],  # average spot charter rate in 2019 (https://www.statista.com/statistics/1112660/lng-tanker-average-spot-charter-rate/)
            "Speed (knots/h)": [
                17
            ],  # Argus LNG daily (MT/Literature/Transport and Contracts)
            "Bunker (mt/d)": [
                99
            ],  # Almost half of tankers are ST (supertankers), Outlook for competitive LNG supply Oxford
            "Bunkers Price ($/mt)": [670],  # Outlook for competitive LNG supply Oxford
            "Boil off": [
                1 / 1000
            ],  # the daily guaranteed maximum boil-off or DGMB (0,1%)
            "Boil Cost $/mmBtu": [5],
            "Heel": [4 / 100],
        }
    )  # 4% of the cargo is retained as the heel (LNG storage tanks need to be kept cool)

    ###########################################################################
    ###########################################################################
    ###########################################################################

    Additional_Costs = pd.DataFrame(
        {
            "Port Costs ($ for 3 days)": [400000],
            "Suez Canal Costs ($/Cargo)": [1000000],  # 0.24 $/mmBtU
            "Panama Canal Costs ($/Cargo)": [950000],  # 0.21 $/mmBtu,
            "Insurance ($/day)": [2600],
            "Fees (Percentage of Charter Costs)": [2 / 100],
        }
    )

    ###########################################################################
    ###########################################################################
    ###########################################################################

    CO2 = pd.DataFrame({"Bunker Fuel": [0.0845], "BOG": [0.0576]})  # t/mmBtu

    CH4 = pd.DataFrame({"Bunker Fuel": [0.0000046], "BOG": [0.0000916]})  # t/mmBtu

    empty_df = pd.DataFrame(
        np.zeros((len(Distances.index), len(Distances.columns))),
        index=export_countries,
        columns=import_countries,
    )

    return (
        Imp_Nodes,
        Exp_Nodes,
        Distances,
        Distances_Suez_Closed,
        LNG_Carrier,
        Additional_Costs,
        CO2,
        CH4,
        empty_df,
    )


###############################################################################
### add costs
### point 2 from original model
###############################################################################


def add_costs(
    Distances, Distances_Suez_Closed, LNG_Carrier, Additional_Costs, CO2, CH4
):
    ###############################################################################
    ### 2.1 (Return) voyage times
    ###############################################################################
    # https://timera-energy.com/deconstructing-lng-shipping-costs/ and OIES articles!
    # Distances x 2 because of traveling to and back
    # Time divided by 24 because of time is measured in days
    # ==> 2 / 24 = 1 / 12 factor
    Time = Distances / (LNG_Carrier.loc[0, "Speed (knots/h)"] * 12)  # in days

    Time_Suez_Closed = Distances_Suez_Closed / (
        LNG_Carrier.loc[0, "Speed (knots/h)"] * 12
    )  # in days

    ###############################################################################
    ### 2.2 Charter costs
    ###############################################################################
    Charter_Costs = (Time + 3) * LNG_Carrier.loc[0, "Spot Charter Rate ($/day)"]  # in $

    Charter_Costs_Suez_Closed = (Time_Suez_Closed + 3) * LNG_Carrier.loc[
        0, "Spot Charter Rate ($/day)"
    ]  # in $

    ###############################################################################
    ### 2.3 Fuel costs
    ###############################################################################
    Fuel_Costs = (
        Time
        * LNG_Carrier.loc[0, "Bunker (mt/d)"]
        * LNG_Carrier.loc[0, "Bunkers Price ($/mt)"]
        + 3 * 25 * LNG_Carrier.loc[0, "Bunkers Price ($/mt)"]
    )

    Fuel_Costs_Suez_Closed = (
        Time_Suez_Closed
        * LNG_Carrier.loc[0, "Bunker (mt/d)"]
        * LNG_Carrier.loc[0, "Bunkers Price ($/mt)"]
        + 3 * 25 * LNG_Carrier.loc[0, "Bunkers Price ($/mt)"]
    )

    ### Boiloff

    BoilOff = (
        Time
        * LNG_Carrier.loc[0, "Boil off"]
        * LNG_Carrier.loc[0, "Capacity (m³)"]
        * MMBtu_LNG
        * 0.98
    )

    BoilOff_Cost = BoilOff * LNG_Carrier.loc[0, "Boil Cost $/mmBtu"]

    ### Suez Closed
    BoilOff_Suez_Closed = (
        Time_Suez_Closed
        * LNG_Carrier.loc[0, "Boil off"]
        * LNG_Carrier.loc[0, "Capacity (m³)"]
        * MMBtu_LNG
    )

    BoilOff_Cost_Suez_Closed = (
        BoilOff_Suez_Closed * LNG_Carrier.loc[0, "Boil Cost $/mmBtu"]
    )

    ##### Emissions
    Consumption_HOF = Time * LNG_Carrier.loc[0, "Bunker (mt/d)"] + 3 * 25

    CO2_Emissions_Bunker = Consumption_HOF * t_oil_MMBtu * CO2.loc[0, "Bunker Fuel"]
    CO2_Emissions_BoilOff = BoilOff * CO2.loc[0, "BOG"]

    CO2_Emissions = CO2_Emissions_Bunker + CO2_Emissions_BoilOff

    CH4_Emissions_Bunker = Consumption_HOF * t_oil_MMBtu * CH4.loc[0, "Bunker Fuel"]
    CH4_Emissions_BoilOff = BoilOff * CH4.loc[0, "BOG"]

    CH4_Emissions = CH4_Emissions_Bunker + CH4_Emissions_BoilOff

    ###############################################################################
    ### 2.4 Agents and Broker Fees + Insurance
    ###############################################################################
    Fees_and_Insurance = (Time + 3) * Additional_Costs.loc[
        0, "Insurance ($/day)"
    ] + Charter_Costs * Additional_Costs.loc[0, "Fees (Percentage of Charter Costs)"]

    Fees_and_Insurance_Suez_Closed = (Time_Suez_Closed + 3) * Additional_Costs.loc[
        0, "Insurance ($/day)"
    ] + Charter_Costs_Suez_Closed * Additional_Costs.loc[
        0, "Fees (Percentage of Charter Costs)"
    ]

    ###############################################################################
    ### 2.5 Suez/Panama Canal Fee
    ###############################################################################
    Canal_Fees = pd.DataFrame(
        np.zeros((len(Distances.index), len(Distances.columns))),
        index=export_countries,
        columns=import_countries,
    )

    for index in Distances.index:
        for columns in Distances.columns:
            if ((Distances.loc[index, columns]) % 5 == 0) and (
                (Distances.loc[index, columns]) % 10 != 0
            ):
                print('Panama Canal')
                print('Exporter:', index)
                print('Importer:', columns)
                Canal_Fees.loc[index, columns] += Additional_Costs.loc[
                    0, "Panama Canal Costs ($/Cargo)"
                ]
            elif (Distances.loc[index, columns]) % 10 == 0:
                print('Suez Canal')
                print('Exporter:', index)
                print('Importer:', columns)
                Canal_Fees.loc[index, columns] += Additional_Costs.loc[
                    0, "Suez Canal Costs ($/Cargo)"
                ]
    
    Canal_Fees.to_excel('data/canal_fees.xlsx')

    ###############################################################################
    ### 2.6 Port Costs
    ###############################################################################
    Port_Costs = pd.DataFrame(
        np.zeros((len(Distances.index), len(Distances.columns))),
        index=export_countries,
        columns=import_countries,
    )

    Port_Costs += Additional_Costs.loc[0, "Port Costs ($ for 3 days)"]

    ###############################################################################
    ### 2.7 Total Costs of Transportation
    ###############################################################################
    Transport_Costs = (
        Charter_Costs
        + Fuel_Costs
        + Fees_and_Insurance
        + Canal_Fees
        + Port_Costs
        + BoilOff_Cost
    )

    Transport_Costs_Suez_Closed = (
        Charter_Costs_Suez_Closed
        + Fuel_Costs_Suez_Closed
        + Fees_and_Insurance_Suez_Closed
        + Canal_Fees
        + Port_Costs
        + BoilOff_Cost_Suez_Closed
    )

    #######

    Transport_Costs_MMBtu = Transport_Costs / (
        (
            0.96 * LNG_Carrier.loc[0, "Capacity (m³)"]
            - LNG_Carrier.loc[0, "Capacity (m³)"]
            * LNG_Carrier.loc[0, "Boil off"]
            * Time
        )
        * MMBtu_LNG
    )  # 1-heel-boil_off = 0.94

    Transport_Costs_MMBtu_Suez_Closed = Transport_Costs_Suez_Closed / (
        (
            0.96 * LNG_Carrier.loc[0, "Capacity (m³)"]
            - LNG_Carrier.loc[0, "Capacity (m³)"]
            * LNG_Carrier.loc[0, "Boil off"]
            * Time_Suez_Closed
        )
        * MMBtu_LNG
    )  # 1-heel-boil_off = 0.94

    ###############################################################################
    ### 2.8 Total Costs
    ###############################################################################
    # taken from EXP_Countries df

    Breakeven = pd.DataFrame(
        [
            (
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
                2.36,
            ),
            (
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
                7.5,
            ),
            (
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
                5.95,
            ),
            (
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
            ),
            (
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
            ),
            (
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
                4.08,
            ),
            (
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
                5.1,
            ),
            (
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
                2.5,
            ),
            (
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
            ),
            (
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
                3.7,
            ),
            (
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
                7.7,
            ),
            (
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
            ),
            (
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
                6.0,
            ),
            (
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
            ),
            (
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
                4.5,
            ),
        ],
        index=export_countries,
        columns=import_countries,
    )

    Total_Costs = Breakeven + Transport_Costs_MMBtu
    Total_Costs_Suez_Closed = Breakeven + Transport_Costs_MMBtu_Suez_Closed
    return Time, Time_Suez_Closed, CO2_Emissions, CH4_Emissions, Total_Costs
