class Rectangle():
    def __init__(self, height, width):
        self.height = height
        self.width = width

    def __eq__(self, rect):
        return (self.height * self.width) == (rect.height * rect.width)

    def __lt__(self, rect):
        return (self.height * self.width) < (rect.height * rect.width)

    def __gt__(self, rect):
        return (self.height * self.width) > (rect.height * rect.width)

r1 = Rectangle(3,6)
r2 = Rectangle(3,5)

print r1 > r2 # True
print r1 < r2 # False
print r1 == r2 # False
