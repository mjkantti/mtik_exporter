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

import yaml
import logging

from collections import namedtuple


''' mtik_exporter conf file handling
'''
class ConfigKeys:
    ''' mtik_exporter config file keys
    '''
    # Section Keys
    ENABLED_KEY = 'enabled'
    HOST_KEY = 'hostname'
    USER_KEY = 'username'
    PASSWD_KEY = 'password'
    PORT_KEY = 'port'

    SSL_KEY = 'use_ssl'
    NO_SSL_CERTIFICATE = 'no_ssl_certificate'
    SSL_CERTIFICATE_VERIFY = 'ssl_certificate_verify'
    SOCKET_TIMEOUT = 'socket_timeout'

    POLLING_INTERVAL_KEY = 'polling_interval'
    SLOW_POLLING_INTERVAL_KEY = 'slow_polling_interval'

    FAST_POLLING_KEYS = 'collectors'
    SLOW_POLLING_KEYS = 'slow_collectors'

    CHECK_FOR_UPDATES_KEY = 'check_for_updates'
    CHECK_FOR_UPDATES_CHANNEL_KEY = 'check_for_updates_channel'
    SYSTEM_INTERVAL_KEY = 'system_interval'

    EXPORTER_INC_DIV = 'delay_inc_div'
    EXPORTER_ADDR = 'export_address'
    EXPORTER_PORT = 'export_port'

    # Base router id labels
    ROUTERBOARD_NAME = 'routerboard_name'
    ROUTERBOARD_ADDRESS = 'routerboard_address'

    # Default values
    DEFAULT_API_PORT = ''
    DEFAULT_POLLING_INTERVAL = 10
    DEFAULT_SLOW_POLLING_INTERVAL = 60
    DEFAULT_EXPORT_PORT = 49090
    DEFAULT_SOCKET_TIMEOUT = 2
    DEFAULT_INITIAL_DELAY = 120
    DEFAULT_MAX_DELAY = 900
    DEFAULT_INC_DIV = 5
    DEFAULT_CHECK_FOR_UPDATES_CHANNEL = ['stable']
    DEFAULT_SYSTEM_INTERVAL = 3600
    DEFAULT_EXPORT_ADDRESS = '::'

    ROUTER_STR_KEYS = {HOST_KEY, USER_KEY, PASSWD_KEY}
    ROUTER_BOOLEAN_KEYS = {ENABLED_KEY, SSL_KEY, NO_SSL_CERTIFICATE, SSL_CERTIFICATE_VERIFY}
    ROUTER_INT_KEYS = {POLLING_INTERVAL_KEY, SLOW_POLLING_INTERVAL_KEY, PORT_KEY, SOCKET_TIMEOUT}
    ROUTER_LIST_KEYS = {FAST_POLLING_KEYS, SLOW_POLLING_KEYS}

    SYSTEM_STR_KEYS = {EXPORTER_ADDR}
    SYSTEM_BOOLEAN_KEYS = {CHECK_FOR_UPDATES_KEY}
    SYSTEM_INT_KEYS = {EXPORTER_PORT, EXPORTER_INC_DIV, SYSTEM_INTERVAL_KEY}
    SYSTEM_LIST_KEYS = {CHECK_FOR_UPDATES_CHANNEL_KEY}

    # mtik_exporter config entry name
    SYSTEM_CONFIG_ENTRY_NAME = 'system'


class ConfigEntry:
    RouterConfigEntry = namedtuple('RouterConfigEntry', list(ConfigKeys.ROUTER_BOOLEAN_KEYS | ConfigKeys.ROUTER_STR_KEYS | ConfigKeys.ROUTER_INT_KEYS | ConfigKeys.ROUTER_LIST_KEYS))
    SystemConfigEntry = namedtuple('SystemConfigEntry', list(ConfigKeys.SYSTEM_BOOLEAN_KEYS | ConfigKeys.SYSTEM_STR_KEYS | ConfigKeys.SYSTEM_INT_KEYS | ConfigKeys.SYSTEM_LIST_KEYS))

