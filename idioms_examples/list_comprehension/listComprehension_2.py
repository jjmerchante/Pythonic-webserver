
def list_a():
    result_list = []
    for el in xrange(10000000):
        result_list.append(el)

def list_b():
    result_list = [el for el in xrange(10000000)]
