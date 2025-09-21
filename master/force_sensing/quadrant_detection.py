def determine_quadrant(n, s, e, w, threshold = 10):
    vertical = n - s
    horizontal = e - w

    if abs(vertical) < threshold:
        vertical = 0
    if abs(horizontal) < threshold:
        horizontal = 0

    if vertical > 0 and horizontal > 0:
        return "quadrant 1"
    elif vertical > 0 and horizontal < 0:
        return "quadrant 2"
    elif vertical < 0 and horizontal < 0:
        return "quadrant 3"
    elif vertical < 0 and horizontal > 0:
        return "quadrant 4"
    elif vertical > 0:
        return "north"
    elif vertical < 0:
        return "south"
    elif horizontal > 0:
        return "east"
    elif horizontal < 0:
        return "west"
    else:
        return "center"
