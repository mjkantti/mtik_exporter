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

import sys
import json
from collections import namedtuple
from configparser import ConfigParser
from abc import ABCMeta, abstractmethod
from mtik_exporter.utils.utils import FSHelper


''' mtik_exporter conf file handling
'''
class ConfigKeys:
    ''' mtik_exporter config file keys
    '''
    # Section Keys
    ENABLED_KEY = 'enabled'
    HOST_KEY = 'hostname'
    PORT_KEY = 'port'
    USER_KEY = 'username'
    PASSWD_KEY = 'password'

    SSL_KEY = 'use_ssl'
    NO_SSL_CERTIFICATE = 'no_ssl_certificate'
    SSL_CERTIFICATE_VERIFY = 'ssl_certificate_verify'

    POLLING_INTERVAL_KEY = 'polling_interval'
    SLOW_POLLING_INTERVAL_KEY = 'slow_polling_interval'

    FAST_POLLING_KEYS = 'collectors'
    SLOW_POLLING_KEYS = 'slow_collectors'

    CHECK_FOR_UPDATES_KEY = 'check_for_updates'
    CHECK_FOR_UPDATES_CHANNEL_KEY = 'check_for_updates_channel'
    CHECK_FOR_UPDATES_INTERVAL_KEY = 'check_for_updates_interval'

    EXPORTER_SOCKET_TIMEOUT = 'socket_timeout'
    EXPORTER_INITIAL_DELAY = 'initial_delay_on_failure'
    EXPORTER_MAX_DELAY = 'max_delay_on_failure'
    EXPORTER_INC_DIV = 'delay_inc_div'
    EXPORTER_VERBOSE_MODE = 'verbose_mode'
    EXPORTER_MAX_SCRAPE_DURATION = 'max_scrape_duration'
    EXPORTER_TOTAL_MAX_SCRAPE_DURATION = 'total_max_scrape_duration'

    # UnRegistered entries placeholder
    NO_ENTRIES_REGISTERED = 'NoEntriesRegistered'

    # Base router id labels
    ROUTERBOARD_NAME = 'routerboard_name'
    ROUTERBOARD_ADDRESS = 'routerboard_address'

    # Default values
    DEFAULT_API_PORT = 80
    DEFAULT_API_SSL_PORT = 443
    DEFAULT_POLLING_INTERVAL = 10
    DEFAULT_SLOW_POLLING_INTERVAL = 60
    DEFAULT_EXPORT_PORT = 49090
    DEFAULT_SOCKET_TIMEOUT = 2
    DEFAULT_INITIAL_DELAY = 120
    DEFAULT_MAX_DELAY = 900
    DEFAULT_INC_DIV = 5
    DEFAULT_MAX_SCRAPE_DURATION = 10
    DEFAULT_TOTAL_MAX_SCRAPE_DURATION = 30
    DEFAULT_CHECK_FOR_UPDATES_CHANNEL = ['stable']
    DEFAULT_CHECK_FOR_UPDATES_INTERVAL = 3600


    ROUTER_BOOLEAN_KEYS = {ENABLED_KEY, SSL_KEY, NO_SSL_CERTIFICATE, SSL_CERTIFICATE_VERIFY}
    ROUTER_INT_KEYS = {POLLING_INTERVAL_KEY, SLOW_POLLING_INTERVAL_KEY, PORT_KEY}
    ROUTER_STR_KEYS = {HOST_KEY, USER_KEY, PASSWD_KEY}
    ROUTER_LIST_KEYS = {FAST_POLLING_KEYS, SLOW_POLLING_KEYS}

    SYSTEM_BOOLEAN_KEYS = {EXPORTER_VERBOSE_MODE, CHECK_FOR_UPDATES_KEY}
    SYSTEM_LIST_KEYS = {CHECK_FOR_UPDATES_CHANNEL_KEY}
    SYSTEM_INT_KEYS = {PORT_KEY, EXPORTER_SOCKET_TIMEOUT, EXPORTER_INITIAL_DELAY, EXPORTER_MAX_DELAY, EXPORTER_INC_DIV, EXPORTER_MAX_SCRAPE_DURATION, EXPORTER_TOTAL_MAX_SCRAPE_DURATION, CHECK_FOR_UPDATES_INTERVAL_KEY}

    # mtik_exporter config entry name
    SYSTEM_CONFIG_ENTRY_NAME = 'SYSTEM'


