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
from mtik_exporter.utils.utils import parse_ros_version, get_available_updates
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class SystemResourceCollector(LoadingCollector):
    ''' System Resource Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'SystemResourceCollector'
        self.metric_store = MetricStore(
            router_id,
            ['version', 'free_memory', 'total_memory', 'cpu', 'cpu_count', 'cpu_frequency', 'cpu_load', 'free_hdd_space', 'total_hdd_space', 'architecture_name', 'board_name'],
            ['uptime', 'write-sect-total', 'bad_blocks'],
            {
                'uptime': lambda c: BaseOutputProcessor.parse_timedelta(c) if c else 0,
                'bad_blocks': lambda b: b.strip('%') if b else b
            }
        )
        self.version_metric_store = MetricStore(router_id, ['current_version', 'channel', 'latest_version'])

        # Metrics
        self.metric_store.create_counter_metric('system_uptime', 'Time interval since boot-up', 'uptime', ['version', 'board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_free_memory', 'Unused amount of RAM', 'free_memory', ['version', 'board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_total_memory', 'Amount of installed RAM', 'total_memory', ['version', 'board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_free_hdd_space', 'Free space on hard drive or NAND', 'free_hdd_space', ['version', 'board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_total_hdd_space', 'Size of the hard drive or NAND', 'total_hdd_space', ['version', 'board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_cpu_load', 'Percentage of used CPU resources', 'cpu_load', ['version', 'board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_cpu_count', 'Number of CPUs present on the system', 'cpu_count', ['version', 'board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_cpu_frequency', 'Current CPU frequency', 'cpu_frequency', ['version', 'board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_hdd_bad_blocks_percent', 'HDD Bad Block percentage', 'bad_blocks', ['version', 'board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_counter_metric('system_hdd_write_sector_count', 'HDD Written Sector Count', 'write_sect_total', ['version', 'board_name', 'cpu', 'architecture_name'])

        # Updates
        self.version_metric_store.create_info_metric('system_latest_version', 'Latest RouterOS version available')
        self.version_metric_store.create_gauge_metric('system_latest_version_built', 'Latest RouterOS version built time', 'latest_built')

    def load(self, router_entry: 'RouterEntry'):
        resource_records = router_entry.api_connection.get('system/resource')

        # Check for updates
        if resource_records and router_entry.config_entry.check_for_updates:
            latest_version_rec = {}
            version, channel = parse_ros_version(resource_records[0].get('version'))
            latest_version_rec['current_version'] = version
            latest_version_rec['channel'] = channel

            newest, built = get_available_updates(channel)
            latest_version_rec['latest_version'] = newest
            latest_version_rec['latest_built'] = built

            self.version_metric_store.set_metrics([latest_version_rec])

        self.metric_store.set_metrics(resource_records)

    def collect(self):
        yield from self.metric_store.get_metrics()
        yield from self.version_metric_store.get_metrics()