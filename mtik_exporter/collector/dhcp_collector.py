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

class DHCPCollector(LoadingCollector):
    ''' DHCP Metrics collector
    '''

    def __init__(self, router_id: dict[str, str], interval: int):
        self.name = 'DHCPCollector'
        self.metric_store = MetricStore(
            router_id,
            ['active_address', 'address', 'mac_address', 'host_name', 'comment', 'server', 'dynamic', 'client_id', 'status', 'address_lists'],
            ['expires_after', 'last_seen'],
            {
                'expires_after': lambda ea: BaseOutputProcessor.parse_timedelta(ea) if ea else None,
                'last_seen': lambda ls: BaseOutputProcessor.parse_timedelta(ls) if ls else None,
            },
            interval=interval
        )

        # Metrics
        self.metric_store.create_info_metric('dhcp_lease', 'DHCP Active Leases')
        self.metric_store.create_gauge_metric('dhcp_lease_expiry', 'DHCP Active Lease Expiry', 'expires_after', ['mac_address', 'comment', 'client_id'])
        self.metric_store.create_gauge_metric('dhcp_lease_last_seen', 'DHCP Active Lease Last Seen', 'last_seen', ['mac_address', 'comment', 'client_id'])

    def load(self, router_entry: 'RouterEntry'):
        dhcp_lease_records = router_entry.api_connection.get('ip/dhcp-server/lease')
        self.metric_store.set_metrics(dhcp_lease_records)
        router_entry.set_dhcp_entries(dhcp_lease_records)

    #def collect(self):
    #    yield from self.lease_metric_store.get_metrics()