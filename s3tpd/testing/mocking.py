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
        expected call.
        """
        return_value = None
        if args:
            return_value = args[0]
        self._expectations.append((name, return_value))

    def do_mock(self, actual_name):
        """
        Does the actual mocking of a method call. If the given actual_name is
        not equal to the expected method name or if no other call is expected a
        MockException is raised. Returns the expected return value.
        """
        if not self._expectations:
            raise MockException("No more method calls are expected")
        expected_name, return_value = self._expectations.pop(0)
        if expected_name != actual_name:
            raise MockException("Expected call to {} but actual call was {}"
                                .format(expected_name, actual_name))
        return return_value


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
