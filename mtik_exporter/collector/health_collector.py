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


class HealthCollector(LoadingCollector):
    ''' System Health Metrics collector
    '''
    def __init__(self, router_id: dict[str, str]):
        self.name = 'HealthCollector'
        self.metric_store = MetricStore(
            router_id,
            [],
            ['voltage', 'temperature', 'phy_temperature', 'cpu_temperature', 'switch_temperature', 'fan1_speed', 'fan2_speed', 'fan3_speed', 'fan4_speed', 'power_consumption'])

        # Metrics
        self.metric_store.create_gauge_metric('system_routerboard_voltage', 'Supplied routerboard voltage', 'voltage')
        self.metric_store.create_gauge_metric('system_routerboard_temperature', 'Routerboard current temperature', 'temperature')
        self.metric_store.create_gauge_metric('system_routerboard_phy_temperature', 'Routerboard current temperature', 'phy_temperature')
        self.metric_store.create_gauge_metric('system_cpu_temperature', 'CPU current temperature', 'cpu_temperature')
        self.metric_store.create_gauge_metric('system_switch_temperature', 'Switch chip current temperature', 'switch_temperature')
        self.metric_store.create_gauge_metric('system_fan_one_speed', 'System fan 1 current speed', 'fan1_speed')
        self.metric_store.create_gauge_metric('system_fan_two_speed', 'System fan 2 current speed', 'fan2_speed')
        self.metric_store.create_gauge_metric('system_fan_three_speed', 'System fan 3 current speed', 'fan3_speed')
        self.metric_store.create_gauge_metric('system_fan_four_speed', 'System fan 4 current speed', 'fan4_speed')
        self.metric_store.create_gauge_metric('system_power_consumption', 'System Power Consumption', 'power_consumption')

    def load_data(self, router_entry: 'RouterEntry'):
        health_records = router_entry.rest_api.get('system/health')
        for record in health_records:
            if 'name' in record:
                # Note: The API in RouterOS v7.X+ returns a response like this:
                # [{'name': 'temperature', 'value': '33', 'type': 'C'}, ...]
                # To make this work for both v6 and v7 add a <name>:<value> pair in v7
                # Otherwise it is not possible to get the value by name (e.g. records['voltage'])
                name = record['name']
                val = record.get('value', None)
                record[name] = val

        self.metric_store.set_metrics(health_records)