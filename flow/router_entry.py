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


from cli.config import config_handler, ConfigKeys
from flow.router_rest_api import RouterRestAPI

class RouterEntry:
    ''' RouterOS Entry
    '''
    def __init__(self, router_name: str):
        self.router_name = router_name
        self.config_entry  = config_handler.config_entry(router_name)
        self.rest_api = RouterRestAPI(router_name, self.config_entry)
        self.router_id = {
            ConfigKeys.ROUTERBOARD_NAME: self.router_name,
            ConfigKeys.ROUTERBOARD_ADDRESS: self.config_entry.hostname
        }