# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
#   python-signalk-client is a python client library for SignalK
#   Copyright (C) 2016  Philip J Freeman <elektron@halo.nu>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""signalk client connection"""

import json
import logging
import requests
import threading
import websocket
from signalk_client.data import Data

class Client(object):
    """Client connection object

    Keyword arguments:
    server -- server host (default None)

    By default, this function uses `zeroconf_server` to automatically locate
    a _signalk-http._tcp.local. service on the local network.

    Optionally, you can pass the hostname of the signalk server via the
    keyword `server`. To specify a port use `hostname:port` format.
    """

    def __init__(self, server=None):
        self.server = server
        self.api_endpoint = None
        self.stream_endpoint = None

        self.__config()

        self.data = Data(requests.get(self.api_endpoint).json())
        self.w_sock = websocket.WebSocketApp(
            "%s?subscribe=all"%(self.stream_endpoint),
            on_message=self.__ws_on_message,
            on_error=self.__ws_on_error,
            on_close=self.__ws_on_close,
            on_open=self.__ws_on_open
            )

        self.websocket_t = threading.Thread(target=self.w_sock.run_forever)
        self.websocket_t.daemon = True
        self.websocket_t.start()

    def __zeroconf_server(self):
        """discover local signalk server
        """

        import time
        from signalk_client.zeroconf import ServiceBrowser, Zeroconf

        class MyListener(object):
            """zeroconf listener object"""
            def __init__(self):
                self.services = {}

            def remove_service(self, zeroconf, service_type, name):
                """service removal function"""
                self.services.pop(name)
                logging.info("zeroconf: service removed: {}".format(name))

            def add_service(self, zeroconf, service_type, name):
                """service add function"""
                info = zeroconf.get_service_info(service_type, name)
                self.services[name] = info
                logging.info("zeroconf: service found: {} @ {}:{}".format(
                    name,
                    info.server,
                    info.port
                    ))

            def get_services(self):
                """service getter"""
                return self.services

        service_type = "_signalk-http._tcp.local."
        zeroconf = Zeroconf()
        listener = MyListener()
        browser = ServiceBrowser(zeroconf, service_type, listener)
        while True:
            time.sleep(2)
            if len(listener.get_services().keys()) > 0:
                break
            logging.warning("No Services of type:{} found.. waiting..".format(
                service_type
                ))
        zeroconf.close()
        services = listener.get_services()
        service_info = services[services.keys()[0]]
        return "%s:%s"%(service_info.server, service_info.port)

    def __config(self):
        """discover endpoints from server
        """

        import requests

        # Set from arg or discover via zeroconf, server address and port
        if self.server == None:
            self.server = self.__zeroconf_server()
        logging.info("Attempting Connection to {}...".format(self.server))

        # Discover API and Stream endpoints
        data = requests.get("http://%s/signalk"%(self.server)).json()
        endpoints = data['endpoints']['v1']
        logging.info("Connected to SignalK Server({})".format(
            endpoints['version']
            ))

        self.api_endpoint = endpoints['signalk-http']
        self.stream_endpoint = endpoints['signalk-ws']

        logging.info("Got endpoints: api_endpoint={} stream_endpoint={}".format(
            self.api_endpoint,
            self.stream_endpoint,
            ))

    def __ws_on_message(self, w_sock, message):
        """websocket message handler"""
        self.data.process_delta(json.loads(message))

    def __ws_on_error(self, w_sock, error):
        """websocket error handler"""
        logging.error("websocket error: {}".format(error))

    def __ws_on_close(self, w_sock):
        """websocket connection close handler"""
        # TODO: handle connection close by reconnecting?
        logging.warning("websocket closed")

    def __ws_on_open(self, w_sock):
        """websocket connection open handler"""
        pass

    def close(self):
        """close the signalk client connection
        """
        logging.warning("Closing websocket...")
        self.w_sock.close()
