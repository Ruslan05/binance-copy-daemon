import mysql.connector as mysql
import config

from persistence.child_account_trade.child_account_repository import ChildAccountRepository
from persistence.child_account_trade.child_account_entity_manager import ChildAccountEntityManager

from business.child_account_trade.child_trader import ChildTrader

from persistence.main_account_trade.main_account_repository import MainAccountRepository
from persistence.main_account_trade.main_account_entity_manager import MainAccountEntityManager

from business.main_account_trade.main_trader import MainTrader


class Main:
    def run(self):

        db_connection = mysql.connect(
            host=config.db_host,
            user=config.db_user,
            passwd=config.db_password,
            database=config.db_name
        )

        # main_account = MainAccountTrades(db_connection)
        # child_account = ChildAccountTrades(db_connection)

        main_account = MainTrader(MainAccountRepository(db_connection), MainAccountEntityManager(db_connection))
        child_account = ChildTrader(ChildAccountRepository(db_connection), ChildAccountEntityManager(db_connection))

        while True:
            main_account.sync_main_account_trades()
            child_account.sync_child_accounts_trades()

        # main_account.sync_main_account_trades()
        # child_account.sync_child_accounts_trades()


main = Main()
main.run()
