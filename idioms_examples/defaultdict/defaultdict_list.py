from collections import defaultdict

d = defaultdict(list)

d["a"].append(1)
d["a"].append(2)
d["b"].append(5)
print(d["c"]) # []
print(d) # defaultdict(<type 'list'>, {'a': [1, 2], 'c': [], 'b': [5]})
