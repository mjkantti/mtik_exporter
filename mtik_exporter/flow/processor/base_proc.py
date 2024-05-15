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

from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server
from prometheus_client.context_managers import Timer
from sched import scheduler
from signal import signal, SIGTERM, SIGINT

from mtik_exporter.cli.config.config import config_handler, ConfigKeys
from mtik_exporter.flow.collector_registry import CollectorRegistry
from mtik_exporter.flow.system_collector_registry import SystemCollectorRegistry
from mtik_exporter.flow.router_entries_handler import RouterEntriesHandler

import logging
logging.basicConfig(format='%(levelname)s %(message)s', level=logging.INFO)

class ExportProcessor:
    ''' Base Export Processing
    '''
    def __init__(self):
        signal(SIGINT, self.exit_gracefully)
        signal(SIGTERM, self.exit_gracefully)

        self.registries = []
        self.s = scheduler()

        self.server = None
        self.thr = None

    def exit_gracefully(self, signal, _):
        logging.warning(f"Caught signal {signal}, stopping")
        for j in self.s.queue:
            logging.warning(f'Cancelling scheduler job')
            self.s.cancel(j)

        logging.info(f'Shut Down HTTP server')
        if self.server:
            self.server.shutdown()

        if self.thr:
            self.thr.join(5)

    def start(self):
        router_entries_handler = RouterEntriesHandler()
        for i, router in enumerate(router_entries_handler.router_entries):
            registry = CollectorRegistry(router)
            self.registries.append(registry)
            
            router = registry.router_entry
            router.api_connection.connect()
            
            interval = registry.router_entry.config_entry.polling_interval
            self.s.enter((i+1), 1, self.run_collectors, argument=(router, registry.fast_collectors, interval, 1))

            slow_interval = registry.router_entry.config_entry.slow_polling_interval
            self.s.enter((i+1)*10, 2, self.run_collectors, argument=(router, registry.slow_collectors, slow_interval, 2))

            for c in registry.fast_collectors:
                logging.info('%s: Adding Fast Collector %s', router.router_name, c.name)
                REGISTRY.register(c)
            
            for c in registry.slow_collectors:
                logging.info('%s: Adding Slow Collector %s', router.router_name, c.name)
                REGISTRY.register(c)
            
        system_collector_registry = SystemCollectorRegistry()
        for c in system_collector_registry.system_collectors:
            logging.info('%s: Adding System Collector %s', router.router_name, c.name)
            REGISTRY.register(c)

        if system_collector_registry.system_collectors:
            self.s.enter(15, 3, self.run_collectors, argument=(None, system_collector_registry.system_collectors, c.interval, 3))

        self.internal_collector = system_collector_registry.interal_collector

        logging.info('Running HTTP metrics server on port %i', config_handler.system_entry().port)

        self.server, self.thr = start_http_server(config_handler.system_entry().port)

        self.s.run()

        logging.info(f'Shut Down Done')
    
    def run_collectors(self, router_entry, collectors, interval, priority):
        self.s.enter(interval, priority, self.run_collectors, argument=(router_entry, collectors, interval, priority))

        if router_entry and not router_entry.api_connection.is_connected():
            logging.info('Router not connected, reconnecting, waiting for 3 seconds')
            router_entry.api_connection.connect()
            return

        logging.debug('Starting data load, polling interval set to: %i', interval)
        for c in collectors:
            internal_labels = {'name': c.name, ConfigKeys.ROUTERBOARD_ADDRESS: '', ConfigKeys.ROUTERBOARD_NAME: ''}
            if router_entry:
                internal_labels.update(router_entry.router_id)
        
            logging.debug('Running %s', c.name)

            with Timer(self.internal_collector.load_time.labels(**internal_labels), 'inc'), self.internal_collector.load_exceptions.labels(**internal_labels).count_exceptions():
                c.load(router_entry)
            self.internal_collector.load_last_run.labels(**internal_labels).set_to_current_time()
            self.internal_collector.load_count.labels(**internal_labels).inc()