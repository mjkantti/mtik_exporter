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

        self.s = scheduler()
        self.collector_registries: list[CollectorRegistry] = []

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
        for router in router_entries_handler.router_entries:
            collector_registry = CollectorRegistry(router)
            self.collector_registries.append(collector_registry)
            for c in collector_registry.fast_collectors:
                logging.info('%s: Adding Fast Collector %s', router.router_name, c.name)
                REGISTRY.register(c)
            
            for c in collector_registry.slow_collectors:
                logging.info('%s: Adding Slow Collector %s', router.router_name, c.name)
                REGISTRY.register(c)
            
            REGISTRY.register(collector_registry.interal_collector)
        
        system_collector_registry = SystemCollectorRegistry()
        for c in system_collector_registry.system_collectors:
            logging.info('%s: Adding System Collector %s', router.router_name, c.name)
            REGISTRY.register(c)


        logging.info('Running HTTP metrics server on port %i', config_handler.system_entry().port)

        self.server, self.thr = start_http_server(config_handler.system_entry().port)

        for i, registry in enumerate(self.collector_registries):
            router = registry.router_entry
            router.api_connection.connect()

            interval = registry.router_entry.config_entry.polling_interval
            for c in registry.fast_collectors:
                self.s.enter((i+1), 1, self.run_collector, argument=(router, c, interval, 1))

            slow_interval = registry.router_entry.config_entry.slow_polling_interval
            for c in registry.slow_collectors:
                self.s.enter((i+1)*10, 2, self.run_collector, argument=(router, c, slow_interval, 2))
        
        for i, c in enumerate(system_collector_registry.system_collectors):
            self.s.enter((i+1)*15, 3, self.run_system_collector, argument=(c, c.interval))

        self.s.run()

        logging.info(f'Shut Down Done')
    
    def run_system_collector(self, collector,  interval):
        self.s.enter(interval, 3, self.run_system_collector, argument=(collector, interval))

        logging.debug('Starting data load, polling interval set to: %i', interval)
        
        logging.debug('Running %s', collector.name)
        start = time()

        #try:
        collector.load(None)

        #finally:
            #stats = router_entry.data_loader_stats.get(collector.get_name(), {})

            #stats['count'] = stats.get('count', 0) + 1
            #stats['duration'] = stats.get('duration', 0) + (time() - start)
            #stats['last_run'] = start
            #stats['name'] = collector.get_name()
            #router_entry.data_loader_stats[collector.get_name()] = stats

    def run_collector(self, router_entry, collector,  interval, priority):
        self.s.enter(interval, priority, self.run_collector, argument=(router_entry, collector, interval, priority))
        if not router_entry.api_connection.is_connected():
            logging.info('Router not connected, reconnecting, waiting for 3 seconds')
            router_entry.api_connection.connect()
            return

        logging.debug('Starting data load, polling interval set to: %i', interval)
        
        logging.debug('Running %s', collector.name)
        start = time()

        try:
            collector.load(router_entry)

        finally:
            stats = router_entry.data_loader_stats.get(collector.get_name(), {})

            stats['count'] = stats.get('count', 0) + 1
            stats['duration'] = stats.get('duration', 0) + (time() - start)
            stats['last_run'] = start
            stats['name'] = collector.get_name()
            router_entry.data_loader_stats[collector.get_name()] = stats


    def run_collectors(self, router_entry, collectors,  interval):
        if not router_entry.api_connection.is_connected():
            logging.info('Router not connected, reconnecting, waiting for 3 seconds')
            router_entry.api_connection.connect()
            self.s.enter(3, 1, self.run_collectors, argument=(router_entry, collectors, interval))
            return

        logging.debug('Starting data load, polling interval set to: %i', interval)
        self.s.enter(interval, 1, self.run_collectors, argument=(router_entry, collectors, interval))
        
        for collector in collectors:
            logging.debug('Running %s', collector.name)
            start = time()

            try:
                collector.load(router_entry)

            finally:
                stats = router_entry.data_loader_stats.get(collector.get_name(), {})

                stats['count'] = stats.get('count', 0) + 1
                stats['duration'] = stats.get('duration', 0) + (time() - start)
                stats['last_run'] = start
                stats['name'] = collector.get_name()
                router_entry.data_loader_stats[collector.get_name()] = stats
