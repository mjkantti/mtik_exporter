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

class FirewallCollector(LoadingCollector):
    ''' Firewall rules traffic metrics collector
    '''
    def __init__(self, router_id: dict[str, str], interval: int):
        self.name = 'FirewallCollector'
        firewall_labels = ['chain', 'action', 'comment']
        firewall_values = ['bytes', 'packets']

        self.ipv4_filter_metric_store = MetricStore(router_id, firewall_labels, firewall_values, interval=interval)
        self.ipv4_mangle_metric_store = MetricStore(router_id, firewall_labels, firewall_values, interval=interval)
        self.ipv4_raw_metric_store = MetricStore(router_id, firewall_labels, firewall_values, interval=interval)

        # Metrics
        self.ipv4_filter_metric_store.create_counter_metric('firewall_filter_bytes', 'Total amount of bytes matched by firewall rules', 'bytes')
        self.ipv4_filter_metric_store.create_counter_metric('firewall_filter_packets', 'Total amount of packets matched by firewall rules', 'packets')

        self.ipv4_mangle_metric_store.create_counter_metric('firewall_mangle_bytes', 'Total amount of bytes matched by firewall mangle rules', 'bytes')
        self.ipv4_mangle_metric_store.create_counter_metric('firewall_mangle_packets', 'Total amount of packets matched by firewall mangle rules', 'packets')

        self.ipv4_raw_metric_store.create_counter_metric('firewall_raw_bytes', 'Total amount of bytes matched by firewall raw rules', 'bytes')
        self.ipv4_raw_metric_store.create_counter_metric('firewall_raw_packets', 'Total amount of packets matched by firewall raw rules', 'packets')

    def load(self, router_entry: 'RouterEntry'):
        #firewall_filter_records = FirewallMetricsDataSource.metric_records_ipv4(router_entry)
        firewall_filter_records = router_entry.api_connection.get('ip/firewall/filter')
        self.ipv4_filter_metric_store.set_metrics(firewall_filter_records)

        #firewall_mangle_records = FirewallMetricsDataSource.metric_records_ipv4(router_entry, fw_type='mangle')
        firewall_mangle_records = router_entry.api_connection.get('ip/firewall/mangle')
        self.ipv4_mangle_metric_store.set_metrics(firewall_mangle_records)

        #firewall_raw_records = FirewallMetricsDataSource.metric_records_ipv4(router_entry, fw_type='raw')
        firewall_raw_records = router_entry.api_connection.get('ip/firewall/raw')
        self.ipv4_raw_metric_store.set_metrics(firewall_raw_records)

    def collect(self):
        # ~*~*~*~*~*~ IPv4 ~*~*~*~*~*~
        yield from self.ipv4_filter_metric_store.get_metrics()
        yield from self.ipv4_mangle_metric_store.get_metrics()
        yield from self.ipv4_raw_metric_store.get_metrics()

class IPv6FirewallCollector(LoadingCollector):
    ''' Firewall rules traffic metrics collector
    '''
    def __init__(self, router_id: dict[str, str], interval: int):
        self.name = 'IPv6FirewallCollector'
        firewall_labels = ['chain', 'action', 'comment']
        firewall_values = ['bytes', 'packets']

        self.ipv6_filter_metric_store = MetricStore(router_id, firewall_labels, firewall_values, interval=interval)
        self.ipv6_mangle_metric_store = MetricStore(router_id, firewall_labels, firewall_values, interval=interval)
        self.ipv6_raw_metric_store = MetricStore(router_id, firewall_labels, firewall_values, interval=interval)

        # Metrics
        self.ipv6_filter_metric_store.create_counter_metric('firewall_filter_ipv6_bytes', 'Total amount of bytes matched by firewall rules (IPv6)', 'bytes')
        self.ipv6_filter_metric_store.create_counter_metric('firewall_filter_ipv6_packets', 'Total amount of packets matched by firewall rules (IPv6)', 'packets')

        self.ipv6_mangle_metric_store.create_counter_metric('firewall_mangle_ipv6_bytes', 'Total amount of bytes matched by firewall mangle rules (IPv6)', 'bytes')
        self.ipv6_mangle_metric_store.create_counter_metric('firewall_mangle_ipv6_packets', 'Total amount of packets matched by firewall mangle rules (IPv6)', 'packets')

        self.ipv6_raw_metric_store.create_counter_metric('firewall_raw_ipv6_bytes', 'Total amount of bytes matched by firewall raw rules (IPv6)', 'bytes')
        self.ipv6_raw_metric_store.create_counter_metric('firewall_raw_ipv6_packets', 'Total amount of packets matched by firewall raw rules (IPv6)', 'packets')


    def load(self, router_entry: 'RouterEntry'):
        #firewall_filter_records_ipv6 =  FirewallMetricsDataSource.metric_records_ipv6(router_entry)
        firewall_filter_records_ipv6 = router_entry.api_connection.get('ipv6/firewall/filter')
        self.ipv6_filter_metric_store.set_metrics(firewall_filter_records_ipv6)

        #firewall_mangle_records_ipv6 =  FirewallMetricsDataSource.metric_records_ipv6(router_entry, fw_type='mangle')
        firewall_mangle_records_ipv6 = router_entry.api_connection.get('ipv6/firewall/mangle')
        self.ipv6_mangle_metric_store.set_metrics(firewall_mangle_records_ipv6)

        #firewall_raw_records_ipv6 = FirewallMetricsDataSource.metric_records_ipv6(router_entry, fw_type='raw')
        firewall_raw_records_ipv6 = router_entry.api_connection.get('ipv6/firewall/raw')
        self.ipv6_raw_metric_store.set_metrics(firewall_raw_records_ipv6)

    def collect(self):
        #for metric, _, _ in self.ipv6_filter_metric_store.metrics + self.ipv6_mangle_metric_store.metrics + self.ipv6_raw_metric_store.metrics:
            #yield metric
        yield from self.ipv6_filter_metric_store.get_metrics()
        yield from self.ipv6_mangle_metric_store.get_metrics()
        yield from self.ipv6_raw_metric_store.get_metrics()