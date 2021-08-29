import unittest
from collections import Counter

from src.main import *
from gwen import given, when, then

# most likely reinventing the wheel
class ImportActor:

    def __init__(self, test_case):
        self.__actual_test_case = test_case
        self.reset()

    def reset(self):
        self._response = None
        self._exception = None

    def calls_global_method(self):
        self._response = global_method()

    def calls_redirecting_global_method(self):
        self._response = global_method_redirect()

    def calls_non_static_class_method(self):
        self._response = StaticImport().non_static_class_method()

    def calls_static_class_method(self):
        self._response = StaticImport.static_class_method()

    # very odd design choice to have stateful unittest.TestCase.
    def received(self, expected):
        self.__actual_test_case.assertIs(self._response, expected)

    def asserts_with_no_self(self, expected):
        try:
            unittest.TestCase.assertIs(None, self._response, expected)
        except Exception as e:
            self._exception = e

    def has_exception(self):
        self.__actual_test_case.assertTrue(self._exception is not None)
        print(self._exception)

    def has_no_exception(self):
        self.__actual_test_case.assertTrue(self._exception is None)


# tests must start with test_
class ImportTest(unittest.TestCase):

    if __name__ == '__main__':
        unittest.main()

    def setUp(self):
        self.import_actor = ImportActor(self)
        self.testing_framework = self.import_actor

    def test_miss_used_lib_throws_exception_on_fail(self):
        given(self.import_actor).calls_global_method()
        when(self.testing_framework).asserts_with_no_self("global")
        then(self.import_actor).has_no_exception()

        when(self.testing_framework).asserts_with_no_self("global_NOK")
        then(self.import_actor).has_exception()

    def test_imports(self):
        when(self.import_actor).calls_global_method()
        then(self.import_actor).received("global")

        when(self.import_actor).calls_redirecting_global_method()
        then(self.import_actor).received("static_class")

        when(self.import_actor).calls_static_class_method()
        then(self.import_actor).received("static_class")

        when(self.import_actor).calls_non_static_class_method()
        then(self.import_actor).received("non_static")


###########################
class InheritanceActor(ImportActor):

    def __init__(self, test_case, delegate):
        super().__init__(test_case)
        self.__delegate = delegate

    def do_run(self, func):
        try:
            self._response = func()
        except Exception as e:
            self._exception = e

    def runs(self):
        return self.do_run( self.__delegate.run)

    def runs2(self):
        return self.do_run(self.__delegate.run2)

    @staticmethod
    def make_inheritance_actor(test_case, delegate):
        return InheritanceActor(test_case, delegate)


class InheritanceTest(unittest.TestCase):
    def test_simple_inheritance(self):
        self.assertIs(A().run(), 1)
        self.assertIs(B().run(), 2)
        self.assertIs(C().run(), 3)

    def testDiamondInheritance(self):
        self.assertIs(D().run(), A().run())
        self.assertIs(F().run(), B().run())

    def test_access(self):
        sut = InheritanceActor.make_inheritance_actor(self, AccessB())
        when(sut).runs()
        then(sut).has_exception()

    ''' Python language itself does not gain final syntax or support. 
    The above objects do not alter how Python works, they are constructs that merely document 
    that an object or reference is to be considered final. '''
    @unittest.skip("final is a lie")
    def test_can_not_change_final_static(self):
        sut = InheritanceActor.make_inheritance_actor(self, Immutability())
        when(sut.runs())
        then(sut).received("static_final")
        then(sut).has_exception()

    @unittest.skip("final is a lie")
    def test_can_not_change_final_member(self):
        sut = InheritanceActor.make_inheritance_actor(self, Immutability())
        when(sut.runs2())
        then(sut).received("non_static_final")
        then(sut).has_exception()


# same as static blocks, very optimization
class Decorator(unittest.TestCase):
    def test_eager_decorate_is_eager(self):
        self.assertIs(call_count, 1)

    def test_lazy_decorate_is_not_eager(self):
        self.assertIs(call_count_lazy, 0)

    def test_highjack(self):
        self.assertTrue(aFunc("c", "d"), "axy")

    # hmmmm
    @unittest.skip("AssertionError: 'axy' is not 'axy")
    def test_types(self):
        expected = "axy"
        result = aFunc("c", "d")

        self.assertTrue(type(expected).__name__ == 'str')
        self.assertTrue(type(result).__name__ == 'str')

        self.assertTrue(result, "axy")
        self.assertIs(result, expected)


class CollectionTests(unittest.TestCase):
    def test_counters(self):
        sut = Counter()
        sut.update((1, 1, 3))
        self.assertEqual(sut.get(1), 2)
        self.assertEqual(sut.get(3), 1)
        self.assertEqual(len(sut.keys()), 2)
        self.assertEqual(len(sut.items()), 2)

    def test_broken_hashes(self):
        sut = Counter()
        sut.update((BrokenHash(), BrokenHash(), BrokenHash()))
        # checks with equals
        self.assertEqual(len(sut.items()), 1)

    def test_broken_equals(self):
        sut = Counter()
        sut.update((BrokenEqualsHashCollision(), BrokenEqualsHashCollision(), BrokenEqualsHashCollision()))
        # same as java, compares hashes, on collision uses equals
        self.assertEqual(3, len(sut.items()))