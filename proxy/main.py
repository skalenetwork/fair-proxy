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

import logging
from time import sleep
from pathlib import Path

from proxy.nginx import update_nginx_config
from proxy.endpoints import generate_endpoints, update_anchor_file
from proxy.helper import init_default_logger, write_json
from proxy.heartbeat import send_heartbeat
from proxy.config import (
    CHAIN_INFO_FILEPATH, MONITOR_INTERVAL, TMP_UPSTREAMS_FOLDER, HEARTBEAT_URL
)

logger = logging.getLogger(__name__)


def setup_environment():
    init_default_logger()
    logger.info("Starting FAIR Proxy server")
    Path(TMP_UPSTREAMS_FOLDER).mkdir(parents=True, exist_ok=True)


def main():
    setup_environment()

    while True:
        logger.info("Starting new endpoint collection cycle...")
        nginx_endpoints, healthy_http_list = generate_endpoints()
        if healthy_http_list:
            update_anchor_file(healthy_http_list)
            logger.info(f'The new anchor endpoints: {healthy_http_list}')
        else:
            logger.warning("No healthy endpoints found. Anchor endpoints file will not be updated")
        write_json(CHAIN_INFO_FILEPATH, nginx_endpoints)
        update_nginx_config(nginx_endpoints)
        send_heartbeat(HEARTBEAT_URL)
        logger.info(f"Proxy cycle finished. Sleeping for {MONITOR_INTERVAL}s")
        sleep(MONITOR_INTERVAL)


if __name__ == '__main__':
    main()
