#https://docs.kraken.com/rest/

#python standard libraries
import time
import base64
import hmac
import hashlib
import os
import json
import logging
import urllib.parse

#third party libraries
import requests

#internal libraries
import CSR_toolkit

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

#https://api.kraken.com/0/public/SystemStatus
api_url = "https://api.kraken.com"
#api_url = "https://127.0.0.1:10000" #testing error handling

kraken_asset_map_balaces = {
    "USD": "ZUSD",
    "BTC": "XXBT",
    "ETH": "XETH",
    "LTC": "XLTC",
    "ETH2": "ETH2",
}

kraken_asset_map_purchases = {
    "USD": "USD",
    "BTC": "XBT",
    "ETH": "ETH",
    "LTC": "LTC",
    "ETH2": "ETH2"
}

def kraken_get_kraken_signature(urlpath, data, api_secret):
    logging.critical("kraken_get_kraken_signature() called")
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(api_secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    logging.error("kraken_get_kraken_signature() returning signature")
    return sigdigest.decode()

def kraken_post_request(uri_path, data, api_key, api_secret):
    logging.critical("kraken_post_request() called")
    headers = {}
    headers['API-Key'] = api_key
    headers['API-Sign'] = kraken_get_kraken_signature(uri_path, data, api_secret)
    try:
        logging.error("attempting to query API")
        response = requests.post((api_url + uri_path), headers=headers, data=data)
    except:
        logging.error("API query timed out - returning 404 response")
        response = CSR_toolkit.StandInStatusCodes(404)
    
    logging.error("kraken_post_request() returning http response")
    return response

def kraken_get_balances(api_key, api_secret):
    logging.critical("kraken_get_balances() called")
    data = {
        "nonce": str(int(1000*time.time()))
    }
    balance_response = kraken_post_request('/0/private/Balance', data, api_key, api_secret)
    if balance_response.status_code == 200: #status code 200 is returned even when there are errors such as API keys invalid, error handling must be done using the error key
        if not balance_response.json()["error"]: #no error
            logging.error("kraken_get_balances() returning success")
            return "success", balance_response
        elif balance_response.json()["error"]: #error
            for error in balance_response.json()["error"]:
                if "invalid key" in error.lower() or "invalid signature" in error.lower():
                    logging.error("kraken_get_balances() returning error: invalid api key")
                    return "error: invalid api key", balance_response
                elif "insufficient funds" in error.lower():
                    logging.error("kraken_get_balances() returning error: insufficient balance")
                    return "error: insufficient balance", balance_response
                elif "invalid nonce" in error.lower():
                    logging.error("kraken_get_balances() returning error: invalid nonce")
                    return "error: invalid nonce", balance_response
                elif "rate limit exceeded" in error.lower():
                    logging.error("kraken_get_balances() returning error: rate limit exceeded")
                    return "error: rate limit exceeded", balance_response
                else:
                    logging.error("kraken_get_balances() returning error: %s" % error.lower())
                    return "error: %s" % error.lower(), balance_response
        else:
            logging.error("kraken_get_balances() returning error: unknown error")
            return "error: unknown error", balance_response
    elif balance_response.status_code == 404:
        logging.error("returning error: exchange unavailable")
        return "error: exchange unavailable", balance_response
    else:
        logging.error("kraken_get_balances() returning error: unknown error")
        return "error: unknown error", balance_response

def kraken_get_balance_specific_asset(asset_input, api_key, api_secret):
    logging.critical("kraken_get_balance_specific_asset() called")
    return_status, balances_response = kraken_get_balances(api_key, api_secret)
    asset_amount = float(0)
    if return_status == "success":
        asset_input = asset_input.upper()
        if "result" in balances_response.json():
            if asset_input in balances_response.json()["result"]:
                asset_amount = float(balances_response.json()["result"][asset_input])
                logging.error("kraken_get_balance_specific_asset() returning success")
                return return_status, asset_amount
        logging.error("kraken_get_balance_specific_asset() returning success")
        return return_status, asset_amount
    elif return_status != "success":
        logging.error("kraken_get_balance_specific_asset() returning %s" % return_status)
        return return_status, asset_amount

def kraken_purchase(api_key, api_secret, currency_pair, coin_amount):
    logging.critical("kraken_purchase() called")
    data = {
    "nonce": str(int(1000*time.time())),
    "ordertype": "market",
    "type": "buy",
    "volume": str(coin_amount), #example 1.25
    "pair": currency_pair, #example XBTUSD
    }

    add_order_response = kraken_post_request('/0/private/AddOrder', data, api_key, api_secret)
    if add_order_response.status_code == 200: #status code 200 is returned even when there are errors such as API keys invalid, error handling must be done using the error key
        if not add_order_response.json()["error"]: #no error
            logging.error("kraken_purchase() returning success")
            return "success", add_order_response
        elif add_order_response.json()["error"]: #error
            for error in add_order_response.json()["error"]:
                if "invalid key" in error.lower() or "invalid signature" in error.lower():
                    logging.error("kraken_purchase() returning error: invalid api key")
                    return "error: invalid api key", add_order_response
                elif "invalid arguments" in error.lower() and "volume" in error.lower():
                    logging.error("kraken_purchase() returning error: invalid volume - increase volume (amount of coin)")
                    return "error: invalid volume - increase volume (amount of coin)", add_order_response
                elif "insufficient funds" in error.lower():
                    logging.error("kraken_purchase() returning error: insufficient balance")
                    return "error: insufficient balance", add_order_response
                elif "invalid nonce" in error.lower():
                    logging.error("kraken_purchase() returning error: invalid nonce")
                    return "error: invalid nonce", add_order_response
                elif "rate limit exceeded" in error.lower():
                    logging.error("kraken_purchase() returning error: rate limit exceeded")
                    return "error: rate limit exceeded", add_order_response
                else:
                    logging.error("kraken_purchase() returning error: %s" % error.lower())
                    return "error: %s" % error.lower(), add_order_response
    elif add_order_response.status_code == 404:
        logging.error("returning error: exchange unavailable")
        return "error: exchange unavailable", add_order_response
    else:
        logging.error("kraken_purchase() returning error: unknown error")
        return "error: unknown error", add_order_response

def kraken_diy_market_purchase(api_key, api_secret, currency_pair, fiat_amount, percentage_increase, price_quote):
    logging.critical("kraken_diy_market_purchase() called")
    fiat_amount = float(fiat_amount)
    percentage_increase = float(percentage_increase)
    price_quote = float(price_quote)
    coin_amount_to_purchase = fiat_amount / price_quote
    coin_amount_to_purchase = float(format(coin_amount_to_purchase, '.8f')) #trim to 8 decimal places, this changes type to string
    
    while_counter = 0
    attempt_threshold = 50

    while True:
        if while_counter >= attempt_threshold:
            break
        return_status, purchase_response = kraken_purchase(api_key, api_secret, currency_pair, coin_amount_to_purchase)
        if return_status == "success":
            logging.error("kraken_diy_market_purchase() returning success - order filled successfully")
            return "success", purchase_response
        elif return_status != "success":
            if "volume" in return_status: #this indicates that the amount of coin to be purchased is less than the $10 minimum
                while_counter += 1
                coin_amount_to_purchase = float(format(coin_amount_to_purchase * (float(1.0) + percentage_increase), '.8f'))
                logging.error("kraken_diy_market_purchase() increasing volume to: %s" % coin_amount_to_purchase)
                logging.error("sleep for n seconds")
                time.sleep(3) #todo figure out better sleep time
            else:
                logging.error("kraken_diy_market_purchase() returning %s" % return_status)
                return return_status, purchase_response
        else:
            logging.error("kraken_diy_market_purchase() returning %s" % return_status)
            return return_status, purchase_response
