import config


class ChildAccountEntityManager:

    def __init__(self, db_connection):
        self.db = db_connection

    def close_child_trade_in_db(self, order, account_name):
        cursor = self.db.cursor()
        query = "UPDATE child_account_spot_order_history SET status = '" + config.CANCELED_STATUS + "' WHERE order_id = " + str(order['order_id']) + " AND account_name = '" + account_name + "'"
        cursor.execute(query)
        self.db.commit()

    def insert_new_trade(self, order, parent_order, account_name):
        cursor = self.db.cursor()
        query = "INSERT INTO child_account_spot_order_history (status, symbol, price, stop_price, original_qty, cummulative_quote_qty, order_id, created_at, updated_at, fk_main_account_order, side, type, time_in_force, account_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
            parent_order.get('id_main_account_spot_order_history'),
            order.get('side'),
            order.get('type'),
            order.get('timeInForce'),
            account_name
        )
        cursor.execute(query, values)
        self.db.commit()

    def mark_parent_market_trade_as_processed(self, parent_order):
        cursor = self.db.cursor()
        query = "UPDATE main_account_spot_order_history SET is_market_trade_cloned=true WHERE id_main_account_spot_order_history=" + str(parent_order.get('id_main_account_spot_order_history'))

        cursor.execute(query)
        self.db.commit()
