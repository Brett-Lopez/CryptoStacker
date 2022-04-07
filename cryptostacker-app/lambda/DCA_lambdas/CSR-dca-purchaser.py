
#standard libraries
import time
import json
import base64
import hmac
import hashlib
import datetime
import gc
import logging
import random

#third party libraries
import boto3
import requests
import bleach

#import custom libraries
import aws_functions_for_lambda
#from crypto_exchange_lib import coinbase_pro_functions #not working atm
import CSR_service_mesh_map
import CSR_toolkit
#exchange libraries
import binance_us_functions
import coinbase_pro_functions
import gemini_functions
import bittrex_functions
import ftx_us_functions
import kraken_functions

#define general functions;
def create_aws_client(aws_service_name_string):
    """
    Create an AWS client object
    """
    logging.error("create AWS client: %s" % aws_service_name_string)
    aws_client_object = boto3.client(aws_service_name_string,
    #region_name=aws_region_name
    )
    return aws_client_object

def iterate_dca_schedule(event_body_dict, exchange_last_run, api_gateway_api_key):
    """
    input: event_body_dict, dictionary created from SQS event, CSR-cron-events-btc lambda creates this message
    input: the exchange name that last ran, output from exchange function or can be mapped to a list of strings "priority_order_reference_list"
    output: no output
    """
    logging.critical("iterate_dca_schedule() called")

    top_of_the_current_minute = CSR_toolkit.top_of_the_current_minute()
    
    if int(event_body_dict["first_run_epoch"]) == 0:
        first_run_epoch = int(top_of_the_current_minute)
    elif int(event_body_dict["first_run_epoch"]) != 0:
        first_run_epoch = event_body_dict["first_run_epoch"]

    #debugging:
    logging.error("top_of_the_current_minute: %s" % top_of_the_current_minute) #debugging
    epoch_sum_temp = int(event_body_dict["interval_time_in_seconds"]) + int(top_of_the_current_minute) #debugging
    logging.error("interval_time_in_seconds: %s" % str(event_body_dict["interval_time_in_seconds"]))
    logging.error("top_of_the_current_minute + %s = %s" % (str(event_body_dict["interval_time_in_seconds"]), str(epoch_sum_temp))) #debugging

    query_string = CSR_service_mesh_map.api_dca_schedule + "?user_id=" + str(event_body_dict["user_id"]) + "&digital_asset=" + str(event_body_dict["digital_asset"]) + "&last_run_epoch=" + str(top_of_the_current_minute) + "&next_run_epoch=" + str(top_of_the_current_minute + int(event_body_dict["interval_time_in_seconds"])) + "&exchange_last_run=" + str(exchange_last_run) + "&first_run_epoch=" + str(first_run_epoch) + "&update=update"
    logging.debug(query_string) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    #api_dca_schedule_response = requests.post(query_string, headers=headers)
    while True:
        api_dca_schedule_response = requests.post(query_string, headers=headers)
        if api_dca_schedule_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)

def iterate_dca_schedule_n_seconds(event_body_dict, exchange_last_run, seconds_input, api_gateway_api_key):
    """
    input: event_body_dict, dictionary created from SQS event, CSR-cron-events-btc lambda creates this message
    input: the exchange name that last ran, output from exchange function or can be mapped to a list of strings "priority_order_reference_list"
    output: no output
    """
    logging.critical("iterate_dca_schedule_n_seconds() called")

    top_of_the_current_minute = CSR_toolkit.top_of_the_current_minute()
    
    if int(event_body_dict["first_run_epoch"]) == 0:
        first_run_epoch = int(top_of_the_current_minute)
    elif int(event_body_dict["first_run_epoch"]) != 0:
        first_run_epoch = event_body_dict["first_run_epoch"]

    #debugging:
    logging.error("top_of_the_current_minute: %s" % top_of_the_current_minute) #debugging
    epoch_sum_temp = int(seconds_input) + int(top_of_the_current_minute) #debugging
    logging.error("interval_time_in_seconds: %s" % str(seconds_input))
    logging.error("top_of_the_current_minute + %s = %s" % (str(seconds_input), str(epoch_sum_temp))) #debugging

    query_string = CSR_service_mesh_map.api_dca_schedule + "?user_id=" + str(event_body_dict["user_id"]) + "&digital_asset=" + str(event_body_dict["digital_asset"]) + "&last_run_epoch=" + str(top_of_the_current_minute) + "&next_run_epoch=" + str(top_of_the_current_minute + int(seconds_input)) + "&exchange_last_run=" + str(exchange_last_run) + "&first_run_epoch=" + str(first_run_epoch) + "&update=update"
    logging.debug(query_string) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    #api_dca_schedule_response = requests.post(query_string, headers=headers)
    while True:
        api_dca_schedule_response = requests.post(query_string, headers=headers)
        if api_dca_schedule_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)

def create_dca_log_event(user_id, was_successful, coin_purchased, fiat_amount, fiat_denomination, exchange_used, interval_time_in_seconds, high_availability_type, exchange_order_id, failure_reason, api_gateway_api_key):
    """
    Input: All information required to insert into the dca_purchase_logs table
    Output: No output at this time
    """
    logging.critical("create_dca_log_event() called")
    current_epoch_time_int = CSR_toolkit.current_time_epoch()
    
    query_string = CSR_service_mesh_map.api_dca_purchase_logs + "?user_id=" + str(user_id) + "&epoch_time=" \
    + str(current_epoch_time_int) + "&was_successful=" + str(was_successful) + "&coin_purchased=" \
    + str(coin_purchased) + "&fiat_amount=" + str(fiat_amount) + "&fiat_denomination=" + str(fiat_denomination) \
    + "&exchange_used=" + str(exchange_used) \
    + "&interval_time_in_seconds=" + str(interval_time_in_seconds) + "&high_availability_type=" + str(high_availability_type) \
    + "&exchange_order_id=" + str(exchange_order_id) + "&failure_reason=" + str(failure_reason)
    logging.error(query_string) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    #api_dca_purchase_logs = requests.post(query_string, headers=headers)
    while True:
        api_dca_purchase_logs = requests.post(query_string, headers=headers)
        if api_dca_purchase_logs.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)

