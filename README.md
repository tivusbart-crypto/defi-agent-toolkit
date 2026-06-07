# 🤖 DeFi Agent Toolkit

> AI-powered DeFi automation toolkit — swap routing, yield optimization, portfolio management across multiple chains.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-brightgreen)](https://wardiinari3-collab.github.io/defi-agent-toolkit/)

## ✨ Features

- **🔄 Smart Swap Router** — Find best rates across 1inch, 0x, 1inch, Paraswap
- **🌾 Yield Optimizer** — Auto-compound and rebalance yield farming positions
- **📊 Portfolio Tracker** — Real-time portfolio valuation across chains
- **🔐 Non-Custodial** — Keys never leave your environment
- **⛓️ Multi-Chain** — Ethereum, Base, Arbitrum, Polygon, Optimism
- **🤖 AI-Powered** — Intelligent routing, gas optimization, timing suggestions
- **⌨️ CLI + API** — Use from terminal or integrate into your apps

## 🚀 Quick Start

```bash
# Install
pip install -e .

# Configure (NEVER commit .env)
cp .env.example .env
# Edit .env with your RPC endpoints and API keys

# Run
defi-agent swap --from ETH --to USDC --amount 0.1 --chain ethereum
defi-agent yield --action optimize --chain base
defi-agent portfolio --address 0x... --chains ethereum,base
```

## 🔐 Security

- **Zero key storage** — Private keys loaded from environment only
- **No telemetry** — No data leaves your machine
- **Simulation first** — All transactions simulated before broadcast
- **Slippage protection** — Configurable max slippage with auto-revert
- **Allowlist only** — Only interact with verified contracts

See [SECURITY.md](SECURITY.md) for full security policy.

## 📖 Documentation

- [Quick Start Guide](docs/quickstart.md)
- [Configuration](docs/configuration.md)
- [Supported Chains](docs/chains.md)
- [API Reference](docs/api.md)
- [Security Best Practices](docs/security.md)

## 📁 Project Structure

```
defi-agent-toolkit/
├── src/defi_agent/
│   ├── core/           # Core engine (router, optimizer, portfolio)
│   ├── chains/         # Chain-specific adapters
│   ├── strategies/     # Yield strategies
│   └── utils/          # Helpers (gas, pricing, validation)
├── config/             # Default configs (no secrets)
├── tests/              # Unit + integration tests
├── docs/               # Documentation
├── examples/           # Usage examples
└── index.html          # Landing page
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
