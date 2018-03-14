class A(object):
    def foo(self,x):
        print "I am a method of A's instance :)"

    @classmethod
    def class_foo(cls,x):
        print "I am a class_method, I know about the class :)"

    @staticmethod
    def static_foo(x):
        print "I am a static_method, I don't know about the class :)"
