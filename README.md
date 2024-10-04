## Description
Yet Another Mikrotik Prometheus Exporter

Fork (at places a rewrite) of https://github.com/akpw/mktxp

#### Main differences with https://github.com/akpw/mktxp
- Compatibility with older RouterOS versions removed (>=7.16 strongly adviced)
- Uses REST Api to fetch metrics from the router
- Added various metric  endpoints (Wireguard etc.), removed some (Connections)
- Fetching metrics and scraping are done asyncronously (scrape does not trigger metric fetching)

#### Configuration
##### Router Side Configuration
To work, mtik_exporter needs three permissions on a Mikrotik device `read`, `api` and `rest-api`.
```
> /user/group/print
...
3 name="metric_collecting" policy=read,api,rest-api,!local,!telnet,!ssh,!ftp,!reboot,!write,
       !policy,!test,!winbox,!password,!web,!sniff,!sensitive,!romon 
   skin=default 
```
To Create
```
/user/group add name=metric_collecting policy=api,read,rest-api
/user/add name=collector group=metric_collecting password={password}
```

##### System
```
[SYSTEM]
    port = 49090
    socket_timeout = 10

    initial_delay_on_failure = 120
    max_delay_on_failure = 900
    delay_inc_div = 5

    verbose_mode = False

    check_for_updates = True
    check_for_updates_channel = ["development", "stable"]
    check_for_updates_interval = 3600
```

##### Router(s)
```
[Sample-Router]
    enabled = False

    hostname = localhost

    username = username
    password = password

    use_ssl = False
    no_ssl_certificate = False
    ssl_certificate_verify = False

    polling_interval = 10
    slow_polling_interval = 60

    collectors = [
        "dhcp",
        "system_resource",
        "health",
        "interface",
        "firewall_filter",
        "firewall_mangle",
        "ipv6_firewall_filter",
        "ipv6_firewall_mangle",
        "ipv6_neighbor",
        "wifi_clients",
        "netwatch",
        "arp",
        "user",
        "queue_simple",
        "queue_tree",
        "wireguard_peers"
        ]

    slow_collectors = [
        "route",
        "ipv6_route",
        "installed_packages",
        "interface_monitor",
        "capsman",
        "identity",
        "wifi",
        "public_ip",
        "wireguard"
        ]
```
##### Collectors
Metrics are collected in two intervals, (which can be same), polling_interval and slow_polling_interval, default values for these are 10 seconds and 60 seconds.
##### Collector Keys
`dhcp` - DHCP Info

`system_resource` - System Resources, CPU, Memory ETC.

`health` - Device Health Info

`interface` - Interfaces Info

`interface_monitor` - Interface Monitoring Metrics, link speed etc.

`firewall_filter` - Firewall Filter Info

`firewall_mangle` - Firewall Mangle info

`firewall_raw` - Firewall Raw Info

`ipv6_firewall_filter` 

`ipv6_firewall_mangle`

`ipv6_firewall_raw`

`ipv6_neighbor` - IPv6 Neighbors

`wifi` - Wifi Interfaces

`wifi_clients` - Wifi Clients

`netwatch` - Netwatch

`arp` - ARP Table

`user` - Users

`queue_simple` - Simple Queues

`queue_tree` - Tree Queues

`wireguard` - Wireguard interfaces

`wireguard_peers` - WG Peers

`route` - Routes

`ipv6_route` - IPv6 Routes

`installed_packages` - Installed Packages and versions

`capsman` - CapsMan

`identity` - Identity

`public_ip` - Public IP (/ip/cloud)

`pool` - IP Pool

`poe` - PoE Metrics

`bgp` - BGP Metrics

`lte` - LTE Interface Metrics

`bridge_hosts` - MAC Table, NOTE this is very slow (takes up to 5 seconds on my devices)

#### Installation
- from sources

```
❯ git clone https://github.com/mjkantti/mtik_exporter
❯ podman build --tag=mtik_exporter_img .
❯ podman run --rm -it -p 49090:49090 -v {path_to_config_file}:/mtik_exporter/config/config.ini mtik_exporter_img
```
