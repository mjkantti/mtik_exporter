# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
## Copyright (c) 2024 Martti Anttila
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.


import ssl
import socket
import collections
import logging
from datetime import datetime
from mtik_exporter.cli.config.config import config_handler

# Fix UTF-8 decode error
# See: https://github.com/akpw/mtik_exporter/issues/47
# The RouterOS-api implicitly assumes that the API response is UTF-8 encoded.
# But Mikrotik uses latin-1.
# Because the upstream dependency is currently abandoned, this is a quick hack to solve the issue

MIKROTIK_ENCODING = 'latin-1'
import routeros_api.api_structure
routeros_api.api_structure.StringField.get_python_value = lambda _, bytes:  bytes.decode(MIKROTIK_ENCODING)
routeros_api.api_structure.default_structure = collections.defaultdict(routeros_api.api_structure.StringField)

from routeros_api import RouterOsApiPool


class RouterAPIConnectionError(Exception):
    pass


class RouterAPIConnection:
    ''' Base wrapper interface for the routeros_api library
    '''
    def __init__(self, router_name: str, config_entry):
        self.router_name: str = router_name
        self.config_entry = config_entry
        self.last_failure_timestamp: float = 0
        self.successive_failure_count: int = 0

        ctx = None
        if self.config_entry.use_ssl and self.config_entry.no_ssl_certificate:
            ctx = ssl.create_default_context()
            ctx.set_ciphers('ADH:@SECLEVEL=0')

        self.connection = RouterOsApiPool(
                host = self.config_entry.hostname,
                username = self.config_entry.username,
                password = self.config_entry.password,
                port = self.config_entry.port,
                plaintext_login = True,
                use_ssl = self.config_entry.use_ssl,
                ssl_verify = self.config_entry.ssl_certificate_verify,
                ssl_context = ctx)

        self.connection.socket_timeout = config_handler.system_entry().socket_timeout
        self.api = None

    def check_connection(self):
        if not self.is_connected():
            return False
        try:
            self.api.get_resource('/system/identity').get()
            return True
        except (socket.error, socket.timeout, Exception) as exc:
            self._set_connect_state(success = False, exc = exc)
            return False

    def get(self, path, **kwargs):
            return self.call(path, 'print', {}, kwargs)
    
    def call(self, path, cmd = 'print', arguments=None, queries=None, additional_queries=()):
        if not self.is_connected():
            return
        try:
            return list(self.api.get_resource(path).call(cmd, arguments=arguments, queries=queries, additional_queries=additional_queries) or [])
        except (socket.error, socket.timeout, Exception) as exc:
            logging.critical('Error getting resource %s', path)
            self._set_connect_state(success = False, exc = exc)
            return []

    def is_connected(self):
        if not (self.connection and self.connection.connected and self.api):
            return False
        return True

    def connect(self):
        connect_time = datetime.now()
        if self.check_connection() or self._in_connect_timeout(connect_time.timestamp()):
            return
        try:
            logging.info('Connecting to router %s@%s', self.router_name, self.config_entry.hostname)
            self.api = self.connection.get_api()
            self._set_connect_state(success = True, connect_time = connect_time)
        except (socket.error, socket.timeout, Exception) as exc:
            self._set_connect_state(success = False, connect_time = connect_time, exc = exc)
            #raise RouterAPIConnectionError

    def router_api(self):
        if not self.is_connected():
            self.connect()
        return self.api

    def _in_connect_timeout(self, connect_timestamp: float):
        connect_delay = self._connect_delay()
        if (connect_timestamp - self.last_failure_timestamp) < connect_delay:
            logging.debug('%s@%s: in connect timeout, %i secs remaining', self.router_name, self.config_entry.hostname, int(connect_delay - (connect_timestamp - self.last_failure_timestamp)))
            logging.debug('Successive failure count: %i', self.successive_failure_count)
            return True
        logging.debug('%s@%s: OK to connect', self.router_name, self.config_entry.hostname)
        if self.last_failure_timestamp > 0:
            logging.debug('Seconds since last failure: %i', connect_timestamp - self.last_failure_timestamp)
            logging.debug('Prior successive failure count: %i', self.successive_failure_count)
        return False

    def _connect_delay(self):
        mtik_exporter_entry = config_handler.system_entry()
        connect_delay = (1 + self.successive_failure_count / mtik_exporter_entry.delay_inc_div) * mtik_exporter_entry.initial_delay_on_failure
        return connect_delay if connect_delay < mtik_exporter_entry.max_delay_on_failure else mtik_exporter_entry.max_delay_on_failure


    def _set_connect_state(self, success: bool = False, connect_time: datetime = datetime.now(), exc: Exception | None = None):
        if success:
            self.last_failure_timestamp = 0
            self.successive_failure_count = 0
            logging.info('Connection to router %s@%s has been established', self.router_name, self.config_entry.hostname)
        else:
            self.api = None
            self.successive_failure_count += 1
            self.last_failure_timestamp = connect_time.timestamp()
            logging.critical('Connection to router %s@%s failed', self.router_name, self.config_entry.hostname)
            logging.critical(exc, exc_info=True)









