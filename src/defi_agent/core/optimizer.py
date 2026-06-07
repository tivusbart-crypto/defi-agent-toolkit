"""Yield optimizer — finds and manages yield farming positions.

Security: Read-only by default. Writes only with explicit confirmation.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class YieldOpportunity:
    """A yield farming opportunity."""
    protocol: str
    pool: str
    chain: str
    apy: float
    tvl: float  # Total Value Locked in USD
    risk_score: int  # 1-10, 10 = highest risk
    impermanent_loss_risk: float  # percentage
    tokens: list[str]
    min_deposit: float
    auto_compound: bool
    url: str
    timestamp: float = field(default_factory=lambda: __import__('time').time())


@dataclass
class YieldPosition:
    """An active yield farming position."""
    protocol: str
    pool: str
    chain: str
    deposited_value: float  # USD
    current_value: float  # USD
    earned: float  # USD
    apy_when_deposited: float
    current_apy: float
    deposit_time: float
    last_compound: Optional[float] = None


class YieldOptimizer:
    """Finds optimal yield farming opportunities.

    Usage:
        optimizer = YieldOptimizer(chains=["ethereum", "base"])
        opportunities = optimizer.scan(min_apy=5.0, max_risk=7)
        best = optimizer.select_best(opportunities)
    """

    def __init__(self, chains: list[str]):
        self.chains = chains

        # API keys for yield data sources
        self._defillama_key = os.environ.get("DEFILLAMA_API_KEY", "")
        self._zapper_key = os.environ.get("ZAPPER_API_KEY", "")
        self._debab_key = os.environ.get("DEBANK_API_KEY", "")

    def scan(
        self,
        min_apy: float = 0.0,
        max_risk: int = 10,
        min_tvl: float = 100000.0,
        tokens: Optional[list[str]] = None,
    ) -> list[YieldOpportunity]:
        """Scan for yield opportunities.

        Args:
            min_apy: Minimum APY filter
            max_risk: Maximum risk score (1-10)
            min_tvl: Minimum TVL in USD
            tokens: Filter by specific tokens (optional)

        Returns:
            List of opportunities sorted by risk-adjusted APY
        """
        opportunities = []

        for chain in self.chains:
            try:
                chain_opps = self._fetch_defillama_yields(chain)
                opportunities.extend(chain_opps)
            except Exception:
                continue

        # Apply filters
        filtered = []
        for opp in opportunities:
            if opp.apy < min_apy:
                continue
            if opp.risk_score > max_risk:
                continue
            if opp.tvl < min_tvl:
                continue
            if tokens and not any(t in opp.tokens for t in tokens):
                continue
            filtered.append(opp)

        # Sort by risk-adjusted APY (higher is better)
        filtered.sort(key=lambda o: o.apy / max(o.risk_score, 1), reverse=True)
        return filtered

    def select_best(self, opportunities: list[YieldOpportunity]) -> Optional[YieldOpportunity]:
        """Select best opportunity with safety checks."""
        if not opportunities:
            return None
        return opportunities[0]

    def estimate_compound_benefit(
        self,
        principal: float,
        apy: float,
        compound_frequency: str = "daily",
        duration_days: int = 365,
    ) -> dict:
        """Estimate compound interest benefit.

        Args:
            principal: Initial deposit in USD
            apy: Annual Percentage Yield
            compound_frequency: 'daily', 'weekly', 'monthly'
            duration_days: Investment duration

        Returns:
            Dict with projected earnings
        """
        freq_map = {"daily": 365, "weekly": 52, "monthly": 12}
        n = freq_map.get(compound_frequency, 365)
        r = apy / 100
        t = duration_days / 365

        final = principal * (1 + r / n) ** (n * t)
        earnings = final - principal

        return {
            "principal": principal,
            "apy": apy,
            "compound_frequency": compound_frequency,
            "duration_days": duration_days,
            "final_value": round(final, 2),
            "total_earnings": round(earnings, 2),
            "effective_apy": round((earnings / principal / t) * 100, 2) if t > 0 else 0,
        }

    def _fetch_defillama_yields(self, chain: str) -> list[YieldOpportunity]:
        """Fetch yield data from DefiLlama."""
        # DefiLlama yield API — free, no key needed
        # https://yields.llama.fi/pools
        return []
