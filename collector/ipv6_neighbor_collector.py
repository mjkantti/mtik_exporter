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


from collector.metric_store import MetricStore, LoadingCollector
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.router_entry import RouterEntry

class IPv6NeighborCollector(LoadingCollector):
    '''IPv6 Neighbor Collector'''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'IPv6NeighborCollector'
        self.metric_store = MetricStore(
            router_id,
            ['address', 'interface', 'mac_address', 'mac_vendor', 'status', 'router'],
            resolve_mac_vendor = True)

        # Metrics
        self.metric_store.create_info_metric('ipv6_neighbor', 'Reachable IPv6 neighbors')

    def load_data(self, router_entry: 'RouterEntry'):
        records = router_entry.rest_api.get('ipv6/neighbor', {'status': 'reachable'})
        # add dhcp info
        self.metric_store.set_metrics(records)
