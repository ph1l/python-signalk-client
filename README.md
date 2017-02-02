# python-signalk-client

This is a python client library for the [Signal-K](http://signalk.org/)
Protocol.

a client application can be found at https://github.com/ph1l/pysk

## Requirements

On Debian Jessie:

    sudo apt-get install python-setuptools python-requests python-websocket \
      python-enum34 python-netifaces python-six libnss-mdns

## Install

    python ./setup.py build
    python ./setup.py test
    sudo python ./setup.py install
