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


from mtik_exporter.cli.config.config import config_handler
from mtik_exporter.flow.router_entry import RouterEntry


class RouterEntriesHandler:
    ''' Handles RouterOS entries defined in mtik_exporter config
    '''
    def __init__(self):
        self._router_entries = {}
        for router_name in config_handler.registered_entries():
            router_entry = RouterEntry(router_name)
            self._router_entries[router_name] = router_entry

    @property
    def router_entries(self):
        return (entry for _, entry in  self._router_entries.items() if entry.config_entry.enabled) if self._router_entries else None
