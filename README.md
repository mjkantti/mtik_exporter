## Description
Yet Another Mikrotik Prometheus Exporter

Fork (at places a rewrite) of https://github.com/akpw/mktxp

#### Main differences with https://github.com/akpw/mktxp
- Compatibility with older RouterOS versions removed (>=7.16 strongly adviced)
- Uses REST Api to fetch metrics from the router
- Added various metric  endpoints (Wireguard etc.), removed some (Connections)
- Fetching metrics and scraping are done asyncronously (scrape does not trigger metric fetching)

#### Configuration
TODO!

#### Installation
- from sources

```
❯ git clone https://github.com/mjkantti/mtik_exporter
❯ podman build --tag=mtik_exporter_img .
❯ podman run --rm -it -p 49090:49090 -v {path_to_config_file}:/mtik_exporter/config/config.ini mtik_exporter_img
```
