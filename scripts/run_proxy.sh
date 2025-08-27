#!/bin/bash

set -e

: "${FAIR_CONTRACTS?Need to set FAIR_CONTRACTS}"
: "${USE_ALB:=False}"

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR=$(dirname $SCRIPT_DIR)

CONFIG_DIR="$PROJECT_DIR/config"
TEMPLATE_FILE="$CONFIG_DIR/nginx.conf.template"
TARGET_FILE="$CONFIG_DIR/nginx.conf"

DATA_DIR="$PROJECT_DIR/data"
ANCHOR_FILE="$DATA_DIR/anchor_endpoints.json"

REAL_IP_START_MARKER="#REAL_IP_CONFIG_START"
REAL_IP_END_MARKER="#REAL_IP_CONFIG_END"

SSL_START_MARKER="#SSL_CONFIG_START"
SSL_END_MARKER="#SSL_CONFIG_END"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "ERROR: Nginx template file is not found at $TEMPLATE_FILE"
    exit 1
fi

if [ ! -f "$ANCHOR_FILE" ]; then
    echo "ERROR: Anchor endpoints file is not found at $ANCHOR_FILE"
    exit 1
fi


if [[ "$USE_ALB" == "True" ]]; then
    # Remove the SSL configuration block between markers from the template
    sed "/${SSL_START_MARKER}/,/${SSL_END_MARKER}/d" "$TEMPLATE_FILE" > "$TARGET_FILE"
else
    # Remove the ALB real IP configuration block between markers from the template
    sed "/${START_MARKER}/,/${END_MARKER}/d" "$TEMPLATE_FILE" > "$TARGET_FILE"
fi

cd "$PROJECT_DIR"
docker compose up --build -d
