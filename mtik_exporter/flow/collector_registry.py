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

import logging

from mtik_exporter.cli.config.config import config_handler

from mtik_exporter.collector.dhcp_collector import DHCPCollector
from mtik_exporter.collector.package_collector import PackageCollector
from mtik_exporter.collector.interface_collector import InterfaceCollector, InterfaceMonitorCollector
from mtik_exporter.collector.health_collector import HealthCollector
from mtik_exporter.collector.identity_collector import IdentityCollector
from mtik_exporter.collector.public_ip_collector import PublicIPAddressCollector
from mtik_exporter.collector.ipv6_neighbor_collector import IPv6NeighborCollector
from mtik_exporter.collector.poe_collector import POECollector
from mtik_exporter.collector.netwatch_collector import NetwatchCollector
from mtik_exporter.collector.pool_collector import PoolCollector
from mtik_exporter.collector.resource_collector import SystemResourceCollector
from mtik_exporter.collector.route_collector import RouteCollector, IPv6RouteCollector
from mtik_exporter.collector.wifi_collector import WifiCollector, WifiClientCollector
from mtik_exporter.collector.capsman_collector import CapsmanCollector
from mtik_exporter.collector.firewall_collector import FirewallCollector, IPv6FirewallCollector
from mtik_exporter.collector.user_collector import UserCollector
from mtik_exporter.collector.queue_collector import QueueTreeCollector
from mtik_exporter.collector.queue_collector import QueueSimpleCollector
from mtik_exporter.collector.wireguard_collector import WireguardCollector, WireguardPeerCollector
from mtik_exporter.collector.bridge_host_collector import BridgeHostCollector
from mtik_exporter.collector.kid_control_device_collector import KidDeviceCollector
from mtik_exporter.collector.bgp_collector import BGPCollector
from mtik_exporter.collector.arp_collector import ARPCollector

from mtik_exporter.collector.latest_version import LatestVersionCollector
from mtik_exporter.collector.internal_collector import InternalCollector

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry
    from mtik_exporter.collector.metric_store import LoadingCollector


class CollectorRegistry:
    ''' mtik_exporter Collectors Registry
    '''
    collector_mapping = {
        'installed_packages': PackageCollector,
        'dhcp': DHCPCollector,
        'system_resource': SystemResourceCollector,
        'health': HealthCollector, 
        'pool': PoolCollector,
        'interface': InterfaceCollector,
        'identity': IdentityCollector,
        'interface_monitor': InterfaceMonitorCollector,
        'firewall': FirewallCollector,
        'ipv6_firewall': IPv6FirewallCollector,
        'ipv6_neighbor': IPv6NeighborCollector,
        'route': RouteCollector,
        'ipv6_route': IPv6RouteCollector,
        'capsman': CapsmanCollector,
        'wifi': WifiCollector,
        'wifi_clients': WifiClientCollector,
        'poe': POECollector,
        'public_ip': PublicIPAddressCollector,
        'netwatch': NetwatchCollector,
        'user': UserCollector,
        'queue_simple': QueueSimpleCollector,
        'queue_tree': QueueTreeCollector,
        'bgp': BGPCollector,
        'arp': ARPCollector,
        'wireguard': WireguardCollector,
        'wireguard_peers': WireguardPeerCollector,
        'kid_control_devices': KidDeviceCollector,
        'bridge_hosts': BridgeHostCollector,
    }

    def __init__(self, router_entry: 'RouterEntry') -> None:
        self.router_entry = router_entry
        self.polling_interval = router_entry.config_entry.polling_interval
        self.slow_polling_interval = router_entry.config_entry.slow_polling_interval

        router_id = router_entry.router_id
        self.fast_collectors: list[LoadingCollector] = []
        self.slow_collectors: list[LoadingCollector] = []

        for key in router_entry.config_entry.collectors:
            cls = self.collector_mapping.get(key)
            if not cls:
                logging.warning('Fast Collector not found: %s ignoring', key)
                continue

            self.fast_collectors.append(cls(router_id, self.polling_interval))

        for key in router_entry.config_entry.slow_collectors:
            cls = self.collector_mapping.get(key)
            if not cls:
                logging.warning('Slow Collector not found: %s ignoring', key)
                continue

            self.slow_collectors.append(cls(router_id, self.slow_polling_interval))


class SystemCollectorRegistry:
    ''' mtik_exporter Collectors Registry
    '''

    def __init__(self) -> None:
        self.system_collectors: list['LoadingCollector'] = []
        self.interal_collector = InternalCollector()

        # SYSTEM Collectors
        if config_handler.system_entry().check_for_updates:
            interval = config_handler.system_entry().check_for_updates_interval
            channel = config_handler.system_entry().check_for_updates_channel

            self.system_collectors.append(LatestVersionCollector(channel, interval))