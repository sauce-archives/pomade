# encoding: utf-8
import json

import selenium
from selenium.webdriver.remote.webdriver import WebDriver
# PatientElement contains the WebElement monkeypatch methods
from helpers import PatientElement


DRIVER_TYPES = [
    'selenium_rc',
    'webdriver',
]


class UnsupportedDriverMethod(Exception):
    pass


class UnsupportedDriver(Exception):
    pass


class NotYetImplementedDriverMethod(Exception):
    pass


def is_rc_type(driver_type):
    return driver_type in ['selenium_rc']


def is_wd_type(driver_type):
    return driver_type in ['webdriver']

def is_fake_selenium_type(driver_type):
    return not is_rc_type(driver_type) and not is_rc_type(driver_type)

DRIVER_STRATEGIES = {'id': 'id',
                     'name': 'name',
                     'class': 'class_name',
                     'css': 'css_selector',
                     'link': 'partial_link_text',
                     'link_text': 'link_text',
                     'xpath': 'xpath',
                     'tag': 'tag_name'}


WD_STRATEGIES = dict((v, k) for k, v in DRIVER_STRATEGIES.iteritems())


class DriverInterface(object):

    driver_type = None

    def __init__(self, driver, driver_type):
        self.driver = driver
        self.driver_type = driver_type
        if self.driver_type not in DRIVER_TYPES:
            raise UnsupportedDriver(self.driver_type)

    @property
    def is_wd_type(self):
        return is_wd_type(self.driver_type)

    @property
    def is_rc_type(self):
        return is_rc_type(self.driver_type)

    def __getattr__(self, name):
        if hasattr(self, 'driver') and hasattr(self.driver, name):
            return getattr(self.driver, name)
        elif name[0:3] == "by_":
            strat = name[3:]
            assert strat in DRIVER_STRATEGIES.keys(), ("Bad locator strategy: "
                                                       "%s" % strat)
            return self._get_finder(strat)
        elif name[0:16] == "find_element_by_":
            wd_strat = name[16:]
            assert wd_strat in WD_STRATEGIES.keys(), ("Bad locator strategy: "
                                                      "%s" % wd_strat)
            return self._get_finder(WD_STRATEGIES[wd_strat])
        raise UnsupportedDriverMethod(name)

    def _get_finder(self, strat):
        strat = DRIVER_STRATEGIES[strat]

        def by(*args, **kwargs):
            multiple = False
            if 'multiple' in kwargs:
                multiple = kwargs.pop('multiple')
            plural = "s" if multiple else ""
            func = getattr(self.driver,
                           "find_element%s_by_%s" % (plural, strat))
            return func(*args, **kwargs)

        return by

    @staticmethod
    def get_for_driver(driver):
        driver_type = None
        if isinstance(driver, DriverInterface):
            driver = driver.driver

        if isinstance(driver, selenium.selenium):
            driver_type = 'selenium_rc'
            driver_class = SeleniumRCTypeInterface
        elif isinstance(driver, WebDriver):
            driver_type = 'webdriver'
            driver_class = DriverInterface
        else:
            raise UnsupportedDriver("Driver %s is not currently supported" %
                                    type(driver))

        return driver_class(driver, driver_type)


class SeleniumRCTypeInterface(DriverInterface):

    def _get_finder(self, strat):
        if strat == "tag":
            strat = "css"

        def by(loc, *args, **kwargs):
            _strat = strat
            if _strat == "class":
                _strat = "css"
                loc = ".%s" % loc
            return WebElementSurrogate(self.driver, self.driver_type, _strat,
                                       loc)

        return by

    def get(self, url):
        return self.driver.open(url)

    @property
    def title(self):
        return self.driver.get_title()

    def execute_script(self, script, *args):
        if script.startswith("return "):
            mangled_script = "this.browserbot.getUserWindow()."
            mangled_script += script.split('return ')[1]

            result = self.driver.get_eval(mangled_script)
            try:
                return json.loads(result)
            except ValueError:
                return result

        raise NotYetImplementedDriverMethod()

    def execute_async_script(self, script, *args):
        raise NotYetImplementedDriverMethod()

    @property
    def current_url(self):
        raise NotYetImplementedDriverMethod()

    @property
    def page_source(self):
        raise NotYetImplementedDriverMethod()

    def close(self):
        raise NotYetImplementedDriverMethod()

    def quit(self):
        raise NotYetImplementedDriverMethod()


class WebElementSurrogate(PatientElement):

    strategy = None
    locator = None
    driver_type = None
    driver = None

    def __init__(self, driver, driver_type, strat, loc):
        self.strategy = strat
        self.locator = loc
        self.rc_locator = "%s=%s" % (strat, loc)
        self.driver_type = driver_type
        self.driver = driver

    def get_rc_locator(self, strat, loc):
        return "%s=%s" % (strat, loc)

    def click(self):
        try:
            if 'checkbox' == self.driver.get_attribute(self.rc_locator + '@type'):
                if self.driver.is_checked(self.rc_locator):
                    return self.driver.uncheck(self.rc_locator)
                else:
                    return self.driver.check(self.rc_locator)
        finally:
            return self.driver.click(self.rc_locator)

    @property
    def text(self):
        text = self.driver.get_text(self.rc_locator)
        return text

    def get_attribute(self, attr):
        return self.driver.get_attribute("%s@%s" % (self.rc_locator, attr))

    def submit(self):
        raise NotYetImplementedDriverMethod()

    def clear(self):
        raise NotYetImplementedDriverMethod()

    def is_selected(self):
        return self.driver.is_checked(self.rc_locator)

    def is_enabled(self):
        raise NotYetImplementedDriverMethod()

    def is_displayed(self):
        return self.driver.is_element_present(self.rc_locator)

    @property
    def size(self):
        raise NotYetImplementedDriverMethod()

    def value_of_css_property(self):
        raise NotYetImplementedDriverMethod()

    @property
    def location(self):
        raise NotYetImplementedDriverMethod()

    @property
    def parent(self):
        raise NotYetImplementedDriverMethod()

    def send_keys(self, text):
        return self.driver.type(self.rc_locator, text)

    def focus(self):
        return self.driver.focus(self.rc_locator)
