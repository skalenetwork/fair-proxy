# FAIR proxy

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

FAIR Proxy is high performance, easy-to-run public service that provides proxied and load-balanced
JSON-RPC endpoints for FAIR chain. It is based on NGINX.

## Usage guide

### Prerequisites

- Docker
- docker-compose

### Repo setup

1. Clone repo & all submodules
2. Copy `data/anchor_endpoints.json.example` to `data/anchor_endpoints.json` and replace the placeholders with the actual anchor endpoint(s) for initializing the FAIR Manager.
3. Put `server.crt` and `server.key` files in `data` folder
4. Export all required environment variables (see below)
5. Run `scripts/run_proxy.sh`

#### Required files

- The file `data/anchor_endpoints.json` - contains a list of anchor endpoints used to initialize the FAIR Manager object. 

#### Required environment variables

- `FAIR_CONTRACTS` - address of `committee` smart contract

#### Optional environment variables

- `HEARTBEAT_URL` - URL for UptimeKuma healthcheck endpoint (optional)
- `USE_ALB` - Set to `True` if the proxy is deployed behind a load balancer (like AWS ALB) that sets the `X-Forwarded-For` header. This configures Nginx to correctly identify the client's real IP address for rate limiting. Defaults to `False` if not set.


## License

[![License](https://img.shields.io/github/license/skalenetwork/skale-proxy.svg)](LICENSE)

All contributions to FAIR Proxy are made under the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html). See [LICENSE](LICENSE).

Copyright (C) 2025-Present SKALE Labs.