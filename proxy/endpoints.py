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


import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

import requests
from skale import FairManager

from proxy.config import ALLOWED_TIMESTAMP_DIFF, ANCHOR_FILEPATH, FAIR_CONTRACTS, URL_PREFIXES
from proxy.helper import make_rpc_call, read_json, write_json
from proxy.skaled_ports import SkaledPorts

logger = logging.getLogger(__name__)


@dataclass
class FairNode:
    id: int
    name: str
    ip: str
    domain: str
    base_port: int
    http_endpoint: str = field(init=False)
    ws_endpoint: str = field(init=False)
    block_ts: int = -1

    def __post_init__(self):
        http_port = self.base_port + SkaledPorts.HTTP_JSON.value
        ws_port = self.base_port + SkaledPorts.WS_JSON.value
        self.http_endpoint = f"{URL_PREFIXES['http']}{self.domain}:{http_port}"
        self.ws_endpoint = f"{URL_PREFIXES['ws']}{self.domain}:{ws_port}"

    def fetch_latest_block_timestamp(self):
        try:
            res = make_rpc_call(self.http_endpoint, 'eth_getBlockByNumber', ['latest', False])
            if res and res.ok:
                timestamp_hex = res.json()['result']['timestamp']
                self.block_ts = int(timestamp_hex, 16)
        except (requests.RequestException, KeyError, TypeError, ValueError) as e:
            logger.warning(f'Could not get block timestamp for {self.http_endpoint}: {e}')
            self.block_ts = -1

    def is_accessible(self) -> bool:
        try:
            response = requests.head(self.http_endpoint, timeout=10)
            return response.status_code < 400
        except requests.RequestException:
            return False

    def is_synced(self, max_timestamp: int) -> bool:
        if self.block_ts < 0:
            return False
        return abs(max_timestamp - self.block_ts) <= ALLOWED_TIMESTAMP_DIFF


def _fetch_active_committee_nodes(fair_manager: FairManager) -> list[FairNode]:
    active_committee_id = fair_manager.committee.get_active_committee_index()
    active_committee = fair_manager.committee.get_committee(active_committee_id)
    node_ids = active_committee.node_ids
    logger.info(f'Found {len(node_ids)} active committee nodes: {node_ids}')
    return [
        FairNode(
            id=node.id, name=node.name, ip=node.ip_str,
            domain=node.domain_name, base_port=node.port
        )
        for node in (fair_manager.nodes.get(node_id) for node_id in node_ids)
    ]


def _filter_healthy_nodes(nodes: list[FairNode]) -> list[FairNode]:
    logger.info('Fetching block timestamps for committee nodes...')
    with ThreadPoolExecutor(max_workers=len(nodes)) as executor:
        list(executor.map(lambda node: node.fetch_latest_block_timestamp(), nodes))

    valid_timestamps = [node.block_ts for node in nodes if node.block_ts >= 0]
    if not valid_timestamps:
        logger.warning('Could not determine a maximum timestamp - no nodes reported a valid block')
        return []
    max_ts = max(valid_timestamps)
    logger.info(f'Maximum block timestamp across all nodes: {max_ts}')

    def check_node_health(node: FairNode) -> FairNode | None:
        if not node.is_accessible():
            logger.warning(f'Node {node.id} ({node.http_endpoint}) is not accessible')
            return None
        if not node.is_synced(max_ts):
            logger.warning(
                f'Node {node.id} ({node.http_endpoint}) is not synced. '
                f'(Node TS: {node.block_ts}, Max TS: {max_ts})'
            )
            return None
        return node

    logger.info('Checking health and sync status for committee nodes...')
    with ThreadPoolExecutor(max_workers=len(nodes)) as executor:
        results = executor.map(check_node_health, nodes)
        healthy_nodes = [node for node in results if node is not None]

    logger.info(f'Found {len(healthy_nodes)} healthy and synchronized nodes')
    logger.debug(f'Healthy nodes: {healthy_nodes}')

    return healthy_nodes


def update_anchor_file(endpoints: list[str]):
    logger.info(f'Updating anchor endpoints file with {len(endpoints)} endpoints')
    data_to_write = {'anchor_endpoints': endpoints}
    write_json(ANCHOR_FILEPATH, data_to_write)


def generate_active_committee_endpoints() -> tuple[dict, list]:
    anchor_endpoints_data = read_json(ANCHOR_FILEPATH)
    anchor_endpoints = anchor_endpoints_data.get('anchor_endpoints', [])
    fair_manager = FairManager(anchor_endpoints, FAIR_CONTRACTS)
    all_nodes = _fetch_active_committee_nodes(fair_manager)
    healthy_nodes = _filter_healthy_nodes(all_nodes)

    healthy_http_endpoints = [node.http_endpoint for node in healthy_nodes]

    nginx_config = {
        'http_endpoints': [
            http_endpoint.removeprefix(URL_PREFIXES['http']) for http_endpoint in
            healthy_http_endpoints
        ],
        'ws_endpoints': [
            node.ws_endpoint.removeprefix(URL_PREFIXES['ws']) for node in healthy_nodes
        ],
    }

    return nginx_config, healthy_http_endpoints


if __name__ == '__main__':
    endpoints = generate_active_committee_endpoints()
    print(f'Endpoints: {endpoints}')
