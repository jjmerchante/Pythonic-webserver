def fib():
    """ Fibonacci generator """
    a, b = 0, 1
    while 1:
       yield b
       a, b = b, a + b

f = fib()
print(f)  # <generator object fib at 0x7f72dce25870>

print(f.next()) # 1
print(f.next()) # 1
print(f.next()) # 2
for i in f:
    print(i)

# 3
# 5
# 8
# "Never" ends
