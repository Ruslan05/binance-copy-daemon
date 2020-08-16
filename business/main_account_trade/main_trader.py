from binance.client import Client
from binance.exceptions import BinanceAPIException
import config


class MainTrader:

    def __init__(self, main_account_repository, main_account_entity_manager):
        self.main_account_repository = main_account_repository
        self.main_account_entity_manager = main_account_entity_manager
        self.client = Client(config.main_account_api_key, config.main_account_api_secret)

    def sync_main_account_trades(self):
        self._sync_active_trades()
        self._sync_market_trades()
        self._sync_closed_trades()

    def _sync_active_trades(self):
        #TODO: create main cursor like this

        for allowed_symbol in config.ALLOWED_SYMBOLS:
            active_trades = self.client.get_open_orders(symbol=allowed_symbol)

            for active_trade in active_trades:
                records = self.main_account_repository.get_main_account_trade_by_id(active_trade)

                if len(records) > 0:
                    continue

                self.main_account_entity_manager.insert_new_trade(active_trade)

    def _sync_market_trades(self):
        for allowed_symbol in config.ALLOWED_SYMBOLS:
            main_acc_orders = self.client.get_all_orders(symbol=allowed_symbol, limit=10)
            for order in main_acc_orders:
                if order['type'] == config.MARKET_TYPE:
                    records = self.main_account_repository.get_main_account_trade_by_id(order)

                    if len(records) > 0:
                        continue

                    self.main_account_entity_manager.insert_new_trade(order)

    def _sync_closed_trades(self):
        records = self.main_account_repository.get_all_active_orders_from_main_account()

        for record in records:
            order = None

            try:
                order = self.client.get_order(
                    symbol=record['symbol'],
                    orderId=record['order_id'])
            except BinanceAPIException:
                self.main_account_entity_manager.update_executed_trade(record['status'], record['order_id'])

            if order is not None and order['status'] != config.NEW_STATUS:
                self.main_account_entity_manager.update_executed_trade(order['status'], order['orderId'])

