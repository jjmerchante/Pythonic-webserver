import time

def time_dec(func):
    def wrap(*arg, **kwargs):
        init_time = time.time()
        res = func(*arg, **kwargs)
        print func.__name__, time.time()-init_time
        return res
    return wrap


@time_dec
def list_a():
    result_list = []
    for el in xrange(10000000):
        result_list.append(el)
    return result_list

@time_dec
def list_b():
    return [el for el in xrange(10000000)]







list_a()
list_b()
