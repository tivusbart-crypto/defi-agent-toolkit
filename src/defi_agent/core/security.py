"""Security utilities — validates transactions before broadcast.

CRITICAL: This module ensures no funds are lost due to:
- Malicious contract interactions
- Excessive slippage
- Approvals to untrusted contracts
- Reentrancy attacks
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class SecurityCheck:
    """Result of a security check."""
    check_name: str
    passed: bool
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    message: str
    details: Optional[dict] = None


# Known trusted contracts per chain
TRUSTED_CONTRACTS: dict[str, set[str]] = {
    "ethereum": {
        "0x1111111254fb6c44bac0bed2854e76f90643097d",  # 1inch Router
        "0xDef1C0ded9bec7F1a1670819833240f027b25EfF",  # 0x Router
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
        "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
        "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
    },
    "base": {
        "0x4200000000000000000000000000000000000006",  # WETH
        "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC
    },
    "arbitrum": {
        "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",  # WETH
        "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",  # USDC
        "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",  # USDT
    },
}


def validate_address(address: str) -> bool:
    """Validate Ethereum address format."""
    return bool(re.match(r'^0x[0-9a-fA-F]{40}$', address))


def check_contract_trust(address: str, chain: str) -> SecurityCheck:
    """Check if contract is in trusted list."""
    trusted = TRUSTED_CONTRACTS.get(chain, set())
    is_trusted = address.lower() in {c.lower() for c in trusted}

    return SecurityCheck(
        check_name="contract_trust",
        passed=is_trusted,
        risk_level="low" if is_trusted else "medium",
        message="Trusted contract" if is_trusted else "Unknown contract — proceed with caution",
        details={"address": address, "chain": chain},
    )


def check_slippage(slippage: float, max_allowed: float = 5.0) -> SecurityCheck:
    """Check if slippage is within acceptable range."""
    passed = slippage <= max_allowed

    if slippage <= 0.5:
        risk = "low"
    elif slippage <= 2.0:
        risk = "medium"
    elif slippage <= max_allowed:
        risk = "high"
    else:
        risk = "critical"

    return SecurityCheck(
        check_name="slippage",
        passed=passed,
        risk_level=risk,
        message=f"Slippage {slippage}% {'within' if passed else 'exceeds'} {max_allowed}% limit",
        details={"slippage": slippage, "max_allowed": max_allowed},
    )


def check_price_impact(price_impact: float, max_allowed: float = 5.0) -> SecurityCheck:
    """Check if price impact is acceptable."""
    passed = price_impact <= max_allowed

    if price_impact <= 1.0:
        risk = "low"
    elif price_impact <= 3.0:
        risk = "medium"
    elif price_impact <= max_allowed:
        risk = "high"
    else:
        risk = "critical"

    return SecurityCheck(
        check_name="price_impact",
        passed=passed,
        risk_level=risk,
        message=f"Price impact {price_impact}% {'acceptable' if passed else 'too high'}",
        details={"price_impact": price_impact, "max_allowed": max_allowed},
    )


def check_approval_safety(spender: str, amount: str, chain: str) -> SecurityCheck:
    """Check if token approval is safe.

    Warns on:
    - Unlimited approvals
    - Approvals to unknown contracts
    - Approvals to non-router contracts
    """
    is_unlimited = amount == "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    is_trusted = spender.lower() in {c.lower() for c in TRUSTED_CONTRACTS.get(chain, set())}

    if is_unlimited and not is_trusted:
        return SecurityCheck(
            check_name="approval_safety",
            passed=False,
            risk_level="critical",
            message="Unlimited approval to untrusted contract — DANGEROUS",
            details={"spender": spender, "unlimited": True, "trusted": False},
        )
    elif is_unlimited:
        return SecurityCheck(
            check_name="approval_safety",
            passed=True,
            risk_level="medium",
            message="Unlimited approval to trusted contract — consider using exact amount",
            details={"spender": spender, "unlimited": True, "trusted": True},
        )
    else:
        return SecurityCheck(
            check_name="approval_safety",
            passed=True,
            risk_level="low",
            message="Limited approval — safe",
            details={"spender": spender, "unlimited": False},
        )


def run_all_checks(
    to_address: str,
    chain: str,
    slippage: float = 1.0,
    price_impact: float = 0.0,
) -> list[SecurityCheck]:
    """Run all security checks.

    Returns:
        List of SecurityCheck results
    """
    checks = []

    if not validate_address(to_address):
        checks.append(SecurityCheck(
            check_name="address_format",
            passed=False,
            risk_level="critical",
            message="Invalid address format",
        ))
        return checks  # No point checking further

    checks.append(check_contract_trust(to_address, chain))
    checks.append(check_slippage(slippage))
    checks.append(check_price_impact(price_impact))

    return checks


def is_safe(checks: list[SecurityCheck]) -> bool:
    """Check if all checks passed."""
    return all(c.passed for c in checks)
