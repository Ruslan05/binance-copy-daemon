from abstract.persistence.child_account_trade.child_account_repository import AbstractChildAccountRepository
import config


class ChildAccountRepository(AbstractChildAccountRepository):

    child_account_order_history_table_name = 'child_account_margin_order_history'
    main_account_order_history_table_name = 'main_account_margin_order_history'

    def __init__(
            self,
            db_connection,
    ):
        AbstractChildAccountRepository.__init__(self, db_connection, self.child_account_order_history_table_name, self.main_account_order_history_table_name)

    def get_child_orders_to_be_closed(self):
        return super()._get_child_orders_to_be_closed()

    def get_main_account_active_trades(self):
        return super()._get_main_account_active_trades()

    def get_child_account_active_trade_by_parent_id(self, parent_id, account_name):
        return super()._get_child_account_active_trade_by_parent_id(parent_id, account_name)