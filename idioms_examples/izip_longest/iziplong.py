from itertools import izip_longest

names = ["John", "Alexander", "Bob", "Alice"]
marks = [5.5, 7, 10]
for name, mark in izip_longest(names, marks, fillvalue="absent"):
    print name, mark

# Jhon 5.5
# Alexander 7
# Bob 10
# Alice absent
