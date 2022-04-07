#python standard libraries
import time
import base64
import hmac
import hashlib
import json
import logging
import datetime
import urllib.parse

#third party libraries
import requests

#internal libraries
import CSR_toolkit

api_base_endpoint = "https://api.gemini.com" #production REST api endpoint URL
#api_base_endpoint = "https://127.0.0.1:10000" #testing error handling

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def gemini_generate_headers(api_key, api_secret, payload):
    logging.critical("gemini_generate_headers() called")
    gemini_api_key = str(api_key)
    gemini_api_secret = str(api_secret).encode()

    date_time_now = datetime.datetime.now()
    payload_nonce =  str(int(time.mktime(date_time_now.timetuple())*1000))
    payload["nonce"] = payload_nonce
    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

    headers = {
        'Content-Type': "text/plain",
        'Content-Length': "0",
        'X-GEMINI-APIKEY': gemini_api_key,
        'X-GEMINI-PAYLOAD': b64,
        'X-GEMINI-SIGNATURE': signature,
        'Cache-Control': "no-cache"
        }

    logging.error("gemini_generate_headers() returning headers")
    return headers

def gemini_get_balance(api_key, api_secret):
    logging.critical("gemini_get_balance() called")
    endpoint = "/v1/balances"
    query_url = api_base_endpoint + endpoint
    
    payload = {
    "nonce": "nonce",
    "request": endpoint}
    
    generated_headers = gemini_generate_headers(api_key, api_secret, payload)
    try:
        logging.error("attempting to query API")
        balance_response = requests.post(query_url, data=None, headers=generated_headers)
    except:
        logging.error("API query timed out - returning 404 response")
        balance_response = CSR_toolkit.StandInStatusCodes(404)

    if balance_response.status_code == 200:
        logging.error("gemini_get_balance() returning success")
        return "success", balance_response
    elif balance_response.status_code == 404: #exchange unavailable #this must come before "elif reason" because there is no json method of StandInStatusCodes
        logging.error("gemini_get_balance() returning error: exchange unavailable")
        return "error: exchange unavailable", balance_response
    elif balance_response.status_code == 400: #invalid signature / invalid api key
        logging.error("gemini_get_balance() returning error: invalid api key")
        return "error: invalid api key", balance_response
    elif balance_response.status_code == 403: #api key invalid
        logging.error("gemini_get_balance() returning error: invalid api key")
        return "error: invalid api key", balance_response
    elif balance_response.status_code == 429: #rate limiting applied
        logging.error("gemini_get_balance() returning error: rate limiting was applied")
        return "error: rate limiting was applied", balance_response
    elif not isinstance(balance_response.json(), type(None)): #if not NoneType
        if "reason" in balance_response.json():
            if balance_response.json()["reason"] == "InvalidNonce":
                logging.error("gemini_get_balance() returning error: invalid nonce")
                return "error: invalid nonce", balance_response
    else:
        logging.error("gemini_get_balance() returning error: unknown error")
        return "error: unknown error", balance_response

def gemini_get_balance_specific_asset(asset_input, api_key, api_secret):
    logging.critical("gemini_get_balance_specific_asset() called")
    asset_amount = float(0)
    return_status, balance_response = gemini_get_balance(api_key, api_secret)
    if return_status == "success":
        for asset in balance_response.json():
            if asset["currency"].upper() == str(asset_input).upper():
                asset_amount = float(asset["amount"])
                logging.error("gemini_get_balance_specific_asset() returning success")
                return "success", asset_amount
        if asset_amount == 0: #todo, remove this if statement and test, it shouldn't be needed
            logging.error("gemini_get_balance_specific_asset() returning success")
            return "success", asset_amount
    else:
        logging.error("gemini_get_balance_specific_asset() returning %s" % return_status)
        return return_status, balance_response

