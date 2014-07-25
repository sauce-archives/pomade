[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/saucelabs/pomade/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

How to install Pomade
---------------------

`pip install pomade`


How to use Pomade
-----------------

Pomade expects a config file called `pomade-config.json` in the same directory as the `nosetests` command is run from. `pomade-config.json` should look something like:

```json
{
  "host": "saucelabs.com",
  "port": 4444,
  "base-url": "<YOUR APP BASE URL>",
  "username": "<YOUR SAUCE USERNAME>",
  "access-key": "<YOUR SAUCE ACCESS KEY>",
  "default-se2-platform": ["LINUX", "chrome", ""]
}
```

To run tests, use `nosetests` as you normally would. For example, to run a test file called `test_tutorials.py` with five concurrency on Sauce with a 90 second timeout:

`nosetests -v --processes=5 --process-timeout=90 test_tutorials.py`





How to run a test on multiple browsers
--------------------------------------

```python
from pomade.helpers import Selenium2TestCase, on_platforms
from login import LoginPage

@on_platforms([["Windows 2012", "internet explorer", "10"], ["Linux", "Chrome", ""]])
class TestLogins(Selenium2TestCase):
    _multi_process_can_split_ = True

    def setUp(self):
        Selenium2TestCase.setUp(self)
        self.get('/login')
        self.login_page = LoginPage(self.driver)

    def test_failed_login(self):
        self.login_page.login_as_expecting_failure("wronguser", "wrongpassword")

    def test_successful_login(self):
        self.login_page.login_as("rightuser", "rightpassword")
```
