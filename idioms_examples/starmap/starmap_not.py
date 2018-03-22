from itertools import starmap
items = [(1, 7), (2, 8), (3, 9)]
res = map(lambda x: x[0]*x[1], items)
print res # res is an iterator
# [7, 16, 27]
