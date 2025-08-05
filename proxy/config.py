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

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.join(DIR_PATH, os.pardir)

PORTS_PER_SCHAIN = 64

MONITOR_INTERVAL = os.getenv('MONITOR_INTERVAL', 10 * 60)

HEARTBEAT_URL = os.getenv('HEARTBEAT_URL')

NGINX_WWW_FOLDER = os.path.join(PROJECT_PATH, 'www')
CHAIN_INFO_FILEPATH = os.path.join(NGINX_WWW_FOLDER, 'chain.json')

DATA_FOLDER = os.path.join(PROJECT_PATH, 'data')
ANCHOR_FILEPATH = os.path.join(DATA_FOLDER, 'anchor_endpoints.json')

FAIR_CONTRACTS = os.getenv('FAIR_CONTRACTS')

TEMPLATES_FOLDER = os.path.join(PROJECT_PATH, 'templates')

UPSTREAM_NGINX_TEMPLATE = os.path.join(TEMPLATES_FOLDER, 'upstream.conf.j2')

UPSTREAMS_FOLDER = os.path.join(PROJECT_PATH, 'conf', 'upstreams')

TMP_UPSTREAMS_FOLDER = os.path.join(PROJECT_PATH, 'conf', 'tmp_upstreams')

PROXY_LOG_FORMAT = '[%(asctime)s] %(process)d %(levelname)s %(module)s: %(message)s'
LONG_LINE = '=' * 100

NGINX_CONTAINER_NAME = 'proxy_nginx'
CONTAINER_RUNNING_STATUS = 'running'

ALLOWED_TIMESTAMP_DIFF = 300

URL_PREFIXES = {'http': 'http://', 'ws': 'ws://'}