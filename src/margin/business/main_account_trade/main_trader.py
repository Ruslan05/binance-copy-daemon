from binance.client import Client
from binance.exceptions import BinanceAPIException
from src import config


class MainTrader:

    def __init__(self, main_account_repository, main_account_entity_manager):
        self.main_account_repository = main_account_repository
        self.main_account_entity_manager = main_account_entity_manager
        self.client = Client(config.main_account_api_key, config.main_account_api_secret)

    def sync_main_account_trades(self):
        self._sync_active_margin_trades()
        self._sync_market_margin_trades()
        self._sync_closed_margin_trades()

    def _sync_active_margin_trades(self):
        for allowed_symbol in config.ALLOWED_SYMBOLS:
            print(allowed_symbol)
            active_trades = self.client.get_open_margin_orders(symbol=allowed_symbol)

            for active_trade in active_trades:
                records = self.main_account_repository.get_main_account_trade_by_id(active_trade)

                if len(records) > 0:
                    continue

                active_trade = self._decorate_active_trade(active_trade)

                self.main_account_entity_manager.insert_new_trade(active_trade)

    def _sync_market_margin_trades(self):
        for allowed_symbol in config.ALLOWED_SYMBOLS:
            main_acc_orders = self.client.get_all_margin_orders(symbol=allowed_symbol, limit=10)
            for order in main_acc_orders:
                if order['type'] == config.MARKET_TYPE:
                    records = self.main_account_repository.get_main_account_trade_by_id(order)

                    if len(records) > 0:
                        continue

                    order = self._decorate_active_trade(order)

                    self.main_account_entity_manager.insert_new_trade(order)

    def _sync_closed_margin_trades(self):
        records = self.main_account_repository.get_all_active_orders_from_main_account()

        for record in records:
            order = None

            try:
                order = self.client.get_margin_order(
                    symbol=record['symbol'],
                    orderId=record['order_id'])
            except BinanceAPIException:
                self.main_account_entity_manager.update_executed_trade(record['status'], record['order_id'])

            if order is not None and order['status'] != config.NEW_STATUS:
                self.main_account_entity_manager.update_executed_trade(order['status'], order['orderId'])

    def _decorate_active_trade(self, active_trade):
        currency = self._get_currency_from_main_order(active_trade)
        active_trades_with_borrowing = self.main_account_repository.get_main_account_active_trade_with_borrowing()
        main_account_balance = self._get_main_account_margin_wallet(currency)
        borrowed = float(main_account_balance['borrowed'])
        active_trade['borrowed'] = 0

        for active_trade_with_borrowing in active_trades_with_borrowing:
            borrowed = borrowed - float(active_trade_with_borrowing['borrowed'])

        if float(main_account_balance['netAsset']) < float(main_account_balance['locked']):
            borrowed = borrowed - float(main_account_balance['free'])
            active_trade['borrowed'] = borrowed

        return active_trade

    def _decorate_executed_market_trade(self, active_trade):
        currency = self._get_currency_from_main_order(active_trade)
        active_trades_with_borrowing = self.main_account_repository.get_main_account_market_trade_with_borrowing()
        main_account_balance = self._get_main_account_margin_wallet(currency)
        borrowed = float(main_account_balance['borrowed'])
        active_trade['borrowed'] = 0

        for active_trade_with_borrowing in active_trades_with_borrowing:
            borrowed = borrowed - float(active_trade_with_borrowing['borrowed'])

        if float(main_account_balance['netAsset']) < float(main_account_balance['locked']):
            borrowed = borrowed - float(main_account_balance['free'])
            active_trade['borrowed'] = borrowed

        return active_trade

    def _get_main_account_margin_wallet(self, currency):
        main_account_assets_info = self.client.get_margin_account()

        for asset_info in main_account_assets_info['userAssets']:
            if asset_info['asset'] == currency:
                return asset_info

        return None

    # TODO: MOVE to service/helper
    def _get_currency_from_main_order(self, main_account_order):
        length = len(main_account_order['symbol'])
        limit = 3

        if main_account_order['side'] == config.SELL:
            return main_account_order['symbol'][:limit]

        if main_account_order['side'] == config.BUY:
            if length > 6:
                limit = 4

            return main_account_order['symbol'][length - limit:]

        return ''