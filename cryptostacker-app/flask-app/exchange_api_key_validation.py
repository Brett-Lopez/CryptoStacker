import requests
import logging
import CSR_toolkit
#import coinbase_pro_functions
from crypto_exchange_lib import coinbase_pro_functions
from crypto_exchange_lib import binance_us_functions
from crypto_exchange_lib import gemini_functions
from crypto_exchange_lib import bittrex_functions
from crypto_exchange_lib import ftx_us_functions
from crypto_exchange_lib import kraken_functions

logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def validate_api_key(exchange, api_key, api_secret, api_passphrase=None):
    """
    input > exchange, api_key, api_secret, api_passphrase (strings)
    output > "valid" or "invalid" (strings)
    """
    logging.critical("validate_api_key() was called")

    if exchange == "coinbase_pro":
        validation_return = validate_api_key_coinbase_pro(api_key, api_secret, api_passphrase)

    if exchange == "bittrex":
        validation_return = validate_api_key_bittrex(api_key, api_secret)

    if exchange == "kraken":
        validation_return = validate_api_key_kraken(api_key, api_secret)

    if exchange == "binance_us":
        validation_return = validate_api_key_binance_us(api_key, api_secret)

    if exchange == "gemini":
        validation_return = validate_api_key_gemini(api_key, api_secret)

    if exchange == "ftx_us":
        validation_return = validate_api_key_ftx_us(api_key, api_secret)

    return validation_return

def validate_api_key_coinbase_pro(api_key, api_secret, api_passphrase):
    logging.critical("validate_api_key_coinbase_pro() was called")
    validation_result = coinbase_pro_functions.coinbase_pro_api_get(api_key, api_secret, api_passphrase, requestpath="/accounts")
    if validation_result.status_code == 200:
        logging.error("validate_api_key_coinbase_pro() returning valid")
        return "valid"
    elif validation_result.status_code == 401:
        logging.error("validate_api_key_coinbase_pro() returning invalid")
        return "invalid"
    else:
        logging.error("validate_api_key_coinbase_pro() returning invalid")
        return "invalid"

def validate_api_key_binance_us(api_key, api_secret):
    logging.critical("validate_api_key_binance_us() was called")
    return_status, validation_response = binance_us_functions.binance_us_account_balances(api_key, api_secret)
    if return_status == "success":
        return "valid"
    elif return_status != "success":
        return "invalid"
    else:
        return "invalid"

def validate_api_key_gemini(api_key, api_secret):
    logging.critical("validate_api_key_gemini() was called")
    return_status, validation_response = gemini_functions.gemini_get_balance(api_key, api_secret)
    if return_status == "success":
        return "valid"
    elif return_status != "success":
        return "invalid"
    else:
        return "invalid"

def validate_api_key_bittrex(api_key, api_secret):
    logging.critical("validate_api_key_bittrex() was called")
    return_status, validation_response = bittrex_functions.bittrex_get_balances(api_key, api_secret)
    if return_status == "success":
        return "valid"
    elif return_status != "success":
        return "invalid"
    else:
        return "invalid"

def validate_api_key_ftx_us(api_key, api_secret):
    logging.critical("validate_api_key_ftx_us() was called")
    return_status, validation_response = ftx_us_functions.ftx_us_get_balances(api_key, api_secret)
    if return_status == "success":
        return "valid"
    elif return_status != "success":
        return "invalid"
    else:
        return "invalid"

def validate_api_key_kraken(api_key, api_secret):
    logging.critical("validate_api_key_kraken() was called")
    return_status, validation_response = kraken_functions.kraken_get_balances(api_key, api_secret)
    if return_status == "success":
        return "valid"
    elif return_status != "success":
        return "invalid"
    else:
        return "invalid"
