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


from collector.metric_store import MetricStore, LoadingCollector
from utils.utils import get_available_updates

class LatestVersionCollector(LoadingCollector):
    ''' Latest RouterOS Version Collector
    '''

    def __init__(self, channels: list[str]):
        self.name = 'LatestVersionCollector'
        self.channels = channels
        self.metric_store = MetricStore({}, ['channel', 'latest_version'])

        self.metric_store.create_info_metric('system_latest_version', 'Latest RouterOS version available')
        self.metric_store.create_gauge_metric('system_latest_version_built', 'Latest RouterOS version built time', 'latest_built')

    def load_data(self, _):
        recs = []
        for c in self.channels:
            latest_version_rec = {}
            latest_version_rec['channel'] = c

            newest, built = get_available_updates(c)
            latest_version_rec['latest_version'] = newest
            latest_version_rec['latest_built'] = built
            recs.append(latest_version_rec)

        self.metric_store.set_metrics(recs)