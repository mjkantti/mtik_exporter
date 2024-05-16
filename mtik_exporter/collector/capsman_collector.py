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

class CapsmanCollector(LoadingCollector):
    ''' CAPsMAN Metrics collector
    '''
    def __init__(self, router_id: dict[str, str], interval: int):
        self.name = 'CapsmanCollector'
        self.metric_store = MetricStore(router_id, ['identity', 'version', 'base_mac', 'board', 'base_mac'], interval=interval)

        # Metrics
        self.metric_store.create_info_metric('capsman_remote_caps', 'CAPsMAN remote caps')

    def load(self, router_entry: 'RouterEntry'):
        recs = router_entry.api_connection.get('interface/wifi/capsman/remote-cap')
        self.metric_store.set_metrics(recs)

    #def collect(self):
    #    yield from self.metric_store.get_metrics()
