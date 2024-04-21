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

class IdentityCollector(LoadingCollector):
    ''' System Identity Metrics collector
    '''
    def __init__(self, router_id: dict[str, str], polling_interval: int):
        self.name = 'IdentityCollector'
        self.metric_store = MetricStore(router_id, ['name'], polling_interval=polling_interval)

    def load(self, router_entry: 'RouterEntry'):
        if self.metric_store.run_fetch():
            #identity_records = IdentityMetricsDataSource.metric_records(router_entry)
            identity_records = router_entry.api_connection.get('/system/identity')
            self.metric_store.set_metrics(identity_records)

    def collect(self):
        if self.metric_store.have_metrics():
            yield self.metric_store.info_collector('system_identity', 'System identity')