def increment_tier_counts(event_body_dict, api_gateway_api_key):
    logging.critical("increment_tier_counts() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    user_id = event_body_dict["user_id"]
    dollar_amount = event_body_dict["dollar_amount"]

    query_string = CSR_service_mesh_map.api_user_subscription_status + "?user_id=" + str(user_id) + "&scope=user_id"
    #api_response = requests.get(query_string, headers=headers)
    while True:
        api_response = requests.get(query_string, headers=headers)
        if api_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)

    user_subscription_status = api_response.json()
    logging.error(user_subscription_status) #debugging

    number_of_transactions_this_month = int(user_subscription_status[4])
    dollar_amount_of_transactions_this_month = int(user_subscription_status[5])
    total_number_of_transactions = int(user_subscription_status[6])
    total_dollar_amount_of_transactions = int(user_subscription_status[7])
    number_of_transactions_this_month += 1
    dollar_amount_of_transactions_this_month += int(dollar_amount)
    total_number_of_transactions += 1
    total_dollar_amount_of_transactions += int(dollar_amount)
    
    logging.error(number_of_transactions_this_month) #debugging
    logging.error(dollar_amount_of_transactions_this_month) #debugging
    logging.error(total_number_of_transactions) #debugging
    logging.error(total_dollar_amount_of_transactions) #debugging

    logging.error("updating user_subscription_status with new stats")
    query_string = CSR_service_mesh_map.api_user_subscription_status + "?user_id=" + str(user_id) + "&number_of_transactions_this_month=" + str(number_of_transactions_this_month) + "&dollar_amount_of_transactions_this_month=" + str(dollar_amount_of_transactions_this_month) + "&total_number_of_transactions=" + str(total_number_of_transactions) + "&total_dollar_amount_of_transactions=" + str(total_dollar_amount_of_transactions) + "&scope=transaction_stats"
    #api_response = requests.post(query_string, headers=headers)
    while True:
        api_response = requests.post(query_string, headers=headers)
        if api_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)

def check_tier_counts(event_body_dict, api_gateway_api_key):
    logging.critical("check_tier_counts() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    user_id = event_body_dict["user_id"]
    dollar_amount = event_body_dict["dollar_amount"]

    query_string = CSR_service_mesh_map.api_user_subscription_status + "?user_id=" + str(user_id) + "&scope=user_id"
    #api_response = requests.get(query_string, headers=headers)
    while True:
        api_response = requests.get(query_string, headers=headers)
        if api_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)

    user_subscription_status = api_response.json()
    logging.error(user_subscription_status) #debugging

    query_string = CSR_service_mesh_map.api_user_payments + "?user_id=" + str(user_id) + "&scope=single_active"
    #api_response = requests.get(query_string, headers=headers)
    while True:
        api_response = requests.get(query_string, headers=headers)
        if api_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)

    user_payments = api_response.json()
    logging.error(user_payments) #debugging

    query_string = CSR_service_mesh_map.api_subscription_tier + "?scope=allsubscriptions"
    #api_response = requests.get(query_string, headers=headers)
    while True:
        api_response = requests.get(query_string, headers=headers)
        if api_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)

    subscription_tier = api_response.json()
    logging.error(subscription_tier) #debugging

    tier_map = {"1": [], "2": [], "3": []}
    tier_map["1"] = subscription_tier[0][1:]
    tier_map["2"] = subscription_tier[1][1:]
    tier_map["3"] = subscription_tier[2][1:]
    logging.error(tier_map) #debugging

    #####temp debugging#############
    #user_subscription_status[3] = "False"
    #user_payments = []
    #####temp debugging#############

    exceeded_tier_limit = False
    if user_payments: #if user_payments isn't empty
        logging.error("user payments ins't empty") #debugging
        paid_tier = str(user_payments[8])
        tier_limits = tier_map[paid_tier]
        logging.error(tier_limits) #debugging
        if user_subscription_status[4] > tier_limits[0]: #if number of transactions this month is greater than tier limit
            logging.error("number of transactions exceeds tier") #debugging
            exceeded_tier_limit = True
        if user_subscription_status[5] > tier_limits[1]: #if dollar amount of transactions this month is greater than tier limit
            logging.error("dollar amount of transactions exceeds tier") #debugging
            exceeded_tier_limit = True
    elif not user_payments: #if user_payments is empty
        logging.error("user payments is empty") #debugging
        paid_tier = str(user_subscription_status[2])
        tier_limits = tier_map[paid_tier]
        logging.error(tier_limits) #debugging
        if user_subscription_status[3] == "True": #if tier locked = True
            logging.error("tier_locked_by_admin True") #debugging
            if user_subscription_status[4] > tier_limits[0]: #if number of transactions this month is greater than tier limit
                logging.error("number of transactions exceeds tier") #debugging
                exceeded_tier_limit = True
            if user_subscription_status[5] > tier_limits[1]: #if dollar amount of transactions this month is greater than tier limit
                logging.error("dollar amount of transactions exceeds tier") #debugging
                exceeded_tier_limit = True
        elif user_subscription_status[3] == "False": #if tier locked = False
            logging.error("tier_locked_by_admin False") #debugging
            paid_tier = str("1")
            tier_limits = tier_map[paid_tier]
            logging.error(tier_limits) #debugging
            if user_subscription_status[4] > tier_limits[0]: #if number of transactions this month is greater than tier limit
                logging.error("number of transactions exceeds tier") #debugging
                exceeded_tier_limit = True
            if user_subscription_status[5] > tier_limits[1]: #if dollar amount of transactions this month is greater than tier limit
                logging.error("dollar amount of transactions exceeds tier") #debugging
                exceeded_tier_limit = True

    return exceeded_tier_limit
        
def reset_failed_dca_counter(event_body_dict, api_gateway_api_key):
    logging.critical("reset_failed_dca_counter() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    user_id = event_body_dict["user_id"]

    query_string = CSR_service_mesh_map.api_failed_dca_counter + "?user_id=" + str(user_id) + "&scope=reset_counter_by_user_id"
    #api_response = requests.post(query_string, headers=headers)
    while True:
        api_response = requests.post(query_string, headers=headers)
        if api_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)

    api_response_json = api_response.json()
    logging.error(api_response_json) #debugging

