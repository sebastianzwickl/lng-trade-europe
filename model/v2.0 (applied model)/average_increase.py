import numpy as np


def calculate_average_increase(year_values):
    
    Delta = year_values[-1] - year_values[0]
    Relative = (Delta / year_values[0])
    _Step = np.around(Relative / 10 * 100, 2)
    print("Average increase between pairs of years:", _Step)
    return
