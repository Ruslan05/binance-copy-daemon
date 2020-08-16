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

#APP
PRECISION = 6
SAFE_ROUND_DOWN_HACK = 0.000001
