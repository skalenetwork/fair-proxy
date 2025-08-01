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
from eth_typing import HexStr
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet
from skale import FairManager
from proxy.skaled_ports import SkaledPorts
from proxy.config import SM_ADDRESS

ENDPOINT = os.getenv('FAIR_ENDPOINT')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')


def init_fair(endpoint) -> FairManager:
    web3 = init_web3(endpoint)
    wallet = Web3Wallet(HexStr(ETH_PRIVATE_KEY), web3)
    return FairManager(endpoint, SM_ADDRESS, wallet)

def generate_endpoints(endpoint: str) -> list:
    fair = init_fair(endpoint)
    node_ids = fair.nodes.get_active_node_ids()
    print(node_ids)
    for node_id in node_ids:
        node = fair.nodes.get(node_id)
        print(f'ID {node_id}: {node}')

def calc_ports(base_port):
    return {
        'httpRpcPort': base_port + SkaledPorts.HTTP_JSON.value,
        'httpsRpcPort': base_port + SkaledPorts.HTTPS_JSON.value,
        'wsRpcPort': base_port + SkaledPorts.WS_JSON.value,
        'wssRpcPort': base_port + SkaledPorts.WSS_JSON.value,
        'infoHttpRpcPort': base_port + SkaledPorts.INFO_HTTP_JSON.value
    }


if __name__ == '__main__':
    generate_endpoints(ENDPOINT)

