from helpers import Selenium2TestHelpers
from assertions import PomadeAssertions, BasicAssertions
from driver_interface import DriverInterface
from decorator import decorator

class UnsupportedDriverBehavior(Exception):
    pass


@decorator
def js_support_required(f, self, *a, **kw):
    if not self.driver.is_fake_selenium_type:
        return f(self, *a, **kw)
    raise UnsupportedDriverBehavior("This driver can't do javascripty things!")


@decorator
def xpath_support_required(f, self, *a, **kw):
    if not self.driver.is_fake_selenium_type:
        return f(self, *a, **kw)
    raise UnsupportedDriverBehavior("This driver can't do xpath!")


class DeferredElement(object):

    def __init__(self, locator_func):
        self.locator_func = locator_func

    def __getattr__(self, attr):
        return getattr(self.locator_func(), attr)

    def __iter__(self):
        return iter(self.locator_func())

    def __getitem__(self, key):
        return self.locator_func()[key]


class Pomade(Selenium2TestHelpers, PomadeAssertions, BasicAssertions):
    def __init__(self, driver):
        self.driver = DriverInterface.get_for_driver(driver)

    def __getattr__(self, name):
        if hasattr(self, 'driver'):
            return getattr(self.driver, name)
        raise AttributeError(name)

    def open(self, wait=True, login=None):
        if login is not None:
            self.login(login)
        self.get(self.url)
        if wait:
            self.wait_for_open()

    def wait_for_open(self):
        if hasattr(self, 'title'):
            self.wait_for_title_present()

    def deferred_element(self, loc, path):
        return DeferredElement(lambda: getattr(self, "by_%s" % loc)(path))

    def deferred_elements(self, loc, path):
        by_attr = getattr(self, "by_%s" % loc)
        return DeferredElement(lambda: by_attr(path, multiple=True))
