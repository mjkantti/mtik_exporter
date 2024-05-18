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

import os, sys, re
import logging

from urllib import request
from collections.abc import Iterable
from datetime import datetime, timezone, timedelta



''' Utilities / Helpers
'''
class FSHelper:
    ''' File System ops helper
    '''
    @staticmethod
    def full_path(path: str, check_parent_path = False):
        ''' Full path
        '''
        if path:
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)
            path = os.path.abspath(path)
            path = os.path.realpath(path)

        # for files, check that the parent dir exists
        if check_parent_path:
            if not os.access(os.path.dirname(path), os.W_OK):
                print('Non-valid folder path:\n\t "{}"'.format(os.path.dirname(path)))
                sys.exit(1)

        return path if path else None

class UniquePartialMatchList(list):
    ''' Enables matching elements by unique "shortcuts"
        e.g:
            >> 'Another' in UniquePartialMatchList(['A long string', 'Another longs string'])
            >> True
            >>'long' in UniquePartialMatchList(['A long string', 'Another longs string'])
            >> False
            >> l.find('Another')
            >> 'Another longs string'
    '''
    def _matched_items(self, partialMatch):
        ''' Generator expression of <matched items>, where <matched item> is
            a tuple of (<matched_element>, <is_exact_match>)
        '''
        def _contains_or_equal(item):
            if isinstance(item, Iterable):
                return (partialMatch in item)
            else:
                return (partialMatch == item)
        return ((item, (partialMatch == item)) for item in self if _contains_or_equal(item))

    def find(self, partialMatch):
        ''' Returns the element in which <partialMatch> can be found
            <partialMatch> is found if it either:
                equals to an element or is contained by exactly one element
        '''
        matched_cnt, unique_match = 0, None
        matched_items = self._matched_items(partialMatch)
        for match, exact_match in matched_items:
            if exact_match:
                # found exact match
                return match
            else:
                # found a partial match
                if not unique_match:
                    unique_match = match
                matched_cnt += 1
        return unique_match if matched_cnt == 1 else None

    def __contains__(self, partialMatch):
        ''' Check if <partialMatch> is contained by an element in the list,
            where <contained> is defined either as:
                either "equals to element" or "contained by exactly one element"
        '''
        return True if self.find(partialMatch) else False


UPDATE_BASE_URL = 'https://upgrade.mikrotik.com/routeros/NEWESTa7'

def get_available_updates(channel: str) -> tuple[str, str]:
    """Check the RSS feed for available updates for a given update channel.
    This method fetches the RSS feed and returns all version from the parsed XML.
    Version numbers are parsed into version.Version instances (part of setuptools)."""
    url = f'{UPDATE_BASE_URL}.{channel}'

    logging.info(f'Fetching available ROS releases from {url}')
    try:
        with request.urlopen(url) as response:
            result = response.read()
            contents = result.decode("utf-8")
            latest_version, build_ts = contents.split()
            return latest_version, build_ts
    except Exception as exc:
        logging.warning(f'Error fetching latest RouterOS Version info: {exc}')
        return 'N/A', ''

def parse_ros_version(ver: str) -> tuple[str, str]:
    """Parse the version returned from the /system/resource command.
    Returns a tuple: (<version>, <channel>).

    >>> parse_ros_version('1.2.3 (stable)')
    1.2.3, stable
    """
    version, channel = re.findall(r'(.+)\s[\[|\(]?([a-z]+)?[\]|\)]?', ver)[0]

    return version, channel

def parse_channel_from_version(ver: str) -> str:
    """Parse the version returned from the /system/resource command.
    Returns a tuple: (<version>, <channel>).

    >>> parse_ros_version('1.2.3 (stable)')
    stable
    """
    _, channel = re.findall(r'(.+)\s[\[|\(]?([a-z]+)?[\]|\)]?', ver)[0]

    return channel

def parse_ros_version_old(ver: str) -> tuple[str, str]:
    """Parse the version returned from the /system/resource command.
    Returns a tuple: (<version>, <channel>).

    >>> parse_ros_version('1.2.3 (stable)')
    1.2.3, stable
    """
    v1, v2, channel = re.findall(r'((?:\d+\.\d+)+)(?:[a-z]+|\.)?(\d+)?\s[\[|\(]?([a-z]+)?[\]|\)]?', ver)[0]
    version = '.'.join([v1, v2])

    return version, channel

def parse_timedelta(time: str) -> float:
    duration_interval_rgx = re.compile(r'((?P<weeks>\d+)w)?'
                                       r'((?P<days>\d+)d)?'
                                       r'((?P<hours>\d+)h)?'
                                       r'((?P<minutes>\d+)m(?![a-z]))?' # Should not match with ms
                                       r'((?P<seconds>\d+)s)?'
                                       r'((?P<milliseconds>\d+)ms)?'
                                       r'((?P<microseconds>\d+)us)?')
    time_dict: dict[str, str] = {}
    try:
        match_res = duration_interval_rgx.match(time)
        if match_res:
            time_dict = match_res.groupdict()
    except Exception as e:
        print(f'Cannot parse {time}, {e}')
        return -1

    return timedelta(**{key: int(value) for key, value in time_dict.items() if value}).total_seconds()

def parse_rates(rate: str | None) -> float:
    if rate is None:
        return 0
    
    rates_rgx = re.compile(r'(\d*(?:\.\d*)?)([GgMmKk]?)bps')
    rc = rates_rgx.search(rate)
    si_table = {
        'G': 9,
        'g': 9,
        'M': 6,
        'm': 6,
        'K': 3,
        'k': 3,
        '': -1,
    }

    return float(rc[1]) * 10 ** si_table.get(rc[2], -1) if rc and len(rc.groups()) == 2 else -1


def add_dhcp_info(registration_record: dict[str, str | float], dhcp_lease_record: dict[str, str | float] | None) -> None:
    dhcp_name = ''
    dhcp_address = 'No DHCP Record'
    dhcp_comment = ''
    dhcp_lease_type = ''

    if dhcp_lease_record:
        dhcp_comment = dhcp_lease_record.get('comment', '')
        dhcp_name = dhcp_lease_record.get('host-name', '')
        dhcp_address = dhcp_lease_record.get('address', '')
        dhcp_lease_type = 'dynamic' if dhcp_lease_record.get('dynamic') == 'true' else 'static'

    registration_record['dhcp_name'] = dhcp_name
    registration_record['dhcp_comment'] = dhcp_comment
    registration_record['dhcp_address'] = dhcp_address
    registration_record['dhcp_lease_type'] = dhcp_lease_type