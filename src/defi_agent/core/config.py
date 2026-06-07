"""Configuration management."""

import os
from pathlib import Path
from typing import Optional

import yaml


class Config:
    """Configuration manager.

    Loads config from:
    1. Environment variables (highest priority)
    2. .env file
    3. config/default.yaml
    """

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path("config")
        self._config: dict = {}
        self._load()

    def _load(self):
        """Load configuration."""
        # Load default config
        default_path = self.config_dir / "default.yaml"
        if default_path.exists():
            with open(default_path) as f:
                self._config = yaml.safe_load(f) or {}

        # Override with environment variables
        self._env_overrides()

    def _env_overrides(self):
        """Override config with environment variables."""
        env_map = {
            "ETH_RPC_URL": ("chains", "ethereum", "rpc_url"),
            "BASE_RPC_URL": ("chains", "base", "rpc_url"),
            "ARB_RPC_URL": ("chains", "arbitrum", "rpc_url"),
            "POLYGON_RPC_URL": ("chains", "polygon", "rpc_url"),
            "OP_RPC_URL": ("chains", "optimism", "rpc_url"),
            "ONEINCH_API_KEY": ("api_keys", "1inch"),
            "ZERORX_API_KEY": ("api_keys", "0x"),
            "PARASWAP_API_KEY": ("api_keys", "paraswap"),
        }

        for env_var, path in env_map.items():
            value = os.environ.get(env_var)
            if value:
                self._set_nested(path, value)

    def _set_nested(self, path: tuple, value):
        """Set nested dict value."""
        d = self._config
        for key in path[:-1]:
            d = d.setdefault(key, {})
        d[path[-1]] = value

    def get(self, *keys, default=None):
        """Get config value by nested keys."""
        d = self._config
        for key in keys:
            if isinstance(d, dict):
                d = d.get(key)
                if d is None:
                    return default
            else:
                return default
        return d

    @property
    def rpc_urls(self) -> dict[str, str]:
        """Get RPC URLs for all chains."""
        chains = self._config.get("chains", {})
        return {name: cfg.get("rpc_url", "") for name, cfg in chains.items()}

    @property
    def api_keys(self) -> dict[str, str]:
        """Get API keys (for internal use only)."""
        return self._config.get("api_keys", {})
