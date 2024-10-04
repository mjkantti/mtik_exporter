## Description
Yet Another Mikrotik Prometheus Exporter

Fork (at places a rewrite) of https://github.com/akpw/mktxp

#### Main differences with https://github.com/akpw/mktxp
- Compatibility with older RouterOS versions removed (>7.16 strongly adviced)
- Uses REST Api to fetch metrics from the router
- Added various metric  endpoints (Wireguard etc.), removed some (Connections)
- Fetching metrics and scraping are done asyncronously (scrape does not trigger metric fetching)
