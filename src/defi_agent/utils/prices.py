"""Price fetching utilities."""

import os
from typing import Optional

import httpx


class PriceFetcher:
    """Fetches token prices from multiple sources.

    Usage:
        fetcher = PriceFetcher()
        price = fetcher.get_price("ETH")
        prices = fetcher.get_prices(["ETH", "USDC", "WBTC"])
    """

    def __init__(self):
        self._coingecko_key = os.environ.get("COINGECKO_API_KEY", "")
        self._client = httpx.Client(timeout=5.0)
        self._cache: dict[str, tuple[float, float]] = {}  # symbol -> (price, timestamp)

    def get_price(self, symbol: str) -> Optional[float]:
        """Get USD price for a token symbol.

        Args:
            symbol: Token symbol (e.g., 'ETH', 'USDC')

        Returns:
            Price in USD or None if not found
        """
        prices = self.get_prices([symbol])
        return prices.get(symbol)

    def get_prices(self, symbols: list[str]) -> dict[str, float]:
        """Get USD prices for multiple tokens.

        Args:
            symbols: List of token symbols

        Returns:
            Dict mapping symbol to USD price
        """
        import time

        result = {}
        to_fetch = []

        # Check cache (5 minute TTL)
        for symbol in symbols:
            if symbol in self._cache:
                price, ts = self._cache[symbol]
                if time.time() - ts < 300:
                    result[symbol] = price
                else:
                    to_fetch.append(symbol)
            else:
                to_fetch.append(symbol)

        if not to_fetch:
            return result

        # Would fetch from CoinGecko/DeFiLlama
        # For now, return cached or empty
        return result

    def close(self):
        """Close HTTP client."""
        self._client.close()
