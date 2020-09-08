#API
main_account_api_key = ''
main_account_api_secret = ''

child_accounts = {
    'account1': {
        'api_key': '',
        'api_secret': ''
    }
}

#DATABASE
db_host = '127.0.0.1'
db_user = 'root'
db_password = 'Passado2468'
db_name = 'binance'

#BINANCE
#STATUSES
NEW_STATUS = 'NEW'
CANCELED_STATUS = 'CANCELED'
EXECUTED_STATUS = 'FILLED'
#ORDER TYPES
LIMIT_TYPE = 'LIMIT'
MARKET_TYPE = 'MARKET'
STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
#SIDES
BUY = 'BUY'
SELL = 'SELL'
#SYMBOLS
ALLOWED_SYMBOLS = ['BTCUSDT', 'ETHUSDT']
ALLOWED_ASSETS = ['USDT', 'ETH', 'BTC']

#APP
PRECISION = 6
SAFE_ROUND_DOWN_HACK = 0.000001
MAIN_ACCOUNT_SPOT_ORDERS_HISTORY_TABLE = 'main_account_spot_order_history'
CHILD_ACCOUNT_SPOT_ORDERS_HISTORY_TABLE = 'child_account_spot_order_history'
MAIN_ACCOUNT_MARGIN_ORDERS_HISTORY_TABLE = 'main_account_margin_order_history'