def increment_failed_dca_counter(event_body_dict, api_gateway_api_key):
    logging.critical("increment_failed_dca_counter() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    user_id = event_body_dict["user_id"]

    query_string = CSR_service_mesh_map.api_failed_dca_counter + "?user_id=" + str(user_id) + "&scope=increment_counter_by_user_id"
    #api_response = requests.post(query_string, headers=headers)
    while True:
        api_response = requests.post(query_string, headers=headers)
        if api_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    
    api_response_json = api_response.json()
    logging.error(api_response_json) #debugging

def coinbase_pro(event_body_dict, api_gateway_api_key_1, api_gateway_api_key_2):
    logging.critical("coinbase_pro() called")

    user_id = event_body_dict["user_id"]
    fiat_purchase_amount = float(event_body_dict["dollar_amount"])
    currency_pair = event_body_dict["currency_pair"]
    price_quote = event_body_dict["price_quote"]
    
    #check_tier_counts + conditional pass/fail
    logging.error("checking tier limit")
    exceeded_tier_limit = check_tier_counts(event_body_dict, api_gateway_api_key_1)
    if exceeded_tier_limit:
        logging.error("returning: error: tier limit exceeded")
        return "error: tier limit exceeded", "coinbase_pro"

    #set variables
    fiat_balance = 0
    #retrieve encrypted API keys from service and decrypt, then set to variables
    query_string = CSR_service_mesh_map.api_keys_read_write + "?user_id=" + str(user_id) + "&exchange=" + "coinbase_pro"
    logging.debug(query_string) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key_2
    #api_query_return = requests.get(query_string, headers=headers)
    while True:
        api_query_return = requests.get(query_string, headers=headers)
        if api_query_return.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)

    api_query_return_json = api_query_return.json()
    if isinstance(api_query_return_json, str):
        if "incorrect exchange" in api_query_return_json:
            return "error: incorrect exchange in service mesh call", "coinbase_pro"
        logging.error("api_query_return_json is string, eval to empty list") #debugging
        api_query_return_json = eval(api_query_return_json)

    if not api_query_return_json:
        logging.error("api key not set")
        return "error: api key not set", "coinbase_pro"
    api_key = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[1])
    api_secret = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[2])
    api_passphrase = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[3])
    api_key = str(api_key.strip())
    api_secret = str(api_secret.strip())
    api_passphrase = str(api_passphrase.strip())

    #get account balances
    time.sleep(int(event_body_dict["sleep_offset_for_nonce"])) #sleep offset from cron events to protect nonce
    return_status, fiat_balance = coinbase_pro_functions.coinbase_pro_get_fiat_balance("USD", api_key, api_secret, api_passphrase) #coinbase pro balance
    if return_status != "success":
        if "invalid api key" in return_status:
            CSR_toolkit.delete_users_exchange_api_key_write_only(user_id, "coinbase_pro", api_gateway_api_key_1) #remove api key from api keys database
            return return_status, "coinbase_pro"
        time.sleep(1) #static sleep
        return_status, fiat_balance = coinbase_pro_functions.coinbase_pro_get_fiat_balance("USD", api_key, api_secret, api_passphrase) #coinbase pro balance
        if return_status != "success":
            if "invalid api key" in return_status:
                CSR_toolkit.delete_users_exchange_api_key_write_only(user_id, "coinbase_pro", api_gateway_api_key_1) #remove api key from api keys database
                return return_status, "coinbase_pro"
            return return_status, "coinbase_pro"
        
    logging.error("fiat balance: %s" % fiat_balance)

    if fiat_balance < fiat_purchase_amount: #end script if balance is below purchase amount
        logging.error("insufficient balance")

        #delete variables containing secrets and run garage collector
        del api_key
        del api_secret
        del api_passphrase
        gc.collect()
        logging.error("gc.collect() complete")
        return "error: insufficient balance", "coinbase_pro"

    elif fiat_balance >= fiat_purchase_amount: #continue script if balance is equal or above purchase amount 
        logging.error("Fiat balance sufficient, beginning purchase loop.")
        time.sleep(1) #static sleep
        #purchase COIN with retry loop
        return_status, purchase_loop_response = coinbase_pro_functions.coinbase_pro_purchase_loop(api_key, api_secret, api_passphrase, currency_pair, fiat_purchase_amount, 3, 5)

        #delete variables containing secrets and run garage collector
        del api_key
        del api_secret
        del api_passphrase
        gc.collect()
        logging.error("gc.collect() complete")

        if return_status != "success":
            logging.error("purchase unsuccessful, returning error")
            return return_status, "coinbase_pro"

        elif return_status == "success":
            logging.error("purchase successful, returning success")
            if isinstance(purchase_loop_response, dict):
                if "id" in purchase_loop_response:
                    purchase_loop_response["id"]
                    #return "success", "coinbase_pro", purchase_loop_response["id"] #bleach.clean(str(current_user.first_name), strip=True)
                    return "success", "coinbase_pro", bleach.clean(str(purchase_loop_response["id"]), strip=True) #bleach.clean(str(purchase_loop_response["id"]), strip=True)
                else:
                    return "success", "coinbase_pro", "order_id_unknown"
            else:
                return "success", "coinbase_pro", "order_id_unknown"

