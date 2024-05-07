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


from mtik_exporter.flow.processor.output import BaseOutputProcessor
from mtik_exporter.collector.metric_store import MetricStore, LoadingCollector
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class WifiCollector(LoadingCollector):
    ''' Wireless Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'WifiCollector'
        self.wifi_interface_metric_store = MetricStore(router_id, ['id', 'name', 'comment', 'configuration', 'configuration_mode', 'configuration_ssid', 'mac_address', 'master'])
        self.wifi_monitor_metric_store = MetricStore(router_id, ['id', 'name', 'comment', 'state', 'channel', 'tx_power'], ['registered_peers', 'authorized_peers'])

        # Metrics
        self.wifi_interface_metric_store.create_info_metric('wifi_interfaces', 'Wifi Interfaces')
        self.wifi_monitor_metric_store.create_info_metric('wifi_interfaces_monitor', 'Wifi Interfaces Monitor')
        self.wifi_monitor_metric_store.create_gauge_metric('wifi_interface_registered_peers', 'Wifi interface registered peers', 'registered_peers', ['id', 'name', 'comment'])
        self.wifi_monitor_metric_store.create_gauge_metric('wifi_interface_authorized_peers', 'Wifi interface authorized peers', 'authorized_peers', ['id', 'name', 'comment'])

    def load(self, router_entry: 'RouterEntry'):
        self.wifi_interface_metric_store.clear_metrics()
        self.wifi_monitor_metric_store.clear_metrics()

        wifi_interface_records = router_entry.api_connection.get('interface/wifi')
        self.wifi_interface_metric_store.set_metrics(wifi_interface_records)

        if wifi_interface_records:
            if_ids = ','.join([str(i.get('id')) for i in wifi_interface_records])
            #monitor_records = router_entry.api_connection.call('/interface/wifi', 'monitor', {'once':'', '.id': if_ids})
            #monitor_records = router_entry.rest_api.post('interface/wifi', 'monitor', {'once': True, '.id': if_ids})
            monitor_records = router_entry.api_connection.call('/interface/wifi', 'monitor', {'once':'', '.id': if_ids})
            for mon_r, w_r in zip(monitor_records, wifi_interface_records):
                mon_r.update({'id': w_r.get('id', ''), 'name': w_r.get('name', ''), 'comment': w_r.get('comment', '')})
            self.wifi_monitor_metric_store.set_metrics(monitor_records)

    def collect(self):
        yield from self.wifi_interface_metric_store.get_metrics()
        yield from self.wifi_monitor_metric_store.get_metrics()

class WifiClientCollector(LoadingCollector):
    ''' Wireless Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'WifiClientCollector'
        self.wifi_registration_metric_store = MetricStore(router_id, ['interface', 'ssid', 'mac_address', 'dhcp_name', 'dhcp_comment', 'dhcp_address'], ['tx_rate', 'rx_rate', 'rx_signal', 'signal', 'uptime', 'rx_bytes', 'tx_bytes'])

        # Metrics
        self.wifi_registration_metric_store.create_info_metric('wifi_clients_devices', 'Registered client devices info')

        self.wifi_registration_metric_store.create_counter_metric('wifi_clients_tx_bytes', 'Number of sent packet bytes',     'tx_bytes', ['mac_address', 'dhcp_name', 'dhcp_comment'])
        self.wifi_registration_metric_store.create_counter_metric('wifi_clients_rx_bytes', 'Number of received packet bytes', 'rx_bytes', ['mac_address', 'dhcp_name', 'dhcp_comment'])

        self.wifi_registration_metric_store.create_gauge_metric('wifi_clients_signal_strength', 'Client devices signal strength', 'signal', ['mac_address', 'dhcp_name', 'dhcp_comment'])
        self.wifi_registration_metric_store.create_gauge_metric('wifi_clients_uptime', 'Client devices uptime', 'uptime', ['mac_address', 'dhcp_name', 'dhcp_comment'])
        self.wifi_registration_metric_store.create_gauge_metric('wifi_clients_rx_rate', 'Client devices RX bitrate', 'rx_rate', ['mac_address', 'dhcp_name', 'dhcp_comment'])
        self.wifi_registration_metric_store.create_gauge_metric('wifi_clients_tx_rate', 'Client devices TX bitrate', 'tx_rate', ['mac_address', 'dhcp_name', 'dhcp_comment'])

    def load(self, router_entry: 'RouterEntry'):
        self.wifi_registration_metric_store.clear_metrics()

        registration_records = router_entry.api_connection.get('interface/wifi/registration-table')
        if registration_records:
            for r in registration_records:
                # Split bytes
                r['tx_bytes'], r['rx_bytes'] = str(r['bytes']).split(',')
                # Parse Uptime
                r['uptime'] = BaseOutputProcessor.parse_timedelta(str(r['uptime']))

                BaseOutputProcessor.add_dhcp_info(router_entry, r, str(r.get('mac-address')))
        self.wifi_registration_metric_store.set_metrics(registration_records)

    def collect(self):
        yield from self.wifi_registration_metric_store.get_metrics()