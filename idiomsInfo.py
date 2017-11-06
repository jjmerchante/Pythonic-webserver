"""
This file contains all the information about the idioms
this is the only way to change some information about the idioms
in the repository
If you add some new idiom add too to the results.html in results section
"""


_beginner_idioms = [{'name': 'listComprehension', 'beautyName': 'List comprehension', 'info': 'http://www.secnetix.de/olli/Python/list_comprehensions.hawk'},
                    {'name': 'idiomMethods1', 'beautyName': 'Beginner magic methods', 'info': 'http://minhhh.github.io/posts/a-guide-to-pythons-magic-methods'},
                    {'name': 'finally', 'beautyName': 'finally keyword', 'info': 'https://docs.python.org/2/tutorial/errors.html#defining-clean-up-actions'},
                    {'name': 'with', 'beautyName': 'with keyword', 'info': 'http://effbot.org/zone/python-with-statement.htm'}]

_intermediate_idioms = [{'name': 'yield', 'beautyName': 'yield keyword', 'info': 'https://jeffknupp.com/blog/2013/04/07/improve-your-python-yield-and-generators-explained/'},
                        {'name': 'lambda', 'beautyName': 'lambda functions', 'info': 'http://www.secnetix.de/olli/Python/lambda_functions.hawk'},
                        {'name': 'generators', 'beautyName': 'generator expressions', 'info': 'https://jeffknupp.com/blog/2013/04/07/improve-your-python-yield-and-generators-explained/'},
                        {'name': 'idiomMethods2', 'beautyName': 'intermediate magic methods', 'info': 'http://minhhh.github.io/posts/a-guide-to-pythons-magic-methods'},
                        {'name': 'defaultdict', 'beautyName': 'defaultdict collection', 'info': 'https://www.accelebrate.com/blog/using-defaultdict-python/'},
                        {'name': 'namedTuple', 'beautyName': 'namedtuple collection', 'info': 'https://pymotw.com/2/collections/namedtuple.html'}]

_advanced_idioms = [{'name': 'idiomMethods3', 'beautyName': 'advanced magic methods', 'info': 'http://minhhh.github.io/posts/a-guide-to-pythons-magic-methods'},
                    {'name': 'orderecdict', 'beautyName': 'orderedDict collection', 'info': 'https://pymotw.com/2/collections/ordereddict.html'},
                    {'name': 'deque', 'beautyName': 'deque collection', 'info': 'https://pymotw.com/2/collections/deque.html'},
                    {'name': 'NestedFunction', 'beautyName': 'Closures', 'info': 'https://realpython.com/blog/python/inner-functions-what-are-they-good-for/'},
                    {'name': 'decorator', 'beautyName': 'decorator', 'info': 'https://www.python.org/dev/peps/pep-0318/'}]

_new_idioms = [{'name': 'classmethodDec', 'beautyName': '@classmethod', 'info': ''},
               {'name': 'staticmethodDec', 'beautyName': '@staticmethod', 'info': ''},
               {'name': 'zip', 'beautyName': 'zip', 'info': ''},
               {'name': 'itertools_izip', 'beautyName': 'itertools.izip', 'info': ''},
               {'name': 'itertools_iziplong', 'beautyName': 'itertools.izip_longest', 'info': ''},
               {'name': 'itertools_imap', 'beautyName': 'itertools.imap', 'info': ''},
               {'name': 'itertools_starmap', 'beautyName': 'itertools.starmap', 'info': ''},
               {'name': 'itertools_tee', 'beautyName': 'itertools.tee', 'info': ''},
               {'name': 'itertools_groupby', 'beautyName': 'itertools.groupby', 'info': ''},
               {'name': 'total_orderingDec', 'beautyName': 'functools.total_ordering decorator', 'info': ''},
               {'name': 'functools_partial', 'beautyName': 'functools.partial', 'info': ''}]

# Create a class for make the idioms more generic
class Idiom():
    def __init__(self, name):
        self.name = name
        self.times = 0
    def __str__(self):
        return self.name



def new_beginner_list():
    ret_list= []
    for item in _beginner_idioms:
        ret_list.append({'name': item["name"],
                         'times': 0,
                         'beautyName': item["beautyName"],
                         'info': item['info']})
    return ret_list

def new_itermediate_list():
    ret_list= []
    for item in _intermediate_idioms:
        ret_list.append({'name': item["name"],
                         'times': 0,
                         'beautyName': item["beautyName"],
                         'info': item['info']})
    return ret_list

def new_advanced_list():
    ret_list= []
    for item in _advanced_idioms:
        ret_list.append({'name': item["name"],
                         'times': 0,
                         'beautyName': item["beautyName"],
                         'info': item['info']})
    return ret_list
