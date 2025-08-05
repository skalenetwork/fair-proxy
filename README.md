# FAIR proxy

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

FAIR Proxy is high performance, easy-to-run public service that provides proxied and load-balanced
JSON-RPC endpoints for FAIR chain. It is based on NGINX.

## Usage guide

### Prerequisites

* Docker
* docker-compose

### Repo setup

1. Clone repo & all submodules:

```bash
git clone --recurse-submodules https://github.com/skalenetwork/fair-proxy.git
cd fair-proxy
```

2. Copy `data/anchor_endpoints.json.example` to `data/anchor_endpoints.json` and replace the placeholders with the actual anchor endpoint(s) for initializing the FAIR Manager:

```bash
cp data/anchor_endpoints.json.example data/anchor_endpoints.json
# Edit data/anchor_endpoints.json with your anchor endpoints
```

3. Put `server.crt` and `server.key` files in `data` folder

4. Export required environment variables:

```bash
export FAIR_CONTRACTS=0x1234567890abcdef...  # FAIR Manager contract address or alias
export HEARTBEAT_URL=https://your-heartbeat-url.com/api/push/xyz  # Optional
export USE_ALB=False  # Set to True if behind load balancer
```

5. Start the proxy:

```bash
scripts/run_proxy.sh
```

6. View logs:

```bash
docker compose logs -f
```

7. Stop the proxy:

```bash
docker compose down
```

#### Required files

* The file `data/anchor_endpoints.json` - contains a list of anchor endpoints used to initialize the FAIR Manager object.

#### Required environment variables

* `FAIR_CONTRACTS` - address of `committee` smart contract

#### Optional environment variables

* `HEARTBEAT_URL` - URL for UptimeKuma healthcheck endpoint (optional)
* `USE_ALB` - Set to `True` if the proxy is deployed behind a load balancer (like AWS ALB) that sets the `X-Forwarded-For` header. This configures Nginx to correctly identify the client's real IP address for rate limiting. Defaults to `False` if not set.

## License

[![License](https://img.shields.io/github/license/skalenetwork/skale-proxy.svg)](LICENSE)

All contributions to FAIR Proxy are made under the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html). See [LICENSE](LICENSE).

Copyright (C) 2025-Present SKALE Labs.
