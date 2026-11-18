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

import importlib
import logging
import pkgutil

from functools import cache

import collector
from collector.metric_store import LoadingCollector
from collector.latest_version import LatestVersionCollector
from collector.internal_collector import InternalCollector

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.router_entry import RouterEntry


@cache
def discover_collectors() -> dict[str, type[LoadingCollector]]:
    ''' Finds every router collector, a collector is any LoadingCollector subclass in the collector package with a key
        Called lazily (not at import time) so the debug log below goes through the configured logger
    '''
    for module in pkgutil.iter_modules(collector.__path__):
        importlib.import_module(f'collector.{module.name}')

    mapping: dict[str, type[LoadingCollector]] = {}
    classes = list(LoadingCollector.__subclasses__())
    while classes:
        cls = classes.pop()
        classes.extend(cls.__subclasses__())
        key = getattr(cls, 'key', None)
        if not key:
            continue
        if key in mapping:
            raise ValueError(f'Duplicate collector key "{key}": {mapping[key].__name__} and {cls.__name__}')
        mapping[key] = cls

    logging.debug('Available collectors: %s', ', '.join(sorted(mapping)))
    return mapping


class CollectorRegistry:
    ''' mtik_exporter Collectors Registry
    '''

    def __init__(self, router_entry: 'RouterEntry') -> None:
        self.collector_mapping = discover_collectors()
        self.router_entry = router_entry
        self.polling_interval = router_entry.config_entry.polling_interval
        self.slow_polling_interval = router_entry.config_entry.slow_polling_interval

        router_id = router_entry.router_id
        self.fast_collectors: list[LoadingCollector] = []
        self.slow_collectors: list[LoadingCollector] = []

        for key in router_entry.config_entry.collectors:
            cls = self.collector_mapping.get(key)
            if not cls:
                logging.warning('Fast Collector not found: %s ignoring', key)
                continue

            self.fast_collectors.append(cls(router_id))

        for key in router_entry.config_entry.slow_collectors:
            cls = self.collector_mapping.get(key)
            if not cls:
                logging.warning('Slow Collector not found: %s ignoring', key)
                continue

            self.slow_collectors.append(cls(router_id))


class SystemCollectorRegistry:
    ''' mtik_exporter Collectors Registry
    '''

    def __init__(self, system_config, keys: list[str]) -> None:
        self.system_collectors: list['LoadingCollector'] = []
        self.interval: int = system_config.system_polling_interval
        self.interal_collector = InternalCollector(keys)

        # SYSTEM Collectors
        if system_config.check_for_updates:
            channel = system_config.check_for_updates_channel

            self.system_collectors.append(LatestVersionCollector(channel))