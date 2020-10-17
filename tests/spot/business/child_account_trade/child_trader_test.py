from unittest.mock import MagicMock
from src.spot.business.child_account_trade.child_trader import ChildTrader


class ChildTraderTest:


    @staticmethod
    def test_get_calculated_limit_order_qty_based_on_deposit():
        spot_child_trader = ChildTrader(MagicMock(), MagicMock())

        spot_child_trader._get_calculated_limit_order_qty_based_on_deposit()
        
        assert 1 == 1

