import pandas as pd

def get_input_data_from_excel_sheets(name=None):
    _to_return = []
    for item in name:
        _get = pd.read_excel('input data/' + item)
        _to_return.append(_get)
    return _to_return
        