from selenium import webdriver
from monkeypatch import monkeypatch
from assertions import spinAssert
from unittest import TestCase
from assertions import PomadeAssertions
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from utils import clean_url
from selenium_extensions import FlexSelenium as selenium
from os.path import isfile
from config import SPIN_TIMEOUT
import os
import config
import time
import httplib
import sys
import json
import base64

def load_config():
    config_file = config.CONFIG_FILE_PATH
    if not isfile(config_file):
        raise Exception("Configuration file does not exist")
    return json.load(open(config_file, "rb"))


# This is a mixin class designed to be used by Selenium2TestCase and
# Pomade. Hence use of self.driver rather than just self. Also,
# self.spinAssert works because these classes both mix in PomadeAssertions.
class Selenium2TestHelpers(object):

    def wait_for_text(self, text, element="body", msg=None, timeout=None):
        msg = msg or "%s didn't appear in element %s" % (text, element)
        self.driver.implicitly_wait(0)
        self.spinAssert(
            msg, lambda: text in self.driver.find_element_by_tag_name(element).text,
            timeout=timeout)
        self.driver.implicitly_wait(SPIN_TIMEOUT)

    def wait_for_text_absent(self, text, element="body", msg=None,
                             timeout=None):
        msg = msg or "%s appeared in element %s" % (text, element)
        by_tag = self.driver.find_element_by_tag_name
        self.driver.implicitly_wait(0)
        self.spinAssert(msg, lambda: text not in by_tag(element).text,
                        timeout=timeout)
        self.driver.implicitly_wait(SPIN_TIMEOUT)

    def wait_for_css_element_present(self, locator, msg=None, timeout=None):
        msg = msg or " waiting for element %s to appear" % locator
        self.driver.implicitly_wait(0)
        self.spinAssert(
            msg, lambda: self.driver.find_element_by_css_selector(locator),
            timeout=timeout)
        self.driver.implicitly_wait(SPIN_TIMEOUT)

    def wait_for_css_element_absent(self, locator, msg=None, timeout=None):
        msg = msg or " waiting for element %s to be removed from DOM" % locator

        def is_element_absent(locator):
            try:
                self.driver.find_element_by_css_selector(locator)
            except NoSuchElementException:
                return True
            return False
        self.driver.implicitly_wait(0)
        self.spinAssert(msg, lambda: is_element_absent(locator), timeout=timeout)
        self.driver.implicitly_wait(SPIN_TIMEOUT)

    def wait_for_css_element_visible(self, locator, msg=None, timeout=None):
        return self.wait_for_css_element_visibility(locator, True, msg, timeout)

    def wait_for_css_element_visibility(self, locator, visiblity, msg=None, timeout=None):
        msg = msg or " waiting for element %s to be %s" % (locator,
                                                           "visible" if visiblity
                                                           else "invisible")

        def is_visible():
            elem = self.driver.find_element_by_css_selector(locator)
            if elem:
                return elem.is_displayed() == visiblity
            return False
        self.driver.implicitly_wait(0)
        self.spinAssert(msg, is_visible, timeout=timeout)
        self.driver.implicitly_wait(SPIN_TIMEOUT)


    def wait_for_title_present(self, msg=" waiting for title", timeout=None):
        self.spinAssert(msg, lambda: len(self.driver.title) > 0, timeout=timeout)

    def wait_for_title(self, title, msg=None, timeout=None):
        msg = msg or "Title never contained %s" % title
        self.spinAssert(msg, lambda: title in self.driver.title, timeout=timeout)

    def wait_for_location(self, url, msg=None, timeout=None):
        msg = msg or "Location (URL) never contained %s" % url
        self.spinAssert(msg, lambda: url in self.driver.current_url, timeout=timeout)

    def wait_for_value_of_css_property(self, element, prop, value, timeout=None):
        self.spinAssert("Property never equal to %s" % value,
                        lambda: element.value_of_css_property(prop) == value,
                        timeout=timeout)

    def wait_for_javascript(self, js_call, msg=None, timeout=None):
        msg = msg or "JS did not return true %s" % js_call

        def execute_script():
            return self.execute_script(js_call)
        self.spinAssert(msg, execute_script, timeout=timeout)

    def get(self, url, https=False):
        url = clean_url(url, self.base_url, https=https)
        self.driver.get(url)


