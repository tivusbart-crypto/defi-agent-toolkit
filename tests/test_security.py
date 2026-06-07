"""Tests for DeFi Agent Toolkit."""

import pytest
from defi_agent.core.security import (
    validate_address,
    check_slippage,
    check_price_impact,
    check_contract_trust,
    run_all_checks,
    is_safe,
)


class TestAddressValidation:
    """Test address validation."""

    def test_valid_address(self):
        assert validate_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2") is True

    def test_invalid_address_short(self):
        assert validate_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C") is False

    def test_invalid_address_no_prefix(self):
        assert validate_address("C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2") is False

    def test_invalid_address_empty(self):
        assert validate_address("") is False


class TestSlippageCheck:
    """Test slippage checks."""

    def test_low_slippage(self):
        check = check_slippage(0.5)
        assert check.passed is True
        assert check.risk_level == "low"

    def test_medium_slippage(self):
        check = check_slippage(1.5)
        assert check.passed is True
        assert check.risk_level == "medium"

    def test_high_slippage(self):
        check = check_slippage(3.0)
        assert check.passed is True
        assert check.risk_level == "high"

    def test_excessive_slippage(self):
        check = check_slippage(10.0, max_allowed=5.0)
        assert check.passed is False
        assert check.risk_level == "critical"


class TestPriceImpactCheck:
    """Test price impact checks."""

    def test_low_impact(self):
        check = check_price_impact(0.5)
        assert check.passed is True
        assert check.risk_level == "low"

    def test_high_impact(self):
        check = check_price_impact(4.0)
        assert check.passed is True
        assert check.risk_level == "high"

    def test_excessive_impact(self):
        check = check_price_impact(10.0, max_allowed=5.0)
        assert check.passed is False


class TestContractTrust:
    """Test contract trust checks."""

    def test_trusted_contract(self):
        check = check_contract_trust(
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "ethereum"
        )
        assert check.passed is True
        assert check.risk_level == "low"

    def test_unknown_contract(self):
        check = check_contract_trust(
            "0x0000000000000000000000000000000000000001",
            "ethereum"
        )
        assert check.passed is False
        assert check.risk_level == "medium"


class TestRunAllChecks:
    """Test running all checks."""

    def test_all_pass(self):
        checks = run_all_checks(
            to_address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            chain="ethereum",
            slippage=1.0,
            price_impact=0.5,
        )
        assert is_safe(checks) is True

    def test_invalid_address(self):
        checks = run_all_checks(
            to_address="invalid",
            chain="ethereum",
        )
        assert is_safe(checks) is False
