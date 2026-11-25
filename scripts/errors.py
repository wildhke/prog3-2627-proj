# Refinement of the errors-error.

try:
    print("\t")
except:
    print("something went wrong.")

try:
    print("\t")
except:
    raise ValueError("Damn, something went wrong.")

try:
    print("\t")
except Exception as e:
    print("Damn, something went wrong.", e)

""" Documentation: https://docs.python.org/3/builtins/exceptions.html

>> In Python, all exceptions must be instances of a class that derives from BaseException.
>> In a try statement with an except clause that mentions a particular class, that clause
>> also handles any exception classes derived from that class (but not exception classes
>> from which it is derived).


Hierachy: https://docs.python.org/3/builtins/exceptions.html#exception-hierarchy
Example, what is raised where: https://numpy.org/doc/stable/reference/generated/numpy.matmul.html
"""

class MyError(BaseException):
    print("WTF. What is going on?!")

try:
    bird.swim()
except Exception as e:
    raise MyError from e


import numpy as np
a = np.array([1,2,3])
b = np.array([[1,2,3], [4,5,6]])

class MyValueError(BaseException):
    def __init__(self):
        print("Can't apply matrix multiplication.")

try:
    ... #np.matmul(a,b)
except ValueError as e:
    raise MyValueError from e


class MyValueErrorWithDetails(ValueError):
    """The shapes do not fit for a matrix multiplication."""

    def __init__(self, shape_a, shape_b):
        self.shape_a = shape_a
        self.shape_b = shape_b
        super().__init__(f"Can't apply matrix multiplication: {shape_a} @ {shape_b}")


try:
    ... #np.matmul(a,b)
except ValueError as e:
        raise MyValueErrorWithDetails(a.shape, b.shape) from e


from numpy.linalg import LinAlgError # To use the specific error, we need to import it -- like a normal module.
try:
    np.linalg.pinv(4)
except LinAlgError as e:
        raise MyValueError from e