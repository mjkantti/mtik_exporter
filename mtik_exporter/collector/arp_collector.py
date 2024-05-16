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

class ARPCollector(LoadingCollector):
    '''ARP Entry collector'''
    def __init__(self, router_id: dict[str, str], interval):
        self.name = 'ARPCollector'
        self.metric_store = MetricStore(
            router_id,
            ['mac_address', 'address', 'interface', 'status', 'dynamic', 'dhcp_name', 'dhcp_comment'],
            interval=interval
            )

        # Metrics
        self.metric_store.create_info_metric('arp_entry', 'ARP Entry Info')

    def load(self, router_entry: 'RouterEntry'):
        arp_records = router_entry.rest_api.get('ip/arp')
        for r in arp_records:
            BaseOutputProcessor.add_dhcp_info(router_entry, r, str(r.get('mac-address')))
        self.metric_store.set_metrics(arp_records)