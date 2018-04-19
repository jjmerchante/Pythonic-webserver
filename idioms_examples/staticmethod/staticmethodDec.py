class A(object):
    def foo(self):
        return "I am a method of A's instance :)"

    @staticmethod
    def static_foo():
        return "I am a static_method, I don't know about the class :)"


print(A.static_foo()) # I am a static_method, I don't know about the class :)
