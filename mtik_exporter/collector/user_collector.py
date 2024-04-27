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


from mtik_exporter.collector.metric_store import MetricStore, LoadingCollector
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class UserCollector(LoadingCollector):
    '''Active Users collector'''

    def __init__(self, router_id: dict[str, str], polling_interval: int):
        self.name = 'UserCollector'
        self.metric_store = MetricStore(
            router_id,
            ['name', 'address', 'via', 'group'],
            ['when', 'count'],
            polling_interval=polling_interval
        )

        # Metrics
        self.metric_store.create_gauge_metric('active_users_last_login', 'Active Users', 'when')
        self.metric_store.create_gauge_metric('active_users_count', 'Active Users Count', 'count')

    def load(self, router_entry: 'RouterEntry'):
        #user_records = UserMetricsDataSource.metric_records(router_entry)
        self.metric_store.clear_metrics()
        user_records = router_entry.api_connection.get('user/active')

        filtered_users = {}
        for usr in user_records:
            k = f'{usr.get("name", "")}_{usr.get("address", "")}_{usr.get("via", "")}'
            t = datetime.fromisoformat(usr.get('when')).replace(tzinfo=timezone.utc).timestamp()
            u = filtered_users.get(k, {})
            #print(filtered_users)
            cnt = u.get('count', 0) + 1
            t = max(t, u.get('when', 0))

            usr.update({'when': t, 'count': cnt})
            filtered_users[k] = usr

        self.metric_store.set_metrics(filtered_users.values())

    def collect(self):
        yield from self.metric_store.get_metrics()