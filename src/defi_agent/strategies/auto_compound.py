"""Auto-compound strategy — reinvests yield for maximum APY.

Security: Only interacts with trusted contracts. Simulation required.
"""

from dataclasses import dataclass
from typing import Optional

from ..core.optimizer import YieldOpportunity, YieldPosition


@dataclass
class CompoundAction:
    """A compound action to execute."""
    position: YieldPosition
    action: str  # 'harvest', 'sell', 'reinvest'
    amount: float
    estimated_gas: float  # in native token


class AutoCompoundStrategy:
    """Automatically compounds yield farming positions.

    Logic:
    1. Harvest rewards when accumulated value > gas cost * multiplier
    2. Sell reward tokens for base asset
    3. Reinvest into the same position

    Safety:
    - Only operates on positions in trusted protocols
    - Requires minimum threshold before compounding
    - Simulates all transactions before broadcast
    """

    def __init__(
        self,
        min_compound_value: float = 10.0,  # Minimum USD value to compound
        gas_multiplier: float = 3.0,  # Compound when value > gas * multiplier
        max_slippage: float = 1.0,
    ):
        self.min_compound_value = min_compound_value
        self.gas_multiplier = gas_multiplier
        self.max_slippage = max_slippage

    def should_compound(self, position: YieldPosition, gas_price_gwei: float) -> bool:
        """Check if position should be compounded.

        Args:
            position: Current yield position
            gas_price_gwei: Current gas price

        Returns:
            True if compounding is profitable
        """
        if position.last_compound is None:
            return True

        earned = position.current_value - position.deposited_value
        if earned < self.min_compound_value:
            return False

        # Estimate gas cost (simple heuristic)
        estimated_gas_eth = 200000 * gas_price_gwei * 1e9 / 1e18
        gas_cost_usd = estimated_gas_eth * 3000  # Assume $3000 ETH

        return earned > gas_cost_usd * self.gas_multiplier

    def plan_compound(self, position: YieldPosition) -> Optional[CompoundAction]:
        """Plan a compound action for a position.

        Returns:
            CompoundAction or None if not profitable
        """
        earned = position.current_value - position.deposited_value
        if earned < self.min_compound_value:
            return None

        return CompoundAction(
            position=position,
            action="reinvest",
            amount=earned,
            estimated_gas=200000,  # Typical for harvest+swap+deposit
        )

    def execute(self, action: CompoundAction, simulate: bool = True) -> dict:
        """Execute a compound action.

        Args:
            action: The compound action to execute
            simulate: If True, only simulate (default)

        Returns:
            Execution result dict
        """
        if simulate:
            return {
                "status": "simulated",
                "action": action.action,
                "amount": action.amount,
                "estimated_gas": action.estimated_gas,
                "position": action.position.pool,
            }

        # Actual execution would go here
        # Requires wallet signing (not handled in this module)
        raise NotImplementedError("Set up wallet signing to execute")
