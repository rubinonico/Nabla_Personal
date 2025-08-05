import argparse
import json
import os
import sys
import time
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

def execute_trade(asset, is_buy, size, max_leverage, cloid):
    """
    Connects to Hyperliquid, performs pre-trade checks, and executes a trade.
    """
    # 1. Securely load API credentials from environment variables
    api_secret = os.environ.get("HYPERLIQUID_API_SECRET")
    user_address = os.environ.get("HYPERLIQUID_ADDRESS")

    if not api_secret or not user_address:
        print(json.dumps({"status": "error", "message": "ERROR: API secret or address not set"}), file=sys.stderr)
        sys.exit(1)

    # 2. Initialize Info object and get the metadata dictionary
    # The updated library returns a dictionary directly.
    info = Info(constants.TESTNET_API_URL, skip_ws=True)
    meta_dictionary = info.meta()

    # 3. Initialize the Exchange object
    exchange = Exchange(user_address, constants.TESTNET_API_URL, api_secret)

    # 4. Manually set the metadata to be absolutely sure it's correct before proceeding
    exchange.info.set_perp_meta(meta_dictionary, 0)

    # 5. Fetch live account state for pre-trade checks
    user_state = info.user_state(user_address)
    available_margin = float(user_state["withdrawable"])

    # 6. Pre-trade Safety Checks
    asset_contexts = info.all_mids()
    oracle_price = float(asset_contexts[asset])
    trade_notional = size * oracle_price
    required_margin = trade_notional / max_leverage

    if required_margin > available_margin:
        msg = f"ERROR: INSUFFICIENT_MARGIN. Required: {required_margin:.2f}, Available: {available_margin:.2f}"
        print(json.dumps({"status": "error", "message": msg}), file=sys.stderr)
        sys.exit(1)

    # 7. Execute Idempotent Trade
    order_result = exchange.order(
        asset,
        is_buy,
        size,
        None, # Price is None for market order
        {"type": "market"},
        cloid=cloid
    )

    if order_result["status"] == "ok":
        print(json.dumps(order_result))
    else:
        print(json.dumps({"status": "error", "data": order_result}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute a hedge trade on Hyperliquid.")
    parser.add_argument("--asset", required=True, type=str, help="Asset to trade, e.g., ETH.")
    parser.add_argument("--is_buy", required=True, type=lambda x: (str(x).lower() == 'true'), help="True for buy, False for sell.")
    parser.add_argument("--size", required=True, type=float, help="Size of the trade in the asset's unit.")
    parser.add_argument("--max_leverage", required=True, type=float, help="Maximum leverage allowed for the trade.")
    parser.add_argument("--cloid", required=True, type=str, help="Client Order ID for idempotency.")

    args = parser.parse_args()

    execute_trade(args.asset, args.is_buy, args.size, args.max_leverage, args.cloid)
