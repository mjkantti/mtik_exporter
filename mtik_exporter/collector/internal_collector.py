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


class InternalCollector(LoadingCollector):
    ''' System Identity Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'InternalCollector'
        #self.collect_metrics = MetricStore(router_id, ['name'], ['duration'])
        self.load_metrics = MetricStore(router_id, ['name'], ['duration', 'count'])

        # Metrics
        self.load_metrics.create_counter_metric('data_load_time', 'Time spent loading metrics in seconds', 'duration')
        self.load_metrics.create_counter_metric('data_load_count', 'Total count of metrics loads since reboot', 'count')

    def load(self, router_entry: 'RouterEntry'):
        self.load_metrics.clear_metrics()
        self.load_metrics.set_metrics(router_entry.data_loader_stats.values())

    def collect(self):
        yield from self.load_metrics.get_metrics()