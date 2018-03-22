from itertools import tee

it = xrange(10)

it1, it2, it3 = tee(it, 3)

print it1.next() # 0
print it2.next() # 0
print it2.next() # 1
print it3.next() # 0
