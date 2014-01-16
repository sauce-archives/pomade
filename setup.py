from distutils.core import setup
setup(
    name = "pomade",
    packages = ["pomade"],
    version = "0.0.2",
    description = "Selenium PageObjects implementation with easy Sauce Labs integration",
    author = "Sauce Labs",
    author_email = "help@saucelabs.com",
    url = "https://github.com/saucelabs/pomade",
    install_requires=['decorator>=3.4.0', 'selenium>=2.38.3', 'nose>=1.3.0'],
)