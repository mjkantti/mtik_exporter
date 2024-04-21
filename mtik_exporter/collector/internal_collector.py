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
        self.name = 'Collector'
        #self.collect_metrics = MetricStore(router_id, ['name'], ['duration'])
        self.load_metrics = MetricStore(router_id, ['name'], ['duration'])
        self.load_count = MetricStore(router_id, [], ['count'])

    def load(self, router_entry: 'RouterEntry'):
        # Collect metrics
        # collect_records = [{'name': key, 'duration': val} for key, val in router_entry.collector_time_spent.items()]
        # self.collect_metrics.set_metrics(collect_records)

        # Load metrics
        load_records: list[dict[str, str | float]] = [{'name': key, 'duration': val} for key, val in router_entry.data_loader_time_spent.items()]
        self.load_metrics.set_metrics(load_records)
        self.load_count.set_metrics([{'count': router_entry.data_load_count}])

    def collect(self):
        #if self.collect_metrics.have_metrics():
        #    yield self.collect_metrics.gauge_collector('collection_time', 'Time spent collecting metrics in seconds', 'duration')

        if self.load_metrics.have_metrics():
            yield self.load_metrics.gauge_collector('data_load_time', 'Time spent loading metrics in seconds', 'duration')
            yield self.load_count.counter_collector('data_load_count', 'Total count of metrics loads since reboot', 'count')