def binance_us(event_body_dict, api_gateway_api_key_1, api_gateway_api_key_2):
    logging.critical("binance_us() called")

    user_id = event_body_dict["user_id"]
    fiat_purchase_amount = float(event_body_dict["dollar_amount"])
    currency_pair = event_body_dict["digital_asset"].upper() + event_body_dict["fiat_denomination"].upper()
    price_quote = event_body_dict["price_quote"]

    #check_tier_counts + conditional pass/fail
    logging.error("checking tier limit")
    exceeded_tier_limit = check_tier_counts(event_body_dict, api_gateway_api_key_1)
    if exceeded_tier_limit:
        logging.error("returning: error: tier limit exceeded")
        return "error: tier limit exceeded", "binance_us"

    #set variables
    fiat_balance = 0
    #retrieve encrypted API keys from service and decrypt, then set to variables
    query_string = CSR_service_mesh_map.api_keys_read_write + "?user_id=" + str(user_id) + "&exchange=" + "binance_us"
    logging.debug(query_string) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key_2
    #api_query_return = requests.get(query_string, headers=headers)
    while True:
        api_query_return = requests.get(query_string, headers=headers)
        if api_query_return.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)

    api_query_return_json = api_query_return.json()
    if isinstance(api_query_return_json, str):
        if "incorrect exchange" in api_query_return_json:
            return "error: incorrect exchange in service mesh call", "binance_us"
        logging.error("api_query_return_json is string, eval to empty list") #debugging
        api_query_return_json = eval(api_query_return_json)

    if not api_query_return_json:
        logging.error("error: api key not set")
        return "error: api key not set", "binance_us"
    api_key = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[1])
    api_secret = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[2])
    api_key = str(api_key.strip())
    api_secret = str(api_secret.strip())
    
    #get account balances
    time.sleep(int(event_body_dict["sleep_offset_for_nonce"])) #sleep offset from cron events to protect nonce
    return_status, fiat_balance = binance_us_functions.binance_us_account_balance_specific_asset("USD", api_key, api_secret)
    if return_status != "success":
        if "invalid api key" in return_status:
            CSR_toolkit.delete_users_exchange_api_key_write_only(user_id, "binance_us", api_gateway_api_key_1) #remove api key from api keys database
            return return_status, "binance_us"
        time.sleep(1)
        return_status, fiat_balance = binance_us_functions.binance_us_account_balance_specific_asset("USD", api_key, api_secret)
        if return_status != "success":
            if "invalid api key" in return_status:
                CSR_toolkit.delete_users_exchange_api_key_write_only(user_id, "binance_us", api_gateway_api_key_1) #remove api key from api keys database
                return return_status, "binance_us"
            return return_status, "binance_us"

    logging.error("fiat balance: %s" % fiat_balance)

    if fiat_balance < fiat_purchase_amount: #end script if balance is below purchase amount
    #if fiat_balance < fiat_purchase_amount+1: #end script if balance is below purchase amount
        logging.error("insufficient balance")

        #delete variables containing secrets and run garage collector
        del api_key
        del api_secret
        gc.collect()
        logging.error("gc.collect() complete")
        return "error: insufficient balance", "binance_us"

    elif fiat_balance >= fiat_purchase_amount: #continue script if balance is equal or above purchase amount 
    #elif fiat_balance >= fiat_purchase_amount+1: #continue script if balance is equal or above purchase amount 
        logging.error("fiat balance sufficient, beginning purchase loop.")
        time.sleep(1) #static sleep
        return_status, purchase_response = binance_us_functions.binance_us_purchase(currency_pair, fiat_purchase_amount, api_key, api_secret)

        #delete variables containing secrets and run garage collector
        del api_key
        del api_secret
        gc.collect()
        logging.error("gc.collect() complete")

        if return_status != "success":
            logging.error("purchase unsuccessful, returning error")
            return return_status, "binance_us"

        if "orderId" in purchase_response.json():
            logging.error("purchase successful, returning success with order ID")
            return "success", "binance_us", str(purchase_response.json()["orderId"])
        else:
            logging.error("purchase successful, returning success")
            return "success", "binance_us", "order_id_unknown"

def gemini(event_body_dict, api_gateway_api_key_1, api_gateway_api_key_2):
    logging.critical("gemini() called")
    user_id = event_body_dict["user_id"]
    fiat_purchase_amount = float(event_body_dict["dollar_amount"])
    currency_pair = event_body_dict["digital_asset"].lower() + event_body_dict["fiat_denomination"].lower()
    price_quote = event_body_dict["price_quote"]

    #check_tier_counts + conditional pass/fail
    logging.error("checking tier limit")
    exceeded_tier_limit = check_tier_counts(event_body_dict, api_gateway_api_key_1)
    if exceeded_tier_limit:
        logging.error("returning: error: tier limit exceeded")
        return "error: tier limit exceeded", "gemini"

    #set variables
    fiat_balance = 0
    #retrieve encrypted API keys from service and decrypt, then set to variables
    query_string = CSR_service_mesh_map.api_keys_read_write + "?user_id=" + str(user_id) + "&exchange=" + "gemini"
    logging.debug(query_string) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key_2
    #api_query_return = requests.get(query_string, headers=headers)
    while True:
        api_query_return = requests.get(query_string, headers=headers)
        if api_query_return.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    
    api_query_return_json = api_query_return.json()
    if isinstance(api_query_return_json, str):
        if "incorrect exchange" in api_query_return_json:
            return "error: incorrect exchange in service mesh call", "gemini"
        logging.error("api_query_return_json is string, eval to empty list") #debugging
        api_query_return_json = eval(api_query_return_json)

    if not api_query_return_json:
        logging.error("error: api key not set")
        return "error: api key not set", "gemini"
    api_key = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[1])
    api_secret = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[2])
    api_key = str(api_key.strip())
    api_secret = str(api_secret.strip())
    
    #get account balances
    time.sleep(int(event_body_dict["sleep_offset_for_nonce"])) #sleep offset from cron events to protect nonce
    return_status, fiat_balance = gemini_functions.gemini_get_balance_specific_asset("USD", api_key, api_secret)
    if return_status != "success":
        if "invalid api key" in return_status:
            CSR_toolkit.delete_users_exchange_api_key_write_only(user_id, "gemini", api_gateway_api_key_1) #remove api key from api keys database
            return return_status, "gemini"
        time.sleep(3)
        return_status, fiat_balance = gemini_functions.gemini_get_balance_specific_asset("USD", api_key, api_secret)
        if return_status != "success":
            if "invalid api key" in return_status:
                CSR_toolkit.delete_users_exchange_api_key_write_only(user_id, "gemini", api_gateway_api_key_1) #remove api key from api keys database
                return return_status, "gemini"
            return return_status, "gemini"

    logging.error("fiat balance: %s" % fiat_balance)

    if fiat_balance < fiat_purchase_amount: #end script if balance is below purchase amount
        logging.error("insufficient balance")

        #delete variables containing secrets and run garage collector
        del api_key
        del api_secret
        gc.collect()
        logging.error("gc.collect() complete")
        return "error: insufficient balance", "gemini"

    elif fiat_balance >= fiat_purchase_amount: #continue script if balance is equal or above purchase amount 
        logging.error("fiat balance sufficient, beginning purchase")
        print("debugging inputs:" + str(fiat_purchase_amount) + " " + str(currency_pair) + " " + "0.01" + " " + str(price_quote)) #debugging
        time.sleep(1) #static sleep
        return_status, purchase_response = gemini_functions.gemini_diy_market_purchase(api_key, api_secret, fiat_purchase_amount, currency_pair, "0.01", price_quote)

        #delete variables containing secrets and run garage collector
        del api_key
        del api_secret
        gc.collect()
        logging.error("gc.collect() complete")

        if return_status != "success":
            logging.error("purchase unsuccessful, returning error")
            return return_status, "gemini"

        if "order_id" in purchase_response.json():
            logging.error("purchase successful, returning success with order ID")
            return "success", "gemini", str(purchase_response.json()["order_id"])
        else:
            logging.error("purchase successful, returning success")
            return "success", "gemini", "order_id_unknown"

