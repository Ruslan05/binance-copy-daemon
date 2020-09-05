import json

from binance.client import Client
from binance.exceptions import BinanceAPIException

import config


class ChildTrader:

    def __init__(self, child_account_repository, child_account_entity_manager):
        self.child_account_repository = child_account_repository
        self.child_account_entity_manager = child_account_entity_manager

        self.main_account_client = Client(config.main_account_api_key, config.main_account_api_secret)
        self.main_account_balance = None
        self.main_loan_max = None

        self.current_side_currency = None
        self.child_account_client = None

    def sync_child_accounts_trades(self):
        self._sync_active_trades()
        self._sync_closed_trades()

    def _sync_active_trades(self):
        main_account_orders = self.child_account_repository.get_main_account_active_trades()

        for main_account_order in main_account_orders:
            self.current_side_currency = self._get_currency_from_main_order(main_account_order)
            self.main_loan_max = float(self.main_account_client.get_max_margin_loan(asset=self.current_side_currency)['amount'])
            self.main_account_balance = self._get_account_balance(self.main_account_client, self.current_side_currency)

            for account_name, child_account in config.child_accounts.items():
                child_account_order = self.child_account_repository.get_child_account_active_trade_by_parent_id(main_account_order['id_main_account_order_history'], account_name)

                if child_account_order is not None:
                    continue

                self.child_account_client = Client(child_account['api_key'], child_account['api_secret'])
                self._place_order(account_name, main_account_order)

    def _place_order(self, account_name, main_account_order):
        try:
            order = None
            if main_account_order['type'] == config.LIMIT_TYPE:
                order = self._place_limit_order(main_account_order)

            if main_account_order['type'] == config.MARKET_TYPE:
                order = self._place_market_order(main_account_order)

            if main_account_order['type'] == config.STOP_LOSS_LIMIT or main_account_order['type'] == config.TAKE_PROFIT_LIMIT:
                order = self._place_stop_loss_limit_order(main_account_order)

            if order is not None:
                self.child_account_entity_manager.insert_new_trade(order, main_account_order, account_name)
                self._sync_loans(order)

        except Exception as e:
            f = open("exception.txt", "a")
            f.write('Child place order exception: ' + str(e) + "\n")
            f.write(json.dumps(main_account_order) + "\n")
            f.close()
        finally:
            self.child_account_entity_manager.mark_parent_market_trade_as_processed(main_account_order)

    def _place_limit_order(self, main_account_order):
        calculated_limit_order_data = self._get_calculated_limit_order_data_based_on_deposit(main_account_order)

        order = self.child_account_client.create_margin_order(
            symbol=main_account_order['symbol'],
            side=main_account_order['side'],
            type=main_account_order['type'],
            timeInForce=main_account_order['time_in_force'],
            quantity=calculated_limit_order_data['calculated_qty'],
            price=main_account_order['price'])

        order['borrowed'] = calculated_limit_order_data['borrowed_resource_amount']

        return order

    def _place_market_order(self, main_account_order):
        calculated_qty = self._get_calculated_market_order_qty_based_on_deposit(self.child_account_client, main_account_order)
        order = None

        if main_account_order['side'] == config.BUY:
            order = self.child_account_client.order_market_buy(
                symbol=main_account_order['symbol'],
                quantity=calculated_qty
            )

        if main_account_order['side'] == config.SELL:
            order = self.child_account_client.order_market_sell(
                symbol=main_account_order['symbol'],
                quantity=calculated_qty
            )

        return order

    def _place_stop_loss_limit_order(self, main_account_order):
        calculated_qty = self._get_calculated_limit_order_data_based_on_deposit(main_account_order)['calculated_qty']
        order = None

        try:
            order = self.child_account_client.create_order(
                symbol=main_account_order['symbol'],
                side=main_account_order['side'],
                timeInForce=main_account_order['time_in_force'],
                quantity=calculated_qty,
                stopPrice=main_account_order['stop_price'],
                price=main_account_order['price'],
                type=main_account_order['type'],
            )
        # TODO: mark order to not be reprocessed to avoid loop order place
        except BinanceAPIException as e:
            f = open("exception.txt", "a")
            f.write('Child place order exception: ' + str(e) + "\n")
            f.write('Type: ' + str(main_account_order['type']) + '; Main order id: ' + str(main_account_order['id_main_account_order_history']) + "\n")
            f.write(json.dumps(main_account_order) + "\n")
            f.close()

        return order

    # Don`t have borrowed amount with order data. So, multiple active orders will work wrong
    def _get_calculated_limit_order_data_based_on_deposit(self, main_account_order):
        if self.current_side_currency == '':
            return {'calculated_qty': 0, 'borrowed_resource_amount': 0}

        if main_account_order['side'] == config.SELL:
            return self._get_sell_limit_order_qty_data(main_account_order)
        if main_account_order['side'] == config.BUY:
            return self._get_buy_limit_order_qty_data(main_account_order)

        return {'calculated_qty': 0, 'borrowed_resource_amount': 0}

    def _get_sell_limit_order_qty_data(self, main_account_order):
        # Calculate the percentage of created order in main account relatively to the main account balance.
        main_account_locked_on_trade = main_account_order['original_qty']
        main_order_net_resource = main_account_locked_on_trade - main_account_order['borrowed']

        if main_order_net_resource < 0:
            main_order_net_resource = 0

        main_order_percentage = (float(main_account_locked_on_trade) / (float(self.main_account_balance['free']) + (main_order_net_resource) + self.main_loan_max + main_account_order['borrowed'])) * 100

        child_account_balance = self._get_account_balance(self.child_account_client, self.current_side_currency)

        if main_account_order['borrowed'] != 0:
            child_loan_max = float(self.child_account_client.get_max_margin_loan(asset=self.current_side_currency)['amount'])
        else:
            child_loan_max = 0

        # Sum which is calculated to spend for child account.
        child_account_order_resource = (float(child_account_balance['free']) + child_loan_max) * (main_order_percentage / 100)
        child_amount_to_borrow = self._get_child_amount_to_borrow(child_account_order_resource, child_account_balance)

        calculated_qty_to_sell = child_account_order_resource
        calculated_qty_to_sell = round(calculated_qty_to_sell - config.SAFE_ROUND_DOWN_HACK, config.PRECISION)

        return {'calculated_qty': calculated_qty_to_sell, 'borrowed_resource_amount': child_amount_to_borrow}

    def _get_buy_limit_order_qty_data(self, main_account_order):
        # Calculate the percentage of created order in main account relatively to the main account balance.
        main_account_locked_on_trade = main_account_order['price'] * main_account_order['original_qty']
        main_order_percentage = (float(main_account_locked_on_trade) / (float(self.main_account_balance['free']) + (main_account_locked_on_trade-main_account_order['borrowed']) + self.main_loan_max + main_account_order['borrowed'])) * 100

        child_account_balance = self._get_account_balance(self.child_account_client, self.current_side_currency)

        if main_account_order['borrowed'] != 0:
            child_loan_max = float(self.child_account_client.get_max_margin_loan(asset=self.current_side_currency)['amount'])
        else:
            child_loan_max = 0

        child_account_order_resource = (float(child_account_balance['free']) + child_loan_max) * (main_order_percentage / 100)
        child_amount_to_borrow = self._get_child_amount_to_borrow(child_account_order_resource, child_account_balance)

        calculated_qty_to_buy = child_account_order_resource / float(main_account_order['price'])
        calculated_qty_to_buy = round(calculated_qty_to_buy - config.SAFE_ROUND_DOWN_HACK, config.PRECISION)

        return {'calculated_qty': calculated_qty_to_buy, 'borrowed_resource_amount': child_amount_to_borrow}

    def _get_child_amount_to_borrow(self, child_account_order_resource, child_account_balance):
        child_amount_to_borrow = child_account_order_resource - float(child_account_balance['free'])

        if child_amount_to_borrow > 0:
            self.child_account_client.create_margin_loan(asset=self.current_side_currency, amount=child_amount_to_borrow)
        else:
            child_amount_to_borrow = 0

        return child_amount_to_borrow

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

    def _get_account_balance(self, client, currency):
        account_assets_info = client.get_margin_account()

        for asset_info in account_assets_info['userAssets']:
            if asset_info['asset'] == currency:
                return asset_info

        return None

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

    def _get_opposite_currency_from_main_order(self, main_account_order):
        length = len(main_account_order['symbol'])
        limit = 3

        if main_account_order['side'] == config.BUY:
            return main_account_order['symbol'][:limit]

        if main_account_order['side'] == config.SELL:
            if length > 6:
                limit = 4

            return main_account_order['symbol'][length - limit:]

        return ''

    def _sync_closed_trades(self):
        child_account_orders_to_be_closed = self.child_account_repository.get_child_orders_to_be_closed()

        for child_account_order in child_account_orders_to_be_closed:
            api_key = config.child_accounts[child_account_order['account_name']]['api_key']
            api_secret = config.child_accounts[child_account_order['account_name']]['api_secret']

            self.child_account_client = Client(api_key, api_secret)
            currency = self._get_currency_from_main_order(child_account_order)

            self.child_account_client.cancel_margin_order(
                symbol=child_account_order['symbol'],
                orderId=child_account_order['order_id']
            )
            if child_account_order['borrowed'] > 0:
                self.child_account_client.repay_margin_loan(asset=currency, amount=child_account_order['borrowed'])

            self.child_account_entity_manager.close_child_trade_in_db(child_account_order, child_account_order['account_name'])

    def _sync_loans(self, order):
        opposite_side_currency = self._get_opposite_currency_from_main_order(order)

        main_account_balance = self._get_account_balance(self.main_account_client, opposite_side_currency)
        main_account_free_loaned = self._get_free_loaned_qty(main_account_balance)
        main_loan_max = float(self.main_account_client.get_max_margin_loan(asset=opposite_side_currency)['amount'])

        # Can`t make child balance as class property due to it`s dynamic change during sync executions above.
        child_account_balance = self._get_account_balance(self.child_account_client, opposite_side_currency)
        child_account_free_loaned = self._get_free_loaned_qty(child_account_balance)
        child_loan_max = float(self.main_account_client.get_max_margin_loan(asset=opposite_side_currency)['amount'])

        main_account_loaned_percentage = (main_account_free_loaned / (main_account_free_loaned + main_loan_max)) * 100
        child_account_free_loaned_based_on_main_account = (child_account_free_loaned + child_loan_max) * (main_account_loaned_percentage / 100)

        if child_account_free_loaned_based_on_main_account > child_account_free_loaned:
            delta = child_account_free_loaned_based_on_main_account - child_account_free_loaned
            self.child_account_client.create_margin_loan(asset=opposite_side_currency, amount=delta)

        if child_account_free_loaned_based_on_main_account < child_account_free_loaned:
            delta = child_account_free_loaned - child_account_free_loaned_based_on_main_account
            self.child_account_client.repay_margin_loan(asset=opposite_side_currency, amount=delta)

    def _get_free_loaned_qty(self, account_balance):
        loaned = 0
        if float(account_balance['netAsset']) <= float(account_balance['locked']):
            loaned = float(account_balance['free'])

        if (float(account_balance['netAsset']) - float(account_balance['locked'])) < float(account_balance['free']):
            loaned = float(account_balance['free']) - (float(account_balance['netAsset']) - float(account_balance['locked']))

        return loaned
