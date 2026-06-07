"""Command-line interface for DeFi Agent Toolkit."""

import argparse
import sys

from .. import __version__
from ..chains import list_chains
from ..core.optimizer import YieldOptimizer
from ..core.portfolio import PortfolioTracker
from ..core.router import SwapRouter
from ..core.security import run_all_checks
from ..utils.gas import GasEstimator


def cmd_swap(args):
    """Handle swap command."""
    print(f"\n🔄 Swap: {args.amount} {args.from_token} → {args.to_token}")
    print(f"   Chain: {args.chain}")
    print(f"   Max slippage: {args.slippage}%")

    router = SwapRouter(chain=args.chain)
    quotes = router.get_quotes(
        from_token=args.from_token,
        to_token=args.to_token,
        amount=args.amount,
        slippage=args.slippage,
    )

    if not quotes:
        print("   ❌ No quotes found")
        return

    best = router.select_best(quotes)
    if best:
        print(f"\n   Best route: {best.aggregator}")
        print(f"   Output: {best.to_amount} {args.to_token}")
        print(f"   Price impact: {best.price_impact}%")
        print(f"   Gas: ~${best.estimated_gas * best.gas_price_gwei * 1e9 / 1e18 * 3000:.2f}")

        # Run security checks
        checks = run_all_checks(
            to_address=best.tx_data.get("to", "") if best.tx_data else "",
            chain=args.chain,
            slippage=args.slippage,
            price_impact=best.price_impact,
        )

        print("\n   Security checks:")
        for check in checks:
            icon = "✅" if check.passed else "❌"
            print(f"   {icon} {check.check_name}: {check.message}")
    else:
        print("   ❌ No safe routes found")

    router.close()


def cmd_yield(args):
    """Handle yield command."""
    print(f"\n🌾 Yield Optimizer")
    print(f"   Chains: {', '.join(args.chains)}")
    print(f"   Min APY: {args.min_apy}%")
    print(f"   Max risk: {args.max_risk}/10")

    optimizer = YieldOptimizer(chains=args.chains)
    opportunities = optimizer.scan(
        min_apy=args.min_apy,
        max_risk=args.max_risk,
        min_tvl=args.min_tvl,
    )

    if not opportunities:
        print("   ❌ No opportunities found")
        return

    print(f"\n   Found {len(opportunities)} opportunities:")
    for i, opp in enumerate(opportunities[:5], 1):
        print(f"\n   {i}. {opp.protocol} - {opp.pool}")
        print(f"      APY: {opp.apy:.2f}% | TVL: ${opp.tvl:,.0f} | Risk: {opp.risk_score}/10")
        print(f"      Tokens: {', '.join(opp.tokens)}")


def cmd_portfolio(args):
    """Handle portfolio command."""
    print(f"\n📊 Portfolio: {args.address}")
    print(f"   Chains: {', '.join(args.chains)}")

    tracker = PortfolioTracker()
    snapshot = tracker.get_portfolio(address=args.address, chains=args.chains)

    print(f"\n   Total value: ${snapshot.total_value_usd:,.2f}")

    if snapshot.tokens:
        print(f"\n   Holdings ({len(snapshot.tokens)} tokens):")
        for token in snapshot.top_holdings[:5]:
            print(f"   • {token.symbol}: ${token.value_usd:,.2f} ({token.chain})")
    else:
        print("   No tokens found")


def cmd_gas(args):
    """Handle gas command."""
    estimator = GasEstimator()

    for chain in args.chains:
        gas = estimator.get_gas_price(chain, speed=args.speed)
        print(f"\n⛽ {chain.capitalize()}")
        print(f"   Base fee: {gas.base_fee:.2f} Gwei")
        print(f"   Priority: {gas.priority_fee:.2f} Gwei")
        print(f"   Max fee: {gas.max_fee:.2f} Gwei")
        print(f"   Est. cost: {gas.estimated_cost_eth:.6f} ETH (${gas.estimated_cost_usd:.2f})")

    estimator.close()


def cmd_chains(args):
    """Handle chains command."""
    chains = list_chains()
    print("\n⛓️ Supported chains:")
    for chain in chains:
        print(f"   • {chain}")


def cmd_version(args):
    """Handle version command."""
    print(f"DeFi Agent Toolkit v{__version__}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="defi-agent",
        description="🤖 DeFi Agent Toolkit — AI-powered DeFi automation",
    )
    parser.add_argument("--version", action="store_true", help="Show version")
    subparsers = parser.add_subparsers(dest="command")

    # Swap command
    swap_parser = subparsers.add_parser("swap", help="Find best swap route")
    swap_parser.add_argument("--from", dest="from_token", required=True, help="Source token")
    swap_parser.add_argument("--to", dest="to_token", required=True, help="Destination token")
    swap_parser.add_argument("--amount", type=float, required=True, help="Amount to swap")
    swap_parser.add_argument("--chain", default="ethereum", help="Chain name")
    swap_parser.add_argument("--slippage", type=float, default=1.0, help="Max slippage %")
    swap_parser.set_defaults(func=cmd_swap)

    # Yield command
    yield_parser = subparsers.add_parser("yield", help="Find yield opportunities")
    yield_parser.add_argument("--chains", nargs="+", default=["ethereum", "base"], help="Chains to scan")
    yield_parser.add_argument("--min-apy", type=float, default=0.0, help="Minimum APY %")
    yield_parser.add_argument("--max-risk", type=int, default=7, help="Max risk score (1-10)")
    yield_parser.add_argument("--min-tvl", type=float, default=100000, help="Minimum TVL $")
    yield_parser.set_defaults(func=cmd_yield)

    # Portfolio command
    portfolio_parser = subparsers.add_parser("portfolio", help="Track portfolio")
    portfolio_parser.add_argument("--address", required=True, help="Wallet address")
    portfolio_parser.add_argument("--chains", nargs="+", default=["ethereum", "base"], help="Chains")
    portfolio_parser.set_defaults(func=cmd_portfolio)

    # Gas command
    gas_parser = subparsers.add_parser("gas", help="Check gas prices")
    gas_parser.add_argument("--chains", nargs="+", default=["ethereum"], help="Chains")
    gas_parser.add_argument("--speed", default="standard", choices=["slow", "standard", "fast"])
    gas_parser.set_defaults(func=cmd_gas)

    # Chains command
    chains_parser = subparsers.add_parser("chains", help="List supported chains")
    chains_parser.set_defaults(func=cmd_chains)

    args = parser.parse_args()

    if args.version:
        cmd_version(args)
    elif hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
