my_str = "{} is {} years old".format("Peter", 50)
# Peter is 50 years old

my_str = "{0} is {1} years old. {1} years old!".format("Peter", 50)
# Peter is 50 years old. 50 years old!

data = {'name': 'Peter', 'age': 50}
my_str = "{name} is {age} years old.".format(**data)
# Peter is 50 years old.

my_str = "{p[name]} is {p[age]} years old.".format(p=data)
# Peter is 50 years old.
