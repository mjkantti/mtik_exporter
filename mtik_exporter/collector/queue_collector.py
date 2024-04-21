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

class QueueTreeCollector(LoadingCollector):
    '''Queue Tree collector'''

    def __init__(self, router_id: dict[str, str], polling_interval: int):
        self.name = 'QueueTreeCollector'
        self.metric_store = MetricStore(
            router_id,
            ['name', 'parent', 'packet_mark', 'limit_at', 'max_limit', 'priority', 'disabled'],
            ['rate', 'bytes', 'queued_bytes', 'dropped'],
            polling_interval=polling_interval,
        )

    def load(self, router_entry: 'RouterEntry'):
        #qt_records = QueueMetricsDataSource.metric_records(router_entry, kind = 'tree')
        qt_records = router_entry.api_connection.get('/queue/tree/')
        self.metric_store.set_metrics(qt_records)

    def collect(self):
        if self.metric_store.have_metrics():
            yield self.metric_store.info_collector('queue_tree', 'Queue Tree Info')
            yield self.metric_store.counter_collector('queue_tree_rates', 'Average passing data rate in bytes per second', 'rate', ['name'])
            yield self.metric_store.counter_collector('queue_tree_bytes', 'Number of processed bytes', 'bytes', ['name'])
            yield self.metric_store.counter_collector('queue_tree_queued_bytes', 'Number of queued bytes', 'queued_bytes', ['name'])
            yield self.metric_store.counter_collector('queue_tree_dropped', 'Number of dropped bytes', 'dropped', ['name'])


class QueueSimpleCollector(LoadingCollector):
    def __init__(self, router_id: dict[str, str], polling_interval: int):
        self.name = 'QueueSimpleCollector'
        self.mestric_store = MetricStore(
            router_id,
            ['name', 'parent', 'packet_mark', 'limit_at', 'max_limit', 'priority', 'bytes', 'packets', 'queued_bytes', 'queued_packets','dropped', 'rate', 'packet_rate', 'disabled'],
            ['bytes_up', 'bytes_down', 'queued_bytes_up', 'queued_bytes_down', 'dropped_up', 'dropped_down'],
            polling_interval=polling_interval,
        )

    def load(self, router_entry: 'RouterEntry'):
        #qt_records = QueueMetricsDataSource.metric_records(router_entry, kind = 'simple')
        queue_records = router_entry.api_connection.get('/queue/simple/')

        # simple queue records need splitting upload/download values
        splitted_queue_records = []
        for queue_record in queue_records:
            splitted_queue_record = {}
            for key, value in queue_record.items():
                split_values = value.split('/')
                if split_values and len(split_values) > 1:
                    splitted_queue_record[f'{key}_up'] = split_values[0]
                    splitted_queue_record[f'{key}_down'] = split_values[1]
                else:
                    splitted_queue_record[key] = value
            splitted_queue_records.append(splitted_queue_record)   

        self.mestric_store.set_metrics(splitted_queue_records)

    '''Simple Queue collector'''
    def collect(self):
        if self.mestric_store.have_metrics():
            yield self.mestric_store.info_collector('queue_simple', 'Queue Simple Info')

            yield self.mestric_store.counter_collector('queue_simple_bytes_upload', 'Number of upload processed bytes', 'bytes_up', ['name'])
            yield self.mestric_store.counter_collector('queue_simple_bytes_download', 'Number of download processed bytes', 'bytes_down', ['name'])

            yield self.mestric_store.counter_collector('queue_simple_queued_bytes_upload', 'Number of upload queued bytes', 'queued_bytes_up', ['name'])
            yield self.mestric_store.counter_collector('queue_simple_queued_bytes_download', 'Number of download queued bytes', 'queued_bytes_down', ['name'])

            yield self.mestric_store.counter_collector('queue_simple_dropped_upload', 'Number of upload dropped bytes', 'dropped_up', ['name'])
            yield self.mestric_store.counter_collector('queue_simple_dropped_download', 'Number of download dropped bytes', 'dropped_down', ['name'])