class ConfigEntry:
    RouterConfigEntry = namedtuple('RouterConfigEntry', list(ConfigKeys.ROUTER_BOOLEAN_KEYS | ConfigKeys.ROUTER_STR_KEYS | ConfigKeys.ROUTER_INT_KEYS | ConfigKeys.ROUTER_LIST_KEYS))
    SystemConfigEntry = namedtuple('SystemConfigEntry', list(ConfigKeys.SYSTEM_BOOLEAN_KEYS | ConfigKeys.SYSTEM_INT_KEYS | ConfigKeys.SYSTEM_LIST_KEYS))

class OSConfig(metaclass=ABCMeta):
    ''' OS-related config
    '''
    @staticmethod
    def os_config():
        ''' Factory method
        '''
        if sys.platform == 'linux':
            return LinuxConfig()
        elif sys.platform == 'darwin':
            return OSXConfig()
        elif sys.platform.startswith('freebsd'):
            return FreeBSDConfig()
        else:
            print(f'Non-supported platform: {sys.platform}')
            return None

    @property
    @abstractmethod
    def mtik_exporter_user_dir_path(self):
        pass


class FreeBSDConfig(OSConfig):
    ''' FreeBSD-related config
    '''
    @property
    def mtik_exporter_user_dir_path(self):
        return FSHelper.full_path('config/config.ini')


class OSXConfig(OSConfig):
    ''' OSX-related config
    '''
    @property
    def mtik_exporter_user_dir_path(self):
        return FSHelper.full_path('config/config.ini')


class LinuxConfig(OSConfig):
    ''' Linux-related config
    '''
    @property
    def mtik_exporter_user_dir_path(self):
        return FSHelper.full_path('config/config.ini')


class CustomConfig(OSConfig):
    ''' Custom config
    '''
    def __init__(self, path):
        self._user_dir_path = path

    @property
    def mtik_exporter_user_dir_path(self):
        return FSHelper.full_path(self._user_dir_path)


