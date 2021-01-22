# binance-copy-daemon

Binance copy daemon is a cli tool writen in python by php developer :) 
The initial idea of the tool is to clone all the operations from one trader (main account) to the child accounts with corresponding recalculation of the deposit.

## Example
Main account has 1000 USDT in a spot wallet, trader decide to make an order and buy BTC for 500 USDT. 
Child account has 100 USDT and see the operation from main account. The daemon will create an order with according recalcualtion of deposit and spend 50 USDT 
buying BTC coin.

## Current status
The implementation is quite raw atm. But we already support:
- Spot account fully.
- Margin account fully.
- Moving of the coins from spot wallet to margin and vice versa.

TODO points:
- Feature trading
- Cover calculations with unit tests.
- Develop logging system.
- Solve the problem with frequent queries blocking by binance.
- Develop UI.
