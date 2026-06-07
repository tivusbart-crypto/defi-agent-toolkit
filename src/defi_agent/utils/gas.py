"""Gas estimation utilities."""

import os
from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass
class GasEstimate:
    """Gas price estimate."""
    chain: str
    base_fee: float  # Gwei
    priority_fee: float  # Gwei
    max_fee: float  # Gwei
    estimated_cost_eth: float
    estimated_cost_usd: float
    speed: str  # 'slow', 'standard', 'fast'


class GasEstimator:
    """Estimates gas prices across chains.

    Usage:
        estimator = GasEstimator()
        gas = estimator.get_gas_price("ethereum", speed="standard")
        print(f"Gas: {gas.max_fee} Gwei (${gas.estimated_cost_usd:.2f})")
    """

    def __init__(self):
        self._alchemy_key = os.environ.get("ALCHEMY_API_KEY", "")
        self._client = httpx.Client(timeout=5.0)

    def get_gas_price(self, chain: str, speed: str = "standard", eth_price: float = 3000.0) -> GasEstimate:
        """Get current gas price estimate.

        Args:
            chain: Chain name
            speed: 'slow', 'standard', or 'fast'
            eth_price: ETH price in USD (for cost estimation)

        Returns:
            GasEstimate with current prices
        """
        # Speed multipliers
        multipliers = {"slow": 0.8, "standard": 1.0, "fast": 1.5}
        multiplier = multipliers.get(speed, 1.0)

        # Default estimates (would be replaced with real API data)
        base_fee = 20.0  # Gwei
        priority_fee = 2.0  # Gwei

        if chain == "base" or chain == "optimism":
            base_fee = 0.01
            priority_fee = 0.001
        elif chain == "arbitrum":
            base_fee = 0.1
            priority_fee = 0.01
        elif chain == "polygon":
            base_fee = 30.0
            priority_fee = 30.0

        max_fee = (base_fee + priority_fee) * multiplier

        # Estimate cost for typical swap (200k gas)
        gas_limit = 200000
        cost_eth = (gas_limit * max_fee * 1e9) / 1e18
        cost_usd = cost_eth * eth_price

        return GasEstimate(
            chain=chain,
            base_fee=base_fee,
            priority_fee=priority_fee,
            max_fee=max_fee,
            estimated_cost_eth=cost_eth,
            estimated_cost_usd=cost_usd,
            speed=speed,
        )

    def close(self):
        """Close HTTP client."""
        self._client.close()
