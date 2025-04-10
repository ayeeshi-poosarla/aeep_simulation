# force_analysis.py

import numpy as np

def force_analysis(bend_values, area, calibration_factor=1.0):
    bend_values = np.array(bend_values)
    
    
    # get pressure: P = F / A
    pressures = bend_values / area
    
    return pressures


