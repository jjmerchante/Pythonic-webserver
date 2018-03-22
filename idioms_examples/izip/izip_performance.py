import time

def time_dec(func):
    def wrap(*arg, **kwargs):
        init_time = time.time()
        res = func(*arg, **kwargs)
        print func.__name__, time.time()-init_time
        return res
    return wrap
from itertools import izip

names = ["John", "Alexander", "Bob", "John", "Alexander", "Bob"]
marks = [5.5, 7, 10]

@time_dec
def z():
    for name, mark in zip(names, marks):
        print name, mark

@time_dec
def iz():
    for name, mark in izip(names, marks):
        print name, mark

z()
iz()
