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
from argparse import ArgumentParser, HelpFormatter
from mtik_exporter.cli.config.config import config_handler, CustomConfig
from mtik_exporter.utils.utils import FSHelper, UniquePartialMatchList


class mtik_exporterCommands:
    INFO = 'info'
    EDIT = 'edit'
    EXPORT = 'export'
    PRINT = 'print'
    SHOW = 'show'

    @classmethod
    def commands_meta(cls):
        return ''.join(('{',
                        f'{cls.INFO}, ',
                        f'{cls.EDIT}, ',
                        f'{cls.EXPORT}, ',
                        f'{cls.PRINT}, ',
                        f'{cls.SHOW}, ',
                        '}'))

class mtik_exporterOptionsParser:
    ''' Base mtik_exporter Options Parser
    '''
    def __init__(self):
        self._script_name = f'mtik_exporter'
        #version = pkg_resources.require("mtik_exporter")[0].version
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
        if namespace.cfg_file:
            config_handler(CustomConfig(namespace.cfg_file))
        else:
            config_handler()

        commands_parser = ArgumentParser(prog = self._script_name,
                                description = 'Prometheus Exporter for Mikrotik RouterOS',
                                formatter_class=mtik_exporterHelpFormatter, parents=[global_options_parser])
        self.parse_commands(commands_parser)
        args = vars(commands_parser.parse_args())

        self._check_args(args, commands_parser)

        return args

    def parse_global_options(self, parser):
        ''' Parses global options
        '''
        parser.add_argument('--cfg-file', dest = 'cfg_file',
                    type = lambda d: self._is_valid_file_path(parser, d),
                    help = 'mtik_exporter config files directory (optional)')

    def parse_commands(self, parser):
        ''' Commands parsing
        '''
        subparsers = parser.add_subparsers(dest = 'sub_cmd',
                                           title = 'mtik_exporter commands',
                                           metavar = mtik_exporterCommands.commands_meta())

        # Info command
        subparsers.add_parser(mtik_exporterCommands.INFO,
                                        description = 'Displays mtik_exporter info',
                                        formatter_class=mtik_exporterHelpFormatter)
        # Show command
        show_parser = subparsers.add_parser(mtik_exporterCommands.SHOW,
                                        description = 'Displays mtik_exporter config router entries',
                                        formatter_class=mtik_exporterHelpFormatter)
        self._add_entry_name(show_parser, registered_only = True, required = False, help = "Config entry name")
        show_parser.add_argument('-cfg', '--config', dest='config',
                                        help = "Shows mtik_exporter config files paths",
                                        action = 'store_true')

    # Options checking
    def _check_args(self, args, parser):
        ''' Validation of supplied CLI arguments
        '''
        # check if there is a cmd to execute
        self._check_cmd_args(args, parser)

    def _check_cmd_args(self, args, parser):
        ''' Validation of supplied CLI commands
        '''
        # base command check
        if 'sub_cmd' not in args or not args['sub_cmd']:
            # If no command was specified, check for the default one
            cmd = self._default_command
            if cmd:
                args['sub_cmd'] = cmd
            else:
                # no appropriate default either
                parser.print_help()
                parser.exit()


    @property
    def _default_command(self):
        ''' If no command was specified, print INFO by default
        '''
        return mtik_exporterCommands.INFO


    # Internal helpers
    @staticmethod
    def _is_valid_file_path(parser, path_arg):
        ''' Checks if path_arg is a valid file path
        '''
        path_arg = FSHelper.full_path(path_arg)
        if not (os.path.exists(path_arg) and os.path.isfile(path_arg)):
            parser.error('"{path_arg}" does not seem to be an existing file path')
        else:
            return path_arg

    @staticmethod
    def _add_entry_name(parser, registered_only = False, required = True, help = 'mtik_exporter Entry name'):
        parser.add_argument('-en', '--entry-name', dest = 'entry_name',
            type = str,
            metavar = list(config_handler.registered_entries()) if registered_only else None,
            required = required,
            choices = UniquePartialMatchList(config_handler.registered_entries())if registered_only else None,
            help = help)

    @staticmethod
    def _add_entry_groups(parser):
        required_args_group = parser.add_argument_group('Required Arguments')
        mtik_exporterOptionsParser._add_entry_name(required_args_group)

class mtik_exporterHelpFormatter(HelpFormatter):
    ''' Custom formatter for ArgumentParser
        Disables double metavar display, showing only for long-named options
    '''
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    #parts.append('%s %s' % (option_string, args_string))
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)

