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
from utils.utils import parse_timedelta, parse_datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.router_entry import RouterEntry

class NetwatchCollector(LoadingCollector):
    ''' Netwatch Metrics collector
    '''

    def __init__(self, router_id: dict[str, str]):
        self.name = 'NetwatchCollector'
        self.metric_store = MetricStore(
            router_id,
            ['name', 'host', 'comment', 'timeout', 'interval', 'type'],
            ['since', 'status', 'loss_count', 'response_count', 'rtt_avg', 'rtt_jitter', 'rtt_max', 'rtt_min', 'rtt_stdev', 'sent_count', 'http_status_code', 'http_resp_time', 'tcp_connect_time'],
            {
                'since': parse_datetime,
                'rtt_avg': parse_timedelta,
                'rtt_jitter': parse_timedelta,
                'rtt_max': parse_timedelta,
                'rtt_min': parse_timedelta,
                'rtt_stdev': parse_timedelta,
                'http_resp_time': parse_timedelta,
                'tcp_connect_time': parse_timedelta,
                'status': lambda value: 1 if value == 'up' else 0
            })

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

    def load_data(self, router_entry: 'RouterEntry'):
        nw_records = router_entry.rest_api.get('tool/netwatch', {'disabled': 'false'})
        if not nw_records:
            return

        for nw in nw_records:
            # Filter high packet loss cases
            if nw['type'] == 'icmp' and float(nw.get('loss-percent', 100)) > 40:
                for k in ['rtt-avg', 'rtt-jitter', 'rtt-max', 'rtt-min', 'rtt-stdev']:
                    nw.pop(k, None)

        self.metric_store.set_metrics(nw_records)