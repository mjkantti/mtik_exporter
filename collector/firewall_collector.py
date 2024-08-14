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


firewall_labels = ['chain', 'action', 'comment']
firewall_values = ['bytes', 'packets']

class FirewallFilterCollector(LoadingCollector):
    ''' Firewall rules traffic metrics collector
    '''
    def __init__(self, router_id: dict[str, str]):
        self.name = 'FirewallFilterCollector'

        self.metric_store = MetricStore(router_id, firewall_labels, firewall_values)

        # Metrics
        self.metric_store.create_counter_metric('firewall_filter_bytes', 'Total amount of bytes matched by firewall rules', 'bytes')
        self.metric_store.create_counter_metric('firewall_filter_packets', 'Total amount of packets matched by firewall rules', 'packets')

    def load_data(self, router_entry: 'RouterEntry'):
        firewall_filter_records = router_entry.rest_api.get('ip/firewall/filter')
        self.metric_store.set_metrics(firewall_filter_records)

class FirewallMangleCollector(LoadingCollector):
    ''' Firewall rules traffic metrics collector
    '''
    def __init__(self, router_id: dict[str, str]):
        self.name = 'FirewallMangleCollector'

        self.metric_store = MetricStore(router_id, firewall_labels, firewall_values)

        # Metrics
        self.metric_store.create_counter_metric('firewall_mangle_bytes', 'Total amount of bytes matched by firewall mangle rules', 'bytes')
        self.metric_store.create_counter_metric('firewall_mangle_packets', 'Total amount of packets matched by firewall mangle rules', 'packets')

    def load_data(self, router_entry: 'RouterEntry'):
        firewall_mangle_records = router_entry.rest_api.get('ip/firewall/mangle')
        self.metric_store.set_metrics(firewall_mangle_records)

class FirewallRawCollector(LoadingCollector):
    ''' Firewall rules traffic metrics collector
    '''
    def __init__(self, router_id: dict[str, str]):
        self.name = 'FirewallRawCollector'

        self.metric_store = MetricStore(router_id, firewall_labels, firewall_values)

        # Metrics
        self.metric_store.create_counter_metric('firewall_raw_bytes', 'Total amount of bytes matched by firewall raw rules', 'bytes')
        self.metric_store.create_counter_metric('firewall_raw_packets', 'Total amount of packets matched by firewall raw rules', 'packets')

    def load_data(self, router_entry: 'RouterEntry'):
        firewall_raw_records = router_entry.rest_api.get('ip/firewall/raw')
        self.metric_store.set_metrics(firewall_raw_records)

class IPv6FirewallFilterCollector(LoadingCollector):
    ''' Firewall rules traffic metrics collector
    '''
    def __init__(self, router_id: dict[str, str]):
        self.name = 'IPv6FirewallFilterCollector'

        self.metric_store = MetricStore(router_id, firewall_labels, firewall_values)

        # Metrics
        self.metric_store.create_counter_metric('firewall_filter_ipv6_bytes', 'Total amount of bytes matched by firewall rules (IPv6)', 'bytes')
        self.metric_store.create_counter_metric('firewall_filter_ipv6_packets', 'Total amount of packets matched by firewall rules (IPv6)', 'packets')

    def load_data(self, router_entry: 'RouterEntry'):
        firewall_filter_records_ipv6 = router_entry.rest_api.get('ipv6/firewall/filter')
        self.metric_store.set_metrics(firewall_filter_records_ipv6)

class IPv6FirewallMangleCollector(LoadingCollector):
    ''' Firewall rules traffic metrics collector
    '''
    def __init__(self, router_id: dict[str, str]):
        self.name = 'IPv6FirewallMangleCollector'

        self.metric_store = MetricStore(router_id, firewall_labels, firewall_values)

        # Metrics
        self.metric_store.create_counter_metric('firewall_mangle_ipv6_bytes', 'Total amount of bytes matched by firewall mangle rules (IPv6)', 'bytes')
        self.metric_store.create_counter_metric('firewall_mangle_ipv6_packets', 'Total amount of packets matched by firewall mangle rules (IPv6)', 'packets')

    def load_data(self, router_entry: 'RouterEntry'):
        firewall_mangle_records_ipv6 = router_entry.rest_api.get('ipv6/firewall/mangle')
        self.metric_store.set_metrics(firewall_mangle_records_ipv6)

class IPv6FirewallRawCollector(LoadingCollector):
    ''' Firewall rules traffic metrics collector
    '''
    def __init__(self, router_id: dict[str, str]):
        self.name = 'IPv6FirewallRawCollector'

        self.metric_store = MetricStore(router_id, firewall_labels, firewall_values)

        # Metrics
        self.metric_store.create_counter_metric('firewall_raw_ipv6_bytes', 'Total amount of bytes matched by firewall raw rules (IPv6)', 'bytes')
        self.metric_store.create_counter_metric('firewall_raw_ipv6_packets', 'Total amount of packets matched by firewall raw rules (IPv6)', 'packets')


    def load_data(self, router_entry: 'RouterEntry'):
        firewall_raw_records_ipv6 = router_entry.rest_api.get('ipv6/firewall/raw')
        self.metric_store.set_metrics(firewall_raw_records_ipv6)