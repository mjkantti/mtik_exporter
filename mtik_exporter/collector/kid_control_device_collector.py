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
from mtik_exporter.utils.utils import parse_rates, parse_timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class KidDeviceCollector(LoadingCollector):
    """ Kid-control device Metrics collector
    """

    def __init__(self, router_id: dict[str, str]):
        self.name = 'KidDeviceCollector'
        self.metric_store = MetricStore(
            router_id,
            ['name', 'user', 'mac_address', 'ip_address', 'disabled'],
            ['bytes_down', 'bytes_up', 'rate_up', 'rate_down', 'bytes_up', 'idle_time'],
            {
                'rate_up': lambda value: parse_rates(value),
                'rate_down': lambda value: parse_rates(value),
                'idle_time': lambda value: parse_timedelta(value) if value else 0, 
                'blocked': lambda value: '1' if value == 'true' else '0',
                'limited': lambda value: '1' if value == 'true' else '0',
                'inactive': lambda value: '1' if value == 'true' else '0',
                'disabled': lambda value: '1' if value == 'true' else '0'
            })

        # Metrics
        self.metric_store.create_info_metric('kid_control_device', 'Kid-control device Info')
        self.metric_store.create_gauge_metric('kid_control_device_bytes_down', 'Number of received bytes', 'bytes_down', ['name', 'mac_address', 'user'])
        self.metric_store.create_gauge_metric('kid_control_device_bytes_up', 'Number of transmitted bytes', 'bytes_up', ['name', 'mac_address', 'user'])
        self.metric_store.create_gauge_metric('kid_control_device_rate_down', 'Device rate down', 'rate_down', ['name', 'mac_address', 'user'])
        self.metric_store.create_gauge_metric('kid_control_device_rate_up', 'Device rate up', 'rate_up', ['name', 'mac_address', 'user'])
        self.metric_store.create_gauge_metric('kid_control_device_idle_time', 'Device idle time', 'idle_time', ['name', 'mac_address', 'user'])

    def load_data(self, router_entry: 'RouterEntry'):
        records = router_entry.rest_api.get('ip/kid-control/device')
        device_records = []
        for record in records:
            if record.get('user'):
                device_records.append(record)

        self.metric_store.set_metrics(device_records)
