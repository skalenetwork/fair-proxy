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
import os
import shutil
import time
from pathlib import Path

import docker

from proxy.config import (
    CONTAINER_RUNNING_STATUS,
    NGINX_CONTAINER_NAME,
    TMP_UPSTREAMS_FOLDER,
    UPSTREAM_NGINX_TEMPLATE,
    UPSTREAMS_FOLDER,
)
from proxy.helper import process_template

logger = logging.getLogger(__name__)
docker_client = docker.DockerClient()


def update_nginx_config(chain_endpoints: dict) -> None:
    process_nginx_config_template(chain_endpoints)
    move_nginx_config()
    monitor_nginx_container()


def move_nginx_config():
    """Moves Nginx config from the temporary directory to the main folder"""
    logger.info('Moving Nginx config from temporary directory...')
    shutil.rmtree(UPSTREAMS_FOLDER, ignore_errors=True)
    shutil.move(TMP_UPSTREAMS_FOLDER, UPSTREAMS_FOLDER)
    Path(TMP_UPSTREAMS_FOLDER).mkdir(parents=True, exist_ok=True)
    logger.info('Nginx config moved')


def monitor_nginx_container(d_client=None):
    logger.info('Going to restart Nginx container')
    d_client = d_client or docker_client
    nginx_container = d_client.containers.get(NGINX_CONTAINER_NAME)

    if is_container_running(nginx_container):
        reload_nginx(nginx_container)
    else:
        logger.info('Nginx container is not running, trying to restart')
        nginx_container.restart()


def reload_nginx(container) -> int:
    """Safely reloads Nginx configuration"""
    logger.info("Waiting briefly before reloading Nginx...")
    time.sleep(0.5)
    logger.info("Sending reload command to Nginx...")
    exit_code, output = container.exec_run(cmd='nginx -s reload')
    if exit_code != 0:
        logger.warning(
            "Could not reload Nginx configuration. "
            f"Exit Code: {exit_code}\n"
            f"Output: {output.decode('utf-8').strip()}"
        )
    else:
        logger.info('Successfully reloaded Nginx service')

    return exit_code


def is_container_running(container) -> bool:
    return container.status == CONTAINER_RUNNING_STATUS


def process_nginx_config_template(chain_info: dict) -> None:
    upstream_dest = os.path.join(TMP_UPSTREAMS_FOLDER, 'fair.conf')
    process_template(UPSTREAM_NGINX_TEMPLATE, upstream_dest, chain_info)


if __name__ == '__main__':
    process_nginx_config_template({})
