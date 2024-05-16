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


from mtik_exporter.collector.metric_store import MetricStore, LoadingCollector
from mtik_exporter.flow.processor.output import BaseOutputProcessor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class IPv6NeighborCollector(LoadingCollector):
    '''IPv6 Neighbor Collector'''

    def __init__(self, router_id: dict[str, str], interval: int):
        self.name = 'IPv6NeighborCollector'
        self.metric_store = MetricStore(router_id, ['address', 'interface', 'mac_address', 'status', 'router', 'dhcp_name', 'dhcp_address', 'dhcp_comment'], interval=interval)

        # Metrics
        self.metric_store.create_info_metric('ipv6_neighbor', 'Reachable IPv6 neighbors')

    def load(self, router_entry: 'RouterEntry'):
        records = router_entry.api_connection.get('/ipv6/neighbor', status='reachable')
        # add dhcp info
        if records:
            for registration_record in records:
                BaseOutputProcessor.add_dhcp_info(router_entry, registration_record, str(registration_record.get('mac-address')))
        self.metric_store.set_metrics(records)

    #def collect(self):
    #    yield from self.metric_store.get_metrics()
