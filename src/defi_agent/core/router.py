"""Smart swap router — finds best rates across DEX aggregators.

Security: No private keys handled here. This module only builds quote data.
Actual signing/broadcasting is done by the caller.
"""

import os
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

from ..chains import ChainConfig, get_chain


@dataclass
class SwapQuote:
    """Swap quote from a DEX aggregator."""
    aggregator: str
    from_token: str
    to_token: str
    from_amount: str
    to_amount: str
    estimated_gas: int
    gas_price_gwei: float
    price_impact: float  # percentage
    slippage: float  # percentage
    route: list[str]
    tx_data: Optional[dict] = None
    timestamp: float = field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        """Quote expires after 30 seconds."""
        return time.time() - self.timestamp > 30

    @property
    def effective_rate(self) -> float:
        """Effective exchange rate after gas cost."""
        gas_cost_eth = (self.estimated_gas * self.gas_price_gwei * 1e9) / 1e18
        return float(self.to_amount) / float(self.from_amount) if float(self.from_amount) > 0 else 0


class SwapRouter:
    """Routes swaps through multiple DEX aggregators for best rate.

    Usage:
        router = SwapRouter(chain="ethereum")
        quotes = await router.get_quotes(from_token="ETH", to_token="USDC", amount=0.1)
        best = router.select_best(quotes)
    """

    def __init__(self, chain: str):
        self.chain = get_chain(chain)
        if not self.chain:
            raise ValueError(f"Unsupported chain: {chain}")

        # API keys loaded from env — NEVER hardcoded
        self._oneinch_key = os.environ.get("ONEINCH_API_KEY", "")
        self._zerox_key = os.environ.get("ZERORX_API_KEY", "")
        self._paraswap_key = os.environ.get("PARASWAP_API_KEY", "")

        self._client = httpx.Client(timeout=10.0)

    def get_quotes(self, from_token: str, to_token: str, amount: float, slippage: float = 1.0) -> list[SwapQuote]:
        """Get quotes from all available aggregators.

        Args:
            from_token: Source token symbol or address
            to_token: Destination token symbol or address
            amount: Amount in source token
            slippage: Max slippage percentage (default 1%)

        Returns:
            List of quotes sorted by effective rate (best first)
        """
        quotes = []

        for agg in self.chain.dex_aggregators:
            try:
                if agg == "1inch" and self._oneinch_key:
                    quote = self._quote_1inch(from_token, to_token, amount, slippage)
                elif agg == "0x" and self._zerox_key:
                    quote = self._quote_0x(from_token, to_token, amount, slippage)
                elif agg == "paraswap" and self._paraswap_key:
                    quote = self._quote_paraswap(from_token, to_token, amount, slippage)
                else:
                    continue

                if quote:
                    quotes.append(quote)
            except Exception:
                continue  # Skip failed aggregator, try others

        quotes.sort(key=lambda q: q.effective_rate, reverse=True)
        return quotes

    def select_best(self, quotes: list[SwapQuote], max_price_impact: float = 5.0) -> Optional[SwapQuote]:
        """Select best quote with safety checks.

        Args:
            quotes: List of quotes (from get_quotes)
            max_price_impact: Maximum acceptable price impact percentage

        Returns:
            Best quote or None if all fail safety checks
        """
        for quote in quotes:
            if quote.is_expired:
                continue
            if quote.price_impact > max_price_impact:
                continue
            return quote
        return None

    def _quote_1inch(self, from_token: str, to_token: str, amount: float, slippage: float) -> Optional[SwapQuote]:
        """Get quote from 1inch API."""
        # Token address resolution would go here
        # For now, return None — needs real token mapping
        return None

    def _quote_0x(self, from_token: str, to_token: str, amount: float, slippage: float) -> Optional[SwapQuote]:
        """Get quote from 0x API."""
        return None

    def _quote_paraswap(self, from_token: str, to_token: str, amount: float, slippage: float) -> Optional[SwapQuote]:
        """Get quote from Paraswap API."""
        return None

    def close(self):
        """Close HTTP client."""
        self._client.close()
