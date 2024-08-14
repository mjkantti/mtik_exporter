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

from collector.dhcp_collector import DHCPCollector
from collector.package_collector import PackageCollector
from collector.interface_collector import InterfaceCollector, InterfaceMonitorCollector
from collector.health_collector import HealthCollector
from collector.identity_collector import IdentityCollector
from collector.public_ip_collector import PublicIPAddressCollector
from collector.ipv6_neighbor_collector import IPv6NeighborCollector
from collector.poe_collector import POECollector
from collector.netwatch_collector import NetwatchCollector
from collector.pool_collector import PoolCollector
from collector.resource_collector import SystemResourceCollector
from collector.route_collector import RouteCollector, IPv6RouteCollector
from collector.wifi_collector import WifiCollector, WifiClientCollector
from collector.capsman_collector import CapsmanCollector
from collector.firewall_collector import FirewallFilterCollector, FirewallMangleCollector, FirewallRawCollector, IPv6FirewallFilterCollector, IPv6FirewallMangleCollector, IPv6FirewallRawCollector
from collector.user_collector import UserCollector
from collector.queue_collector import QueueTreeCollector
from collector.queue_collector import QueueSimpleCollector
from collector.wireguard_collector import WireguardCollector, WireguardPeerCollector
from collector.bridge_host_collector import BridgeHostCollector
from collector.kid_control_device_collector import KidDeviceCollector
from collector.bgp_collector import BGPCollector
from collector.arp_collector import ARPCollector

from collector.latest_version import LatestVersionCollector
from collector.internal_collector import InternalCollector

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.router_entry import RouterEntry
    from collector.metric_store import LoadingCollector


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
        'firewall_filter': FirewallFilterCollector,
        'firewall_mangle': FirewallMangleCollector,
        'firewall_raw': FirewallRawCollector,
        'ipv6_firewall_filter': IPv6FirewallFilterCollector,
        'ipv6_firewall_mangle': IPv6FirewallMangleCollector,
        'ipv6_firewall_raw': IPv6FirewallRawCollector,
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

            self.fast_collectors.append(cls(router_id))

        for key in router_entry.config_entry.slow_collectors:
            cls = self.collector_mapping.get(key)
            if not cls:
                logging.warning('Slow Collector not found: %s ignoring', key)
                continue

            self.slow_collectors.append(cls(router_id))


class SystemCollectorRegistry:
    ''' mtik_exporter Collectors Registry
    '''

    def __init__(self, system_config, keys: list[str]) -> None:
        self.system_collectors: list['LoadingCollector'] = []
        self.interval: int = system_config.system_interval
        self.interal_collector = InternalCollector(keys)

        # SYSTEM Collectors
        if system_config.check_for_updates:
            channel = system_config.check_for_updates_channel

            self.system_collectors.append(LatestVersionCollector(channel))