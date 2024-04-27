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

    def __init__(self, router_id: dict[str, str], polling_interval: int):
        self.name = 'PackageCollector'
        self.metric_store = MetricStore(router_id, ['name', 'version', 'build_time', 'disabled'], polling_interval=polling_interval)
        #self.metric_store_updates = MetricStore(router_id, ['channel', 'latest_version', 'build_time', 'status'], polling_interval=polling_interval)

        # Metrics
        self.metric_store.create_info_metric('installed_packages', 'Installed Packages')

    def load(self, router_entry: 'RouterEntry'):
        if self.metric_store.run_fetch():
            self.metric_store.clear_metrics()
            #package_records = PackageMetricsDataSource.metric_records(router_entry)
            package_record = router_entry.api_connection.get('system/package')
            self.metric_store.set_metrics(package_record)

            #if router_entry.config_entry.check_for_updates:
            #    #package_update_records = PackageMetricsDataSource.metric_records_update(router_entry)
            #    package_update_records = router_entry.api_connection.get('/system/package/update')
            #    for pkg_upd in package_update_records:
            #        if not 'latest-version' in pkg_upd:
            #            latest_version, build_time = get_available_updates(pkg_upd['channel'])
            #            pkg_upd['latest_version'] = latest_version
            #            pkg_upd['build_time'] = build_time

            #    self.metric_store_updates.set_metrics(package_update_records)

    def collect(self):
        yield from self.metric_store.get_metrics()

        #if self.metric_store_updates.have_metrics():
        #    yield self.metric_store_updates.info_collector('update', 'Latest package versions info')
