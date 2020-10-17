from src.abstract.persistence.main_account_trade.main_account_entity_manager import AbstractMainAccountEntityManager


class MainAccountEntityManager(AbstractMainAccountEntityManager):

    main_account_order_history_table_name = 'main_account_spot_order_history'

    def __init__(
            self,
            db_connection
    ):
        AbstractMainAccountEntityManager.__init__(self, db_connection, self.main_account_order_history_table_name)

    def insert_new_trade(self, active_trade):
        super()._insert_new_trade(active_trade)

    def update_executed_trade(self, order_status, order_id):
        super()._update_executed_trade(order_status, order_id)
