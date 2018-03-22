from itertools import starmap
items = [(1, 7), (2, 8), (3, 9)]
res = starmap(lambda x, y: x*y, items)
print list(res) # res is an iterator
# [7, 16, 27]
