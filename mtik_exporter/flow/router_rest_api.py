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
import logging

class RouterRestAPI:
    ''' Base wrapper interface for the routeros_api library
    '''
    def __init__(self, router_name: str, config_entry):
        self.router_name: str = router_name
        self.config_entry = config_entry
        self.last_failure_timestamp: float = 0
        self.successive_failure_count: int = 0
        self.auth = (config_entry.username, config_entry.password)
        #self.base_url = f'http://{config_entry.hostname}:{config_entry.port}/rest'
        self.base_url = f'http://{config_entry.hostname}/rest'
        self.ses = requests.Session()
        
        self.timeout = 10


    def get(self, path, params = {}):
        url = f"{self.base_url}/{path}"
        logging.info("Hitting %s", url)
        try:
            resp = self.ses.get(url, auth=self.auth, params=params)
            resp.raise_for_status()
            logging.info(f"Done, took: {resp.elapsed.total_seconds()}")

            return resp.json()
        except Exception as exc:
            logging.critical(f'Got Exception: {exc}')

        return None
    
    def post(self, path, command, data):
        url = f"{self.base_url}/{path}/{command}"
        logging.info("Hitting %s", url)
        try:
            resp = self.ses.post(url, auth=self.auth, json=data)
            resp.raise_for_status()
            logging.info(f"Done, took: {resp.elapsed.total_seconds()}")

            return resp.json()
        except Exception as exc:
            logging.critical(f'Got Exception: {exc}')

        return None
    