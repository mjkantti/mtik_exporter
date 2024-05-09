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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class InterfaceCollector(LoadingCollector):
    ''' Router Interface Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'InterfaceCollector'
        self.interface_metric_store = MetricStore(
            router_id,
            ['id', 'name', 'comment', 'type', 'mtu', 'mac_address', 'running'],
            ['rx_byte', 'tx_byte', 'rx_packet', 'tx_packet', 'rx_error', 'tx_error', 'rx_drop', 'tx_drop', 'link_downs']
        )

        # Metrics
        self.interface_metric_store.create_counter_metric('interface_rx_byte', 'Number of received bytes', 'rx_byte')
        self.interface_metric_store.create_counter_metric('interface_tx_byte', 'Number of transmitted bytes', 'tx_byte')

        self.interface_metric_store.create_counter_metric('interface_rx_packet', 'Number of packets received', 'rx_packet')
        self.interface_metric_store.create_counter_metric('interface_tx_packet', 'Number of transmitted packets', 'tx_packet')

        self.interface_metric_store.create_counter_metric('interface_rx_error', 'Number of packets received with an error', 'rx_error')
        self.interface_metric_store.create_counter_metric('interface_tx_error', 'Number of packets transmitted with an error', 'tx_error')

        self.interface_metric_store.create_counter_metric('interface_rx_drop', 'Number of received packets being dropped', 'rx_drop')
        self.interface_metric_store.create_counter_metric('interface_tx_drop', 'Number of transmitted packets being dropped', 'tx_drop')

        self.interface_metric_store.create_counter_metric('link_downs', 'Number of times link went down', 'link_downs')

    def load(self, router_entry: 'RouterEntry'):
        self.interface_metric_store.clear_metrics()
        #interface_traffic_records = InterfaceTrafficMetricsDataSource.metric_records(router_entry)
        #interface_traffic_records = router_entry.api_connection.get('/interface')
        interface_traffic_records = router_entry.api_connection.get('interface')

        interface_traffic_records_running = [ift for ift in interface_traffic_records if ift['running'] == 'true']
        self.interface_metric_store.set_metrics(interface_traffic_records_running)

    def collect(self):
        yield from self.interface_metric_store.get_metrics()

class InterfaceMonitorCollector(LoadingCollector):
    ''' Router Interface Monitor Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'InterfaceMonitorCollector'
        self.interface_monitor_metric_store = MetricStore(
            router_id,
            ['id', 'name', 'comment'],
            ['full_duplex', 'status', 'rate', 'sfp_temperature'],
            {
                'status': lambda value: '1' if value=='link-ok' else '0',
                'rate': BaseOutputProcessor.parse_rates,
                'full_duplex': lambda value: '1' if value=='true' else (None if value is None else '0'),
                'sfp_temperature': lambda value: None if value is None else value
            }
        )

        self.interface_monitor_metric_store.create_gauge_metric('interface_status', 'Current interface link status', 'status')
        self.interface_monitor_metric_store.create_gauge_metric('interface_rate', 'Actual interface connection data rate', 'rate')

        self.interface_monitor_metric_store.create_gauge_metric('interface_full_duplex', 'Full duplex data transmission', 'full_duplex')

        self.interface_monitor_metric_store.create_gauge_metric('interface_sfp_temperature', 'Current SFP temperature', 'sfp_temperature')

    def load(self, router_entry: 'RouterEntry'):
        self.interface_monitor_metric_store.clear_metrics()
        #interface_traffic_records = InterfaceTrafficMetricsDataSource.metric_records(router_entry)
        #interface_traffic_records = router_entry.api_connection.get('/interface')
        interface_traffic_records = router_entry.api_connection.call('interface/ether','print', {'proplist':'.id,name,comment,running'} )

        if interface_traffic_records:
            monitor_records = []
            if_ids = []
            for ifc in interface_traffic_records:
                if ifc.get('running', 'true') == 'false' or ifc.get('disabled', 'false') == 'true':
                    monitor_records.append({ 'id': ifc.get('id', ''), 'name': ifc.get('name', ''), 'comment': ifc.get('comment', ''), 'status': 'link-down' })
                else:
                    if_ids.append({'id': str(ifc.get('id')), 'name': str(ifc.get('name')), 'comment': str(ifc.get('comment'))})

            #monitor_records_running = InterfaceMonitorMetricsDataSource.metric_records(router_entry, if_ids)
            id_str = ','.join([i.get('id') for i in if_ids])
            #monitor_records_running = router_entry.api_connection.call('/interface/ether', 'monitor', {'once':'', '.id': id_str})
            #monitor_records_running = router_entry.rest_api.post('interface/ether', 'monitor', {'once': True, '.id': id_str})
            monitor_records_running = router_entry.api_connection.call('/interface/ether', 'monitor', {'once':'', '.id': id_str})
            for if_info, mr in zip(if_ids, monitor_records_running):
                if_info.update(mr)
                monitor_records.append(if_info)

            self.interface_monitor_metric_store.set_metrics(monitor_records)

    def collect(self):
        yield from self.interface_monitor_metric_store.get_metrics()