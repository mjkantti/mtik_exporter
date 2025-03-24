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

import requests
import json
import logging
import time

# Mikrotik returns everything with latin1 encoding
mtik_encoding = 'latin1'

class RouterRestAPI:
    ''' Base wrapper for the routeros rest api
    '''
    def __init__(self, router_name: str, config_entry):
        self.router_name: str = router_name
        self.config_entry = config_entry
        self.last_failure_timestamp: float = 0
        self.successive_failure_count: int = 0
        self.auth = (config_entry.username, config_entry.password)

        protocol = 'https' if config_entry.use_ssl else 'http'
        host_url = f'{protocol}://{config_entry.hostname}'
        if config_entry.port:
            host_url += f':{config_entry.port}'
        self.base_url = f'{host_url}/rest'

        self.timeout = config_entry.socket_timeout
        self.retry_timer = time.time()
        self.ses = requests.Session()

    def get(self, path, params = {}):
        if time.time() < self.retry_timer:
            raise Exception("retry_timer_skip")

        url = f"{self.base_url}/{path}"
        logging.debug("Hitting %s", url)
        try:
            resp = self.ses.get(url, auth=self.auth, timeout=self.timeout, params=params)
            resp.raise_for_status()
            logging.debug(f"Done, took: {resp.elapsed.total_seconds()}")

            c = resp.content.decode(mtik_encoding)
            return json.loads(c, strict = False)
        except ConnectionError as connection_error:
            # Connection error, set retry timer to 30s
            self.retry_timer = time.time() + 30
            raise connection_error
        except requests.exceptions.HTTPError as http_error:
            # HTTP Error, no retry timer
            raise http_error
        except requests.exceptions.Timeout as timeout_error:
            # Timeout, set retry timer to 30s
            self.retry_timer = time.time() + 30
            raise timeout_error
        except Exception as exc:
            # Other exception set retry timer to 20s
            self.retry_timer = time.time() + 20
            raise exc
    
    def post(self, path, command, data):
        if time.time() < self.retry_timer:
            return []

        url = f"{self.base_url}/{path}/{command}"
        logging.debug("Hitting %s", url)
        try:
            resp = self.ses.post(url, auth=self.auth, timeout=self.timeout, json=data)
            resp.raise_for_status()
            logging.debug(f"Done, took: {resp.elapsed.total_seconds()}")

            c = resp.content.decode(mtik_encoding)
            return json.loads(c)
        except ConnectionError as connection_error:
            # Connection error, set retry timer to 30s
            self.retry_timer = time.time() + 30
        except requests.exceptions.HTTPError as http_error:
            # HTTP Error, no retry timer
            logging.critical(f'Unsuccesful HTTP Request: {http_error}')
        except requests.exceptions.Timeout as timeout_error:
            # Timeout, set retry timer to 30s
            self.retry_timer = time.time() + 30
            logging.critical(f'Timeout Occured: {timeout_error}')
        except Exception as exc:
            # Other exception set retry timer to 10s
            self.retry_timer = time.time() + 10
            logging.critical(f'Got Exception: {exc}')

        return None
    