import config


class MainAccountEntityManager:

    def __init__(self, db_connection):
        self.db = db_connection

    def insert_new_trade(self, active_trade):
        cursor = self.db.cursor()
        query = "INSERT INTO main_account_order_history " \
                "(status, symbol, price, stop_price, original_qty, cummulative_quote_qty, order_id, created_at, updated_at, side, type, time_in_force) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            active_trade['status'],
            active_trade['symbol'],
            active_trade['price'],
            active_trade.get('stopPrice',),
            active_trade['origQty'],
            active_trade.get('cummulativeQuoteQty',),
            active_trade['orderId'],
            active_trade['time'],
            active_trade['updateTime'],
            active_trade['side'],
            active_trade['type'],
            active_trade['timeInForce'],
        )
        cursor.execute(query, values)
        self.db.commit()

    def update_executed_trade(self, order_status, order_id):
        cursor = self.db.cursor()
        query = "UPDATE main_account_order_history SET status = %s WHERE order_id = %s"
        values = (
            order_status,
            order_id
        )
        cursor.execute(query, values)
        self.db.commit()