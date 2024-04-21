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


from mtik_exporter.collector.metric_store import MetricStore
from urllib import request, error as urlerror
from datetime import datetime, timezone

class LatestVersionCollector():
    ''' Latest RouterOS Version Collector
    '''

    def __init__(self):
        self.ms = MetricStore({}, ['version'], ['ts'], {
            'ts': lambda v: datetime.fromtimestamp(int(v), timezone.utc),
        })

    def load(self, _):
        contents_stable = ''
        contents_dev = ''

        try:
            b_contents_stable = request.urlopen("https://upgrade.mikrotik.com/routeros/NEWESTa7.stable").read()
            contents_stable = b_contents_stable.decode("utf-8")
            v_stable, ts_stable = contents_stable.split()

            b_contents_dev = request.urlopen("https://upgrade.mikrotik.com/routeros/NEWESTa7.development").read()
            contents_dev = b_contents_dev.decode("utf-8")
            v_dev, ts_dev = contents_dev.split()

            self.ms.set_metrics([
                {'channel': 'stable', 'version': v_stable, 'ts': ts_stable},
                {'channel': 'development', 'version': v_dev, 'ts': ts_dev},
            ])
        #except urlerror.URLError as e:
        #    ResponseData = e.reason
        except Exception as exc:
            print(f'Error fetching latest RouterOS Version info: {exc}')
            return None


    def collect(self):
        if self.ms.have_metrics():
            yield self.ms.info_collector('latest_routeros', 'Latest RouterOS Versions')
            yield self.ms.gauge_collector('latest_routeros_published', 'Latest RouterOS Version publish timestamp', 'ts')