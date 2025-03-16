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
from sched import scheduler
from signal import signal, SIGTERM, SIGINT
from time import time, sleep

from flow.collector_registry import CollectorRegistry, SystemCollectorRegistry
from flow.router_entry import RouterEntry
from cli.config import config_handler, ConfigKeys
from cli.options import OptionsParser

import logging
import sys

class ExportProcessor:
    ''' Base Export Processing
    '''
    def __init__(self):
        signal(SIGINT, self.exit_gracefully)
        signal(SIGTERM, self.exit_gracefully)

        self.option_parser = OptionsParser()
        self.registries = []
        self.s = scheduler(time, sleep)

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

        logging.info(f'Shut Down Done')
        sys.exit(1)

    def start(self):
        self.option_parser.parse_options()

        self._router_entries = {}
        start_time = round(time(), -1)

        system_config = config_handler.system_entry()
        system_collector_registry = SystemCollectorRegistry(system_config, ['name', ConfigKeys.ROUTERBOARD_NAME, ConfigKeys.ROUTERBOARD_ADDRESS])
        self.internal_collector = system_collector_registry.interal_collector

        for router_name in config_handler.registered_entries():
            router = RouterEntry(router_name)
            if not router.config_entry.enabled:
                logging.info('%s: Skipping disabled router', router_name)
                continue

            registry = CollectorRegistry(router)
            self.registries.append(registry)

            interval = registry.router_entry.config_entry.polling_interval
            self.s.enterabs(start_time + interval, 1, self.run_collectors, argument=(router, registry.fast_collectors, interval, start_time, 1))
            #self.run_collectors(router, registry.fast_collectors, interval, start_time, 1)

            slow_interval = registry.router_entry.config_entry.slow_polling_interval
            self.s.enterabs(start_time + interval, 2, self.run_collectors, argument=(router, registry.slow_collectors, slow_interval, start_time, 2))
            #self.run_collectors(router, registry.slow_collectors, slow_interval, start_time, 2)

            for c in registry.fast_collectors:
                logging.info('%s: Adding Fast Collector %s', router.router_name, c.name)
                REGISTRY.register(c)

            for c in registry.slow_collectors:
                logging.info('%s: Adding Slow Collector %s', router.router_name, c.name)
                REGISTRY.register(c)

        interval = system_collector_registry.interval
        for c in system_collector_registry.system_collectors:
            logging.info('Adding System Collector %s', c.name)
            REGISTRY.register(c)

        self.run_collectors(None, system_collector_registry.system_collectors, interval, start_time, 3)

        logging.info('Running HTTP metrics server on address %s port %i', system_config.export_address, system_config.export_port)

        self.server, self.thr = start_http_server(port=system_config.export_port, addr=system_config.export_address)

        self.s.run()

        logging.info(f'Shut Down Done')

    def run_collectors(self, router_entry, collectors, interval, start_time, priority):
        next_run = start_time + interval
        while next_run < time():
            next_run += interval

        self.s.enterabs(next_run, priority, self.run_collectors, argument=(router_entry, collectors, interval, next_run, priority))

        logging.debug('Starting data load, polling interval set to: %i', interval)
        logged_skip = False

        for c in collectors:
            internal_labels = {'name': c.name, ConfigKeys.ROUTERBOARD_ADDRESS: '', ConfigKeys.ROUTERBOARD_NAME: ''}
            if router_entry:
                internal_labels.update(router_entry.router_id)

            logging.debug('Running %s', c.name)

            try:
                with self.internal_collector.time(internal_labels), self.internal_collector.count_exceptions(internal_labels):
                    c.load(router_entry)
                self.internal_collector.inc_load_count(internal_labels)
            except Exception as e:
                if str(e) == 'retry_timer_skip':
                    if not logged_skip:
                        logging.critical("Skipping Load because of previous error")
                        logged_skip = True
                    continue
                logging.exception('Catched exception while loading')
            self.internal_collector.set_last_run(internal_labels)

if __name__ == '__main__':
    ExportProcessor().start()
