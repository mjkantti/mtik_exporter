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
        #'check_for_updates': ,
        'wireguard': WireguardCollector,
        'wireguard_peers': WireguardPeerCollector,
        'kid_control_devices': KidDeviceCollector,
        'bridge_hosts': BridgeHostCollector,
    }

    def __init__(self, router_entry: 'RouterEntry') -> None:
        self.router_entry = router_entry
        self.fast_collectors: list[LoadingCollector] = []
        self.slow_collectors: list[LoadingCollector] = []

        self.polling_interval = router_entry.config_entry.polling_interval
        self.slow_polling_interval = router_entry.config_entry.slow_polling_interval
        router_id = router_entry.router_id

        for key in router_entry.config_entry.collectors:
            print(f'GETTING: {key}')
            cls = self.collector_mapping.get(key)
            self.fast_collectors.append(cls(router_id, self.polling_interval))

        for key in router_entry.config_entry.slow_collectors:
            print(f'GETTING: {key}')
            cls = self.collector_mapping.get(key)
            self.slow_collectors.append(cls(router_id, self.slow_polling_interval))

        self.interal_collector = InternalCollector(router_id)

        #self.register(SystemResourceCollector(router_id, polling_interval))
        #self.register(HealthCollector(router_id, polling_interval))

        #if router_entry.config_entry.ipv6_neighbor:
        #    self.register(IPv6NeighborCollector(router_id, polling_interval))

        #if router_entry.config_entry.pool:
        #    self.register(PoolCollector(router_id, polling_interval))

        #if router_entry.config_entry.interface:
        #    self.register(InterfaceCollector(router_id, polling_interval, slow_polling_interval))

        #if router_entry.config_entry.firewall:
        #    self.register(FirewallCollector(router_id, polling_interval))

        #if router_entry.config_entry.ipv6_firewall:
        #    self.register(IPv6FirewallCollector(router_id, polling_interval))

        #if router_entry.config_entry.netwatch:
        #    self.register(NetwatchCollector(router_id, polling_interval))

        #if router_entry.config_entry.wifi_clients:
        #    self.register(WifiClientCollector(router_id, polling_interval))

        #if router_entry.config_entry.user:
        #    self.register(UserCollector(router_id, polling_interval))

        #if router_entry.config_entry.queue:
        #    self.register(QueueTreeCollector(router_id, polling_interval))
        #    self.register(QueueSimpleCollector(router_id, polling_interval))

        #if router_entry.config_entry.wireguard_peers:
        #    self.register(WireguardPeerCollector(router_id, polling_interval))

        #if router_entry.config_entry.kid_control_devices:
        #    self.register(KidDeviceCollector(router_id, polling_interval))

        #if router_entry.config_entry.bgp:
        #    self.register(BGPCollector(router_id, polling_interval))

        ## SLOW POLLING TARGETS            
        #self.register(IdentityCollector(router_id, slow_polling_interval))
        #if router_entry.config_entry.public_ip:
        #    self.register(PublicIPAddressCollector(router_id, slow_polling_interval))
        #if router_entry.config_entry.installed_packages:
        #    self.register(PackageCollector(router_id, slow_polling_interval))
        #if router_entry.config_entry.poe:
        #    self.register(POECollector(router_id, slow_polling_interval))
        #if router_entry.config_entry.route:
        #    self.register(RouteCollector(router_id, slow_polling_interval))
        #if router_entry.config_entry.ipv6_route:
        #    self.register(IPv6RouteCollector(router_id, slow_polling_interval))
        #if router_entry.config_entry.capsman:
        #    self.register(CapsmanCollector(router_id, slow_polling_interval))
        #if router_entry.config_entry.wireguard:
        #    self.register(WireguardCollector(router_id, slow_polling_interval))
        #if router_entry.config_entry.wifi:
        #    self.register(WifiCollector(router_id, slow_polling_interval))
        
        ## This could be very slow
        #if router_entry.config_entry.bridge_hosts:
        #    self.register(BridgeHostCollector(router_id, slow_polling_interval))


        #self.register(InternalCollector(router_id))

    def register(self, collector: 'LoadingCollector'):
        self.registered_collectors.append(collector)
