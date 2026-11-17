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
system:
  # Address and port the metrics HTTP server listens on, "::" listens on all interfaces (IPv4 and IPv6)
  export_address: "::"
  export_port: 49090

  # Debug logging, same as the --debug command line flag
  debug_mode: False

  check_for_updates: True
  check_for_updates_channel:
    - development
    - stable
  # How often collectors running on the exporter host (not on the router) are polled, e.g. the update check
  system_polling_interval: 3600
```

##### Router(s)
```
Sample-Router:
  enabled: False

  hostname: localhost
  # Port of the router's REST API (www or www-ssl service), leave out to use the default port (80, or 443 with use_tls)
  # host_port: 8080

  username: username
  password: password

  use_tls: False
  no_ssl_certificate: False
  ssl_certificate_verify: False

  # Seconds to wait for the router to connect or respond before giving up
  request_timeout: 2

  polling_interval: 10
  slow_polling_interval: 60

  collectors:
    - dhcp
    - system_resource
    - health
    - interface
    - firewall_filter
    - firewall_mangle
    - ipv6_firewall_filter
    - ipv6_firewall_mangle
    - ipv6_neighbor
    - wifi_clients
    - netwatch
    - arp
    - user
    - queue_simple
    - queue_tree
    - wireguard_peers

  slow_collectors:
    - route
    - ipv6_route
    - installed_packages
    - interface_monitor
    - capsman
    - identity
    - wifi
    - public_ip
    - wireguard
```
**NOTE:** TLS support is not fully implemented. `use_tls` switches the connection to https, but `no_ssl_certificate` and `ssl_certificate_verify` are not implemented and have no effect. The certificate is always verified, so https only works if the router has a certificate trusted by the exporter host (a self-signed certificate will fail).

##### Collectors
Metrics are collected in two intervals, (which can be same), polling_interval and slow_polling_interval, default values for these are 10 seconds and 60 seconds.

Any collector key can be listed under either `collectors` (polled every `polling_interval`) or `slow_collectors` (polled every `slow_polling_interval`). The split in the sample configuration is only a suggestion, put rarely changing data in the slow group.
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

`containers` - Containers and their running state

`kid_control_devices` - Kid Control Devices, traffic and rates

`zerotier` - ZeroTier Interfaces

`zerotier_peers` - ZeroTier Peers and latency

`zerotier_controller` - ZeroTier Controller Members

`bridge_hosts` - MAC Table. **WARNING:** this can be very slow (takes up to 5 seconds on some devices), not recommended if it takes that long. All routers and collectors are loaded one at a time, so while this loads every other collector waits and their data is delayed.

#### Installation
- from Docker Registry
```
❯ podman pull quay.io/mjkantti/mtik_exporter
❯ podman run --rm -it -p 49090:49090 -v {path_to_config_file}:/mtik_exporter/config/config.yml mtik_exporter
```
- from sources

```
❯ git clone https://github.com/mjkantti/mtik_exporter
❯ podman build --tag=mtik_exporter_img .
❯ podman run --rm -it -p 49090:49090 -v {path_to_config_file}:/mtik_exporter/config/config.yml mtik_exporter_img
```
