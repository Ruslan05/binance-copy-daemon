import config
import time


class ChildAccountRepository:

    def __init__(self, db_connection):
        self.db = db_connection
        self.daemon_start_time = str(round(time.time() * 1000))

    def get_child_orders_to_be_closed(self):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT caoh.* FROM child_account_order_history caoh INNER JOIN main_account_order_history maoh ON caoh.fk_main_account_order = maoh.id_main_account_order_history WHERE caoh.status = '" + config.NEW_STATUS + "' and maoh.status = '" + config.CANCELED_STATUS + "'"
        cursor.execute(query)

        return cursor.fetchall()

    def get_main_account_active_trades(self):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM main_account_order_history WHERE (status = '" + config.NEW_STATUS + "' OR (status = '" + config.EXECUTED_STATUS + "' AND type = '" + config.MARKET_TYPE + "' AND updated_at > '" + self.daemon_start_time + "') AND is_market_trade_cloned IS NULL)"
        cursor.execute(query)

        return cursor.fetchall()

    def get_child_account_active_trade_by_parent_id(self, parent_id, account_name):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM child_account_order_history WHERE status = '" + config.NEW_STATUS + "' AND fk_main_account_order = " + str(parent_id) + " AND account_name = '" + account_name + "'"
        cursor.execute(query)

        return cursor.fetchone()
