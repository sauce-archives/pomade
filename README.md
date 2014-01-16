[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/saucelabs/pomade/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

Pomade
------

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
