####################################################################################################
# The limits on the API are based on the IPs, not the API keys.
# The order rate limit is counted against each account.
####################################################################################################
# https://support.binance.us/hc/en-us/articles/360051091473-Does-Binance-US-have-an-API-
# https://github.com/binance-us/binance-official-api-docs
####################################################################################################

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

api_base_endpoint = "https://api.binance.us" #new production REST api endpoint URL
#api_base_endpoint = "https://127.0.0.1:10000" #testing error handling

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def binance_us_generate_signature(API_SECRET, query_string):
    """
    """
    logging.critical("binance_us_generate_signature() called")
    signature_return = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
    return signature_return.hexdigest()

def binance_us_generate_headers(API_KEY):
    """
    """
    logging.critical("binance_us_generate_headers() called")
    headers = {
    'Accept': 'application/json',
    'X-MBX-APIKEY': API_KEY
    }
    return headers

def binance_us_purchase(symbol, fiat_amount, API_KEY, API_SECRET):
    """
    """
    logging.critical("binance_us_purchase() called")
    full_endpoint = api_base_endpoint + "/api/v3/order"
    
    #symbol = coin_symbol + fiat_symbol #BTCUSD
    side = "BUY" #hard coded
    order_type = "MARKET" #hard coded
    timeInForce = "FOK" #hard coded
    quoteOrderQty = fiat_amount
    recvWindow = "5000" #hard coded
    timestamp = int(time.time()*1000)

    headers = binance_us_generate_headers(API_KEY)

    query_string_before_signature = "symbol=" + str(symbol) + "&" + "side=" + str(side) + "&" + "type=" + str(order_type) + "&" \
    + "&" + "quoteOrderQty=" + str(quoteOrderQty) + "&" + "recvWindow=" + str(recvWindow) + "&" + "timestamp=" + str(timestamp)

    generated_signature = binance_us_generate_signature(API_SECRET, query_string_before_signature)

    query_string_with_signature = query_string_before_signature + "&" + "signature=" + str(generated_signature)

    full_query_string_with_endpoint = full_endpoint + "?" + query_string_with_signature

    try:
        logging.error("attempting to query API")
        purchase_response = requests.post(full_query_string_with_endpoint, headers=headers)
    except:
        logging.error("API query timed out - returning 404 response")
        purchase_response = CSR_toolkit.StandInStatusCodes(404)

    if purchase_response.status_code == 200:
        logging.error("returning success")
        return "success", purchase_response
    
    elif purchase_response.status_code == 400:
        if "insufficient balance" in purchase_response.json()["msg"].lower():
            logging.error("returning error: insufficient balance")
            return "error: insufficient balance", purchase_response
        elif "signature" in purchase_response.json()["msg"].lower():
            logging.error("returning error: invalid api key")
            return "error: invalid api key", purchase_response
        else:
            logging.error("returning error: unknown error")
            return "error: unknown error", purchase_response
    
    elif purchase_response.status_code == 401: #permission denied, invalid API key
        if "api" or "key" in purchase_response.json()["msg"].lower():
            logging.error("returning error: invalid api key")
            return "error: invalid api key", purchase_response
        else:
            logging.error("returning error: unknown error")
            return "error: unknown error", purchase_response
    
    elif purchase_response.status_code == 429: #return code is used when breaking a request rate limit.
        logging.error("returning error: breaking rate limit")
        return "error: breaking rate limit", purchase_response

    elif purchase_response.status_code == 418: #return code is used when an IP has been auto-banned for continuing to send requests after receiving 429 codes.
        logging.error("returning error: IP has been auto-banned for breaking rate limit")
        return "error: IP has been auto-banned for breaking rate limit", purchase_response

    elif purchase_response.status_code == 404:
        logging.error("returning error: exchange unavailable")
        return "error: exchange unavailable", purchase_response

    else:
        logging.error("returning error: unknown error")
        return "error: unknown error", purchase_response
    
def binance_us_account_balances(API_KEY, API_SECRET):
    """
    """
    logging.critical("binance_us_account_balances() called")
    full_endpoint = api_base_endpoint + "/api/v3/account"
    recvWindow = "5000" #hard coded
    timestamp = int(time.time()*1000)

    headers = binance_us_generate_headers(API_KEY)

    query_string_before_signature = "recvWindow=" + str(recvWindow) + "&" + "timestamp=" + str(timestamp)

    generated_signature = binance_us_generate_signature(API_SECRET, query_string_before_signature)

    query_string_with_signature = query_string_before_signature + "&" + "signature=" + str(generated_signature)

    full_query_string_with_endpoint = full_endpoint + "?" + query_string_with_signature
    
    try:
        logging.error("attempting to query API")
        account_balance_response = requests.get(full_query_string_with_endpoint, headers=headers)
    except:
        logging.error("API query timed out - returning 404 response")
        account_balance_response = CSR_toolkit.StandInStatusCodes(404)

    if account_balance_response.status_code == 200:
        logging.error("returning success")
        return "success", account_balance_response
    
    elif account_balance_response.status_code == 400:
        if "signature" in account_balance_response.json()["msg"].lower():
            logging.error("returning error: invalid api key")
            return "error: invalid api key", account_balance_response
        else:
            logging.error("returning error: unknown error")
            return "error: unknown error", account_balance_response

    elif account_balance_response.status_code == 401:
        if "api" or "key" in account_balance_response.json()["msg"].lower():
            logging.error("returning error: invalid api key")
            return "error: invalid api key", account_balance_response
        else:
            logging.error("returning error: unknown error")
            return "error: unknown error", account_balance_response
    
    elif account_balance_response.status_code == 429: #return code is used when breaking a request rate limit.
        logging.error("returning error: breaking rate limit")
        return "error: breaking rate limit", account_balance_response

    elif account_balance_response.status_code == 418: #return code is used when an IP has been auto-banned for continuing to send requests after receiving 429 codes.
        logging.error("returning error: IP has been auto-banned for breaking rate limit")
        return "error: IP has been auto-banned for breaking rate limit", account_balance_response

    elif account_balance_response.status_code == 404:
        logging.error("returning error: exchange unavailable")
        return "error: exchange unavailable", account_balance_response

    else:
        logging.error("returning error: unknown error")
        return "error: unknown error", account_balance_response

def binance_us_account_balance_specific_asset(asset_input, API_KEY, API_SECRET):
    logging.critical("binance_us_account_balance_specific_asset() called")
    asset_balance = 0 #set to 0 as a default incase the asset doesn't exist yet
    return_status, balance_response = binance_us_account_balances(API_KEY, API_SECRET)
    if balance_response.status_code == 200:
        for asset_iter in balance_response.json()["balances"]:
            if asset_iter["asset"].upper() == str(asset_input).upper():
                asset_balance = int(float(asset_iter["free"]))
                logging.error("returning asset balance")
                return return_status, asset_balance
    elif balance_response.status_code == 404:
        logging.error("returning: error: exchange unavailable")
        return "error: exchange unavailable", balance_response
    else:
        logging.error("returning error")
        return return_status, balance_response
