from pprint import pformat
import json
import time
import traceback
import sys
import config

SPIN_TIMEOUT = config.SPIN_TIMEOUT

class FailTestException(Exception):
    pass


def spinAssert(msg, test, timeout=None, args=[]):
    timeout = timeout or SPIN_TIMEOUT
    name = getattr(test, '__name__', 'unknown')
    last_e = None
    for i in xrange(timeout):
        try:
            if not test(*args):
                raise AssertionError(msg)
            if i > 0:
                print msg, "success on %s (%s)" % (i + 1, name)
            break
        except FailTestException:
            raise
        except Exception, e:
            if (str(e), type(e)) != (str(last_e), type(last_e)):
                print msg, "(try: %s):" % (i + 1),  str(e), type(e)
                traceback.print_exc(file=sys.stdout)
            last_e = e
        time.sleep(1)
    else:
        print "%s fail (%s tries) (%s)" % (msg, i + 1, name)
        raise AssertionError(msg)


class PomadeAssertions(object):

    def _format(self, var):
        formatted_var = pformat(var)
        return formatted_var

    def assert_equal(self, first, second, message=None):
        self.assertEqual(first, second, message)

    def assert_not_equal(self, first, second, message=None):
        self.assertNotEqual(first, second, message)

    def assert_is_valid_json(self, filename):
        try:
            with open(filename) as fo:
                json.load(fo)
        except ValueError, e:
            self.fail(filename + " is not valid json (%s)" % e.message)

    def assert_less(self, first, second, message=None):
        message = (message if message
            else "%s not less than %s" % (first, second))
        self.assertTrue(first < second, message)

    def assert_less_equal(self, first, second, message=None):
        message = (message if message
            else "%s not less than or equal to %s" % (first, second))
        self.assertTrue(first <= second, message)

    def assert_greater(self, first, second, message=None):
        message = (message if message
            else "%s not greater than %s" % (first, second))
        self.assertTrue(first > second, message)

    def assert_greater_equal(self, first, second, message=None):
        message = (message if message
            else "%s not greater than or equal to %s" % (first, second))
        self.assertTrue(first >= second, message)

    def assert_none(self, item, message=None):
        message = (message if message
            else "%s should have been None" % pformat(item))
        self.assertTrue(item is None, message)

    def assert_not_none(self, item, message=None):
        message = (message if message
            else "%s should not have been None" % pformat(item))
        self.assertFalse(item is None, message)

    def assert_excepts(self, exception_type, func, *args, **kwargs):
        excepted = False
        try:
            val = func(*args, **kwargs)
            print ("assert_excepts: Crap. That wasn't supposed to work."
                " Here's what I got: ", pformat(val))
        except exception_type, e:
            print ("assert_excepts: Okay, %s failed the way it was supposed"
                " to: %s" % (func, e))
            excepted = True
        self.assertTrue(excepted, "assert_excepts: calling %s didn't raise %s"
            % (func, exception_type))

    def assert_in(self, needle, haystack, message=None):
        return self.assert_contains(haystack, needle, message)

    def assert_not_in(self, needle, haystack, message=None):
        return self.assert_not_contains(haystack, needle, message)

    def assert_contains(self, haystack, needle, message=None):
        displaystack = self._format(haystack)
        message = (message if message
            else "%s not found in %s" % (needle, displaystack))

        its_in_there = False
        try:
            if needle in haystack:
                its_in_there = True
        except:
            pass

        try:
            if not its_in_there and haystack in needle:
                print "! HEY !" * 5
                print "HEY! it looks like you called assert_contains backwards"
                print "! HEY !" * 5
        except:
            pass

        self.assertTrue(needle in haystack, message)

    def assert_any(self, conditions, message=None):
        message = (message if message
            else "%s were all False" % pformat(conditions))
        self.assertTrue(any(conditions), message)

    def assert_not_any(self, conditions, message=None):
        message = (message if message
            else "%s was not all False" % pformat(conditions))
        self.assertFalse(any(conditions), message)

    def assert_not_contains(self, haystack, needle, message=None):
        displaystack = self._format(haystack)
        message = (message if message
            else "%s not wanted but found in %s" % (needle, displaystack))
        self.assertFalse(needle in haystack, message)

    def assert_startswith(self, haystack, needle, message=None):
        displaystack = self._format(haystack)
        message = (message if message
            else "%s should have been at the beginning of %s"
            % (needle, displaystack))
        self.assertTrue(haystack.startswith(needle), message)

    def assert_endswith(self, haystack, needle, message=None):
        displaystack = self._format(haystack)
        message = (message if message
            else "%s should have been at the end of %s"
            % (needle, displaystack))
        self.assertTrue(haystack.endswith(needle), message)

    def assert_not_startswith(self, haystack, needle, message=None):
        displaystack = self._format(haystack)
        message = (message if message
            else "%s should not have been at the beginning of %s"
            % (needle, displaystack))
        self.assertFalse(haystack.startswith(needle), message)

    def assert_is(self, expected, actual, message=None):
        message = message if message else "%s is not %s" % (expected, actual)
        self.assertTrue(expected is actual)

    def assert_is_not(self, expected, actual, message=None):
        message = message if message else "%s is %s" % (expected, actual)
        self.assertTrue(expected is not actual)

    def spinAssert(self, *args, **kwargs):
        return spinAssert(*args, **kwargs)


class BasicAssertions(object):
    # PomadeAssertions depends on these basic assertions, which come with
    # unittest.TestCase but we don't want to subclass that here. So let's
    # just duplicate the functionality, sigh
    def assertTrue(self, test, msg=None):
        msg = msg or "%s was not true" % test
        assert test is True

    def assertEqual(self, obj1, obj2, msg=None):
        msg = msg or "%s != %s" % (obj1, obj2)
        assert obj1 == obj2, msg

    def assertFalse(self, test, msg):
        msg = msg or "%s was not false" % test
        assert test is False, msg

    def assertNotEqual(self, obj1, obj2, msg):
        msg = msg or "%s == %s" % (obj1, obj2)
        assert obj1 != obj2, msg