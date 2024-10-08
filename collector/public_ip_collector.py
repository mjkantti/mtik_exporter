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

class PublicIPAddressCollector(LoadingCollector):
    '''Public IP address collector'''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'PublicIPAddressCollector'
        self.metric_store = MetricStore(
            router_id,
            ['public_address', 'dns_name', 'public_address_ipv6'],
            [],
            {
                'dns_name': lambda name: 'ddns_disabled' if not name else name,
                #'public_address_ipv6': lambda addr: '' if not addr else addr,
                #'public_address_ipv4': lambda addr: '' if not addr else addr,
            })

        # Metrics
        self.metric_store.create_info_metric('public_ip_address', 'Public IP address')

    def load_data(self, router_entry: 'RouterEntry'):
        address_record = router_entry.rest_api.get('ip/cloud')
        if address_record:
            self.metric_store.set_metrics([address_record])

