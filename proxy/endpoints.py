#   -*- coding: utf-8 -*-
#
#   This file is part of FAIR Proxy
#
#   Copyright (C) 2025 - Present SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.


import os
import requests
import logging

from skale import FairManager
from proxy.skaled_ports import SkaledPorts
from proxy.config import SM_ADDRESS, ANCHOR_FILEPATH
from proxy.helper import make_rpc_call
from proxy.config import ALLOWED_TIMESTAMP_DIFF
from proxy.helper import read_json

logger = logging.getLogger(__name__)

URL_PREFIXES = {
    'http': 'http://',
    'https': 'https://',
    'ws': 'ws://',
    'wss': 'wss://',
    'infoHttp': 'http://'
}


class FairManagerInitError(Exception):
    """Custom exception for failures during FairManager initialization"""
    pass

def init_fair() -> FairManager:
    """Initializes a FairManager by trying a list of anchor endpoints"""
    try:
        endpoints_data = read_json(ANCHOR_FILEPATH)
        http_endpoints = endpoints_data.get('http_endpoints', [])
    except Exception as e:
        raise FairManagerInitError(f"Failed to read or parse anchor endpoints file: {e}") from e

    for endpoint in http_endpoints:
        try:
            return FairManager(endpoint, SM_ADDRESS)
        except Exception as e:
            logger.info(f"Failed to connect to anchor endpoint '{endpoint}': {e}")

    raise FairManagerInitError("No working anchor endpoint found. FAIR manager "
                               "could not be initialized.")


def _compose_endpoints(node_dict, endpoint_type):
    for prefix_name in URL_PREFIXES:
        prefix = URL_PREFIXES[prefix_name]
        port = node_dict[f'{prefix_name}RpcPort']
        key_name = f'{prefix_name}_endpoint_{endpoint_type}'
        node_dict[key_name] = f'{prefix}{node_dict[endpoint_type]}:{port}'


def generate_endpoints() -> dict:
    fair = init_fair()
    logger.info(f'FAIR Manager is inited with endpoint {fair._endpoint}')
    node_ids = fair.nodes.get_active_node_ids()
    logger.info(node_ids)
    nodes = []
    for node_id in node_ids:

        node = fair.nodes.get(node_id)
        node_dict = {
            'id': node.id,
            'name': node.name,
            'ip': node.ip_str,
            'base_port': node.port,
            'domain': node.domain_name
        }
        logger.debug(f'ID {node_id}: {node}')
        node_dict.update(calc_ports(node_dict['base_port']))
        _compose_endpoints(node_dict, endpoint_type='domain')
        nodes.append(node_dict)
    return get_endpoint_dict(nodes)


def calc_ports(base_port):
    return {
        'httpRpcPort': base_port + SkaledPorts.HTTP_JSON.value,
        'httpsRpcPort': base_port + SkaledPorts.HTTPS_JSON.value,
        'wsRpcPort': base_port + SkaledPorts.WS_JSON.value,
        'wssRpcPort': base_port + SkaledPorts.WSS_JSON.value,
        'infoHttpRpcPort': base_port + SkaledPorts.INFO_HTTP_JSON.value
    }


def get_block_ts(http_endpoint: str) -> int:
    try:
        res = make_rpc_call(http_endpoint, 'eth_getBlockByNumber', ['latest', False])
        if res and res.json():
            res_data = res.json()
            latest_schain_timestamp_hex = res_data['result']['timestamp']
            return int(latest_schain_timestamp_hex, 16)
    except Exception as e:
        logger.warning(f'Failed to request latest block for {http_endpoint} ({e})')
    return -1


def is_node_out_of_sync(ts: int, compare_ts: int) -> bool:
    return abs(compare_ts - ts) > ALLOWED_TIMESTAMP_DIFF


def url_ok(url) -> bool:
    try:
        r = requests.head(url, timeout=10)
        return bool(r.status_code)
    except requests.exceptions.RequestException:
        return False


def get_endpoint_dict(nodes):
    http_endpoints = []
    ws_endpoints = []
    for node in nodes:
        http_endpoint = node['http_endpoint_domain']
        node['block_ts'] = get_block_ts(http_endpoint)

    max_ts = max(node['block_ts'] for node in nodes)
    logger.info(f'max_ts: {max_ts}')

    for node in nodes:
        http_endpoint = node['http_endpoint_domain']
        if not url_ok(http_endpoint):
            logger.warning(f'{http_endpoint} is not accesible, removing from the list')
            continue
        if is_node_out_of_sync(node['block_ts'], max_ts):
            logger.warning(f'{http_endpoint} ts: {node["block_ts"]}, max ts for chain: {max_ts}, '
                           f'allowed timestamp diff: {ALLOWED_TIMESTAMP_DIFF}')
            continue
        http_endpoints.append(http_endpoint.removeprefix(URL_PREFIXES['http']))
        ws_endpoints.append(node['ws_endpoint_domain'].removeprefix(URL_PREFIXES['ws']))
    return {
        'http_endpoints': http_endpoints,
        'ws_endpoints': ws_endpoints,
    }


if __name__ == '__main__':
    endpoints = generate_endpoints()
    print(f'Endpoints: {endpoints}')
