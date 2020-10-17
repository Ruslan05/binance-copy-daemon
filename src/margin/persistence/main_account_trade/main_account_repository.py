from src.abstract.persistence.main_account_trade.main_account_repository import AbstractMainAccountRepository
from src import config


class MainAccountRepository(AbstractMainAccountRepository):

    main_account_order_history_table_name = 'main_account_margin_order_history'

    def __init__(self, db_connection):
        self.db = db_connection
        AbstractMainAccountRepository.__init__(self, db_connection, self.main_account_order_history_table_name)

    def get_main_account_trade_by_id(self, trade):
        return super()._get_main_account_trade_by_id(trade)

    def get_all_active_orders_from_main_account(self):
        return super()._get_all_active_orders_from_main_account()

    def get_main_account_active_trade_with_borrowing(self):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM " + self.main_account_order_history_table_name + " WHERE borrowed > 0 AND " + "status='" + config.NEW_STATUS + "'"
        cursor.execute(query)

        return cursor.fetchall()

    def get_main_account_market_trade_with_borrowing(self):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM " + self.main_account_order_history_table_name + " WHERE borrowed > 0 AND " + \
                "status='" + config.EXECUTED_STATUS + "' and is_market_trade_cloned = NULL"
        cursor.execute(query)

        return cursor.fetchall()
