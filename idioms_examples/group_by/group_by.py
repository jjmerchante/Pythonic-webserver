from itertools import groupby

# Show the words with the same initial letter together
words = ["dog", "cat", "house", "car", "function", "class", "foo"]

# words MUST be sorted
words_sorted = sorted(words)

for key, group in groupby(words_sorted, lambda x: x[0]):
    print list(group) # group is iterator

# ['car', 'cat', 'class']
# ['dog']
# ['foo', 'function']
# ['house']
