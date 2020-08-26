import config


class AbstractChildAccountEntityManager:

    def __init__(
            self,
            db_connection,
            child_account_order_history_table_name,
            main_account_order_history_table_name,
    ):
        self.db = db_connection
        self.child_account_order_history_table_name = child_account_order_history_table_name
        self.main_account_order_history_table_name = main_account_order_history_table_name
        super(AbstractChildAccountEntityManager, self).__init__()

    def _close_child_trade_in_db(self, order, account_name):
        cursor = self.db.cursor()
        query = "UPDATE  " + self.child_account_order_history_table_name + " SET status = '" + config.CANCELED_STATUS + "' WHERE order_id = " + str(order['order_id']) + " AND account_name = '" + account_name + "'"
        cursor.execute(query)
        self.db.commit()

    def _insert_new_trade(self, order, parent_order, account_name):
        cursor = self.db.cursor()
        query = "INSERT INTO  " + self.child_account_order_history_table_name + " (status, symbol, price, stop_price, original_qty, cummulative_quote_qty, order_id, created_at, updated_at, fk_main_account_order, side, type, time_in_force, account_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            order.get('status', config.NEW_STATUS),
            order.get('symbol'),
            order.get('price'),
            order.get('stopPrice'),
            order.get('origQty'),
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

    def _mark_parent_market_trade_as_processed(self, parent_order):
        cursor = self.db.cursor()
        query = "UPDATE  " + self.main_account_order_history_table_name + " SET is_market_trade_cloned=true WHERE id_main_account_order_history=" + str(parent_order.get('id_main_account_order_history'))

        cursor.execute(query)
        self.db.commit()
