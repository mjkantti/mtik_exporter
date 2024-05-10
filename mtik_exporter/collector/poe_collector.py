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

class POECollector(LoadingCollector):
    ''' POE Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'POECollector'
        self.metric_store = MetricStore(router_id, ['id', 'name', 'comment', 'poe_out', 'poe_priority', 'poe_voltage', 'poe_out_status', 'poe_out_voltage', 'poe_out_current', 'poe_out_power'])

        # Metrics
        self.metric_store.create_info_metric('poe', 'POE Metrics')

    def load(self, router_entry: 'RouterEntry'):
        poe_records = router_entry.api_connection.get('interface/ethernet/poe')

        if poe_records:
            if_ids = ','.join([str(i.get('id')) for i in poe_records if i.get('running', 'true') == 'true' and i.get('disabled', 'false') == 'false'])

            if if_ids:
                #monitor_records = InterfaceMonitorMetricsDataSource.metric_records(router_entry, if_ids, kind='ethernet/poe')
                monitor_records = router_entry.api_connection.call('/interface/ethernet/poe', 'monitor', {'once':'', '.id': if_ids})
                #monitor_records = router_entry.rest_api.post('interface/ethernet/poe', 'monitor', {'once': True, '.id': if_ids})

                for poe_r, mon_r in zip(poe_records, monitor_records):
                    poe_r.update(mon_r)


        self.metric_store.set_metrics(poe_records)

    def collect(self):
        yield from self.metric_store.get_metrics()