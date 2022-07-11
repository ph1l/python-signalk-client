# python-signalk-client

This is a python client library for the [Signal-K](http://signalk.org/)
Protocol.

a client application can be found at https://github.com/ph1l/pysk

## Requirements

On Debian Jessie:

    sudo apt-get install python3-setuptools python3-requests python3-websocket \
      python3-netifaces python3-six libnss-mdns

## Install

    python3 ./setup.py build
    python3 ./setup.py test
    sudo python3 ./setup.py install
