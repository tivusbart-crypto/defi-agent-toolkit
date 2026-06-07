"""Chain configuration and management."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ChainConfig:
    """Chain configuration."""
    chain_id: int
    name: str
    rpc_url: str
    native_token: str
    wrapped_native: str
    block_explorer: str
    dex_aggregators: list[str]
    avg_block_time: float  # seconds


# Supported chains — RPC URLs loaded from env, not hardcoded
SUPPORTED_CHAINS: Dict[str, ChainConfig] = {
    "ethereum": ChainConfig(
        chain_id=1,
        name="Ethereum",
        rpc_url="",  # Loaded from ETH_RPC_URL env
        native_token="ETH",
        wrapped_native="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        block_explorer="https://etherscan.io",
        dex_aggregators=["1inch", "0x", "paraswap"],
        avg_block_time=12.0,
    ),
    "base": ChainConfig(
        chain_id=8453,
        name="Base",
        rpc_url="",  # Loaded from BASE_RPC_URL env
        native_token="ETH",
        wrapped_native="0x4200000000000000000000000000000000000006",
        block_explorer="https://basescan.org",
        dex_aggregators=["1inch", "0x"],
        avg_block_time=2.0,
    ),
    "arbitrum": ChainConfig(
        chain_id=42161,
        name="Arbitrum One",
        rpc_url="",  # Loaded from ARB_RPC_URL env
        native_token="ETH",
        wrapped_native="0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        block_explorer="https://arbiscan.io",
        dex_aggregators=["1inch", "0x", "paraswap"],
        avg_block_time=0.25,
    ),
    "polygon": ChainConfig(
        chain_id=137,
        name="Polygon",
        rpc_url="",  # Loaded from POLYGON_RPC_URL env
        native_token="MATIC",
        wrapped_native="0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
        block_explorer="https://polygonscan.com",
        dex_aggregators=["1inch", "0x", "paraswap"],
        avg_block_time=2.0,
    ),
    "optimism": ChainConfig(
        chain_id=10,
        name="Optimism",
        rpc_url="",  # Loaded from OP_RPC_URL env
        native_token="ETH",
        wrapped_native="0x4200000000000000000000000000000000000006",
        block_explorer="https://optimistic.etherscan.io",
        dex_aggregators=["1inch", "0x"],
        avg_block_time=2.0,
    ),
}


def get_chain(name: str) -> Optional[ChainConfig]:
    """Get chain config by name."""
    return SUPPORTED_CHAINS.get(name.lower())


def list_chains() -> list[str]:
    """List supported chain names."""
    return list(SUPPORTED_CHAINS.keys())
