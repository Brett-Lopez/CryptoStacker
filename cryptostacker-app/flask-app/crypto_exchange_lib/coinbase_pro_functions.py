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

#todo: add 401 and non-200 error handling to these functions
#todo: btc & ltc buy loop, switch to single currency pair
#api_base_endpoint = "https://api.pro.coinbase.com" #old production REST api endpoint URL
api_base_endpoint = "https://api.exchange.coinbase.com" #new production REST api endpoint URL
#api_base_endpoint = "https://127.0.0.1:10000" #testing error handling

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def coinbase_pro_get_auth_headers(api_key, secret_key, passphrase, requestpath, method="GET", message_body=""):
    """
    Generates the auth headers required for API calls
    Output: dictionary of required coinbase API headers
    """
    logging.critical("coinbase_pro_get_auth_headers() called")
    epoch_timestamp = str(time.time())
    message = epoch_timestamp + method + requestpath + message_body
    message = message.encode('ascii')
    hmac_key = base64.b64decode(secret_key)
    signature = hmac.new(hmac_key, message, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest())
    generated_headers = {
        'Content-Type': 'Application/JSON',
        'CB-ACCESS-SIGN': signature_b64,
        'CB-ACCESS-TIMESTAMP': epoch_timestamp,
        'CB-ACCESS-KEY': api_key,
        'CB-ACCESS-PASSPHRASE': passphrase
    }
    return generated_headers

def coinbase_pro_api_get(api_key, api_secret, api_passphrase, method="GET", message_body="", requestpath="", params=None):
    """
    Generic Coinbase API GET request
    Output: Coinbase API response
    """
    logging.critical("coinbase_pro_api_get() called")
    requestpath = requestpath
    generated_signature = coinbase_pro_get_auth_headers(api_key, api_secret, api_passphrase, requestpath, method=method, message_body=message_body)
    api_full_request_url = api_base_endpoint + requestpath
    try:
        logging.error("attempting to query API")
        coinbase_api_response = requests.get(api_full_request_url, data=message_body, headers=generated_signature)
    except:
        logging.error("API query timed out - returning 404 response")
        coinbase_api_response = CSR_toolkit.StandInStatusCodes(404)
    return coinbase_api_response

def coinbase_pro_api_post(api_key, api_secret, api_passphrase, method="POST", message_body="", requestpath="", amount=None, currency=None, payment_method_id=None):
    """
    Generic Coinbase API POST request
    Output: Coinbase API response
    """
    logging.critical("coinbase_pro_api_post() called")
    requestpath = requestpath
    generated_signature = coinbase_pro_get_auth_headers(api_key, api_secret, api_passphrase, requestpath, method=method, message_body=message_body)
    api_full_request_url = api_base_endpoint + requestpath
    try:
        logging.error("attempting to query API")
        coinbase_api_response = requests.post(api_full_request_url, data=message_body, headers=generated_signature)
    except:
        logging.error("API query timed out - returning 404 response")
        coinbase_api_response = CSR_toolkit.StandInStatusCodes(404)
    return coinbase_api_response

def coinbase_pro_get_fiat_balance(fiat, api_key, api_secret, api_passphrase):
    """
    Retrieve your fiat balance, this should be renamed to GetCoinbaseFiatbalance
    Input: fiat currency such as "USD" - string
    Input: API key
    Input: API secret
    Input: API passphrase
    Output: USD balance - float
    """
    logging.critical("coinbase_pro_get_fiat_balance() called")
    account_balances_response = coinbase_pro_api_get(api_key, api_secret, api_passphrase, requestpath="/accounts")
    
    if account_balances_response.status_code == 200:
        account_balances_response_object = account_balances_response.json()
        for currency in account_balances_response_object:
            if currency["currency"] == fiat:
                USD_balance = eval(currency["balance"]) #todo change eval() to float()
        #This sequence of truncating to decimal places is required by coinbase's api which will often complain that an amount is too specific, trim to $0.01 to be safe.  These steps could also be done with math.trunc.
        USD_balance = float(USD_balance) #change type to float
        USD_balance = format(USD_balance, '.2f') #trim to 2 decimal places, this changes type to string
        USD_balance = float(USD_balance) #change type to float
        logging.error("returning: success")
        return "success", USD_balance

    elif account_balances_response.status_code == 401:
        logging.error("returning: error: invalid api key")
        return "error: invalid api key", account_balances_response
    
    elif account_balances_response.status_code == 404:
        logging.error("returning: error: exchange unavailable")
        return "error: exchange unavailable", account_balances_response

    else:
        logging.error("returning: error: unknown error")
        return "error: unknown error", account_balances_response

def coinbase_pro_market_purchase(amount, tradingpair, api_key, api_secret, api_passphrase):
    """
    Submit a market order
    Input: amount, the fiat amount which will be trimmed down to two decimal places - supported types: string, int, float
    Input: tradingpair, the crypto/fiat pair to trade
    Output: Coinbase API response
    """
    logging.critical("coinbase_pro_market_purchase() called")
    amount = format(amount, '.2f') #trim to 2 decimal places, this changes type to string
    amount = float(amount) #change type to float
    message_body = {
    "type": "market",
    "side": "buy",
    "product_id": tradingpair,
    #"size": "BTC_AMOUNT_HERE", #base currency 
    "funds": amount #amount of USD to be used in market purchase
    }
    json_message_body = json.dumps(message_body)
    purchase_response = coinbase_pro_api_post(api_key, api_secret, api_passphrase, method="POST", message_body=json_message_body, requestpath="/orders")
    
    if purchase_response.status_code == 200:
        logging.error("returning: success")
        return "success", purchase_response

    elif purchase_response.status_code == 401:
        logging.error("returning: error: invalid api key")
        return "error: invalid api key", purchase_response
    
    elif purchase_response.status_code == 404:
        logging.error("returning: error: exchange unavailable")
        return "error: exchange unavailable", purchase_response

    else:
        logging.error("returning: error: unknown error")
        return "error: unknown error", purchase_response

