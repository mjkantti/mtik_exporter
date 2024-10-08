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
from utils.utils import parse_ros_version, parse_timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.router_entry import RouterEntry

class SystemResourceCollector(LoadingCollector):
    ''' System Resource Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'SystemResourceCollector'
        self.metric_store = MetricStore(
            router_id,
            ['version', 'channel', 'current_version', 'cpu', 'architecture_name', 'board_name'],
            ['uptime', 'write-sect-total', 'bad_blocks', 'cpu_count', 'cpu_frequency', 'free_memory', 'total_memory', 'cpu_load', 'free_hdd_space', 'total_hdd_space'],
            {
                'uptime': parse_timedelta,
                'bad_blocks': lambda b: b.strip('%') if b else b
            })
        self.version_metric_store = MetricStore(router_id, ['current_version', 'channel', 'latest_version'])

        # Metrics
        self.metric_store.create_info_metric('system', 'System Resource Information')

        self.metric_store.create_counter_metric('system_uptime', 'Time interval since boot-up', 'uptime', ['board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_free_memory', 'Unused amount of RAM', 'free_memory', ['board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_total_memory', 'Amount of installed RAM', 'total_memory', ['board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_free_hdd_space', 'Free space on hard drive or NAND', 'free_hdd_space', ['board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_total_hdd_space', 'Size of the hard drive or NAND', 'total_hdd_space', ['board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_cpu_load', 'Percentage of used CPU resources', 'cpu_load', ['board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_cpu_count', 'Number of CPUs present on the system', 'cpu_count', ['board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_cpu_frequency', 'Current CPU frequency', 'cpu_frequency', ['board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_gauge_metric('system_hdd_bad_blocks_percent', 'HDD Bad Block percentage', 'bad_blocks', ['board_name', 'cpu', 'architecture_name'])
        self.metric_store.create_counter_metric('system_hdd_write_sector_count', 'HDD Written Sector Count', 'write_sect_total', ['board_name', 'cpu', 'architecture_name'])

        # Updates
        self.version_metric_store.create_info_metric('system_latest_version', 'Latest RouterOS version available')
        self.version_metric_store.create_gauge_metric('system_latest_version_built', 'Latest RouterOS version built time', 'latest_built')

    def load_data(self, router_entry: 'RouterEntry'):
        resource_record = router_entry.rest_api.get('system/resource')
        if resource_record:
            ver, channel = parse_ros_version(resource_record['version'])
            if channel:
                resource_record['current_version'] = ver
                resource_record['channel'] = channel

            self.metric_store.set_metrics([resource_record])