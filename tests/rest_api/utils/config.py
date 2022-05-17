# Copyright (C) 2021 Intel Corporation
#
# SPDX-License-Identifier: MIT

import os.path as osp
import requests

ROOT_DIR = osp.dirname(__file__)
ASSETS_DIR = osp.abspath(osp.join(ROOT_DIR, '..', 'assets'))
# Suppress the warning from Bandit about hardcoded passwords
USER_PASS = '!Q@W#E$R' # nosec
BASE_URL = 'http://localhost:8080/'
API_URL = BASE_URL + 'api/'

def _to_query_params(**kwargs):
    return '&'.join([f'{k}={v}' for k,v in kwargs.items()])

def get_server_url(endpoint, **kwargs):
    return BASE_URL + endpoint + '?' + _to_query_params(**kwargs)

def get_api_url(endpoint, **kwargs):
    return API_URL + endpoint + '?' + _to_query_params(**kwargs)

def get_method(username, endpoint, **kwargs):
    return requests.get(get_api_url(endpoint, **kwargs), auth=(username, USER_PASS))

def options_method(username, endpoint, **kwargs):
    return requests.options(get_api_url(endpoint, **kwargs), auth=(username, USER_PASS))

def delete_method(username, endpoint, **kwargs):
    return requests.delete(get_api_url(endpoint, **kwargs), auth=(username, USER_PASS))

def patch_method(username, endpoint, data, **kwargs):
    return requests.patch(get_api_url(endpoint, **kwargs), json=data, auth=(username, USER_PASS))

def post_method(username, endpoint, data, **kwargs):
    return requests.post(get_api_url(endpoint, **kwargs), json=data, auth=(username, USER_PASS))

def server_get(username, endpoint, **kwargs):
    return requests.get(get_server_url(endpoint, **kwargs), auth=(username, USER_PASS))
