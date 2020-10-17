import mysql.connector as mysql
from src import config
import time

from src.spot.persistence.child_account_trade.child_account_repository import ChildAccountRepository as SpotChildAccountRepository
from src.spot.persistence.child_account_trade.child_account_entity_manager import ChildAccountEntityManager as SpotChildAccountEntityManager
from src.spot.business.child_account_trade.child_trader import ChildTrader as SpotChildTrader

from src.spot.persistence.main_account_trade.main_account_repository import MainAccountRepository as SpotMainAccountRepository
from src.spot.persistence.main_account_trade.main_account_entity_manager import MainAccountEntityManager as SpotMainAccountEntityManager
from src.spot.business.main_account_trade.main_trader import MainTrader as SpotMainTrader

from src.margin.persistence.child_account_trade.child_account_repository import ChildAccountRepository as MarginChildAccountRepository
from src.margin.persistence.child_account_trade.child_account_entity_manager import ChildAccountEntityManager as MarginChildAccountEntityManager
from src.margin.business.child_account_trade.child_trader import ChildTrader as MarginChildTrader

from src.margin.persistence.main_account_trade.main_account_repository import MainAccountRepository as MarginMainAccountRepository
from src.margin.persistence.main_account_trade.main_account_entity_manager import MainAccountEntityManager as MarginMainAccountEntityManager
from src.margin.business.main_account_trade.main_trader import MainTrader as MarginMainTrader

from src.wallet.business.wallet_synchronizer import WalletSynchronizer


class Main:
    def run(self):

        db_connection = mysql.connect(
            host=config.db_host,
            user=config.db_user,
            passwd=config.db_password,
            database=config.db_name
        )

        spot_main_account = SpotMainTrader(SpotMainAccountRepository(db_connection), SpotMainAccountEntityManager(db_connection))
        spot_child_account = SpotChildTrader(SpotChildAccountRepository(db_connection), SpotChildAccountEntityManager(db_connection))

        margin_main_account = MarginMainTrader(MarginMainAccountRepository(db_connection), MarginMainAccountEntityManager(db_connection))
        margin_child_account = MarginChildTrader(MarginChildAccountRepository(db_connection), MarginChildAccountEntityManager(db_connection))

        wallet_synchronizer = WalletSynchronizer()

        while True:
            spot_main_account.sync_main_account_trades()
            spot_child_account.sync_child_accounts_trades()

            margin_main_account.sync_main_account_trades()
            margin_child_account.sync_child_accounts_trades()

            wallet_synchronizer.sync_wallets()

            time.sleep(1)
main = Main()
main.run()
