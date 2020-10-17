from binance.client import Client

from src import config


class WalletSynchronizer:

    def sync_wallets(self):
        for asset in config.ALLOWED_ASSETS:
            main_account_wallet_percentages = self._get_main_account_percentage_per_wallet_by_asset(asset)

            if main_account_wallet_percentages is None:
                return

            for account_name, child_account in config.child_accounts.items():
                child_account_client = Client(child_account['api_key'], child_account['api_secret'])

                child_account_spot_balance = child_account_client.get_asset_balance(asset=asset)
                child_account_margin_balance = self._get_margin_account_balance(child_account_client, asset)
                child_spot_net_asset = float(child_account_spot_balance['free']) + float(child_account_spot_balance['locked'])
                child_account_margin_net_asset = 0

                if float(child_account_margin_balance['netAsset']) > 0:
                    child_account_margin_net_asset = float(child_account_margin_balance['netAsset'])

                child_account_asset_sum = child_spot_net_asset + child_account_margin_net_asset

                desired_amount_at_child_spot_wallet = child_account_asset_sum * (main_account_wallet_percentages['spot_percentage'] / 100)

                if child_spot_net_asset > desired_amount_at_child_spot_wallet:
                    spot_wallet_delta = child_spot_net_asset - desired_amount_at_child_spot_wallet
                    spot_wallet_delta = round(spot_wallet_delta - config.SAFE_ROUND_DOWN_HACK, config.PRECISION)

                    if spot_wallet_delta > 0:
                        transaction = child_account_client.transfer_spot_to_margin(asset=asset, amount=spot_wallet_delta)

                if child_spot_net_asset < desired_amount_at_child_spot_wallet:
                    spot_wallet_delta = desired_amount_at_child_spot_wallet - child_spot_net_asset
                    spot_wallet_delta = round(spot_wallet_delta - config.SAFE_ROUND_DOWN_HACK, config.PRECISION)

                    if spot_wallet_delta > 0:
                        transaction = child_account_client.transfer_margin_to_spot(asset=asset, amount=spot_wallet_delta)


    def _get_main_account_percentage_per_wallet_by_asset(self, asset):
        main_account_client = Client(config.main_account_api_key, config.main_account_api_secret)

        main_account_spot_balance = main_account_client.get_asset_balance(asset=asset)
        main_account_margin_balance = self._get_margin_account_balance(main_account_client, asset)
        main_account_margin_net_asset = 0

        if float(main_account_margin_balance['netAsset']) > 0:
            main_account_margin_net_asset = float(main_account_margin_balance['netAsset'])

        main_account_asset_sum = float(main_account_spot_balance['free']) + float(main_account_spot_balance['locked']) \
                                 + main_account_margin_net_asset

        if main_account_asset_sum == 0:
            return None

        main_account_spot_percentage = ((float(main_account_spot_balance['free']) +
                                         float(main_account_spot_balance['locked'])) / main_account_asset_sum) * 100

        main_account_margin_percentage = (main_account_margin_net_asset / main_account_asset_sum) * 100

        return {
            'spot_percentage': main_account_spot_percentage,
            'margin_percentage': main_account_margin_percentage
        }

    def _get_margin_account_balance(self, client, currency):
        account_assets_info = client.get_margin_account()

        for asset_info in account_assets_info['userAssets']:
            if asset_info['asset'] == currency:
                return asset_info

        return None