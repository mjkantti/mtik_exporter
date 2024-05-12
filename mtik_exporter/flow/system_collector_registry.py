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

from mtik_exporter.cli.config.config import config_handler
from mtik_exporter.collector.latest_version import LatestVersionCollector

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mtik_exporter.collector.metric_store import LoadingCollector


class SystemCollectorRegistry:
    ''' mtik_exporter Collectors Registry
    '''

    def __init__(self) -> None:
        self.system_collectors: list['LoadingCollector'] = []

        # SYSTEM Collectors
        if config_handler.system_entry().check_for_updates:
            interval = config_handler.system_entry().check_for_updates_interval
            channel = config_handler.system_entry().check_for_updates_channel

            self.system_collectors.append(LatestVersionCollector(channel, interval))