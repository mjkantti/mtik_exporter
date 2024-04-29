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

from time import time
from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server
from sched import scheduler
from signal import signal, SIGTERM, SIGINT

from mtik_exporter.cli.config.config import config_handler
from mtik_exporter.flow.collector_registry import CollectorRegistry
from mtik_exporter.flow.router_entries_handler import RouterEntriesHandler

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

class ExportProcessor:
    ''' Base Export Processing
    '''
    def __init__(self):
        signal(SIGINT, self.exit_gracefully)
        signal(SIGTERM, self.exit_gracefully)

        self.s = scheduler()
        self.collector_registries: list[CollectorRegistry] = []

        self.server = None
        self.thr = None
        self.running = True

    def exit_gracefully(self, signal, _):
        logging.warning(f"Caught signal {signal}, stopping")
        self.server.shutdown()
        self.thr.join(5)
        self.running = False

    def start(self):
        router_entries_handler = RouterEntriesHandler()
        for router in router_entries_handler.router_entries:
            collector_registry = CollectorRegistry(router)
            self.collector_registries.append(collector_registry)
            for c in collector_registry.registered_collectors:
                REGISTRY.register(c)

        logging.info('Running HTTP metrics server on port %i', config_handler.system_entry().port)

        self.server, self.thr = start_http_server(config_handler.system_entry().port)

        for registry in self.collector_registries:
            self.run_registry(registry)

        self.s.run()


    def run_registry(self, registry: 'CollectorRegistry'):
        if not self.running:
            return

        router = registry.router_entry
        if not router.api_connection.is_connected():
            logging.info('Router not connected, reconnecting, waiting for 3 seconds')
            router.api_connection.connect()
            self.s.enter(3, 1, self.run_registry, argument=(registry, ))
            return

        interval = registry.router_entry.config_entry.polling_interval        
        logging.debug('Starting data load, polling interval set to: %i', interval)
        self.s.enter(interval, 1, self.run_registry, argument=(registry, ))
        router.data_loader_time_spent.clear()
        
        for collector in registry.registered_collectors:
            logging.debug('Running %s', collector.name)
            start = time()
            collector.load(router)
            router.data_loader_time_spent[collector.get_name()] = time() - start
        router.data_load_count += 1