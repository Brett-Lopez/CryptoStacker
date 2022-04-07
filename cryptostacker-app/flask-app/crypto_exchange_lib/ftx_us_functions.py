#https://docs.ftx.us/#overview
#Hitting our rate limits will result in HTTP 429 errors. Non-order placement requests do not count towards rate limits. Rate limits are tiered by account trading volumes. For details, please see this post here. Note that limits in the linked post are at the account level
#https://docs.ftx.us/#rate-limits
#https://help.ftx.com/hc/en-us/articles/360052595091-2020-11-20-Ratelimit-Updates
#https://github.com/wanth1997/python-ftx/blob/master/ftx/authentication.py

#python standard libraries
import time
import base64
import hmac
import hashlib
import json
import logging
import urllib.parse

#third party libraries
import requests

#internal libraries
import CSR_toolkit

api_base_endpoint = "https://ftx.us" #new production REST api endpoint URL
#api_base_endpoint = "https://127.0.0.1:10000" #testing error handling

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def ftx_us_generate_headers(api_key, api_secret, endpoint, http_method, request_body=""):
    logging.critical("ftx_us_generate_headers() called")

    nonce = int(time.time()*1000)
    message = str(nonce) + http_method.upper() + endpoint + request_body
    print(message)
    
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    headers = {
            'FTXUS-KEY': api_key,
            'FTXUS-TS': str(nonce),
            'FTXUS-SIGN': signature
            }
    logging.error("ftx_us_generate_headers() returning headers")
    return headers

def ftx_us_get_balances(api_key, api_secret):
    logging.critical("ftx_us_get_balances() called")
    endpoint = "/api/wallet/balances"
    full_url = api_base_endpoint + endpoint
    headers = ftx_us_generate_headers(api_key, api_secret, endpoint, "GET", request_body="")
    try:
        logging.error("attempting to query API")
        balances_response = requests.get(full_url, headers=headers)
    except:
        logging.error("API query timed out - returning 404 response")
        balances_response = CSR_toolkit.StandInStatusCodes(404)

    if balances_response.status_code == 200:
        return "success", balances_response
    elif balances_response.status_code == 401:
        return "error: invalid api key", balances_response
    elif balances_response.status_code == 404:
        return "error: exchange unavailable", balances_response
    elif balances_response.status_code == 429:
        return "error: invalid api key", balances_response
    else:
        return "error: unknown error", balances_response

def ftx_us_get_balance_specific_asset(asset_input, api_key, api_secret):
    logging.critical("ftx_us_get_balance_specific_asset() called")
    asset_amount = float(0)
    return_status, balances_response = ftx_us_get_balances(api_key, api_secret)
    if return_status == "success":
        for asset in balances_response.json()["result"]:
            if asset["coin"].upper() == asset_input.upper(): 
                asset_amount = float(asset["free"]) #should we use availableWithoutBorrow instead of free?
                return "success", asset_amount
    else:
        return return_status, balances_response

def ftx_us_market_purchase(api_key, api_secret, currency_pair, fiat_amount, price_quote):
    logging.critical("ftx_us_market_purchase() called")
    endpoint = "/api/orders"
    full_url = api_base_endpoint + endpoint
    fiat_amount = float(fiat_amount)
    price_quote = float(price_quote)
    coin_amount_to_purchase = fiat_amount / price_quote
    coin_amount_to_purchase = format(coin_amount_to_purchase, '.8f') #trim to n decimal places, this changes type to string

    payload = { #this purchases all $100 worth of balance
        "market": currency_pair, #example "BTC/USD"
        "side": "buy",
        "type": "market",
        "price": "0",
        "size": str(coin_amount_to_purchase)
        #"reduceOnly": false,
        #"ioc": false,
        #"postOnly": false,
        #"clientId": null,
    }
    request_body = json.dumps(payload)
    headers = ftx_us_generate_headers(api_key, api_secret, endpoint, "POST", request_body=request_body)
    try:
        logging.error("attempting to query API")
        purchase_response = requests.post(full_url, headers=headers, json=payload)
    except:
        logging.error("API query timed out - returning 404 response")
        purchase_response = CSR_toolkit.StandInStatusCodes(404)
    print(purchase_response.status_code)
    print(purchase_response.json())
    if purchase_response.status_code == 200:
        return "success", purchase_response
    elif purchase_response.status_code == 401:
        return "error: invalid api key", purchase_response
    elif purchase_response.status_code == 400:
        logging.error("error: insufficient balance or missing parameter")
        return "error: insufficient balance", purchase_response
    elif purchase_response.status_code == 404:
        return "error: exchange unavailable", purchase_response
    elif purchase_response.status_code == 429:
        return "error: rate limiting was applied", purchase_response
    else:
        return "error: unknown error", purchase_response
