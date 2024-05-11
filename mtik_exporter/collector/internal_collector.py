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

    def __init__(self, router: 'RouterEntry'):
        self.name = 'InternalCollector'
        self.router = router
        #self.collect_metrics = MetricStore(router_id, ['name'], ['duration'])
        self.load_metrics = MetricStore(router.router_id, ['name'], ['duration', 'count', 'last_run'])

        # Metrics
        self.load_metrics.create_counter_metric('data_load_time', 'Time spent loading metrics in seconds', 'duration')
        self.load_metrics.create_counter_metric('data_load_count', 'Total count of metrics loads since reboot', 'count')
        self.load_metrics.create_gauge_metric('data_load_last_run', 'Last run timestamp of metrics load', 'last_run')

    def load(self, router_entry: 'RouterEntry'):
        pass

    def collect(self):
        self.load_metrics.set_metrics(self.router.data_loader_stats.values())
        yield from self.load_metrics.get_metrics()