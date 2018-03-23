from collections import Counter

s = "Honorificabilitudinitatibus"

c = Counter(s) # Counter from iterable
print c['i'] # 7
print list(c.elements()) # ['a', 'a', 'c', 'b', 'b', 'd', 'f', 'i', 'i', 'i', 'i', 'i', 'i', 'i', 'H', 'l', 'o', 'o', 'n', 'n', 's', 'r', 'u', 'u', 't', 't', 't']
print c.most_common(4) # [('i', 7), ('t', 3), ('a', 2), ('b', 2)]

print c # Counter({'i': 7, 't': 3, 'a': 2, ...
c.subtract(['i'])
print c # Counter({'i': 6, 't': 3, 'a': 2,
