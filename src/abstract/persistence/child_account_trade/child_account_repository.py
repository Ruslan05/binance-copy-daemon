from src import config
import time


class AbstractChildAccountRepository:

    def __init__(
            self,
            db_connection,
            child_account_order_history_table_name,
            main_account_order_history_table_name
    ):
        self.db = db_connection
        self.daemon_start_time = str(round(time.time() * 1000))
        self.child_account_order_history_table_name = child_account_order_history_table_name
        self.main_account_order_history_table_name = main_account_order_history_table_name
        super(AbstractChildAccountRepository, self).__init__()

    def _get_child_orders_to_be_closed(self):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT caoh.* FROM " + self.child_account_order_history_table_name + " caoh INNER JOIN " + self.main_account_order_history_table_name + " maoh ON caoh.fk_main_account_order = maoh.id_main_account_order_history WHERE caoh.status = '" + config.NEW_STATUS + "' and maoh.status = '" + config.CANCELED_STATUS + "'"
        cursor.execute(query)

        return cursor.fetchall()

    def _get_main_account_active_trades(self):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT maohtn.* FROM " + self.main_account_order_history_table_name + " maohtn " \
                "LEFT JOIN " + self.child_account_order_history_table_name + " caohtn ON " \
                " maohtn.id_main_account_order_history = caohtn.fk_main_account_order " \
                " WHERE caohtn.id_child_account_order_history is NULL AND " \
                " (maohtn.status = '" + config.NEW_STATUS + "' OR (maohtn.status = '" + config.EXECUTED_STATUS + "'"\
                " AND maohtn.type = '" + config.MARKET_TYPE + "' AND maohtn.updated_at > '" + self.daemon_start_time + "')" \
                " AND maohtn.is_market_trade_cloned IS NULL)"
        cursor.execute(query)

        return cursor.fetchall()

    def _get_child_account_active_trade_by_parent_id(self, parent_id, account_name):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM " + self.child_account_order_history_table_name + " WHERE status = '" + config.NEW_STATUS + "' AND fk_main_account_order = " + str(parent_id) + " AND account_name = '" + account_name + "'"
        cursor.execute(query)

        return cursor.fetchone()
