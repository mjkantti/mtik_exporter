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

from abc import abstractmethod
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, InfoMetricFamily, Metric
from prometheus_client.registry import Collector
from collections.abc import Callable
from time import time

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.flow.router_entry import RouterEntry

class MetricStore():
    ''' Base Collector methods
        For use by custom collector
    '''
    def __init__(self, router_id: dict[str, str],
                 metric_labels: list[str],
                 metric_values: list[str] = [],
                 translation_table: dict[str, Callable[[str | None], str | float | None]]={},
                 interval: int = 0):
        self.router_id = router_id
        self.ts: float = 0
        self.metric_labels = self.add_router_labels(metric_labels)
        self.metric_values = metric_values
        self.translation_table = translation_table
        self.interval = interval

        self.metrics: list[tuple[Metric, list[str], str | None]] = []

    def create_info_metric(self, name: str, decription: str):
        self.metrics.append((InfoMetricFamily(f'mtik_exporter_{name}', decription, labels=self.metric_labels), self.metric_labels, None))

    def create_gauge_metric(self, name: str, decription: str, value: str, labels = []):
        labels = self.add_router_labels(labels) if labels else self.metric_labels
        self.metrics.append((GaugeMetricFamily(f'mtik_exporter_{name}', decription, labels=labels), labels, value))

    def create_counter_metric(self, name: str, decription: str, value: str, labels = []):
        labels = self.add_router_labels(labels) if labels else self.metric_labels
        self.metrics.append((CounterMetricFamily(f'mtik_exporter_{name}', decription, labels=labels), labels, value))

    def get_metrics(self):
        lag = time() - self.ts
        if lag > self.interval * 1.5:
            metric_names = [m[0].name for m in self.metrics]
            logging.warn('Metrics too old to show for: %s, last updated: %is ago', ', '.join(metric_names), lag)
            return
        if not self.ts:
            return
        for metric, _, _ in self.metrics:
            yield metric

    def _clear_metrics(self):
        for metric, _, _ in self.metrics:
            metric.samples.clear()

    def set_metrics(self, router_records: list[dict[str, str | float]] = []):
        self.ts = time()
        self._clear_metrics()

        if not router_records:
            router_records = []

        for router_record in router_records:
            # Some routeros endpoints do not support filtering by disabled flag, do it here instead
            if router_record.get('disabled', 'false') == 'true':
                continue

            translated_record = {}
            # Normalize keys
            for key, value in router_record.items():
                k = key
                if key.startswith(('.', '_', '-')):
                    k = k[1:]
                if k.endswith(('.', '_', '-')):
                    k = k[:-1]

                k = k.replace('.', '_').replace('-', '_')
                translated_record[k] = value

            # Add Router labels
            for k, v in self.router_id.items():
                translated_record[k] = v

            # translate fields if needed
            for key, func in self.translation_table.items():
                val = func(str(translated_record.get(key)) if key in translated_record else None)
                if val != None:
                    translated_record[key] = val

            for metric, labels, value in self.metrics:
                v = None
                # Info Metrics
                if not value:
                    v = {}
                else:
                    v = translated_record.get(value)
                    if v == None:
                        continue

                lv: list[str] = [str(translated_record.get(label, '')) for label in labels]
                metric.add_metric(lv, v)

    def add_router_labels(self, labels: list[str]):
        return labels + list(self.router_id.keys())

class LoadingCollector(Collector):
    name: str

    def get_name(self):
        return self.name

    @abstractmethod
    def load(self, router_entry: 'RouterEntry', interval: int) -> None:
        pass