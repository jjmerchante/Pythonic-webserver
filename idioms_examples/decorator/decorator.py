import time

def time_dec(func):
    def wrap(*arg, **kwargs):
        init_time = time.time()
        res = func(*arg, **kwargs)
        print(func.__name__, time.time()-init_time)
        return res
    return wrap

@time_dec
def foo(n):
    out = 0
    for i in range(n):
        out = out + i
    return out

@time_dec
def bar(n):
    return sum(range(n))

foo(10000000)
bar(10000000)


"""
OUTPUT:
foo 0.555375337600708
bar 0.183899402618408
"""
