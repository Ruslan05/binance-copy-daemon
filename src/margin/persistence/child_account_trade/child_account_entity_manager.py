from src.abstract.persistence.child_account_trade.child_account_entity_manager import AbstractChildAccountEntityManager
from src import config


class ChildAccountEntityManager(AbstractChildAccountEntityManager):

    main_account_order_history_table_name = 'main_account_margin_order_history'
    child_account_order_history_table_name = 'child_account_margin_order_history'

    def __init__(
            self,
            db_connection
    ):
        AbstractChildAccountEntityManager.__init__(self, db_connection, self.child_account_order_history_table_name, self.main_account_order_history_table_name)

    def close_child_trade_in_db(self, order, account_name):
        super()._close_child_trade_in_db(order, account_name)

    def insert_new_trade(self, order, parent_order, account_name):
        cursor = self.db.cursor()
        query = "INSERT INTO  " + self.child_account_order_history_table_name + " (status, symbol, price, stop_price, original_qty, borrowed, cummulative_quote_qty, order_id, created_at, updated_at, fk_main_account_order, side, type, time_in_force, account_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            order.get('status', config.NEW_STATUS),
            order.get('symbol'),
            order.get('price'),
            order.get('stopPrice'),
            order.get('origQty'),
            order.get('borrowed'),
            order.get('cummulativeQuoteQty', ),
            order.get('orderId'),
            order.get('time'),
            order.get('updateTime'),
            parent_order.get('id_main_account_order_history'),
            order.get('side'),
            order.get('type'),
            order.get('timeInForce'),
            account_name
        )
        cursor.execute(query, values)
        self.db.commit()

    def mark_parent_market_trade_as_processed(self, parent_order):
        super()._mark_parent_market_trade_as_processed(parent_order)