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

class RouteCollector(LoadingCollector):
    ''' IP Route Metrics collector
    '''
    def __init__(self, router_id: dict[str, str], interval: int):
        self.name = 'RouteCollector'
        self.metric_store = MetricStore(
            router_id,
            ['comment', 'type', 'dst_address', 'gateway', 'distance', 'connect', 'dynamic', 'bgp', 'ospf', 'active'],
            interval=interval
        )

        # Metrics
        self.metric_store.create_info_metric('routes', 'Routes Info')

    def load(self, router_entry: 'RouterEntry'):
        route_records = router_entry.api_connection.get('ip/route')
        self.metric_store.set_metrics(route_records)

    def collect(self):
        yield from self.metric_store.get_metrics()

class IPv6RouteCollector(LoadingCollector):
    ''' IP Route Metrics collector
    '''
    def __init__(self, router_id: dict[str, str], interval: int):
        self.name = 'IPv6RouteCollector'
        self.metric_store = MetricStore(
            router_id,
            ['comment', 'type', 'dst_address', 'gateway', 'distance', 'connect', 'dynamic', 'bgp', 'ospf', 'active'],
            interval=interval
        )

        # Metrics
        self.metric_store.create_info_metric('ipv6_routes', 'IPv6 Routes Info')

    def load(self, router_entry: 'RouterEntry'):
        route_records = router_entry.api_connection.get('ipv6/route')
        self.metric_store.set_metrics(route_records)

    def collect(self):
        yield from self.metric_store.get_metrics()