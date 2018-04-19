from collections import defaultdict

s = "Honorificabilitudinitatibus"
d = defaultdict(int)
for char in s:
    d[char] += 1 # Doesn't raise KeyError

print(d)
#defaultdict(<type 'int'>, {'a': 2, 'c': 1, 'b': 2, 'd': 1, 'f': 1, 'i': 7, 'H': 1, 'l': 1, 'o': 2, 'n': 2, 's': 1, 'r': 1, 'u': 2, 't': 3})
