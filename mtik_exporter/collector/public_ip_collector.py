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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class PublicIPAddressCollector(LoadingCollector):
    '''Public IP address collector'''

    def __init__(self, router_id: dict[str, str], polling_interval: int):
        self.name = 'PublicIPAddressCollector'
        self.metric_store = MetricStore(
            router_id,
            ['public_address', 'dns_name', 'public_address_ipv6'],
            [],
            {
                'dns_name': lambda name: 'ddns_disabled' if not name else name,
                'public_address_ipv6': lambda addr: '' if not addr else addr,
                'public_address_ipv4': lambda addr: '' if not addr else addr,
            },
            polling_interval=polling_interval
        )

    def load(self, router_entry: 'RouterEntry'):
        if self.metric_store.run_fetch():
            #address_records = PublicIPAddressDatasource.metric_records(router_entry)
            address_records = router_entry.api_connection.get('/ip/cloud/')
            self.metric_store.set_metrics(address_records)

    def collect(self):
        if self.metric_store.have_metrics():
            yield self.metric_store.info_collector('public_ip_address', 'Public IP address')

