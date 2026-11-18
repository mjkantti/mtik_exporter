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


class LTECollector(LoadingCollector):
    ''' Router LTE Metrics collector
    '''
    key, name = 'lte', 'LTECollector'

    def __init__(self, router_id: dict[str, str]):
        self.metric_store = MetricStore(
            router_id,
            ['id', 'name', 'comment', 'current_operator', 'data_class', 'status'],
            {
                'session_uptime': parse_timedelta,
            })

        self.metric_store.create_info_metric('lte', 'LTE Link Info')

        self.metric_store.create_gauge_metric('lte_uptime', 'LTE Link Uptime', 'session_uptime', ['id', 'name', 'comment'])
        self.metric_store.create_gauge_metric('lte_rsrp', 'LTE Link RSRP', 'rsrp', ['id', 'name', 'comment'])
        self.metric_store.create_gauge_metric('lte_rsrq', 'LTE Link RSRQ', 'rsrq', ['id', 'name', 'comment'])
        self.metric_store.create_gauge_metric('lte_rssi', 'LTE Link RSSI', 'rssi', ['id', 'name', 'comment'])
        self.metric_store.create_gauge_metric('lte_sinr', 'LTE Link SINR', 'sinr', ['id', 'name', 'comment'])

    def load_data(self, router_entry: 'RouterEntry'):
        interface_lte_records = router_entry.rest_api.get('interface/lte', {'.proplist':'.id,name,comment,running'})

        if interface_lte_records:
            monitor_records = []
            if_ids = []
            for ifc in interface_lte_records:
                # Same labels for up and down interfaces, so the series identity does not change with link state
                if_info = {'id': str(ifc.get('.id', '')), 'name': str(ifc.get('name', '')), 'comment': str(ifc.get('comment', ''))}
                if ifc.get('running', 'true') == 'false' or ifc.get('disabled', 'false') == 'true':
                    if_info['status'] = 'link-down'
                    monitor_records.append(if_info)
                else:
                    if_ids.append(if_info)

            id_str = ','.join([i.get('id') for i in if_ids if i])
            if id_str:
                monitor_records_running = router_entry.rest_api.post('interface/lte', 'monitor', data = {'once': True, '.id': id_str})
                for if_info, mr in zip(if_ids, monitor_records_running):
                    if_info.update(mr)
                    monitor_records.append(if_info)

            self.metric_store.set_metrics(monitor_records)