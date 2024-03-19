import pandas as pd
import numpy as np

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


_panama_exporter=[]
_panama_importer=[]

for exporter in Distances.index:
    for importer in Distances.columns:
        _dis = Distances.at[exporter, importer]
        
        #  information whether or not route uses suez or panama canal is included in the distance
        #  if route over suze canal: distance rounded on 0
        #  if route over panama canal: distance rounded on 5
        #  else no route used. 
        
        if np.mod(_dis, 10) != 0:
            if np.mod(_dis, 5) == 0:
                _panama_exporter.append(exporter)
                _panama_importer.append(importer)
            else:
                pass
        else:
            pass

_panama = pd.DataFrame({'Exporter' : _panama_exporter, 'Importer': _panama_importer})
_panama.to_excel('panama routes.xlsx', index=False)
        

    
    
    

