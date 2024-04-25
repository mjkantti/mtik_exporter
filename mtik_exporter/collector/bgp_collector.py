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
from mtik_exporter.flow.processor.output import BaseOutputProcessor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class BGPCollector(LoadingCollector):
    '''BGP collector'''
    def __init__(self, router_id: dict[str, str], polling_interval):
        self.name = 'BGPCollector'
        self.metric_store = MetricStore(
            router_id,
            ['name', 'remote_address', 'remote_as', 'local_as', 'remote_afi', 'local_afi'],
            ['prefix_count', 'local_messages', 'local_bytes', 'remote_messages', 'remote_bytes', 'established', 'uptime'],
            {
                'established': lambda value: '1' if value=='true' else '0',
                'uptime': lambda value: BaseOutputProcessor.parse_timedelta(value) if value else None
            },
            polling_interval,
            )

        # Metrics
        self.metric_store.create_info_metric('bgp_sessions_info', 'BGP sessions info')

        session_id_labes = ['name']
        self.metric_store.create_counter_metric('bgp_remote_messages', 'Number of remote messages', 'remote_messages', session_id_labes)
        self.metric_store.create_counter_metric('bgp_local_messages', 'Number of local messages', 'local_messages', session_id_labes)
        self.metric_store.create_counter_metric('bgp_remote_bytes', 'Number of remote bytes', 'remote_bytes', session_id_labes)
        self.metric_store.create_counter_metric('bgp_local_bytes', 'Number of local bytes', 'local_bytes', session_id_labes)
        self.metric_store.create_gauge_metric('bgp_prefix_count', 'BGP prefix count', 'prefix_count', session_id_labes)
        self.metric_store.create_gauge_metric('bgp_established', 'BGP established', 'established', session_id_labes)
        self.metric_store.create_gauge_metric('bgp_uptime', 'BGP uptime in seconds', 'uptime', session_id_labes)

    def load(self, router_entry: 'RouterEntry'):
        self.metric_store.clear_metrics()
        #bgp_records = BGPMetricsDataSource.metric_records(router_entry)
        bgp_records = router_entry.rest_api.get('routing/bgp/session')
        self.metric_store.set_metrics(bgp_records)

    def collect(self):
        yield from self.metric_store.get_metrics()