def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print "Division by zero not allowed!"
    else:
        print "The result is", result
    finally:
        print "Goodbye :)"

divide(6, 2)
# The result is 3
# Goodbye :)

divide(6, 0)
# Division by zero not allowed!
# Goodbye :)
