import config


class MainAccountRepository:

    def __init__(self, db_connection):
        self.db = db_connection

    def get_main_account_trade_by_id(self, trade):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM main_account_spot_order_history WHERE order_id = %s"
        conditions = (
            trade['orderId'],
        )
        cursor.execute(query, conditions)

        return cursor.fetchall()

    def get_all_active_orders_from_main_account(self):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM main_account_spot_order_history WHERE status = '" + config.NEW_STATUS + "'"
        cursor.execute(query)

        return cursor.fetchall()