def gemini_purchase(api_key, api_secret, currency_pair, coin_amount_to_purchase, fiat_price):
    logging.critical("gemini_purchase() called")
    endpoint = "/v1/order/new"
    query_url = api_base_endpoint + endpoint

    payload = {
        "request": endpoint,
        "nonce": "payload_nonce",
        "symbol": str(currency_pair).lower(), #example btcusd
        "amount": str(coin_amount_to_purchase),
        "price": str(fiat_price),
        "side": "buy",
        "type": "exchange limit",
        "options": ["fill-or-kill"] 
    }

    generated_headers = gemini_generate_headers(api_key, api_secret, payload)
    
    try:
        logging.error("attempting to query API")
        purchase_response = requests.post(query_url, data=None, headers=generated_headers)
    except:
        logging.error("API query timed out - returning 404 response")
        purchase_response = CSR_toolkit.StandInStatusCodes(404)

    logging.error(purchase_response.json()) #debugging remove later
    if purchase_response.status_code == 200:
        logging.error("gemini_purchase() returning success")
        return "success", purchase_response
    elif purchase_response.status_code == 404: #exchange unavailable #this must come before "elif reason" because there is no json method of StandInStatusCodes
        logging.error("gemini_purchase() returning error: exchange unavailable")
        return "error: exchange unavailable", purchase_response
    elif purchase_response.status_code == 406: #Insufficient Funds
        logging.error("gemini_purchase() returning error: insufficient balance")
        return "error: insufficient balance", purchase_response
    elif purchase_response.status_code == 400: #invalid signature / invalid API key
        logging.error("gemini_purchase() returning error: invalid API key")
        return "error: invalid API key", purchase_response
    elif purchase_response.status_code == 403: #api key invalid
        logging.error("gemini_purchase() returning error: invalid API key")
        return "error: invalid API key", purchase_response
    elif purchase_response.status_code == 429: #rate limiting applied
        logging.error("gemini_purchase() returning error: rate limiting was applied")
        return "error: rate limiting was applied", purchase_response
    elif not isinstance(purchase_response.json(), type(None)): #if not NoneType
        if "reason" in purchase_response.json():
            if purchase_response.json()["reason"] == "InvalidNonce":
                logging.error("gemini_get_balance() returning error: invalid nonce")
                return "error: invalid nonce", purchase_response
            elif purchase_response.json()["reason"] == "InvalidQuantity":
                logging.error("gemini_get_balance() returning error: invalid quantity")
                return "error: invalid quantity", purchase_response
    else:
        logging.error("gemini_purchase() returning error: unknown error")
        return "error: unknown error", purchase_response

def gemini_diy_market_purchase(api_key, api_secret, fiat_amount, currency_pair, percentage_increase, price_quote):
    logging.critical("gemini_diy_market_purchase() called")
    fiat_amount = float(fiat_amount)
    percentage_increase = float(percentage_increase)
    price_quote = float(price_quote)
    coin_amount_to_purchase = fiat_amount / price_quote

    #eth: 6, btc: 8, #ltc: 5
    if currency_pair.lower() == "btcusd":
        coin_amount_to_purchase = format(coin_amount_to_purchase, '.8f') #trim to n decimal places, this changes type to string
    if currency_pair.lower() == "ethusd":
        coin_amount_to_purchase = format(coin_amount_to_purchase, '.6f') #trim to n decimal places, this changes type to string
    if currency_pair.lower() == "ltcusd":
        coin_amount_to_purchase = format(coin_amount_to_purchase, '.5f') #trim to n decimal places, this changes type to string
    
    while_counter = 0
    attempt_threshold = 100

    while True:
        if while_counter >= attempt_threshold:
            break
        return_status, purchase_response = gemini_purchase(api_key, api_secret, currency_pair, coin_amount_to_purchase, price_quote)
        print(purchase_response.json()) #debugging remove later
        if return_status == "success":
            if float(purchase_response.json()["executed_amount"]) != float(0):
                logging.error("gemini_diy_market_purchase() returning success - order filled successfully")
                return "success", purchase_response
            elif float(purchase_response.json()["executed_amount"]) == float(0):
                while_counter += 1
                price_quote = float(format(price_quote * (float(1.0) + percentage_increase), '.2f'))
                logging.error("gemini_diy_market_purchase() increase bid to: %s" % price_quote)
                logging.error("sleep for n seconds")
                time.sleep(3) #todo figure out better sleep time

        elif purchase_response.status_code == 404:
            logging.error("gemini_diy_market_purchase() exchange unavailable")
            return "error: exchange unavailable", purchase_response
        elif purchase_response.status_code == 429:
            logging.error("gemini_diy_market_purchase() rate limited, sleeping for n seconds")
            logging.error("sleep for n seconds")
            time.sleep(61) #todo figure out better sleep time
        elif return_status != "success":
            logging.error("gemini_diy_market_purchase() returning %s" % return_status)
            return return_status, purchase_response
        else:
            logging.error("gemini_diy_market_purchase() returning %s" % return_status)
            return return_status, purchase_response

def gemini_get_current_price():
    logging.critical("gemini_get_current_price() called")
    #price information which is subject to IP based rate limiting of 120 requests per minute
    #this function should not be used, instead use coingecko data that is fed into DCA purchaser from cron-events
    base_url = "https://api.gemini.com/v1"
    response = requests.get(base_url + "/pubticker/btcusd")
    btc_data = response.json()
    print(btc_data)
    return btc_data

#200 	Request was successful
#30x 	API entry point has moved, see Location: header. Most likely an http: to https: redirect.
#400 	Auction not open or paused, ineligible timing, market not open, or the request was malformed; in the case of a private API request, missing or malformed Gemini private API authentication headers
#403 	The API key is missing the role necessary to access this private API endpoint
#404 	Unknown API entry point or Order not found
#406 	Insufficient Funds
#429 	Rate Limiting was applied
#500 	The server encountered an error
#502 	Technical issues are preventing the request from being satisfied
#503 	The exchange is down for maintenance
