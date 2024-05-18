# coding=utf8
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

class WireguardCollector(LoadingCollector):
    '''Wireguard collector'''

    def __init__(self, router_id: dict[str, str], interval: int):
        self.name = 'WireguardCollector'
        self.metric_store = MetricStore(router_id, ['name', 'mtu', 'listen_port', 'public_key', 'comment', 'running'], interval=interval)

        # Metrics
        self.metric_store.create_info_metric('wireguard_interfaces', 'Wireguard Interfaces')

    def load(self, router_entry: 'RouterEntry'):
        recs = router_entry.rest_api.get('interface/wireguard')
        self.metric_store.set_metrics(recs)


class WireguardPeerCollector(LoadingCollector):
    '''Wireguard collector'''

    def __init__(self, router_id: dict[str, str], interval: int):
        self.name = 'WireguardPeerCollector'
        self.metric_store = MetricStore(
            router_id,
            ['name', 'interface', 'public_key', 'endpoint_address', 'endpoint_port', 'current_endpoint_address', 'current_endpoint_port', 'allowed_address', 'comment'],
            ['tx', 'rx', 'last_handshake'],
            {
                'last_handshake': lambda c: parse_timedelta(c) if c else 0
            },
            interval=interval
        )

        # Metrics
        self.metric_store.create_info_metric('wireguard_peer', 'Wireguard Peer Info')

        wg_peer_labels = ['interface', 'name', 'comment']
        self.metric_store.create_gauge_metric('wireguard_peer_last_handshake', 'Wireguard Peer Last Handshake', 'last_handshake', wg_peer_labels)
        self.metric_store.create_counter_metric('wireguard_peer_tx_bytes', 'Wireguard Peer TX Bytes', 'tx', wg_peer_labels)
        self.metric_store.create_counter_metric('wireguard_peer_rx_bytes', 'Wireguard Peer RX Bytes', 'rx', wg_peer_labels)

    def load(self, router_entry: 'RouterEntry'):
        recs = router_entry.rest_api.get('interface/wireguard/peers')
        self.metric_store.set_metrics(recs)