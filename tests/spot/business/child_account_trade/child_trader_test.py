from unittest.mock import MagicMock
import unittest
from src.spot.business.child_account_trade.child_trader import ChildTrader
from src.spot.persistence.child_account_trade.child_account_repository import ChildAccountRepository as SpotChildAccountRepository
from src.spot.persistence.child_account_trade.child_account_entity_manager import ChildAccountEntityManager as SpotChildAccountEntityManager
from binance.client import Client


class ChildTraderTest(unittest.TestCase):

    def test_get_calculated_limit_order_qty_based_on_deposit_successful_buy(self):
        child_client_mock = MagicMock(autospec=Client())
        child_client_mock.get_asset_balance = MagicMock(
            return_value={'free': 45, 'locked': 0, 'asset': 'BTC'}
        )
        main_order_mock = {
            'id_main_account_order_history': '1',
            'status': 'NEW',
            'symbol': 'BTC',
            'price': 9000,
            'stop_price': '',
            'original_qty': 0.005033,
            'cummulative_quote_qty': '',
            'order_id': '',
            'created_at': '',
            'updated_at': '',
            'side': 'BUY',
            'type': 'LIMIT',
            'time_in_force': '',
            'is_market_trade_cloned': ''
        }
        main_client_mock = MagicMock(autospec=Client())
        main_client_mock.get_asset_balance = MagicMock(return_value={'free': 0, 'locked': 45, 'asset': 'BTC'})

        spot_child_trader = ChildTrader(
            MagicMock(autospec=SpotChildAccountRepository),
            MagicMock(autospec=SpotChildAccountEntityManager)
        )
        spot_child_trader.main_account_client = main_client_mock

        expected_value = 0.004999
        actual_value = spot_child_trader._get_calculated_limit_order_qty_based_on_deposit(
            child_client_mock, main_order_mock
        )

        self.assertEqual(actual_value, expected_value)

    def test_get_calculated_limit_order_qty_based_on_deposit_successful_sell(self):
        child_client_mock = MagicMock(autospec=Client())
        child_client_mock.get_asset_balance = MagicMock(
            return_value={'free': 45, 'locked': 0, 'asset': 'BTC'}
        )

        main_order_mock = {
          'id_main_account_order_history': '1',
          'status': 'NEW',
          'symbol': 'BTC',
          'price': 9000,
          'stop_price': '',
          'original_qty': 0.005033,
          'cummulative_quote_qty': '',
          'order_id': '',
          'created_at': '',
          'updated_at': '',
          'side': 'SELL',
          'type': 'LIMIT',
          'time_in_force': '',
          'is_market_trade_cloned': ''
        }
        main_client_mock = MagicMock(autospec=Client())
        main_client_mock.get_asset_balance = MagicMock(return_value={'free': 0, 'locked': 45, 'asset': 'BTC'})

        spot_child_trader = ChildTrader(
            MagicMock(autospec=SpotChildAccountRepository),
            MagicMock(autospec=SpotChildAccountEntityManager)
        )
        spot_child_trader.main_account_client = main_client_mock

        expected_value = 44.999999
        actual_value = spot_child_trader._get_calculated_limit_order_qty_based_on_deposit(
            child_client_mock, main_order_mock
        )

        self.assertEqual(actual_value, expected_value)


