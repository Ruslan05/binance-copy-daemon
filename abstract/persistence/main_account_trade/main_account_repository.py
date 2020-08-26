import config


class AbstractMainAccountRepository:

    def __init__(
            self,
            db_connection,
            main_account_order_history_table_name
    ):
        self.db = db_connection
        self.main_account_order_history_table_name = main_account_order_history_table_name
        super(AbstractMainAccountRepository, self).__init__()

    def _get_main_account_trade_by_id(self, trade):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM " + self.main_account_order_history_table_name + " WHERE order_id = %s"
        conditions = (
            trade['orderId'],
        )
        cursor.execute(query, conditions)

        return cursor.fetchall()

    def _get_all_active_orders_from_main_account(self):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM " + self.main_account_order_history_table_name + " WHERE status = '" + config.NEW_STATUS + "'"
        cursor.execute(query)

        return cursor.fetchall()