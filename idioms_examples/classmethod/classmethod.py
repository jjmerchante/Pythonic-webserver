class A(object):
    def foo(self):
        return "I am a method of A's instance :)"

    @classmethod
    def class_foo(cls):
        return "I am a class_method, I know about the class :)", cls

print(A.class_foo()) # ('I am a class_method, I know about the class :)', <class '__main__.A'>)
