# force_analysis.py

import numpy as np
import math

def force_analysis(n, s, e, w):
    x = e - w
    y = n - s

    angle = math.degrees(math.atan2(x, y))

    if angle < 0:
        angle += 360

    return angle


