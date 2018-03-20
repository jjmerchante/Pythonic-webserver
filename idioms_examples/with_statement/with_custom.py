class File(object):
    def __init__(self, name, mode='r'):
        self.file = open(name, mode)
    def __enter__(self):
        return self.file
    def __exit__(self, type, value, traceback):
        self.file.close()

with File("my_file.txt", 'w') as f:
    f.write("hi")