def get_available_btc_ltc_eth_balances(api_key, api_secret, api_passphrase):
    """
    Retrieves the balances of BTC and LTC and ETH
    Output: bitcoin's available balance & litecoin's available balance - floats
    """
    logging.critical("get_available_btc_ltc_eth_balances() called")
    bitcoin_available_balance = float(0)
    litecoin_available_balance = float(0)
    ether_available_balance = float(0)
    message_body = {
    "currency": "BTC",
    "currency": "LTC",
    "currency": "ETH"
    }
    json_message_body = json.dumps(message_body) #convert dict to json object
    balances_response_object = coinbase_pro_api_get(api_key, api_secret, api_passphrase, method="GET", message_body=json_message_body, requestpath="/accounts")
    if balances_response_object.status_code == 200:
        balances_response_object = balances_response_object.json()
        for item in balances_response_object:
            if item["currency"].upper() == "BTC":
                bitcoin_available_balance = item["available"]
            if item["currency"].upper() == "LTC":
                litecoin_available_balance = item["available"]
            if item["currency"].upper() == "ETH":
                ether_available_balance = item["available"]
        logging.error("returning: success")
        return "success", float(bitcoin_available_balance), float(litecoin_available_balance), float(ether_available_balance)
    
    elif balances_response_object.status_code == 404:
        logging.error("returning: error: exchange unavailable")
        return "error: exchange unavailable", balances_response_object

    else:
        logging.error("returning: error: unknown error")
        return "error: unknown error", balances_response_object

def coinbase_pro_purchase_loop(api_key, api_secret, api_passphrase, CurrencyPair_String, fiat_purchase_amount, retry_threshold, sleep_time_seconds):
    #todo improve this function to make use of status codes from coinbase_pro_market_purchase()
    """
    Because order submissions can fail for numerous reasons (though not common) this function attempts purchases multiple times until successful and uses the global sleep value between retrys
    Input: CurrencyPair_String, the crypto/fiat pair to trade ("BTC-USD", "LTC-USD")
    Input: retry_threshold, the number of retries that will be attempted
    Output: Coinbase API response
    """
    logging.critical("coinbase_pro_purchase_loop() called")

    purchase_retry_tracker = True
    retry_counter = 0

    while purchase_retry_tracker is True: #retry while loop
        logging.warning("Purchasing %s" % CurrencyPair_String)
        return_status, purchase_response = coinbase_pro_market_purchase(fiat_purchase_amount, CurrencyPair_String, api_key, api_secret, api_passphrase)
        purchase_response_object = purchase_response.json()
        
        if purchase_response.status_code == 404:
            logging.error("returning: error: exchange unavailable")
            return "error: exchange unavailable", purchase_response

        if return_status == "success":
            if "product_id" in purchase_response_object: #if purchase successful break while loop
                if purchase_response_object["product_id"] == CurrencyPair_String: #key/value pair found in a successful purchase submission
                    logging.warning("purchase success")
                    logging.warning("Purchase response object: %s" % purchase_response_object)
                    return "success", purchase_response_object
            if "message" in purchase_response_object:
                if purchase_response_object["message"] == "Insufficient funds":
                    logging.warning("Insufficient funds")
                    logging.warning("Purchase response object: %s" % purchase_response_object)
                    return "error: insufficient funds", purchase_response_object
            logging.warning("Purchase response object: %s" % purchase_response_object)
            retry_counter += 1
            if retry_counter > retry_threshold: #if retry hits threshold break while loop
                logging.warning("retry_threshold reached")
                logging.warning("Purchase response object: %s" % purchase_response_object)
                logging.error("returning: error: all attempts failed")
                return "error: all attempts failed", purchase_response_object
            time.sleep(sleep_time_seconds)
            logging.debug("end of while loop #%s" % retry_counter)



def coinbase_pro_validate_transfer_disabled(api_key, api_secret, api_passphrase, currency, crypto_address):
    """
    We want to ensure users are not setting overly permissive coinbase API keys.  Only the "trade" permission is required for CryptoStacker, the "transfer" permission is not required and therefore overly permissive.
    Input: API keys, fiat currency, crypto address (can be fake)
    """
    logging.critical("coinbase_pro_validate_transfer_disabled() called")
    currency_var = urllib.parse.quote_plus(str(currency))
    crypto_address_var = urllib.parse.quote_plus(str(crypto_address))

    request_path_string = "/withdrawals/fee-estimate?currency=" + currency_var + "&crypto_address=" + crypto_address_var
    
    estimated_fee_response = coinbase_pro_api_get(api_key, api_secret, api_passphrase, requestpath=request_path_string)

    #estimated_fee_response = estimated_fee_response.json()

    if estimated_fee_response.status_code == 200:
        return "success", estimated_fee_response

    elif estimated_fee_response.status_code == 401:
        return "invalid", estimated_fee_response

    elif estimated_fee_response.status_code == 403:
        return "forbidden, no transfer role/permission", estimated_fee_response

    elif estimated_fee_response.status_code == 404:
        logging.error("returning: error: exchange unavailable")
        return "error: exchange unavailable", estimated_fee_response

    else:
        return "error: unknown error", estimated_fee_response