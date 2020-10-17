from src.abstract.persistence.child_account_trade.child_account_entity_manager import AbstractChildAccountEntityManager


class ChildAccountEntityManager(AbstractChildAccountEntityManager):

    main_account_order_history_table_name = 'main_account_spot_order_history'
    child_account_order_history_table_name = 'child_account_spot_order_history'

    def __init__(
            self,
            db_connection
    ):
        AbstractChildAccountEntityManager.__init__(self, db_connection, self.child_account_order_history_table_name, self.main_account_order_history_table_name)

    def close_child_trade_in_db(self, order, account_name):
        super()._close_child_trade_in_db(order, account_name)

    def insert_new_trade(self, order, parent_order, account_name):
        super()._insert_new_trade(order, parent_order, account_name)

    def mark_parent_market_trade_as_processed(self, parent_order):
        super()._mark_parent_market_trade_as_processed(parent_order)
