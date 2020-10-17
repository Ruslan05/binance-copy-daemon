import json

from binance.client import Client
from binance.exceptions import BinanceAPIException

from src import config


class ChildTrader:

    def __init__(self, child_account_repository, child_account_entity_manager):
        self.child_account_repository = child_account_repository
        self.child_account_entity_manager = child_account_entity_manager

    def sync_child_accounts_trades(self):
        self._sync_active_trades()
        self._sync_closed_trades()

    def _sync_active_trades(self):
        main_account_orders = self.child_account_repository.get_main_account_active_trades()

        for main_account_order in main_account_orders:
            for account_name, child_account in config.child_accounts.items():
                child_account_order = self.child_account_repository.get_child_account_active_trade_by_parent_id(main_account_order['id_main_account_order_history'], account_name)

                if child_account_order is not None:
                    continue

                self._place_order(child_account, account_name, main_account_order)

    def _place_order(self, account, account_name, main_account_order):
        client = Client(account['api_key'], account['api_secret'])

        try:
            order = None
            if main_account_order['type'] == config.LIMIT_TYPE:
                order = self._place_limit_order(client, main_account_order)

            if main_account_order['type'] == config.MARKET_TYPE:
                order = self._place_market_order(client, main_account_order)

            if main_account_order['type'] == config.STOP_LOSS_LIMIT or main_account_order['type'] == config.TAKE_PROFIT_LIMIT:
                order = self._place_stop_loss_limit_order(client, main_account_order)

            if order is not None:
                self.child_account_entity_manager.insert_new_trade(order, main_account_order, account_name)

        except Exception as e:
            f = open("exception.txt", "a")
            f.write('Child place order exception: ' + str(e) + "\n")
            f.write(json.dumps(main_account_order) + "\n")
            f.close()
        finally:
            self.child_account_entity_manager.mark_parent_market_trade_as_processed(main_account_order)

    def _place_limit_order(self, client, main_account_order):
        calculated_qty = self._get_calculated_limit_order_qty_based_on_deposit(client, main_account_order)
        order = None

        if main_account_order['side'] == config.BUY:
            order = client.order_limit_buy(
                symbol=main_account_order['symbol'],
                quantity=calculated_qty,
                price=main_account_order['price'])

        if main_account_order['side'] == config.SELL:
            order = client.order_limit_sell(
                symbol=main_account_order['symbol'],
                quantity=calculated_qty,
                price=main_account_order['price'])

        return order

    def _place_market_order(self, client, main_account_order):
        calculated_qty = self._get_calculated_market_order_qty_based_on_deposit(client, main_account_order)
        order = None

        if main_account_order['side'] == config.BUY:
            order = client.order_market_buy(
                symbol=main_account_order['symbol'],
                quantity=calculated_qty
            )

        if main_account_order['side'] == config.SELL:
            order = client.order_market_sell(
                symbol=main_account_order['symbol'],
                quantity=calculated_qty
            )

        return order

    def _place_stop_loss_limit_order(self, client, main_account_order):
        calculated_qty = self._get_calculated_limit_order_qty_based_on_deposit(client, main_account_order)
        order = None

        try:
            order = client.create_order(
                symbol=main_account_order['symbol'],
                side=main_account_order['side'],
                timeInForce=main_account_order['time_in_force'],
                quantity=calculated_qty,
                stopPrice=main_account_order['stop_price'],
                price=main_account_order['price'],
                type=main_account_order['type'],
            )
        except BinanceAPIException as e:
            f = open("exception.txt", "a")
            f.write('Child place order exception: ' + str(e) + "\n")
            f.write('Type: ' + str(main_account_order['type']) + '; Main order id: ' + str(main_account_order['id_main_account_order_history']) + "\n")
            f.write(json.dumps(main_account_order) + "\n")
            f.close()

        return order

    # TODO: discuss precision
    def _get_calculated_limit_order_qty_based_on_deposit(self, client, main_account_order):
        main_account_client = Client(config.main_account_api_key, config.main_account_api_secret)
        currency = self._get_currency_from_main_order(main_account_order)
        child_account_balance_free = float(client.get_asset_balance(asset=currency)['free'])

        if child_account_balance_free == 0 or currency == '':
            return 0

        main_account_balance = main_account_client.get_asset_balance(asset=currency)

        if main_account_order['side'] == config.SELL:
            # Calculate the percentage of created order in main account relatively to the main account balance.
            main_account_locked_on_trade = main_account_order['original_qty']
            main_order_percentage = (float(main_account_locked_on_trade) / (
                        float(main_account_balance['free']) + float(main_account_locked_on_trade))) * 100
            # Sum which is calculated to spend for child account.
            calculated_qty_to_sell = child_account_balance_free * (main_order_percentage / 100)

            return round(calculated_qty_to_sell - config.SAFE_ROUND_DOWN_HACK, config.PRECISION)

        if main_account_order['side'] == config.BUY:
            # Calculate the percentage of created order in main account relatively to the main account balance.
            main_account_locked_on_trade = main_account_order['price'] * main_account_order['original_qty']
            main_order_percentage = (float(main_account_locked_on_trade) / (float(main_account_balance['free']) + float(main_account_locked_on_trade))) * 100
            # Sum which is calculated to spend for child account.
            child_account_order_resource = child_account_balance_free * (main_order_percentage / 100)
            calculated_qty_to_buy = child_account_order_resource / float(main_account_order['price'])

            return round(calculated_qty_to_buy - config.SAFE_ROUND_DOWN_HACK, config.PRECISION)

        return 0

    # TODO: discuss precision
    def _get_calculated_market_order_qty_based_on_deposit(self, client, main_account_order):
        main_account_client = Client(config.main_account_api_key, config.main_account_api_secret)
        currency = self._get_currency_from_main_order(main_account_order)
        child_account_balance_free = float(client.get_asset_balance(asset=currency)['free'])

        if child_account_balance_free == 0 or currency == '':
            return 0

        main_account_balance = main_account_client.get_asset_balance(asset=currency)

        if main_account_order['side'] == config.SELL:
            # Calculate the percentage of created order in main account relatively to the main account balance.
            main_account_locked_on_trade = main_account_order['original_qty']
            main_order_percentage = (float(main_account_locked_on_trade) / (
                        float(main_account_balance['free']) + float(main_account_locked_on_trade))) * 100
            # Sum which is calculated to spend for child account.
            calculated_qty_to_sell = child_account_balance_free * (main_order_percentage / 100)

            return round(calculated_qty_to_sell - config.SAFE_ROUND_DOWN_HACK, config.PRECISION)

        if main_account_order['side'] == config.BUY:
            # Calculate the percentage of created order in main account relatively to the main account balance.
            main_account_locked_on_trade = main_account_order['cummulative_quote_qty']
            main_order_percentage = (float(main_account_locked_on_trade) / (float(main_account_balance['free']) + float(main_account_locked_on_trade))) * 100
            # Sum which is calculated to spend for child account.
            child_account_order_resource = child_account_balance_free * (main_order_percentage / 100)
            calculated_qty_to_buy = child_account_order_resource / (main_account_order['cummulative_quote_qty'] / main_account_order['original_qty'])

            return round(calculated_qty_to_buy - config.SAFE_ROUND_DOWN_HACK, config.PRECISION)

        return 0

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

    def _sync_closed_trades(self):
        child_account_orders_to_be_closed = self.child_account_repository.get_child_orders_to_be_closed()

        for child_account_order in child_account_orders_to_be_closed:
            api_key = config.child_accounts[child_account_order['account_name']]['api_key']
            api_secret = config.child_accounts[child_account_order['account_name']]['api_secret']

            client = Client(api_key, api_secret)
            try:
                client.cancel_order(
                    symbol=child_account_order['symbol'],
                    orderId=child_account_order['order_id']
                )
            except Exception as e:
                f = open("exception.txt", "a")
                f.write('Child cancel order exception: ' + str(e) + "\n")
                f.write(json.dumps(child_account_order) + "\n")
                f.close()
            finally:
                self.child_account_entity_manager.close_child_trade_in_db(child_account_order, child_account_order['account_name'])