def bittrex(event_body_dict, api_gateway_api_key_1, api_gateway_api_key_2):
    logging.critical("bittrex() called")
    user_id = event_body_dict["user_id"]
    fiat_purchase_amount = float(event_body_dict["dollar_amount"])
    currency_pair = event_body_dict["digital_asset"].upper() + "-" + event_body_dict["fiat_denomination"].upper()
    price_quote = event_body_dict["price_quote"]

    #check_tier_counts + conditional pass/fail
    logging.error("checking tier limit")
    exceeded_tier_limit = check_tier_counts(event_body_dict, api_gateway_api_key_1)
    if exceeded_tier_limit:
        logging.error("returning: error: tier limit exceeded")
        return "error: tier limit exceeded", "bittrex"

    #set variables
    fiat_balance = 0
    #retrieve encrypted API keys from service and decrypt, then set to variables
    query_string = CSR_service_mesh_map.api_keys_read_write + "?user_id=" + str(user_id) + "&exchange=" + "bittrex"
    logging.debug(query_string) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key_2
    #api_query_return = requests.get(query_string, headers=headers)
    while True:
        api_query_return = requests.get(query_string, headers=headers)
        if api_query_return.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    
    api_query_return_json = api_query_return.json()
    if isinstance(api_query_return_json, str):
        if "incorrect exchange" in api_query_return_json:
            return "error: incorrect exchange in service mesh call", "bittrex"
        logging.error("api_query_return_json is string, eval to empty list") #debugging
        api_query_return_json = eval(api_query_return_json)

    if not api_query_return_json:
        logging.error("error: api key not set")
        return "error: api key not set", "bittrex"
    api_key = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[1])
    api_secret = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[2])
    api_key = str(api_key.strip())
    api_secret = str(api_secret.strip())
    
    #get account balances
    time.sleep(int(event_body_dict["sleep_offset_for_nonce"])) #sleep offset from cron events to protect nonce
    return_status, fiat_balance = bittrex_functions.bittrex_get_balance_specific_asset("USD", api_key, api_secret)
    if return_status != "success":
        if "invalid api key" in return_status:
            CSR_toolkit.delete_users_exchange_api_key_write_only(user_id, "bittrex", api_gateway_api_key_1) #remove api key from api keys database
            return return_status, "bittrex"
        time.sleep(1)
        return_status, fiat_balance = bittrex_functions.bittrex_get_balance_specific_asset("USD", api_key, api_secret)
        if return_status != "success":
            if "invalid api key" in return_status:
                CSR_toolkit.delete_users_exchange_api_key_write_only(user_id, "bittrex", api_gateway_api_key_1) #remove api key from api keys database
                return return_status, "bittrex"            
            return return_status, "bittrex"

    logging.error("fiat balance: %s" % fiat_balance)

    if fiat_balance < fiat_purchase_amount: #end script if balance is below purchase amount
        logging.error("insufficient balance")

        #delete variables containing secrets and run garage collector
        del api_key
        del api_secret
        gc.collect()
        logging.error("gc.collect() complete")
        return "error: insufficient balance", "bittrex"

    elif fiat_balance >= fiat_purchase_amount: #continue script if balance is equal or above purchase amount 
        logging.error("fiat balance sufficient, beginning purchase")
        time.sleep(1) #static sleep
        return_status, purchase_response = bittrex_functions.bittrex_market_purchase(api_key, api_secret, currency_pair, fiat_purchase_amount, price_quote)

        #delete variables containing secrets and run garage collector
        del api_key
        del api_secret
        gc.collect()
        logging.error("gc.collect() complete")

        if return_status != "success":
            logging.error("purchase unsuccessful, returning error")
            return return_status, "bittrex"

        if "id" in purchase_response.json():
            logging.error("purchase successful, returning success with order ID")
            return "success", "bittrex", str(purchase_response.json()["id"])
        else:
            logging.error("purchase successful, returning success")
            return "success", "bittrex", "order_id_unknown"

def ftx_us(event_body_dict, api_gateway_api_key_1, api_gateway_api_key_2):
    logging.critical("ftx_us() called")
    user_id = event_body_dict["user_id"]
    fiat_purchase_amount = float(event_body_dict["dollar_amount"])
    currency_pair = event_body_dict["digital_asset"].upper() + "/" + event_body_dict["fiat_denomination"].upper()
    price_quote = event_body_dict["price_quote"]

    #check_tier_counts + conditional pass/fail
    logging.error("checking tier limit")
    exceeded_tier_limit = check_tier_counts(event_body_dict, api_gateway_api_key_1)
    if exceeded_tier_limit:
        logging.error("returning: error: tier limit exceeded")
        return "error: tier limit exceeded", "ftx_us"

    #set variables
    fiat_balance = 0
    #retrieve encrypted API keys from service and decrypt, then set to variables
    query_string = CSR_service_mesh_map.api_keys_read_write + "?user_id=" + str(user_id) + "&exchange=" + "ftx_us"
    logging.debug(query_string) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key_2
    #api_query_return = requests.get(query_string, headers=headers)
    while True:
        api_query_return = requests.get(query_string, headers=headers)
        if api_query_return.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    
    api_query_return_json = api_query_return.json()
    if isinstance(api_query_return_json, str):
        if "incorrect exchange" in api_query_return_json:
            return "error: incorrect exchange in service mesh call", "ftx_us"
        logging.error("api_query_return_json is string, eval to empty list") #debugging
        api_query_return_json = eval(api_query_return_json)

    if not api_query_return_json:
        logging.error("error: api key not set")
        return "error: api key not set", "ftx_us"
    api_key = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[1])
    api_secret = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[2])
    api_key = str(api_key.strip())
    api_secret = str(api_secret.strip())
    
    #get account balances
    time.sleep(int(event_body_dict["sleep_offset_for_nonce"])) #sleep offset from cron events to protect nonce
    return_status, fiat_balance = ftx_us_functions.ftx_us_get_balance_specific_asset("USD", api_key, api_secret)
    if return_status != "success":
        if "invalid api key" in return_status:
            CSR_toolkit.delete_users_exchange_api_key_write_only(user_id, "ftx_us", api_gateway_api_key_1) #remove api key from api keys database
            return return_status, "ftx_us"
        time.sleep(1)        
        return_status, fiat_balance = ftx_us_functions.ftx_us_get_balance_specific_asset("USD", api_key, api_secret)
        if return_status != "success":
            if "invalid api key" in return_status:
                CSR_toolkit.delete_users_exchange_api_key_write_only(user_id, "ftx_us", api_gateway_api_key_1) #remove api key from api keys database
                return return_status, "ftx_us"            
            return return_status, "ftx_us"

    logging.error("fiat balance: %s" % fiat_balance)

    if fiat_balance < fiat_purchase_amount: #end script if balance is below purchase amount
        logging.error("insufficient balance")

        #delete variables containing secrets and run garage collector
        del api_key
        del api_secret
        gc.collect()
        logging.error("gc.collect() complete")
        return "error: insufficient balance", "ftx_us"

    elif fiat_balance >= fiat_purchase_amount: #continue script if balance is equal or above purchase amount 
        logging.error("fiat balance sufficient, beginning purchase")        
        time.sleep(1) #static sleep
        return_status, purchase_response = ftx_us_functions.ftx_us_market_purchase(api_key, api_secret, currency_pair, fiat_purchase_amount, price_quote)

        #delete variables containing secrets and run garage collector
        del api_key
        del api_secret
        gc.collect()
        logging.error("gc.collect() complete")
        
        if return_status != "success":
            logging.error("purchase unsuccessful, returning error")
            return return_status, "ftx_us"

        if "result" in purchase_response.json():
            if "id" in purchase_response.json()["result"]:
                logging.error("purchase successful, returning success with order ID")
                return "success", "ftx_us", str(purchase_response.json()["result"]["id"]) 
        else:
            logging.error("purchase successful, returning success")
            return "success", "ftx_us", "order_id_unknown" 

