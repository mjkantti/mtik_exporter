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


class IPConnectionCollector(LoadingCollector):
    ''' IP Connection Metrics collector
    '''
    def __init__(self, router_id: dict[str, str], polling_interval):
        self.name = 'IPConnectionCollector'
        self.metric_store = MetricStore(router_id, [], ['count'])
        self.connection_stats_metric_store = MetricStore(router_id, ['src_address', 'dst_addresses'], ['connection_count'], polling_interval=polling_interval)

    def load(self, router_entry: 'RouterEntry'):
        connection_records = IPConnectionDatasource.metric_records(router_entry)
        self.metric_store.set_metrics(connection_records)

        if router_entry.config_entry.connection_stats:
            connection_stats_records = IPConnectionStatsDatasource.metric_records(router_entry)
            self.connection_stats_metric_store.set_metrics(connection_stats_records)

    def collect(self):
        if self.metric_store.have_metrics():
           yield self.metric_store.gauge_collector('ip_connections_total', 'Number of IP connections', 'count')

        if self.connection_stats_metric_store.have_metrics():
            yield self.connection_stats_metric_store.gauge_collector('connection_stats', 'Open connection stats', 'connection_count')