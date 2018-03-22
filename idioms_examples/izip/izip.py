from itertools import izip

names = ["John", "Alexander", "Bob"]
marks = [5.5, 7, 10]
for name, mark in izip(names, marks):
    print name, mark

# Jhon 5.5
# Alexander 7
# Bob 10
