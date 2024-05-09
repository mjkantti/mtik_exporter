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

import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class RouterboardMetricsDataSource:
    ''' Routerboard Metrics data provider
    '''
    @staticmethod
    def metric_records(router_entry: 'RouterEntry') -> list[dict[str, str | float]]:
        try:
            return list(router_entry.api_connection.router_api().get_resource('/system/routerboard').get() or [])
        except Exception as Argument:
            logging.exception('Error getting routerboard info from router %s@%s', router_entry.router_name, router_entry.config_entry.hostname)
            return []

    @staticmethod
    def firmware_version(router_entry: 'RouterEntry'):
        try:
            version_st = router_entry.api_connection.router_api().get_resource('/system/routerboard').call('print', {'proplist':'current-firmware'})[0]
            if version_st.get('current-firmware'):
                return version_st['current-firmware']
            return None
        except Exception as exc:
            print(f'Error getting routerboard current-firmware from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return []

    @staticmethod
    def firmware_upgrade_version(router_entry):
        try:
            version_st = router_entry.api_connection.router_api().get_resource('/system/routerboard').call('print', {'proplist':'upgrade-firmware'})[0]
            if version_st.get('upgrade-firmware'):
                return version_st['upgrade-firmware']
            return None
        except Exception as exc:
            print(f'Error getting routerboard upgrade-firmware from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return []

