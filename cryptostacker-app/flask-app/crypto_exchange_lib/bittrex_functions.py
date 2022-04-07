#https://bittrex.github.io/api/v3#topic-REST-API-Overview
#https://github.com/Bittrex/bittrex.github.io/issues/160
#The Bittrex API employs call limits on all REST endpoints to ensure the efficiency and availability of the platform for all customers. Limits are set such that they should not interfere with legitimate usage patterns. Frequent polling for updates on market data, order status, history, etc. is discouraged and will likely result in your requests failing with a 429 status code. If you need frequent updates, subscribe to the websocket instead of polling. Frivolous order placement and cancellation in a tight loop with low fill rates is also discouraged.
#Throttling is tracked on a minute by minute basis with the limit resetting at the start of the next minute. In general, making a maximum of 60 API calls per minute should be safe, but higher request rates are allowed depending on the usage pattern. If you receive a throttling error, back off for the remainder of the minute and reduce the rate of subsequent requests.
#Additional information and help on this topic are available for corporate and high-volume customers via their account managers.

#python standard libraries
import time
import base64
import hmac
import hashlib
import json
import logging
import urllib.parse
import datetime

#third party libraries
import requests

#internal libraries
import CSR_toolkit

api_base_endpoint = "https://api.bittrex.com/v3" #production REST api endpoint URL
#api_base_endpoint = "https://127.0.0.1:10000" #testing error handling

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def bittrex_generate_headers(api_key, api_secret, full_url, http_method, request_body="", subaccountId=""):
    logging.critical("bittrex_generate_headers() called")

    nonce = int(time.time()*1000)
    contenthash = hashlib.sha512(request_body.encode()).hexdigest()
    message = str(nonce) + full_url + http_method + contenthash
    signature = hmac.new(api_secret.encode(),
                        message.encode(), hashlib.sha512).hexdigest()
    headers = {
                'Content-Type': 'application/json',
                "Api-Key": api_key,
                "Api-Timestamp": str(nonce),
                "Api-Content-Hash": contenthash, 
                "Api-Signature": signature,
            }
    logging.error("bittrex_generate_headers() returning headers")
    return headers

def bittrex_get_balances(api_key, api_secret):
    logging.critical("bittrex_get_balances() called")
    endpoint = "/balances"
    query_url = api_base_endpoint + endpoint

    headers = bittrex_generate_headers(api_key, api_secret, query_url, "GET")
    try:
        logging.error("attempting to query API")
        balances_response = requests.get(query_url, headers=headers)
    except:
        logging.error("API query timed out - returning 404 response")
        balances_response = CSR_toolkit.StandInStatusCodes(404)

    if balances_response.status_code == 200:
        logging.error("bittrex_get_balances() returning success")
        return "success", balances_response
    elif balances_response.status_code == 401:
        logging.error("bittrex_get_balances() returning error: invalid api key")
        return "error: invalid api key", balances_response
    elif balances_response.status_code == 403:
        logging.error("bittrex_get_balances() returning error: invalid api key")
        return "error: invalid api key", balances_response
    elif balances_response.status_code == 429:
        logging.error("bittrex_get_balances() returning error: rate limiting was applied")
        return "error: rate limiting was applied", balances_response
    elif balances_response.status_code == 404:
        logging.error("bittrex_get_balances() returning error: exchange unavailable")
        return "error: exchange unavailable", balances_response
    else:
        logging.error("bittrex_get_balances() returning error: unknown error")
        return "error: unknown error", balances_response

def bittrex_get_balance_specific_asset(asset_input, api_key, api_secret):
    logging.critical("bittrex_get_balance_specific_asset() called")
    asset_amount = float(0)
    return_status, balance_response = bittrex_get_balances(api_key, api_secret)
    if return_status == "success":
        for asset in balance_response.json():
            if asset["currencySymbol"].upper() == asset_input.upper():
                asset_amount = float(asset["available"])
                logging.error("bittrex_get_balance_specific_asset() returning success")
                return "success", asset_amount
    else:
        logging.error("bittrex_get_balance_specific_asset() returning %s" % str(return_status))
        return return_status, balance_response

def bittrex_market_purchase(api_key, api_secret, currency_pair, fiat_amount, price_quote):
    logging.critical("bittrex_market_purchase() called")
    endpoint = "/orders"
    query_url = api_base_endpoint + endpoint
    fiat_amount = float(fiat_amount)
    price_quote = float(price_quote)
    coin_amount_to_purchase = fiat_amount / price_quote
    coin_amount_to_purchase = format(coin_amount_to_purchase, '.8f') #trim to 8 decimal places, this changes type to string
    
    payload = {
        "marketSymbol": currency_pair, #example: ETH-USD
        "direction": "BUY",
        "type": "MARKET",
        "quantity": str(coin_amount_to_purchase),
        "timeInForce": "IMMEDIATE_OR_CANCEL"  #"timeInForce": "GOOD_TIL_CANCELLED, IMMEDIATE_OR_CANCEL, FILL_OR_KILL, POST_ONLY_GOOD_TIL_CANCELLED, BUY_NOW, INSTANT "
        #"timeInForce": "FILL_OR_KILL"  #"timeInForce": "GOOD_TIL_CANCELLED, IMMEDIATE_OR_CANCEL, FILL_OR_KILL, POST_ONLY_GOOD_TIL_CANCELLED, BUY_NOW, INSTANT "
    }
    
    request_body = json.dumps(payload)
    headers = bittrex_generate_headers(api_key, api_secret, query_url, "POST", request_body=request_body)
    try:
        logging.error("attempting to query API")
        purchase_response = requests.post(query_url, json=payload, headers=headers)
    except:
        logging.error("API query timed out - returning 404 response")
        purchase_response = CSR_toolkit.StandInStatusCodes(404)

    if purchase_response.status_code == 200:
        logging.error("bittrex_market_purchase() returning success")
        return "success", purchase_response
    if purchase_response.status_code == 201:
        logging.error("bittrex_market_purchase() returning success")
        return "success", purchase_response
    elif purchase_response.status_code == 409:
        logging.error("bittrex_market_purchase() returning error: insufficient balance")
        return "error: insufficient balance", purchase_response
    elif purchase_response.status_code == 401:
        logging.error("bittrex_market_purchase() returning error: invalid api key")
        return "error: invalid api key", purchase_response
    elif purchase_response.status_code == 403:
        logging.error("bittrex_market_purchase() returning error: invalid api key")
        return "error: invalid api key", purchase_response
    elif purchase_response.status_code == 404:
        logging.error("bittrex_market_purchase() returning error: exchange unavailable")
        return "error: exchange unavailable", purchase_response
    elif purchase_response.status_code == 429:
        logging.error("bittrex_market_purchase() returning error: rate limiting was applied")
        return "error: rate limiting was applied", purchase_response
    else:
        logging.error("bittrex_market_purchase() returning error: unknown error")
        return "error: unknown error", purchase_response
