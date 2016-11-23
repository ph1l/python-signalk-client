# vim:et:ts=4:sts=4:ai

from setuptools import setup, find_packages
setup(
    name = "signalk_client",
    version = "0.1.0",
    test_suite="tests",
    packages = find_packages(),
    install_requires = [
        "requests",
        "websocket_client",
        # for zeroconf
        'enum-compat',
        'netifaces',
        'six',
        ],
    package_data={'signalk_client': ['include/*']},
    author = "Philip J Freeman",
    author_email = "elektron@halo.nu",
    description = "",
    license = "GPL3",
    keywords = "",
    url = "https://github.com/ph1l/python-signalk-client",
)
