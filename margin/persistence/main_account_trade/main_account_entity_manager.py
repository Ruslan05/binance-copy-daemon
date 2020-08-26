from abstract.persistence.main_account_trade.main_account_entity_manager import AbstractMainAccountEntityManager


class MainAccountEntityManager(AbstractMainAccountEntityManager):

    main_account_order_history_table_name = 'main_account_margin_order_history'

    def __init__(self, db_connection):
        self.db = db_connection
        AbstractMainAccountEntityManager.__init__(self, db_connection, self.main_account_order_history_table_name)

    def insert_new_trade(self, active_trade):
        cursor = self.db.cursor()
        query = "INSERT INTO " + self.main_account_order_history_table_name + " " \
                "(status, symbol, price, stop_price, original_qty, cummulative_quote_qty, borrowed, order_id, created_at, updated_at, side, type, time_in_force) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            active_trade['status'],
            active_trade['symbol'],
            active_trade['price'],
            active_trade.get('stopPrice',),
            active_trade['origQty'],
            active_trade.get('cummulativeQuoteQty',),
            active_trade['borrowed'],
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
        super()._update_executed_trade(order_status, order_id)