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
from utils.utils import parse_timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.router_entry import RouterEntry

class WifiCollector(LoadingCollector):
    ''' Wireless Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'WifiCollector'
        self.metric_store = MetricStore(router_id, ['id', 'name', 'comment', 'configuration', 'configuration_mode', 'configuration_ssid', 'mac_address', 'master', 'state', 'channel', 'tx_power'], ['registered_peers', 'authorized_peers'])

        # Metrics
        self.metric_store.create_info_metric('wifi_interfaces', 'Wifi Interfaces')
        self.metric_store.create_gauge_metric('wifi_interface_registered_peers', 'Wifi interface registered peers', 'registered_peers', ['id', 'name', 'comment'])
        self.metric_store.create_gauge_metric('wifi_interface_authorized_peers', 'Wifi interface authorized peers', 'authorized_peers', ['id', 'name', 'comment'])

    def load_data(self, router_entry: 'RouterEntry'):
        wifi_interface_records = router_entry.rest_api.get('interface/wifi')

        monitor_records = []
        if wifi_interface_records:
            if_ids = ','.join([str(i.get('.id')) for i in wifi_interface_records])
            monitor_records = router_entry.rest_api.post('interface/wifi', 'monitor', {'once': True, '.id': if_ids})
            for mon_r, w_r in zip(monitor_records, wifi_interface_records):
                w_r.update(mon_r)
        self.metric_store.set_metrics(wifi_interface_records)

class WifiClientCollector(LoadingCollector):
    ''' Wireless Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'WifiClientCollector'
        self.metric_store = MetricStore(
            router_id,
            ['interface', 'ssid', 'mac_address', 'mac_vendor'],
            ['tx_rate', 'rx_rate', 'rx_signal', 'signal', 'uptime', 'rx_bytes', 'tx_bytes'],
            resolve_mac_vendor = True)

        # Metrics
        self.metric_store.create_info_metric('wifi_clients_devices', 'Registered client devices info')

        self.metric_store.create_counter_metric('wifi_clients_tx_bytes', 'Number of sent packet bytes',     'tx_bytes', ['mac_address'])
        self.metric_store.create_counter_metric('wifi_clients_rx_bytes', 'Number of received packet bytes', 'rx_bytes', ['mac_address'])

        self.metric_store.create_gauge_metric('wifi_clients_signal_strength', 'Client devices signal strength', 'signal', ['mac_address'])
        self.metric_store.create_gauge_metric('wifi_clients_uptime', 'Client devices uptime', 'uptime', ['mac_address'])
        self.metric_store.create_gauge_metric('wifi_clients_rx_rate', 'Client devices RX bitrate', 'rx_rate', ['mac_address'])
        self.metric_store.create_gauge_metric('wifi_clients_tx_rate', 'Client devices TX bitrate', 'tx_rate', ['mac_address'])

    def load_data(self, router_entry: 'RouterEntry'):
        registration_records = router_entry.rest_api.get('interface/wifi/registration-table')
        if registration_records:
            for r in registration_records:
                # Split bytes
                r['tx_bytes'], r['rx_bytes'] = str(r['bytes']).split(',')
                # Parse Uptime
                r['uptime'] = parse_timedelta(str(r['uptime']))

        self.metric_store.set_metrics(registration_records)