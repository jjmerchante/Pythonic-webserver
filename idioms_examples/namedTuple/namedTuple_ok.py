from collections import namedtuple

def get_point():
    point = namedtuple("point", "x y")
    # ...
    x = 2.0
    y = -3.5
    return point(x, y)

point = get_point()
print(point.x, point.y) # better
