#!/usr/bin/env python
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


from mtik_exporter.cli.options import mtik_exporterOptionsParser
from mtik_exporter.flow.processor.base_proc import ExportProcessor

class mtik_exporterDispatcher:
    ''' Base mtik_exporter Commands Dispatcher
    '''
    def __init__(self):
        self.option_parser = mtik_exporterOptionsParser()

    # Dispatcher
    def dispatch(self):
        self.option_parser.parse_options()
        ExportProcessor().start()

        return True

def main():
    mtik_exporterDispatcher().dispatch()

if __name__ == '__main__':
    main()

