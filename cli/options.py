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


import os
import logging
from argparse import ArgumentParser
from cli.config import config_handler

class OptionsParser:
    ''' Base mtik_exporter Options Parser
    '''
    def __init__(self):
        self._script_name = f'mtik_exporter'
        self._description =  \
f'''
Prometheus Exporter for Mikrotik RouterOS
Supports gathering metrics across multiple RouterOS devices, all easily configurable via built-in CLI interface.
Comes along with a dedicated Grafana dashboard (https://grafana.com/grafana/dashboards/13679)
Selected metrics info can be printed on the command line. For more information, run: 'mtik_exporter -h'
'''

    @property
    def description(self):
        return self._description

    @property
    def script_name(self):
        return self._script_name

    # Options Parsing Workflow
    def parse_options(self):
        ''' General Options parsing workflow
        '''

        global_options_parser = ArgumentParser(add_help=False)
        self.parse_global_options(global_options_parser)
        namespace, _ = global_options_parser.parse_known_args()
        logging.basicConfig(format='%(levelname)s %(message)s', level=namespace.loglevel)
        config_handler(namespace.cfg_file)

    def parse_global_options(self, parser):
        ''' Parses global options
        '''
        parser.add_argument('--cfg-file', dest = 'cfg_file',
                    type = lambda d: self._is_valid_file_path(parser, d),
                    default = 'config/config.yml',
                    help = 'mtik_exporter config files directory (optional)')
        parser.add_argument('--debug', dest = 'loglevel',
                    const = logging.DEBUG, action = 'store_const',
                    default=logging.WARNING,
                    help='Debug Logging')
        parser.add_argument('--verbose', dest = 'loglevel',
                    const = logging.INFO, action = 'store_const',
                    help = "More Verbose output")


    # Internal helpers
    @staticmethod
    def _is_valid_file_path(parser, path_arg):
        ''' Checks if path_arg is a valid file path
        '''
        if not (os.path.exists(path_arg) and os.path.isfile(path_arg)):
            parser.error('"{path_arg}" does not seem to be an existing file path')
        else:
            return path_arg