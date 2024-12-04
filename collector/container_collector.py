# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
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

class ContainerCollector(LoadingCollector):
    '''Container collector'''
    def __init__(self, router_id: dict[str, str]):
        self.name = 'ContainerCollector'
        self.metric_store = MetricStore(
            router_id,
            ['name', 'tag', 'os', 'arch', 'interface', 'root_dir', 'status', 'comment'],
            ['state']
            )

        # Metrics
        self.metric_store.create_gauge_metric('container_running', 'Container Info (running)', 'state')

    def load_data(self, router_entry: 'RouterEntry'):
        container_records = router_entry.rest_api.get('container')
        for cnt in container_records:
            cnt['state'] = 1 if cnt.get('status') == 'running' else 0
        self.metric_store.set_metrics(container_records)