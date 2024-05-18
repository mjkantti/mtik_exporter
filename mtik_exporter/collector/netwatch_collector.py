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
from mtik_exporter.utils.utils import parse_timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

from datetime import datetime, timezone

class NetwatchCollector(LoadingCollector):
    ''' Netwatch Metrics collector
    '''

    def __init__(self, router_id: dict[str, str], interval: int):
        self.name = 'NetwatchCollector'
        self.metric_store = MetricStore(
            router_id,
            ['name', 'host', 'comment', 'timeout', 'interval', 'type'],
            ['since', 'status', 'loss_count', 'response_count', 'rtt_avg', 'rtt_jitter', 'rtt_max', 'rtt_min', 'rtt_stdev', 'sent_count', 'http_status_code', 'http_resp_time', 'tcp_connect_time'],
            {
                'status': lambda value: 1 if value == 'up' else 0,
                'since': lambda value: datetime.fromisoformat(value).replace(tzinfo=timezone.utc).timestamp() if value else None,
                'rtt_avg': lambda value: parse_timedelta(value) if value else None,
                'rtt_jitter': lambda value: parse_timedelta(value) if value else None,
                'rtt_max': lambda value: parse_timedelta(value) if value else None,
                'rtt_min': lambda value: parse_timedelta(value) if value else None,
                'rtt_stdev': lambda value: parse_timedelta(value) if value else None,
                'http_resp_time': lambda value: parse_timedelta(value) if value else None,
                'tcp_connect_time': lambda value: parse_timedelta(value) if value else None,
            },
            interval=interval
        )

        # Create metrics
        self.metric_store.create_gauge_metric('netwatch_status', 'Netwatch Status Metrics', 'status')
        self.metric_store.create_gauge_metric('netwatch_since', 'Netwatch Status Since Metrics', 'since')

        # ICMP
        self.metric_store.create_gauge_metric('netwatch_icmp_loss_count', 'Netwatch ICMP Loss Count', 'loss_count')
        self.metric_store.create_gauge_metric('netwatch_icmp_response_count', 'Netwatch ICMP Loss Count', 'response_count')
        self.metric_store.create_gauge_metric('netwatch_icmp_sent_count', 'Netwatch ICMP Sent Count', 'sent_count')
        self.metric_store.create_gauge_metric('netwatch_icmp_rtt_avg', 'Netwatch ICMP RTT Average', 'rtt_avg')
        self.metric_store.create_gauge_metric('netwatch_icmp_rtt_jitter', 'Netwatch ICMP RTT Jitter', 'rtt_jitter')
        self.metric_store.create_gauge_metric('netwatch_icmp_rtt_max', 'Netwatch ICMP RTT Max', 'rtt_max')
        self.metric_store.create_gauge_metric('netwatch_icmp_rtt_min', 'Netwatch ICMP RTT Min', 'rtt_min')
        self.metric_store.create_gauge_metric('netwatch_icmp_rtt_stdev', 'Netwatch ICMP RTT Standard Deviation', 'rtt_stdev')

        # HTTP(S)
        self.metric_store.create_gauge_metric('netwatch_http_status_code', 'Netwatch HTTP Status Code', 'http_status_code')
        self.metric_store.create_gauge_metric('netwatch_http_response_time', 'Netwatch HTTP Response Time', 'http_resp_time')
        self.metric_store.create_gauge_metric('tcp_connect_time', 'Netwatch HTTP TCP Connect Time', 'tcp_connect_time')

    def load(self, router_entry: 'RouterEntry'):
        nw_records = router_entry.rest_api.get('tool/netwatch', {'disabled': 'false'})
        if not nw_records:
            return

        for nw in nw_records:
            # Filter high packet loss cases
            if nw['type'] == 'icmp' and float(nw.get('loss-percent', 100)) > 40:
                [nw.pop(key, None) for key in ['rtt_avg', 'rtt_jitter', 'rtt_max', 'rtt_min', 'rtt_stdev']]

        self.metric_store.set_metrics(nw_records)