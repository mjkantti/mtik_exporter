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


from prometheus_client.context_managers import Timer
from prometheus_client.core import Gauge, Counter
from typing import TYPE_CHECKING


class InternalCollector():
    ''' System Identity Metrics collector
    '''

    def __init__(self, label_names):
        self.name = 'InternalCollector'
        labels = label_names
        self.load_time = Counter(f'mtik_exporter_data_load_time', 'Total time spent loading metrics in seconds', labelnames=labels)
        self.load_count = Counter(f'mtik_exporter_data_load_count', 'Total count of metrics loads since reboot', labelnames=labels)
        self.load_last_run = Gauge(f'mtik_exporter_data_load_last_run', 'Last run timestamp of metrics load', labelnames=labels)
        self.load_exceptions = Counter(f'mtik_exporter_data_load_errors', 'Data Load Error Count', labelnames=labels)

    def time(self, labelvalues):
        return Timer(self.load_time.labels(**labelvalues), 'inc')

    def count_exceptions(self, labelvalues):
        return self.load_exceptions.labels(**labelvalues).count_exceptions()

    def set_last_run(self, labelvalues):
        return self.load_last_run.labels(**labelvalues).set_to_current_time()

    def inc_load_count(self, labelvalues):
        return self.load_count.labels(**labelvalues).inc()