from collections import defaultdict
import time



def time_dec(func):
    def wrap(*arg, **kwargs):
        init_time = time.time()
        res = func(*arg, **kwargs)
        print func.__name__, time.time()-init_time
        return res
    return wrap

@time_dec
def f1():
    s = "HonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibus"
    d = defaultdict(int)
    for char in s:
        d[char] += 1

@time_dec
def f2():
    s = "HonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibuHonorificabilitudinitatibus"
    d = defaultdict(int)
    for char in s:
        if char not in d:
            d[char] = 0
        d[char] += 1


f1()
f2()
