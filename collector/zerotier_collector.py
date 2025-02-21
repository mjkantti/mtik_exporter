# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
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

class ZeroTierInterfaceCollector(LoadingCollector):
    '''ZeroTier collector'''
    def __init__(self, router_id: dict[str, str]):
        self.name = 'ZeroTierInterfaceCollector'
        self.metric_store = MetricStore(
            router_id,
            ['instance', 'mac_address', 'mtu', 'name', 'network', 'network_name', 'status', 'allow_default', 'allow_managed', 'allow_global', 'bridge', 'type'],
            ['running'],
            {
                'running': lambda x: 1 if x == 'true' else 0
            })

        # Metrics
        self.metric_store.create_gauge_metric('zerotier_interface', 'ZeroTier Interface', 'running')

    def load_data(self, router_entry: 'RouterEntry'):
        zerotier_interface_records = router_entry.rest_api.get('zerotier/interface')
        self.metric_store.set_metrics(zerotier_interface_records)

class ZeroTierPeerCollector(LoadingCollector):
    '''ZeroTier peer collector'''
    def __init__(self, router_id: dict[str, str]):
        self.name = 'ZeroTierPeerCollector'
        self.metric_store = MetricStore(
            router_id,
            ['zt_address', 'instance', 'bonded', 'role', 'preferred_endpoint'],
            ['latency'],
            {
                'latency': parse_timedelta
            })

        # Metrics
        self.metric_store.create_gauge_metric('zerotier_peer_latency', 'ZeroTier Peer Latency', 'latency')

    def load_data(self, router_entry: 'RouterEntry'):
        # Not usable yet
        zerotier_peer_records = router_entry.rest_api.get('zerotier/peer')
        for peer in zerotier_peer_records:
            path = peer.get('path', '').split(',')
            for i, x in enumerate(path):
                if x == 'preferred':
                    peer['preferred_endpoint'] = path[i + 1]
        
        self.metric_store.set_metrics(zerotier_peer_records)

class ZeroTierControllerCollector(LoadingCollector):
    '''ZeroTier collector'''
    def __init__(self, router_id: dict[str, str]):
        self.name = 'ZeroTierControllerCollector'
        self.metric_store = MetricStore(
            router_id,
            ['authorized', 'comment', 'inactive', 'ip_address', 'name', 'network', 'zt_address'],
            ['last_seen'],
            {
                'last_seen': parse_timedelta
            })

        # Metrics
        self.metric_store.create_gauge_metric('zerotier_controller_member_last_seen', 'ZeroTier Controller Member Last Seen', 'last_seen')

    def load_data(self, router_entry: 'RouterEntry'):
        zerotier_controller_member_records = router_entry.rest_api.get('zerotier/controller/member')
        self.metric_store.set_metrics(zerotier_controller_member_records)