def kraken(event_body_dict, api_gateway_api_key_1, api_gateway_api_key_2):
    logging.critical("kraken() called")
    user_id = event_body_dict["user_id"]
    fiat_purchase_amount = float(event_body_dict["dollar_amount"])
    currency_pair = kraken_functions.kraken_asset_map_purchases[event_body_dict["digital_asset"].upper()] + kraken_functions.kraken_asset_map_purchases[event_body_dict["fiat_denomination"].upper()]
    price_quote = event_body_dict["price_quote"]

    #check_tier_counts + conditional pass/fail
    logging.error("checking tier limit")
    exceeded_tier_limit = check_tier_counts(event_body_dict, api_gateway_api_key_1)
    if exceeded_tier_limit:
        logging.error("returning: error: tier limit exceeded")
        return "error: tier limit exceeded", "kraken"

    #set variables
    fiat_balance = 0
    #retrieve encrypted API keys from service and decrypt, then set to variables
    query_string = CSR_service_mesh_map.api_keys_read_write + "?user_id=" + str(user_id) + "&exchange=" + "kraken"
    logging.debug(query_string) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key_2
    #api_query_return = requests.get(query_string, headers=headers)
    while True:
        api_query_return = requests.get(query_string, headers=headers)
        if api_query_return.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)

    api_query_return_json = api_query_return.json()
    if isinstance(api_query_return_json, str):
        if "incorrect exchange" in api_query_return_json:
            return "error: incorrect exchange in service mesh call", "kraken"
        logging.error("api_query_return_json is string, eval to empty list") #debugging
        api_query_return_json = eval(api_query_return_json)
    
    if not api_query_return_json:
        logging.error("error: api key not set")
        return "error: api key not set", "kraken"
    api_key = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[1])
    api_secret = aws_functions_for_lambda.decrypt_string_with_kms(api_query_return_json[2])
    api_key = str(api_key.strip())
    api_secret = str(api_secret.strip())
    
    #get account balances
    time.sleep(int(event_body_dict["sleep_offset_for_nonce"])) #sleep offset from cron events to protect nonce
    return_status, fiat_balance = kraken_functions.kraken_get_balance_specific_asset(kraken_functions.kraken_asset_map_balaces[event_body_dict["fiat_denomination"].upper()], api_key, api_secret)
    if return_status != "success":
        if "invalid api key" in return_status:
            CSR_toolkit.delete_users_exchange_api_key_write_only(user_id, "kraken", api_gateway_api_key_1) #remove api key from api keys database
            return return_status, "kraken"
        time.sleep(1)        
        return_status, fiat_balance = kraken_functions.kraken_get_balance_specific_asset(kraken_functions.kraken_asset_map_balaces[event_body_dict["fiat_denomination"].upper()], api_key, api_secret)
        if return_status != "success":
            if "invalid api key" in return_status:
                CSR_toolkit.delete_users_exchange_api_key_write_only(user_id, "kraken", api_gateway_api_key_1) #remove api key from api keys database
                return return_status, "kraken"            
            return return_status, "kraken", "order_id_placeholder" #purchase_response["id?"]

    logging.error("fiat balance: %s" % fiat_balance)

    if fiat_balance < fiat_purchase_amount: #end script if balance is below purchase amount
        logging.error("insufficient balance")

        #delete variables containing secrets and run garage collector
        del api_key
        del api_secret
        gc.collect()
        logging.error("gc.collect() complete")
        return "error: insufficient balance", "kraken"

    elif fiat_balance >= fiat_purchase_amount: #continue script if balance is equal or above purchase amount 
        logging.error("fiat balance sufficient, beginning purchase")
        print("debugging inputs:" + str(fiat_purchase_amount) + " " + str(currency_pair) + " " + "0.01" + " " + str(price_quote)) #debugging
        time.sleep(1) #static sleep
        return_status, purchase_response = kraken_functions.kraken_diy_market_purchase(api_key, api_secret, currency_pair, fiat_purchase_amount, "0.01", price_quote)

        #delete variables containing secrets and run garage collector
        del api_key
        del api_secret
        gc.collect()
        logging.error("gc.collect() complete")

        if return_status != "success":
            logging.error("purchase unsuccessful, returning error")
            return return_status, "kraken"

        if "result" in purchase_response.json():
            if "txid" in purchase_response.json()["result"]:
                logging.error("purchase successful, returning success")
                return "success", "kraken", str(purchase_response.json()["result"]["txid"][0])
        else:
            logging.error("purchase successful, returning success")
            return "success", "kraken", "order_id_unknown"

def crypto_com(event_body_dict):
    #no api keys available to US users
    print("mock crypto_com")
    return "failed", "crypto_com"

def coinbase(event_body_dict):
    #fees too high
    print("mock coinbase")
    return "failed", "coinbase"

def pass_function(user_id, dollar_amount, currency_pair):
    pass

