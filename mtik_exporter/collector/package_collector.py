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
from mtik_exporter.utils.utils import get_available_updates
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class PackageCollector(LoadingCollector):
    '''Installed Packages collector'''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'PackageCollector'
        self.metric_store = MetricStore(router_id, ['name', 'version', 'build_time', 'disabled'])
        #self.metric_store_updates = MetricStore(router_id, ['channel', 'latest_version', 'build_time', 'status'], polling_interval=polling_interval)

        # Metrics
        self.metric_store.create_info_metric('installed_packages', 'Installed Packages')

    def load(self, router_entry: 'RouterEntry'):
        self.metric_store.clear_metrics()

        package_record = router_entry.rest_api.get('system/package')
        self.metric_store.set_metrics(package_record)