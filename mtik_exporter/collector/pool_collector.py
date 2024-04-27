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

class PoolCollector(LoadingCollector):
    ''' IP Pool Metrics collector
    '''

    def __init__(self, router_id: dict[str, str], polling_interval: int):
        self.name = 'PoolCollector'
        self.metric_store = MetricStore(router_id, ['pool', 'address', 'owner', 'info'], polling_interval=polling_interval)

        # Metrics
        self.metric_store.create_info_metric('ip_pool_device', 'Used Addresses in IP Pool')

    def load(self, router_entry: 'RouterEntry'):
        self.metric_store.clear_metrics()
        #pool_used_records = PoolUsedMetricsDataSource.metric_records(router_entry)
        pool_used_records = router_entry.api_connection.get('ip/pool/used')
        self.metric_store.set_metrics(pool_used_records)

    def collect(self):
        yield from self.metric_store.get_metrics()
