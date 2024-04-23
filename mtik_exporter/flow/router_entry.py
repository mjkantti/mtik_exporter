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


from mtik_exporter.cli.config.config import config_handler, mtik_exporterConfigKeys
from mtik_exporter.flow.router_connection import RouterAPIConnection
from mtik_exporter.flow.router_rest_api import RouterRestAPI

class RouterEntry:
    ''' RouterOS Entry
    '''
    def __init__(self, router_name: str):
        self.router_name = router_name
        self.config_entry  = config_handler.config_entry(router_name)
        #self.api_connection = RouterAPIConnection(router_name, self.config_entry)
        self.rest_api = RouterRestAPI(router_name, self.config_entry)
        self.router_id = {
            mtik_exporterConfigKeys.ROUTERBOARD_NAME: self.router_name,
            mtik_exporterConfigKeys.ROUTERBOARD_ADDRESS: self.config_entry.hostname
            }

        #self.collector_time_spent: dict[str, float] =  {}
        self.data_loader_time_spent: dict[str, float] =  {}
        self.data_load_count: float = 1
        self._dhcp_entries: list[dict[str, str | float]] = []

    def set_dhcp_entries(self, entries: list[dict[str, str | float]]):
        self._dhcp_entries = entries

    def dhcp_record(self, key: str, value: str):
        return next((e for e in self._dhcp_entries if e.get(key) == value), None)

    def is_ready(self):
        is_ready = True
        if not self.api_connection.check_connection():
            is_ready = False
            # let's get connected now
            self.api_connection.connect()
        return is_ready
