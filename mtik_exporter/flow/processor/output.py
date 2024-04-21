# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
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


import re
from datetime import timedelta
from mtik_exporter.cli.config.config import config_handler

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry


class BaseOutputProcessor:
    @staticmethod
    def add_dhcp_info(router_entry: 'RouterEntry', registration_record: dict[str, str | float], key: str, id_key: str = 'mac_address') -> None:
        dhcp_name = ''
        dhcp_address = 'No DHCP Record'
        dhcp_comment = ''

        dhcp_lease_record = router_entry.dhcp_record(id_key, key)
        if dhcp_lease_record:
            dhcp_comment = dhcp_lease_record.get('comment', '')
            dhcp_name = dhcp_lease_record.get('host_name', '')
            dhcp_address = dhcp_lease_record.get('address', '')

        registration_record['dhcp_name'] = dhcp_name
        registration_record['dhcp_comment'] = dhcp_comment
        registration_record['dhcp_address'] = dhcp_address

    @staticmethod
    def parse_rates(rate: str | None) -> float:
        if rate is None:
            return 0
        rates_rgx = config_handler.re_compiled.get('rates_rgx')
        if not rates_rgx:
            rates_rgx = re.compile(r'(\d*(?:\.\d*)?)([GgMmKk]?)bps')
            config_handler.re_compiled['rates_rgx'] = rates_rgx
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

    @staticmethod
    def parse_timedelta(time: str) -> float:
        duration_interval_rgx = config_handler.re_compiled.get('duration_interval_rgx')
        if not duration_interval_rgx:
            duration_interval_rgx = re.compile(r'((?P<weeks>\d+)w)?'
                                               r'((?P<days>\d+)d)?'
                                               r'((?P<hours>\d+)h)?'
                                               r'((?P<minutes>\d+)m(?![a-z]))?' # Should not match with ms
                                               r'((?P<seconds>\d+)s)?'
                                               r'((?P<milliseconds>\d+)ms)?'
                                               r'((?P<microseconds>\d+)us)?')
            config_handler.re_compiled['duration_interval_rgx'] = duration_interval_rgx
        time_dict: dict[str, str] = {}
        try:
            match_res = duration_interval_rgx.match(time)
            if match_res:
                time_dict = match_res.groupdict()
        except Exception as e:
            print(f'Cannot parse {time}, {e}')

        return timedelta(**{key: int(value) for key, value in time_dict.items() if value}).total_seconds()

    @staticmethod
    def parse_signal_strength(signal_strength: str) -> str:
        wifi_signal_strength_rgx = config_handler.re_compiled.get('wifi_signal_strength_rgx')
        if not wifi_signal_strength_rgx:
            # wifi_signal_strength_rgx = re.compile(r'(-?\d+(?:\.\d+)?)(dBm)?')
            wifi_signal_strength_rgx = re.compile(r'(-?\d+(?:\.\d+)?)')
            config_handler.re_compiled['wifi_signal_strength_rgx'] = wifi_signal_strength_rgx
        res = wifi_signal_strength_rgx.search(signal_strength)
        if res:
            return res.group()
        return '-1'
