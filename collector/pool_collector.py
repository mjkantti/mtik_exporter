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

class PoolCollector(LoadingCollector):
    ''' IP Pool Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'PoolCollector'
        self.metric_store = MetricStore(router_id, ['pool', 'address', 'owner', 'info'])

        # Metrics
        self.metric_store.create_info_metric('ip_pool_device', 'Used Addresses in IP Pool')

    def load_data(self, router_entry: 'RouterEntry'):
        pool_used_records = router_entry.rest_api.get('ip/pool/used')
        self.metric_store.set_metrics(pool_used_records)
