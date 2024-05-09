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

from collections import namedtuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class IPConnectionDatasource:
    ''' IP connections data provider
    '''
    @staticmethod
    def metric_records(router_entry: 'RouterEntry') -> list[dict[str, str | float]]:
        try:
            answer = router_entry.api_connection.router_api().get_binary_resource('/ip/firewall/connection/').call('print', {'count-only': b''})
            # answer looks and feels like an empty list: [], but it has a special attribute `done_message`
            done_message = answer.done_message
            # `done_msg` is a dict with the return code as a key - which is the count that we are looking for
            cnt = done_message['ret'].decode()
            records = [{'count': cnt}]
            return records
        except Exception as exc:
            print(f'Error getting IP connection info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return []


class IPConnectionStatsDatasource:
    ''' IP connections stats data provider
    '''
    @staticmethod
    def metric_records(router_entry: 'RouterEntry') -> list[dict[str, str | float]]:
        try:
            connection_records = router_entry.api_connection.router_api().get_resource('/ip/firewall/connection/').call('print', {'proplist':'src-address,dst-address,protocol'})
             # calculate number of connections per src-address
            connections_per_src_address = {}
            for connection_record in connection_records:
                #address, port = (connection_record['src-address'].split(':') + [None])[:2]
                address = connection_record['src-address'].split(':')[0]
                destination = f"{connection_record.get('dst-address')}({connection_record.get('protocol')})"

                count, destinations = 0, set()
                if connections_per_src_address.get(address):
                    count, destinations = connections_per_src_address[address]
                count += 1
                destinations.add(destination)
                connections_per_src_address[address] = ConnStatsEntry(count, destinations)

            # compile connections-per-interface records
            records = []
            for key, entry in connections_per_src_address.items():
                record = {'src_address': key, 'connection_count': entry.count, 'dst_addresses': ', '.join(entry.destinations)}
                records.append(record)
            return records
        except Exception as exc:
            print(f'Error getting IP connection stats info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return []


ConnStatsEntry = namedtuple('ConnStatsEntry', ['count', 'destinations'])