class SystemConfigHandler:
    # two-phase init
    def __init__(self):
        pass

    # two-phase init, to enable custom config
    def __call__(self, os_config = None):
        self.os_config = os_config if os_config else OSConfig.os_config()
        if not self.os_config:
            sys.exit(1)

        # if needed, stage the user config data
        self.usr_conf_data_path = self.os_config.mtik_exporter_user_dir_path

        self.re_compiled = {}

        self._read_from_disk()

    # mtik_exporter entries
    def registered_entries(self):
        ''' All mtik_exporter registered entries
        '''
        # This is sections
        return (entry_name for entry_name in self.config.sections() if entry_name != ConfigKeys.SYSTEM_CONFIG_ENTRY_NAME)

    def registered_entry(self, entry_name):
        ''' A specific mtik_exporter registered entry by name
        '''
        if entry_name in self.config:
            return self.config[entry_name]
        return None

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
        self.config = ConfigParser()
        self.config.read(self.usr_conf_data_path)

    def _config_entry_reader(self, entry_name):
        config_entry_reader = {}

        for key in ConfigKeys.ROUTER_BOOLEAN_KEYS:
            if self.config[entry_name].get(key) is not None:
                config_entry_reader[key] = self.config.getboolean(entry_name, key)
            else:
                config_entry_reader[key] = False

        for key in ConfigKeys.ROUTER_STR_KEYS:
            if self.config[entry_name].get(key, raw=True):
                config_entry_reader[key] = self.config[entry_name].get(key, raw=True)
            else:
                config_entry_reader[key] = self._default_value_for_key(key)

        for key in ConfigKeys.ROUTER_LIST_KEYS:
            collectors = json.loads(self.config[entry_name].get(key))
            config_entry_reader[key] = collectors

        for key in ConfigKeys.ROUTER_INT_KEYS:
            if self.config[entry_name].get(key):
                config_entry_reader[key] = self.config.getint(entry_name, key)
            else:
                config_entry_reader[key] = self._default_value_for_key(key)

        # port
        if self.config[entry_name].get(ConfigKeys.PORT_KEY):
            config_entry_reader[ConfigKeys.PORT_KEY] = self.config.getint(entry_name, ConfigKeys.PORT_KEY)
        else:
            config_entry_reader[ConfigKeys.PORT_KEY] = self._default_value_for_key(
                ConfigKeys.SSL_KEY, config_entry_reader[ConfigKeys.SSL_KEY])

        return config_entry_reader

    def _system_entry_reader(self):
        system_entry_reader = {}
        entry_name = ConfigKeys.SYSTEM_CONFIG_ENTRY_NAME

        for key in ConfigKeys.SYSTEM_INT_KEYS:
            if self.config[entry_name].get(key):
                system_entry_reader[key] = self.config.getint(entry_name, key)
            else:
                system_entry_reader[key] = self._default_value_for_key(key)

        for key in ConfigKeys.SYSTEM_BOOLEAN_KEYS:
            if self.config[entry_name].get(key):
                system_entry_reader[key] = self.config.getboolean(entry_name, key)
            else:
                system_entry_reader[key] = self._default_value_for_key(key)

        for key in ConfigKeys.SYSTEM_LIST_KEYS:
            if self.config[entry_name].get(key) is not None:
                collectors = json.loads(self.config[entry_name].get(key))
                system_entry_reader[key] = collectors
            else:
                system_entry_reader[key] = self._default_value_for_key(key)

        return system_entry_reader

    def _default_value_for_key(self, key, value=None):
        return {
            ConfigKeys.SSL_KEY: lambda value: ConfigKeys.DEFAULT_API_SSL_PORT if value else ConfigKeys.DEFAULT_API_PORT,
            ConfigKeys.PORT_KEY: lambda _: ConfigKeys.DEFAULT_EXPORT_PORT,
            ConfigKeys.POLLING_INTERVAL_KEY: lambda _: ConfigKeys.DEFAULT_POLLING_INTERVAL,
            ConfigKeys.SLOW_POLLING_INTERVAL_KEY: lambda _: ConfigKeys.DEFAULT_SLOW_POLLING_INTERVAL,
            ConfigKeys.EXPORTER_SOCKET_TIMEOUT: lambda _: ConfigKeys.DEFAULT_SOCKET_TIMEOUT,
            ConfigKeys.EXPORTER_INITIAL_DELAY: lambda _: ConfigKeys.DEFAULT_INITIAL_DELAY,
            ConfigKeys.EXPORTER_MAX_DELAY: lambda _: ConfigKeys.DEFAULT_MAX_DELAY,
            ConfigKeys.EXPORTER_INC_DIV: lambda _: ConfigKeys.DEFAULT_INC_DIV,
            ConfigKeys.EXPORTER_MAX_SCRAPE_DURATION: lambda _: ConfigKeys.DEFAULT_MAX_SCRAPE_DURATION,
            ConfigKeys.EXPORTER_TOTAL_MAX_SCRAPE_DURATION: lambda _: ConfigKeys.DEFAULT_TOTAL_MAX_SCRAPE_DURATION,
            ConfigKeys.CHECK_FOR_UPDATES_CHANNEL_KEY: lambda _: ConfigKeys.DEFAULT_CHECK_FOR_UPDATES_CHANNEL,
            ConfigKeys.CHECK_FOR_UPDATES_INTERVAL_KEY: lambda _: ConfigKeys.DEFAULT_CHECK_FOR_UPDATES_INVERVAL,
        }[key](value)


# Simplest possible Singleton impl
config_handler = SystemConfigHandler()
