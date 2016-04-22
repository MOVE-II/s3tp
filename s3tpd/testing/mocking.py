# Copyright 2016-2016 the s3tp authors, LGPLv3+. See copying.md for legal info.
"""
Basic implementation of a mocking mixin that adds mocking functionality to
other classes.
"""

from abc import ABCMeta
from functools import wraps


class MockException(Exception):
    """
    An exception that can be raised while mocking objects.
    """
    pass


class Expectation:
    """
    Base class for an expected behavior of a mocked class. Simulates a method
    call of the mocked class.
    """

    def __init__(self, name):
        """
        Constructor.
        """
        self._name = name

    def execute(self, actual_name):
        """
        Simulates the expected method. If the actually called method has not
        the same name a MockException is raised.
        """
        if self._name != actual_name:
            raise MockException("Expected call to {} but actual call was {}"
                                .format(self._name, actual_name))


class ReturnExpectation(Expectation):
    """
    Implementation of an expected behavior for methods that return a value.
    """

    def __init__(self, name, return_value):
        """
        Constructor.
        """
        super().__init__(name)
        self._return_value = return_value

    def execute(self, actual_name):
        """
        Simulates the expected method and returns the expected value.
        """
        super().execute(actual_name)
        return self._return_value


class ExceptionExpectation(Expectation):
    """
    Implementation of an expected behavior for methods that raise an exception.
    """

    def __init__(self, name, exception):
        """
        Constructor.
        """
        super().__init__(name)
        self._exception = exception

    def execute(self, actual_name):
        """
        Simulates the expected method and raises the expected exception
        """
        super().execute(actual_name)
        raise self._exception



class Mock:
    """
    Encapsulates the state of a mocking object. Keeps track of expected method
    calls and whether the object has already been baked.
    """

    def __init__(self):
        """
        Creates a new Mock with no expectations.
        """
        self._baked = False
        self._expectations = list()

    def bake(self):
        """
        Bakes this mock and thus makes it ready for replaying the programmed
        actions.
        """
        self._baked = True

    def is_baked(self):
        """
        Returns whether this mock has been baked.
        """
        return self._baked

    def expect(self, name, *args):
        """
        Adds an expectation to this mock. A call to the method with the given
        name is expected. The given return value will be returned by the
        expected call. If the given return value is an exception type, it will
        be raised instead.
        """
        value = None
        if args:
            value = args[0]
            if isinstance(value, Exception):
                self._expectations.append(ExceptionExpectation(name, value))
                return
        self._expectations.append(ReturnExpectation(name, value))

    def do_mock(self, actual_name):
        """
        Does the actual mocking of a method call. If the given actual_name is
        not equal to the expected method name or if no other call is expected a
        MockException is raised. Simulates the expected method call.
        """
        if not self._expectations:
            raise MockException("No more method calls are expected")
        return self._expectations.pop(0).execute(actual_name)


def create_mock(function):
    """
    Creates a mocking proxy for the given function.
    """
    @wraps(function)
    def _inner(self, *args, **_):
        if self._mock.is_baked():
            return self._mock.do_mock(function.__name__)
        self._mock.expect(function.__name__, *args)
        return self
    return _inner


class MockingMetaClass(ABCMeta):
    """
    Meta class that replaces all methods of a class by mocking methods.
    """

    # functions that are excluded from being mocked
    NON_MOCKING_FUNCTIONS = ['__init__', 'bake']

    def __new__(mcs, name, bases, attrs):
        """
        Replaces all methods of the constructed class with mocking methods.
        """
        for attr_name, value in attrs.items():
            if attr_name not in MockingMetaClass.NON_MOCKING_FUNCTIONS\
                    and callable(value):
                attrs[attr_name] = create_mock(value)
        return super().__new__(mcs, name, bases, attrs)


class MockingMixin(metaclass=MockingMetaClass):
    """
    A mixin that adds mocking functionality to other classes.
    """

    def __init__(self):
        """
        Initializes the internal mock.
        """
        self._mock = Mock()

    def bake(self):
        """
        Bakes this mocking object.
        """
        self._mock.bake()
