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

    def __init__(self, router_id: dict[str, str], interval: int):
        self.name = 'UserCollector'
        self.metric_store = MetricStore(
            router_id,
            ['name', 'address', 'via', 'group'],
            ['when'],
            {
                'when': lambda w: datetime.fromisoformat(w).replace(tzinfo=timezone.utc).timestamp()
            },
            interval=interval
        )

        # Metrics
        self.metric_store.create_gauge_metric('active_users_last_login', 'Active Users', 'when')
        self.metric_store.create_gauge_metric('active_users_count', 'Active Users Count', 'count')

    def load(self, router_entry: 'RouterEntry'):
        user_records = router_entry.rest_api.get('user/active')
        self.metric_store.set_metrics(user_records)