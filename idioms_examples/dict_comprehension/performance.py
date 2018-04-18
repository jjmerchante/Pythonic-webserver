def time_dec(func):
    import time
    def wrap(*arg, **kwargs):
        init_time = time.time()
        res = func(*arg, **kwargs)
        print func.__name__, time.time()-init_time
        return res
    return wrap

@time_dec
def f1():
    d = {}
    for k in range(10000):
        d[k] = k**2

@time_dec
def f2():
    dict_compr = {k: k**2 for k in range(10000)}

f1()
f2()
