from collections import deque

d = deque([1,2,3,4])
d.append(d.pop())
print(d) # deque([1, 2, 3, 4])
d.appendleft(d.popleft())
print(d) # deque([1, 2, 3, 4])