def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s', level=CSR_toolkit.logging_level_var)
    logging.error("LAMBDA BEGINNING")
    datetime_now_object = datetime.datetime.now()
    top_of_the_current_minute_build = datetime_now_object.replace(second=00, microsecond=00)
    top_of_the_current_minute_epoch = top_of_the_current_minute_build.strftime('%s')
    logging.error("top_of_the_current_minute_epoch: %s" % top_of_the_current_minute_epoch)
    logging.error("retrieve service mesh secret for API calls") 
    service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF")) #{'CSR_Service_Mesh_Secret_1': 'test12345'}
    service_mesh_secret_2 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_2-TF")) #{'CSR_Service_Mesh_Secret_1': 'test12345'}

    for record in event["Records"]: # the rest of the code needs to be inside this for loop
        logging.error("event record body:") #debugging
        logging.error(record["body"]) #debugging
        event_body_dict = eval(record["body"])
        
        exchange_priority_dict = {
            "1": event_body_dict["exchange_priority"]["1"],
            "2": event_body_dict["exchange_priority"]["2"],
            "3": event_body_dict["exchange_priority"]["3"],
            "4": event_body_dict["exchange_priority"]["4"],
            "5": event_body_dict["exchange_priority"]["5"],
            "6": event_body_dict["exchange_priority"]["6"]
        }

        logging.error("exchange_priority_dict") #debugging
        logging.error(exchange_priority_dict) #debugging

        map_of_functions = {
            "coinbase": coinbase,
            "coinbase_pro": coinbase_pro,
            "bittrex": bittrex,
            "kraken": kraken,
            "gemini": gemini,
            "binance_us": binance_us,
            "ftx_us": ftx_us,
            "crypto_com": crypto_com,
            "not_set": pass_function
        }

        function_order_of_priority_dict = {
        #    "1": coinbase,
        #    "2": bittrex,
        #    "3": kraken,
        #    "4": gemini,
        #    "5": binance_us,
        #    "6": crypto_com,
        #    "7": coinbase_pro
        }
        
        #create list of functions - round_robin, failover, simultaneous
        function_order_of_priority_list = []
        priority_order_reference_list = []
        logging.error("--------------------------------")
        logging.error("create list of functions - round_robin, failover, simultaneous")
        logging.error("begin loop: item in exchange_priority_dict")
        for item in exchange_priority_dict:
            logging.error(item)
            logging.error(exchange_priority_dict[item])
            if exchange_priority_dict[item] == "not_set":
                break
            function_order_of_priority_dict[item] = map_of_functions[exchange_priority_dict[item]]
            priority_order_reference_list.append(exchange_priority_dict[item]) #list of exchange names (strings) in order
            function_order_of_priority_list.append(map_of_functions[exchange_priority_dict[item]]) #list of functions

        purchase_success_counter = 0
        purchase_failed_insufficient_balance_counter = 0
        purchase_failed_invalid_or_missing_api_key_counter = 0
        purchase_tier_limit_exceeded_counter = 0
        exchange_unavailable_counter = 0
        unknown_error_counter = 0
        
        #HA type - failover
        if event_body_dict["high_availability_type"] == "failover":
            logging.error("begin loop in event_body_dict[high_availability_type] == failover")
            for function in function_order_of_priority_list:
                #function_result, exchange_returned = function(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], service_mesh_secret_2["CSR_Service_Mesh_Secret_2"])
                response_tuple = function(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], service_mesh_secret_2["CSR_Service_Mesh_Secret_2"])
                function_result = response_tuple[0]
                exchange_returned = response_tuple[1]
                if function_result == "success":
                    purchase_success_counter += 1
                    if len(response_tuple) >= 3:
                        exchange_order_id = response_tuple[2]
                    else:
                        exchange_order_id = "order_id_unknown"
                    logging.error("exchange_order_id")
                    logging.error(exchange_order_id)
                    iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "True", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], str(exchange_order_id), "n/a", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    increment_tier_counts(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    reset_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    break
                elif function_result == "error: insufficient balance":
                    purchase_failed_insufficient_balance_counter += 1
                    iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Insufficient Balance", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                elif function_result == "error: tier limit exceeded":
                    purchase_tier_limit_exceeded_counter += 1
                    iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Monthly transaction limit exceeded for your tier, please upgrade.", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                elif "exchange unavailable" in function_result.lower():
                    exchange_unavailable_counter += 1
                    iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Exchange Unavailable", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                elif "nonce" in function_result.lower():
                    iterate_dca_schedule_n_seconds(event_body_dict, str(exchange_returned), 300, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Nonce error, event will retry shortly", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    purchase_failed_insufficient_balance_counter += 1
                elif "api key" in function_result.lower():
                    purchase_failed_invalid_or_missing_api_key_counter += 1
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "API Key Invalid", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                else:
                    unknown_error_counter += 1
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Unknown Error", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])

        #HA type - single_exchange
        if event_body_dict["high_availability_type"] == "single_exchange":
            logging.error("begin loop in event_body_dict[high_availability_type] == single_exchange")
            for function in function_order_of_priority_list:
                #function_result, exchange_returned = function(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], service_mesh_secret_2["CSR_Service_Mesh_Secret_2"])
                response_tuple = function(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], service_mesh_secret_2["CSR_Service_Mesh_Secret_2"])
                function_result = response_tuple[0]
                exchange_returned = response_tuple[1]
                if function_result == "success":
                    purchase_success_counter += 1
                    if len(response_tuple) >= 3:
                        exchange_order_id = response_tuple[2]
                    else:
                        exchange_order_id = "order_id_unknown"
                    logging.error("exchange_order_id")
                    logging.error(exchange_order_id)
                    iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "True", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], str(exchange_order_id), "n/a", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    increment_tier_counts(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    reset_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    break
                elif function_result == "error: insufficient balance":
                    purchase_failed_insufficient_balance_counter += 1
                    iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Insufficient Balance", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    break
                elif function_result == "error: tier limit exceeded":
                    purchase_tier_limit_exceeded_counter += 1
                    iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Monthly transaction limit exceeded for your tier, please upgrade.", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    break
                elif "exchange unavailable" in function_result.lower():
                    exchange_unavailable_counter += 1
                    iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Exchange Unavailable", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    break
                elif "nonce" in function_result.lower():
                    iterate_dca_schedule_n_seconds(event_body_dict, str(exchange_returned), 300, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Nonce error, event will retry shortly", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    purchase_failed_insufficient_balance_counter += 1
                    break
                elif "api key" in function_result.lower():
                    purchase_failed_invalid_or_missing_api_key_counter += 1
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "API Key Invalid", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    break
                else:
                    unknown_error_counter += 1
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Unknown Error", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    break

        #HA type - simultaneous
        if event_body_dict["high_availability_type"] == "simultaneous":
            logging.error("begin loop in event_body_dict[high_availability_type] == simultaneous")
            for function in function_order_of_priority_list:
                #function_result, exchange_returned = function(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], service_mesh_secret_2["CSR_Service_Mesh_Secret_2"])
                response_tuple = function(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], service_mesh_secret_2["CSR_Service_Mesh_Secret_2"])
                function_result = response_tuple[0]
                exchange_returned = response_tuple[1]
                if function_result == "success":
                    purchase_success_counter += 1
                    if len(response_tuple) >= 3:
                        exchange_order_id = response_tuple[2]
                    else:
                        exchange_order_id = "order_id_unknown"
                    logging.error("exchange_order_id")
                    logging.error(exchange_order_id)
                    iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "True", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], str(exchange_order_id), "n/a", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    increment_tier_counts(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    reset_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                elif function_result == "error: insufficient balance":
                    purchase_failed_insufficient_balance_counter += 1
                    iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Insufficient Balance", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                elif function_result == "error: tier limit exceeded":
                    purchase_tier_limit_exceeded_counter += 1
                    iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Monthly transaction limit exceeded for your tier, please upgrade.", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                elif "exchange unavailable" in function_result.lower():
                    exchange_unavailable_counter += 1
                    iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Exchange Unavailable", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                elif "nonce" in function_result.lower():
                    iterate_dca_schedule_n_seconds(event_body_dict, str(exchange_returned), 300, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "nonce error, event will retry shortly", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    purchase_failed_insufficient_balance_counter += 1
                elif "api key" in function_result.lower():
                    purchase_failed_invalid_or_missing_api_key_counter += 1
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "API Key invalid", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                else:
                    unknown_error_counter += 1
                    create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Unknown Error", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])

        #HA type - round_robin
        if event_body_dict["high_availability_type"] == "round_robin":
            if event_body_dict["exchange_last_run"] != priority_order_reference_list[-1] and event_body_dict["exchange_last_run"].lower() != "none" and len(function_order_of_priority_list) > 1:
                logging.error("begin loop 1 in event_body_dict[high_availability_type] == round_robin")
                index_location = priority_order_reference_list.index(str(event_body_dict["exchange_last_run"]))
                function_order_of_priority_list_reordered = function_order_of_priority_list[index_location+1:]
                for function in function_order_of_priority_list[:index_location+1]:
                    function_order_of_priority_list_reordered.append(function)

                for function in function_order_of_priority_list_reordered:
                    #function_result, exchange_returned = function(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], service_mesh_secret_2["CSR_Service_Mesh_Secret_2"])
                    response_tuple = function(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], service_mesh_secret_2["CSR_Service_Mesh_Secret_2"])
                    function_result = response_tuple[0]
                    exchange_returned = response_tuple[1]
                    if function_result == "success":
                        purchase_success_counter += 1
                        if len(response_tuple) >= 3:
                            exchange_order_id = response_tuple[2]
                        else:
                            exchange_order_id = "order_id_unknown"
                        logging.error("exchange_order_id")
                        logging.error(exchange_order_id)
                        iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        create_dca_log_event(str(event_body_dict["user_id"]), "True", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], str(exchange_order_id), "n/a", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        increment_tier_counts(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        reset_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        break
                    elif function_result == "error: insufficient balance":
                        purchase_failed_insufficient_balance_counter += 1
                        iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Insufficient Balance", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    elif function_result == "error: tier limit exceeded":
                        purchase_tier_limit_exceeded_counter += 1
                        iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Monthly transaction limit exceeded for your tier, please upgrade.", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    elif "exchange unavailable" in function_result.lower():
                        exchange_unavailable_counter += 1
                        iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Exchange Unavailable", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    elif "nonce" in function_result.lower():
                        iterate_dca_schedule_n_seconds(event_body_dict, str(exchange_returned), 300, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "nonce error, event will retry shortly", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        purchase_failed_insufficient_balance_counter += 1
                    elif "api key" in function_result.lower():
                        purchase_failed_invalid_or_missing_api_key_counter += 1
                        create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "API Key invalid", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    else:
                        unknown_error_counter += 1
                        create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Unknown Error", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            else:
                logging.error("begin loop 2 in event_body_dict[high_availability_type] == round_robin")
                for function in function_order_of_priority_list:
                    #function_result, exchange_returned = function(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], service_mesh_secret_2["CSR_Service_Mesh_Secret_2"])
                    response_tuple = function(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], service_mesh_secret_2["CSR_Service_Mesh_Secret_2"])
                    function_result = response_tuple[0]
                    exchange_returned = response_tuple[1]
                    if function_result == "success":
                        purchase_success_counter += 1
                        if len(response_tuple) >= 3:
                            exchange_order_id = response_tuple[2]
                        else:
                            exchange_order_id = "order_id_unknown"
                        logging.error("exchange_order_id")
                        logging.error(exchange_order_id)
                        iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        create_dca_log_event(str(event_body_dict["user_id"]), "True", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], str(exchange_order_id), "n/a", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        increment_tier_counts(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        reset_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        break
                    elif function_result == "error: insufficient balance":
                        purchase_failed_insufficient_balance_counter += 1
                        iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Insufficient Balance", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    elif function_result == "error: tier limit exceeded":
                        purchase_tier_limit_exceeded_counter += 1
                        iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Monthly transaction limit exceeded for your tier, please upgrade.", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    elif "exchange unavailable" in function_result.lower():
                        exchange_unavailable_counter += 1
                        iterate_dca_schedule(event_body_dict, str(exchange_returned), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Exchange Unavailable", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    elif "nonce" in function_result.lower():
                        iterate_dca_schedule_n_seconds(event_body_dict, str(exchange_returned), 300, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "nonce error, event will retry shortly", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        purchase_failed_insufficient_balance_counter += 1
                    elif "api key" in function_result.lower():
                        purchase_failed_invalid_or_missing_api_key_counter += 1
                        create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "API Key invalid", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    else:
                        unknown_error_counter += 1
                        create_dca_log_event(str(event_body_dict["user_id"]), "False", event_body_dict["digital_asset"].lower(), str(event_body_dict["dollar_amount"]), event_body_dict["fiat_denomination"], exchange_returned, str(event_body_dict["interval_time_in_seconds"]), event_body_dict["high_availability_type"], "n/a", "Unknown Error", service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                        increment_failed_dca_counter(event_body_dict, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])

        if purchase_success_counter == 0 and purchase_failed_insufficient_balance_counter == 0 and purchase_tier_limit_exceeded_counter == 0 and exchange_unavailable_counter == 0 and purchase_failed_invalid_or_missing_api_key_counter > 0:
            logging.error("all failures were due to API keys being invalid or null, deleting current DCA schedule")
            CSR_toolkit.delete_dca_schedule(str(event_body_dict["user_id"]), str(event_body_dict["digital_asset"]).lower(), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])

    logging.error("lambda_handler ends")