@monkeypatch(webdriver.remote.webelement.WebElement)
class PatientElement():
    def wait_for_attribute(self, attribute, expected, msg=None, timeout=None):
        if expected is True:
            expected = "true"
        if expected is False or expected is None:
            expected = "false"
        expected = unicode(expected)
        msg = (msg or "element's %s attribute never became %s"
               % (attribute, expected))
        return spinAssert(msg,
                          lambda: expected in self.get_attribute(attribute),
                          timeout=timeout)

    def _dodgy_test_for_element_being_removed_from_the_dom(self):
        try:
            self.is_displayed()
            return False
        except StaleElementReferenceException:
            return True

    def wait_for_removed(self, msg=None, timeout=None):
        msg = (msg or "element was never removed")
        return spinAssert(msg, lambda: self._dodgy_test_for_element_being_removed_from_the_dom(),
                          timeout=timeout)

    def wait_for_displayed(self, expected=True, msg=None, timeout=None):
        msg = (msg or "element never became " +
               ("displayed" if expected else "not displayed"))
        return spinAssert(msg, lambda: expected == self.is_displayed(),
                          timeout=timeout)

    def wait_for_enabled(self, expected=True, msg=None, timeout=None):
        msg = (msg or "element never became "
               + ("enabled" if expected else "not enabled"))
        return spinAssert(msg, lambda: expected == self.is_enabled(),
                          timeout=timeout)

    def wait_for_selected(self, expected=True, msg=None, timeout=None):
        msg = (msg or "element never became " +
               ("selected" if expected else "not selected"))
        return spinAssert(msg, lambda: expected == self.is_selected(),
                          timeout=timeout)

    def wait_for_css_property(self, property, expected, msg=None, timeout=None):
        expected = unicode(expected)
        msg = (msg or "element's %s css property never became %s"
               % (property, expected))
        return spinAssert(msg,
                          lambda: expected == self.value_of_css_property(property),
                          timeout=timeout)

    def wait_for_location(self, expected, msg=None, timeout=None):
        msg = (msg or "element's location in the renderable canvas never became %s"
               % (expected))
        return spinAssert(msg, lambda: expected in self.location,
                          timeout=timeout)

    def wait_for_parent(self, expected, msg=None, timeout=None):
        msg = msg or "element's parent never became %s" % (expected)
        return spinAssert(msg, lambda: expected == self.parent,
                          timeout=timeout)

    def wait_for_size(self, expected, msg=None, timeout=None):
        msg = msg or "element's size never became %s" % (expected)
        return spinAssert(msg, lambda: expected == self.size, timeout=timeout)

    def wait_for_tag_name(self, expected, msg=None, timeout=None):
        expected = unicode(expected)
        msg = msg or "element's tagName property never became %s" % (expected)
        return spinAssert(msg, lambda: expected == self.tag_name,
                          timeout=timeout)

    def wait_for_text(self, expected, msg=None, timeout=None):
        expected = unicode(expected)
        msg = msg or "element's text never became %s" % (expected)
        return spinAssert(msg, lambda: expected in self.text, timeout=timeout)

    def wait_for_value(self, expected, msg=None, timeout=None):
        return self.wait_for_attribute('value', expected, msg, timeout)

    def focus(self): 
        return self.send_keys(Keys.TAB)


class BaseSeleniumTestCase(TestCase):
    _multiprocess_can_split_ = True
    selenium_test = True
    tags = []
    extensions = None
    base_url = ''
    job_id = ''
    stop_on_teardown = True
    web_traceback_locator = "#traceback_data #short_text_version textarea"
    break_on_fail = True if os.environ.get('BREAK_ON_FAIL', False) else False

    @property
    def passed(self):
        return sys.exc_info() == (None, None, None)

    def report_pass_fail(self, passed=None):
        base64string = base64.encodestring('%s:%s' % (self.username,
                                                      self.access_key))[:-1]
        result = json.dumps({'passed': self.passed if passed is None else passed})
        connection = httplib.HTTPConnection(self.host)
        connection.request('PUT',
                           '/rest/v1/%s/jobs/%s' % (self.username, self.job_id),
                           result, headers={"Authorization": "Basic %s" % base64string})
        result = connection.getresponse()
        return result.status == 200


class Selenium2TestCase(BaseSeleniumTestCase, Selenium2TestHelpers):
    os = None
    browser = None
    version = None
    extra_capabilities = {}

    def __init__(self, *args, **kwargs):
        
        return BaseSeleniumTestCase.__init__(self, *args, **kwargs)

    def __getattr__(self, name):
        if (hasattr(self, 'driver') and
            hasattr(self.driver, name)):
            return getattr(self.driver, name)
        if name == 'name':
            if hasattr(self, '_testMethodName'):
                return self._testMethodName
            if hasattr(type(self), '__name__'):
                return str(type(self).__name__)
        raise AttributeError(
            "I don't have the '{0}' attribute. This can happen if you don't "
            "run setUp (which creates the browser object you may need)."
            "".format(name))

    def setUp(self, extra=None, profile=None):
        extra = {} if extra is None else extra
        self.config = load_config() or self.fail("WTF SRSLY")

        if self.os is None:
            self.os = self.config['default-se2-platform'][0]
            self.browser = self.config['default-se2-platform'][1]
            self.version = self.config['default-se2-platform'][2]
             
        self.base_url = self.config['base-url']
        self.host = self.config['host']
        self.port = self.config['port']
        self.username = self.config['username']
        self.access_key = self.config['access-key']
        self.driver = self._start_selenium()
        self.driver.implicitly_wait(SPIN_TIMEOUT)

    def _make_sauce_config(self):
        dc = {'platform': self.os,
              'browserName': self.browser,
              'version': self.version,
              'name': getattr(self, '_testMethodName',
                              self.name).replace('_', ' ').capitalize(),
              'max-duration': 600,
              'record-video': True,
              'selenium-version': self.config.get('selenium-version', None),
              'video-upload-on-pass': False,
              'tags': self.tags + ["Selenium 2"],
              }
        if self.browser.lower() in ["ipad", "iphone"]:
            dc.pop('selenium-version', None)
        return dc

    def _start_selenium(self, host=None, port=None, extra=None, profile=None):
        extra = {} if extra is None else extra
        dc = self._make_sauce_config()
        dc.update(extra)

        # Make sure we use the right class for Appium tests
        if 'app' in dc and not isinstance(self, AppiumTestCase):
            self.fail("Don't use Selenium2TestCase for Appium tests,"
                      " use AppiumTestCase: %s" % dc)

        # command_executor has to be a binary string because the
        # authors of webdriver don't speak python very well
        self.driver = webdriver.Remote(
            desired_capabilities=dc,
            browser_profile=profile,
            command_executor=("http://%s:%s@%s:%s/wd/hub"
                              % (self.username,
                                 self.access_key,
                                 host or self.host,
                                 port or self.port)).encode('utf-8'))

        self.job_id = self.driver.session_id

        return self.driver

    def tearDown(self):
        self.report_pass_fail()
        if self.stop_on_teardown:
            self.driver.quit() 