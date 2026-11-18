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

class RetryTimerSkip(Exception):
    ''' Request skipped because the router is backing off after a previous error, not an error by itself
    '''

class RouterRestAPI:
    ''' Base wrapper for the routeros rest api
    '''
    def __init__(self, router_name: str, config_entry):
        self.router_name: str = router_name
        self.config_entry = config_entry
        self.last_failure_timestamp: float = 0
        self.successive_failure_count: int = 0
        self.auth = (config_entry.username, config_entry.password)

        protocol = 'https' if config_entry.use_tls else 'http'
        host_url = f'{protocol}://{config_entry.hostname}'
        if config_entry.host_port:
            host_url += f':{config_entry.host_port}'
        self.base_url = f'{host_url}/rest'

        self.timeout = config_entry.request_timeout
        self.retry_timer = time.time()
        self.ses = requests.Session()

    def get(self, path, params = {}):
        return self._request('GET', f"{self.base_url}/{path}", params=params)

    def post(self, path, command, data):
        return self._request('POST', f"{self.base_url}/{path}/{command}", json=data)

    def _request(self, method, url, **kwargs):
        if time.time() < self.retry_timer:
            raise RetryTimerSkip(self.router_name)

        logging.debug("Hitting %s %s", method, url)
        try:
            resp = self.ses.request(method, url, auth=self.auth, timeout=self.timeout, **kwargs)
            resp.raise_for_status()
            logging.debug("Done %s %s, took: %.3fs", method, url, resp.elapsed.total_seconds())

            c = resp.content.decode(mtik_encoding)
            return json.loads(c, strict = False)
        except requests.exceptions.HTTPError as http_error:
            # Auth failures will not fix themselves, back off to avoid flooding the router log with failed logins
            # Other HTTP errors (e.g. 404 for an endpoint missing on this device) only affect one collector, no retry timer
            if http_error.response is not None and http_error.response.status_code in (401, 403):
                logging.error('%s: Authentication failed (HTTP %i), check username, password and group policy',
                              self.router_name, http_error.response.status_code)
                self.retry_timer = time.time() + 60
            raise
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # Connection error or timeout, set retry timer to 30s
            self.retry_timer = time.time() + 30
            raise
        except Exception:
            # Other exception set retry timer to 20s
            self.retry_timer = time.time() + 20
            raise
