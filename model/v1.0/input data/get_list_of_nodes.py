import pandas as pd

data = pd.read_excel('delivered ex-ship price 2019.xlsx')
_nodesA = data.Origin
_nodesB = data.Destination

list_of_nodes = sorted(list(set(list(_nodesA) + list(_nodesB))))