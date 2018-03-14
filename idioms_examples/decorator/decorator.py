import time

def time_dec(func):
    def wrap(*arg, **kwargs):
        init_time = time.time()
        res = func(*arg, **kwargs)
        print func.__name__, time.time()-init_time
        return res
    return wrap

@time_dec
def foo(n):
    out = 0
    for i in xrange(n):
        out = out + i
    return out

@time_dec
def bar(n):
    return sum(xrange(n))

bar(100000000)
foo(100000000)

"""
OUTPUT:
bar 0.63298201561
foo 2.44244480133
"""
