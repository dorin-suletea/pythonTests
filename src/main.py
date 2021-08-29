import string
from typing import Final

class A:
    def run(self):
        return 1


class B:
    def run(self):
        return 2


class C(A, B):
    def run(self):
        return 3


class D(A, B):
    def run2(self):
        return None


class F(B, A):
    def run2(self):
        return None


class E(D):
    def run2(self):
        return None


class StaticImport:

    @staticmethod
    def static_class_method():
        return "static_class"

    # todo : @SuppressWarnings??
    def non_static_class_method(self):
        return "non_static"


####
def global_method_redirect():
    return StaticImport.static_class_method()


def global_method():
    return "global"


class AccessA:
    __private = "private"
    _almost_private = "almost_private"


class AccessB(AccessA):
    # this is public static
    space = " "

    def run(self):
        return AccessB.space.join(self.__private, self._almost_private)


class Immutability:
    static_final: Final = "static_final"

    def __init__(self):
        self.const: Final = "non_static_final"

    def run(self):
        static_final = "s"
        return static_final

    def run2(self):
        self.const = 3
        return self.const


call_count = 0
call_count_lazy = 0

def eager_decorate(func):
    func()


@eager_decorate
def eagerly_decorated():
    global call_count
    call_count += 1


def lazy_decorate(func):
    def hook():
        return func
    return hook


@lazy_decorate
def lazily_decorated():
    global call_count_lazy
    call_count_lazy += 1


def highjack_decorator(func):
    def hook_with_parameters(first, second):
        return func("x", "y")
    return hook_with_parameters

@highjack_decorator
def aFunc(first, second):
    return "a" + first + second


class BrokenHash:

    def __init__(self):
        self.__bad_hash = 0;

    def __eq__(self, other):
        return True

    def __hash__(self):
        self.__bad_hash += 1
        # cant return stateful increment, very nice
        # return self.__bad_hash += 1
        return self.__bad_hash


class BrokenEqualsHashCollision:

    def __init__(self):
        self.__bad_hash = 0

    def __eq__(self, other):
        return False

    def __hash__(self):
        return self.__bad_hash
