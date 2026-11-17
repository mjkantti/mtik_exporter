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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.router_entry import RouterEntry

def milliamps_to_amps(value: str | None) -> float | None:
    # RouterOS reports PoE current in mA, export in SI base unit
    # On a non-numeric value return None, the raw value is kept and skipped with a warning by the metric store
    try:
        return float(value) / 1000 if value else None
    except ValueError:
        return None

class POECollector(LoadingCollector):
    ''' POE Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'POECollector'
        self.metric_store = MetricStore(
            router_id,
            ['id', 'name', 'comment', 'poe_out', 'poe_priority', 'poe_voltage', 'poe_out_status'],
            {
                'poe_out_current': milliamps_to_amps
            })

        # Metrics
        self.metric_store.create_info_metric('poe', 'POE Metrics')

        # Live readings as gauges, as labels every change would create a new series
        poe_labels = ['id', 'name', 'comment']
        self.metric_store.create_gauge_metric('poe_out_voltage', 'PoE voltage applied to the powered device in volts', 'poe_out_voltage', poe_labels)
        self.metric_store.create_gauge_metric('poe_out_current', 'PoE current drawn by the powered device in amps', 'poe_out_current', poe_labels)
        self.metric_store.create_gauge_metric('poe_out_power', 'PoE power consumption of the powered device in watts', 'poe_out_power', poe_labels)

    def load_data(self, router_entry: 'RouterEntry'):
        poe_records = router_entry.rest_api.get('interface/ethernet/poe')

        if poe_records:
            # Only monitor active ports, monitor results are returned in the same order as the requested ids
            active_records = [i for i in poe_records if i.get('running', 'true') == 'true' and i.get('disabled', 'false') == 'false']
            if_ids = ','.join([str(i.get('.id')) for i in active_records])

            if if_ids:
                monitor_records = router_entry.rest_api.post('interface/ethernet/poe', 'monitor', {'once': True, '.id': if_ids})

                for poe_r, mon_r in zip(active_records, monitor_records):
                    poe_r.update(mon_r)

        self.metric_store.set_metrics(poe_records)