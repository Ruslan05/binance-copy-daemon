from abstract.persistence.main_account_trade.main_account_repository import AbstractMainAccountRepository


class MainAccountRepository(AbstractMainAccountRepository):

    main_account_order_history_table_name = 'main_account_spot_order_history'

    def __init__(
            self,
            db_connection,
    ):
        AbstractMainAccountRepository.__init__(self, db_connection, self.main_account_order_history_table_name)

    def get_main_account_trade_by_id(self, trade):
        return super()._get_main_account_trade_by_id(trade)

    def get_all_active_orders_from_main_account(self):
        return super()._get_all_active_orders_from_main_account()