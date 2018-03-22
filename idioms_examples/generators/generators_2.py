def my_xrange(n):
    # I should use range in Python3 or xrange in Python2
    # But this is bit more intuitive for beginner Python programmers
    i = 0
    while i < n:
        yield i
        i += 1


def my_range(n):
    # I should use range in Python2 for a list comprehension
    # But this is bit more intuitive for beginner Python programmers
    l = []
    i = 0
    while i < n:
        l.append(i)
        i += 1
    return l

for i in my_xrange(10000000):
    pass
# It took 0.514423131943 sec

for i in my_range(10000000):
    pass
# It took 0.966587781906 sec
