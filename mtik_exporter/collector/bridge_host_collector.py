# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
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

from mtik_exporter.flow.processor.output import BaseOutputProcessor
from mtik_exporter.collector.metric_store import MetricStore, LoadingCollector

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class BridgeHostCollector(LoadingCollector):
    '''Bridge host (MAC Table) collector'''
    def __init__(self, router_id: dict[str, str], polling_interval: int):
        self.name = 'BridgeHostsCollector'
        self.metric_store = MetricStore(
            router_id,
            ['mac_address', 'vid', 'bridge', 'interface', 'on_interface', 'dhcp_name', 'dhcp_comment', 'dhcp_address'],
            ['prefix_count', 'local_messages', 'local_bytes', 'remote_messages', 'remote_bytes', 'established', 'uptime'],
            polling_interval=polling_interval,
            )

        # Metrics
        self.metric_store.create_info_collector('bridge_host', 'Wireguard Interfaces')

    def load(self, router_entry: 'RouterEntry'):
        if self.metric_store.run_fetch():
            self.metric_store.clear_metrics()
            #bridge_host_records = BridgeHostMetricsDataSource.metric_records(router_entry)
            bridge_host_records = router_entry.rest_api.get('interface/bridge/host', {'local': 'false', 'external': 'true'})
            if bridge_host_records:
                for r in bridge_host_records:
                    BaseOutputProcessor.add_dhcp_info(router_entry, r, str(r.get('mac-address')))
            self.metric_store.set_metrics(bridge_host_records)

    def collect(self):
        return self.metric_store.get_metrics()