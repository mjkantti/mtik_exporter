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
import os
import re

from datetime import datetime, timedelta, timezone
from ipaddress import ip_address
from urllib import request
from mac_vendor_lookup import BaseMacLookup, MacLookup, VendorNotFoundError

UPDATE_BASE_URL = 'https://upgrade.mikrotik.com/routeros/NEWESTa7'
UPDATE_TIMEOUT = 10

# RouterOS duration, e.g. 1w2d3h4m5s6ms7us
DURATION_RGX = re.compile(r'((?P<weeks>\d+)w)?'
                          r'((?P<days>\d+)d)?'
                          r'((?P<hours>\d+)h)?'
                          r'((?P<minutes>\d+)m(?![a-z]))?' # Should not match with ms
                          r'((?P<seconds>\d+)s)?'
                          r'((?P<milliseconds>\d+)ms)?'
                          r'((?P<microseconds>\d+)us)?')

# RouterOS rate, e.g. 2.5Gbps, and the power of ten for each unit prefix
RATE_RGX = re.compile(r'(\d*(?:\.\d*)?)([GgMmKk]?)bps')
RATE_SI_EXPONENTS = {
    'G': 9,
    'g': 9,
    'M': 6,
    'm': 6,
    'K': 3,
    'k': 3,
    '': 0,
}

# MAC vendor list location, the Docker image sets this so the list downloaded at build time is used at runtime
if os.environ.get('MAC_VENDORS_CACHE'):
    BaseMacLookup.cache_path = os.environ['MAC_VENDORS_CACHE']
mac_lookup = MacLookup()

def get_available_updates(channel: str) -> tuple[str, str]:
    """Check the RSS feed for available updates for a given update channel.
    This method fetches the RSS feed and returns all version from the parsed XML.
    Version numbers are parsed into version.Version instances (part of setuptools)."""
    url = f'{UPDATE_BASE_URL}.{channel}'

    logging.info(f'Fetching available ROS releases from {url}')
    try:
        with request.urlopen(url, timeout=UPDATE_TIMEOUT) as response:
            result = response.read()
            contents = result.decode("utf-8")
            latest_version, build_ts = contents.split()
            return latest_version, build_ts
    except Exception as exc:
        logging.warning(f'Error fetching latest RouterOS Version info: {exc}')
        return 'N/A', ''

def parse_timedelta(time: str) -> float | None:
    if not time:
        return None

    time_dict: dict[str, str] = {}
    try:
        match_res = DURATION_RGX.match(time)
        if match_res:
            time_dict = match_res.groupdict()
    except Exception as e:
        print(f'Cannot parse {time}, {e}')
        return -1

    return timedelta(**{key: int(value) for key, value in time_dict.items() if value}).total_seconds()

def parse_datetime(dt: str) -> float | None:
    if not dt:
        return None

    try:
        dtime = datetime.fromisoformat(dt)
        if not dtime.tzinfo:
            dtime = dtime.replace(tzinfo=timezone.utc)

        return dtime.timestamp()
    except Exception as e:
        print(f'Cannot parse datetime {dt}, {e}')
        return -1

def parse_rates(rate: str | None) -> float:
    if rate is None:
        return 0
    
    rc = RATE_RGX.search(rate)

    return float(rc[1]) * 10 ** RATE_SI_EXPONENTS.get(rc[2], -1) if rc and len(rc.groups()) == 2 else -1

def get_mac_vendor(mac: str) -> str:
    if not mac:
        return ''

    try:
        return mac_lookup.lookup(mac)
    except VendorNotFoundError:
        return ''
    except Exception as exc:
        # Malformed MAC or vendor list not available, do not fail the whole collector load
        logging.warning('MAC vendor lookup failed for %s: %s', mac, exc)
        return ''

def ip4_to_hex(ip_str):
    # Converts IPv4 to an 8-character zero-padded hex string (e.g., "10.3.3.3" -> "0a030303")
    # Anything that is not an address (empty, pool name) returns an empty string instead of failing the whole load
    try:
        return f'{int(ip_address(ip_str)):08x}'
    except ValueError:
        return ''