import unittest
from unittest.mock import Mock

from _context import recipie

from recipie.functools import *


class AttribSpec(unittest.TestCase):
    def testAttribAddFunctionToNameSpace(self):

        def outer():
            return "outer"

        @attrib(outer)
        def inner():
            return "inner"

        self.assertEqual(outer(), "outer")
        self.assertEqual(outer.inner(), "inner")

        with self.subTest("Inner is not accessible at the global space"):
            self.assertRaises(NameError, inner)


class DefaultOnErrorSpec(unittest.TestCase):

    @default_on_error(1, AssertionError)    
    def positive(self, i):
        if i==0:
            raise ValueError("Value is 0")
        assert (i > 0), "Argument must be positive"
        return i

    def test_default_value_returns_function_evaluation_on_no_error(self):
        self.assertEqual(self.positive(2), 2)
        self.assertEqual(self.positive(3), 3)

    def test_default_last_arg_returns_default_value_when_error_matches_specified_error(self):
        self.assertEqual(self.positive(-1), 1)

    def test_default_last_arg_raises_error_that_does_not_match_specified_error(self):
        with self.assertRaises(ValueError):
            self.positive(0)

class RetrySpec(unittest.TestCase):
    def testTriesLessThan2RaisesAssertionError(self):
        with self.assertRaises(AssertionError):
            @retry(1, Exception)
            def _func():
                pass

        with self.assertRaises(AssertionError):
            @retry(0, Exception)
            def _func():
                pass

    def testTriesAtLeast2DoesNotRaisesError(self):
        @retry(2, Exception)
        def _func_a():
            pass

        @retry(3, Exception)
        def _func_b():
            pass

    def testRetryCallsFunctionWithNoErrorOnce(self):
        func = Mock(return_value=True)
        log = Mock()
        target = retry(3, Exception, log_error=log)(func)

        self.assertEqual(target(), True)
        func.assert_called_once()
        log.assert_not_called()

    def testRetryStopsOnSuccessCallBeforReachingSpecifiedTries(self):
        log = Mock()
        call_count = 0
        tries = 3
        @retry(tries, ValueError)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Failed at first two calls")
            return True

        self.assertTrue(test_func())
        self.assertEqual(call_count, 3)


    def testRetryCallPropagatesExceptionOnReachingSpecifiedTries(self):
        func = Mock(side_effect = ValueError)
        log = Mock()
        tries = 3

        target = retry(tries, ValueError, log_error=log)(func)
        
        self.assertRaises(ValueError, target)
        self.assertEqual(func.call_count, tries)
        self.assertEqual(log.call_count, tries-1)

    def testRetryStopsOnUnlistedError(self):
        func = Mock(side_effect=ValueError)
        log = Mock()
        tries = 3

        target = retry(tries, AssertionError, log_error=log)(func)

        self.assertRaises(ValueError, target)
        func.assert_called_once()
        log.assert_not_called()

    def testRetryStopsOnUnmatchedFilteredError(self):
        func = Mock(side_effect=ValueError)
        log = Mock()
        tries = 3
        reject_all = lambda x: False

        target = retry(tries, ValueError, delay_gen=retry.no_delay, log_error=log, error_filter=reject_all)(func)

        self.assertRaises(ValueError, target)
        func.assert_called_once()
        log.assert_not_called()