class SystemConfigHandler:
    # two-phase init, to enable custom config
    def __call__(self, data_path):
        self.data_path = data_path
        self._read_from_disk()

    # mtik_exporter entries
    def registered_entries(self):
        ''' All mtik_exporter registered entries
        '''
        # This is sections
        return (entry_name for entry_name in self.routers_config)

    def config_entry(self, entry_name):
        ''' Given an entry name, reads and returns the entry info
        '''
        entry_reader = self._config_entry_reader(entry_name)
        return ConfigEntry.RouterConfigEntry(**entry_reader) if entry_reader else None

    def system_entry(self):
        ''' mtik_exporter internal config entry
        '''
        _entry_reader = self._system_entry_reader()
        return ConfigEntry.SystemConfigEntry(**_entry_reader)

    # Helpers
    def _read_from_disk(self):
        ''' (Force-)Read conf data from disk
        '''
        self.system_config = {}
        self.routers_config = {}
        config = {}
        try:
            with open(self.data_path) as cfgstr:
                config = yaml.safe_load(cfgstr)
        except:
            logging.exception(f'Could not reaad {self.data_path}')

        try:
            self.system_config = config.pop(ConfigKeys.SYSTEM_CONFIG_ENTRY_NAME)
        except:
            logging.exception(f'Could not find "system" entry in config file {self.data_path}')

        self.routers_config = config


    def _config_entry_reader(self, entry_name):
        logging.info('%s: Reading Config for router', entry_name)
        config_entry_reader = {}

        for key in ConfigKeys.ROUTER_BOOLEAN_KEYS:
            config_entry_reader[key] = self.routers_config[entry_name].get(key, False)

        for key in ConfigKeys.ROUTER_STR_KEYS | ConfigKeys.ROUTER_INT_KEYS:
            config_entry_reader[key] = self.routers_config[entry_name].get(key, self._default_value_for_key(key))

        for key in ConfigKeys.ROUTER_LIST_KEYS:
            config_entry_reader[key] = self.routers_config[entry_name].get(key, [])

        return config_entry_reader

    def _system_entry_reader(self):
        logging.info('Reading System Config')
        system_entry_reader = {}

        for key in ConfigKeys.SYSTEM_BOOLEAN_KEYS:
            system_entry_reader[key] = self.system_config.get(key, False)

        for key in ConfigKeys.SYSTEM_STR_KEYS | ConfigKeys.SYSTEM_INT_KEYS | ConfigKeys.SYSTEM_LIST_KEYS:
            system_entry_reader[key] = self.system_config.get(key, self._default_value_for_key(key))

        return system_entry_reader

    def _default_value_for_key(self, key):
        logging.info('Getting Default value for %s', key)
        return {
            ConfigKeys.SSL_KEY: False,
            ConfigKeys.PORT_KEY: '',
            ConfigKeys.POLLING_INTERVAL_KEY: ConfigKeys.DEFAULT_POLLING_INTERVAL,
            ConfigKeys.SLOW_POLLING_INTERVAL_KEY: ConfigKeys.DEFAULT_SLOW_POLLING_INTERVAL,
            ConfigKeys.SOCKET_TIMEOUT: ConfigKeys.DEFAULT_SOCKET_TIMEOUT,
            ConfigKeys.EXPORTER_INC_DIV: ConfigKeys.DEFAULT_INC_DIV,
            ConfigKeys.CHECK_FOR_UPDATES_CHANNEL_KEY: ConfigKeys.DEFAULT_CHECK_FOR_UPDATES_CHANNEL,
            ConfigKeys.SYSTEM_INTERVAL_KEY: ConfigKeys.DEFAULT_SYSTEM_INTERVAL,
            ConfigKeys.EXPORTER_ADDR: ConfigKeys.DEFAULT_EXPORT_ADDRESS,
            ConfigKeys.EXPORTER_PORT: ConfigKeys.DEFAULT_EXPORT_PORT,
        }.get(key)


# Simplest possible Singleton impl
config_handler = SystemConfigHandler()
