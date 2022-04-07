#standard lib:
import datetime
import logging
import threading
import calendar
import urllib.parse

#third party:
import requests
import pytz
from dateutil.relativedelta import *

#interal:
import CSR_service_mesh_map


logging_level_var = logging.INFO

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging_level_var)

supported_exchanges_list = ['coinbase_pro', 'bittrex', 'kraken', 'binance_us', 'gemini', 'ftx_us', 'not_set']
supported_exchanges_list_without_notset = ['coinbase_pro', 'bittrex', 'kraken', 'binance_us', 'gemini', 'ftx_us']
supported_exchanges_list_without_notset_with_all = ["all", 'coinbase_pro', 'bittrex', 'kraken', 'binance_us', 'gemini', 'ftx_us']

map_of_exchange_names_computer_to_human = {'coinbase_pro': "Coinbase Pro", 'bittrex': "Bittrex", 'kraken': "Kraken", 'binance_us': "Binance US", 'gemini': "Gemini", 'ftx_us': "FTX US", 'not_set': "Not set"}

timezones_from_computer_to_human_friendly_map = {"America/Los_Angeles": "Pacific", "America/Denver": "Mountain", "America/Chicago": "Central", "America/New_York": "Eastern", "America/Anchorage": "Alaska", "US/Hawaii": "Hawaii", "US/Arizona": "Arizona"}
timezones_from_lower_case_human_friendly_to_computer_map = {"pacific": "America/Los_Angeles", "mountain": "America/Denver", "central": "America/Chicago", "eastern": "America/New_York", "alaska": "America/Anchorage", "hawaii": "US/Hawaii", "arizona": "US/Arizona"}

supported_high_availability_type_list = ["failover", "round_robin", "simultaneous", "single_exchange"]
supported_high_availability_type_human_friendly_map = {"failover": "Failover", "round_robin": "Round Robin", "simultaneous":"Simultaneous", "single_exchange": "Single Exchange"}

supported_coins_list = ["btc", "ltc", "eth"]

persona_verification_status_map = {"unknown": 0, "not_yet_submitted_for_verification": 1, "pending_verification": 2, "verified": 3, "verification_failed": 9}

lambda_throttle_sleep_time = 5

class StandInStatusCodes():
    #used for status code error handling when a requests method fails due to server timeout, unreachable, etc
    def __init__(self, status_code):
        self.status_code = status_code

def top_of_the_current_minute() -> int:
    """
    output: top of the current minute in epoch - type: int
    """
    logging.critical("top_of_the_current_minute() called") #debugging
    datetime_now_object = datetime.datetime.now()
    top_of_the_current_minute_build = datetime_now_object.replace(second=00, microsecond=00)
    top_of_the_current_minute_epoch = top_of_the_current_minute_build.strftime('%s')
    logging.error("top_of_the_current_minute_epoch:") #debugging
    logging.error(top_of_the_current_minute_epoch) #debugging
    return int(top_of_the_current_minute_epoch)

def current_time_epoch() -> int:
    """
    output: current time in epoch - type: int
    """
    logging.critical("current_time_epoch() called") #debugging
    datetime_now_object = datetime.datetime.now()
    datetime_now_epoch = datetime_now_object.strftime('%s')
    logging.error("datetime_now_epoch:") #debugging
    logging.error(datetime_now_epoch) #debugging
    return int(datetime_now_epoch)

def datetime_plus_days(date_time_object, number_of_days):
    """
    Intended use, rolling n day windows that don't require natural months
    input: dateteime object & number of days (int)
    output: future dateteime object - true days not natural
    """
    new_datetime_object = date_time_object + datetime.timedelta(days=number_of_days)
    return new_datetime_object

def epoch_plus_months_epoch(initial_epoch_time, number_of_months) -> int:
    """
    input: epoch & number of months
    output: future epoch - natural months / time
    """
    logging.critical("epoch_plus_months_epoch() called") #debugging
    initial_time_datetime_object = datetime.datetime.fromtimestamp(int(initial_epoch_time))
    future_datetime_object = initial_time_datetime_object + relativedelta(months=+int(number_of_months))
    future_epoch = future_datetime_object.strftime('%s')
    #logging.error(future_datetime_object) #debugging
    #logging.error(future_epoch) #debugging
    return future_epoch

def epoch_plus_hours_epoch(initial_epoch_time, number_of_hours) -> int:
    """
    input: epoch & number of hours
    output: future epoch - natural months / time
    """
    logging.critical("epoch_plus_hours_epoch() called") #debugging
    initial_time_datetime_object = datetime.datetime.fromtimestamp(int(initial_epoch_time))
    future_datetime_object = initial_time_datetime_object + relativedelta(hours=+int(number_of_hours))
    future_epoch = future_datetime_object.strftime('%s')
    #logging.error(future_datetime_object) #debugging
    #logging.error(future_epoch) #debugging
    return future_epoch

def epoch_to_datetime_object(epoch_time) -> datetime:
    logging.critical("epoch_to_datetime_object() called") #debugging
    datetime_object = datetime.datetime.fromtimestamp(int(epoch_time))
    return datetime_object

def datetime_plus_months(initial_time_datetime_object, number_of_months) -> int:
    """
    input: datetime object & number of months
    output: new datetime object - natural months / time
    """
    logging.critical("datetime_plus_months() called") #debugging
    future_datetime_object = initial_time_datetime_object + relativedelta(months=+int(number_of_months))
    #logging.error(future_datetime_object) #debugging
    return future_datetime_object

def get_quarter(date_time_object):
    logging.error("get_quarter() called")
    return int((date_time_object.month - 1) / 3 + 1)

def get_first_day_of_the_quarter(date_time_object):
    logging.critical("get_first_day_of_the_quarter() called")
    quarter = get_quarter(date_time_object)
    return datetime.datetime(date_time_object.year, 3 * quarter - 2, 1)

def get_last_day_of_the_quarter(date_time_object):
    logging.critical("get_last_day_of_the_quarter() called")
    quarter = get_quarter(date_time_object)
    last_day_of_quarter = datetime.datetime(date_time_object.year + 3 * quarter // 12, 3 * quarter % 12 + 1, 1) + datetime.timedelta(days=-1)
    last_day_of_quarter = last_day_of_quarter.replace(hour=23, minute=59, second=59)
    return last_day_of_quarter

def get_first_and_last_day_of_the_last_quarter():
    logging.critical("get_first_and_last_day_of_the_last_quarter() called")
    date_time_object_now = datetime.datetime.now()
    first_day_of_the_quarter = get_first_day_of_the_quarter(date_time_object_now)
    last_quarter = first_day_of_the_quarter + datetime.timedelta(days=-1)
    first_day_of_the_last_quarter = get_first_day_of_the_quarter(last_quarter)
    last_day_of_the_last_quarter = get_last_day_of_the_quarter(last_quarter)
    return first_day_of_the_last_quarter, last_day_of_the_last_quarter

def get_first_and_last_day_of_the_month():
    logging.critical("get_first_and_last_day_of_the_month() called")
    date_time_object_now = datetime.datetime.now()
    current_year = int(date_time_object_now.strftime("%Y"))
    current_month = int(date_time_object_now.strftime("%m"))
    first_and_last_tuple = calendar.monthrange(current_year, current_month)
    first_day_of_the_month = date_time_object_now.replace(day=first_and_last_tuple[0], hour=00, minute=00, second=00, microsecond=00)
    last_day_of_the_month = date_time_object_now.replace(day=first_and_last_tuple[1], hour=23, minute=59, second=59, microsecond=00)
    return first_day_of_the_month, last_day_of_the_month

def get_first_and_last_day_of_the_last_month():
    logging.critical("get_first_and_last_day_of_the_last_month() called")
    date_time_object_now = datetime.datetime.now()
    last_day_of_last_month = date_time_object_now.replace(day=1, hour=12) - datetime.timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)
    first_day_of_last_month = first_day_of_last_month.replace(hour=00, minute=00, second=00, microsecond=00)
    last_day_of_last_month = last_day_of_last_month.replace(hour=23, minute=59, second=59, microsecond=00)
    return first_day_of_last_month, last_day_of_last_month

def get_first_and_last_day_of_the_year():
    logging.critical("get_first_and_last_day_of_the_year() called")
    date_time_object_now = datetime.datetime.now()
    current_year = int(date_time_object_now.strftime("%Y"))
    first_and_last_month_12_tuple = calendar.monthrange(current_year, 12)
    first_day_of_the_month = date_time_object_now.replace(month=1, day=1, hour=00, minute=00, second=00, microsecond=00)
    last_day_of_the_month = date_time_object_now.replace(month=12, day=first_and_last_month_12_tuple[1], hour=23, minute=59, second=59, microsecond=00)
    return first_day_of_the_month, last_day_of_the_month

def get_first_and_last_day_of_the_last_year():
    logging.critical("get_first_and_last_day_of_the_last_year() called")
    date_time_object_now = datetime.datetime.now()
    current_year = int(date_time_object_now.strftime("%Y"))
    last_year = current_year - 1
    first_and_last_month_12_tuple = calendar.monthrange(last_year, 12)
    first_day_of_the_month = date_time_object_now.replace(year=last_year, month=1, day=1, hour=00, minute=00, second=00, microsecond=00)
    last_day_of_the_month = date_time_object_now.replace(year=last_year, month=12, day=first_and_last_month_12_tuple[1], hour=23, minute=59, second=59, microsecond=00)
    return first_day_of_the_month, last_day_of_the_month






def delete_users_exchange_api_key_write_only(user_id, exchange, api_gateway_api_key):
    logging.critical("delete_users_exchange_api_key_write_only() called")
    #todo switch query string from read_write endpoint to write_only endpoint
    #query_string_delete = "https://rnywj5tnv4.execute-api.us-east-2.amazonaws.com/prod/api-keys-read-write?user_id=5&exchange=coinbase_pro&delete=delete"
    query_string_delete = CSR_service_mesh_map.api_keys_write + "?user_id=" + str(user_id) + "&exchange=" + exchange + "&delete=delete"
    logging.error(query_string_delete) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    api_query_delete_return = requests.post(query_string_delete, headers=headers)
    logging.error(api_query_delete_return.json())


def delete_dca_schedule(user_id, digital_asset, api_gateway_api_key):
    logging.critical("delete_dca_schedule() called")
    #query_string_delete = "https://rnywj5tnv4.execute-api.us-east-2.amazonaws.com/prod/dca-schedule?user_id=50&digital_asset=btc&delete=delete"
    query_string_delete = CSR_service_mesh_map.api_dca_schedule + "?user_id=" + str(user_id) + "&digital_asset=" + digital_asset + "&delete=delete"
    logging.error(query_string_delete) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    api_query_delete_return = requests.post(query_string_delete, headers=headers)
    logging.error(api_query_delete_return.json())


def get_api_keys_metadata(user_id, exchange, api_gateway_api_key):
    logging.critical("get_api_keys_metadata() called")
    meta_data_api_query = CSR_service_mesh_map.api_keys_metadata + "?user_id=" + str(user_id) + "&exchange=" + str(exchange)
    logging.error(meta_data_api_query) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    meta_data_api_query_response = requests.get(meta_data_api_query, headers=headers)
    logging.error(meta_data_api_query_response.json()) #debugging
    if meta_data_api_query_response.status_code == 200:
        return meta_data_api_query_response.json()

def set_api_keys_metadata(user_id, exchange, keys_expiration_epoch, api_gateway_api_key):
    logging.critical("set_api_keys_metadata() called")
    meta_data_api_query = CSR_service_mesh_map.api_keys_metadata + "?user_id=" + str(user_id) + "&exchange=" + str(exchange) + "&keys_expiration_epoch=" + str(keys_expiration_epoch)
    logging.error(meta_data_api_query) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    meta_data_api_query_response = requests.post(meta_data_api_query, headers=headers)
    logging.error(meta_data_api_query_response.json()) #debugging
    if meta_data_api_query_response.status_code == 200:
        return meta_data_api_query_response.json()

def delete_api_keys_metadata(user_id, exchange, api_gateway_api_key):
    logging.critical("delete_api_keys_metadata() called")
    meta_data_api_query = CSR_service_mesh_map.api_keys_metadata + "?user_id=" + str(user_id) + "&exchange=" + str(exchange) + "&delete=delete"
    logging.error(meta_data_api_query) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    meta_data_api_query_response = requests.post(meta_data_api_query, headers=headers)
    logging.error(meta_data_api_query_response.json()) #debugging
    if meta_data_api_query_response.status_code == 200:
        return meta_data_api_query_response.json()

def build_list_of_all_brand_ambassador_referral_codes(api_gateway_api_key):
    logging.critical("build_list_of_all_brand_ambassador_referral_codes() called")
    list_of_referral_codes_strings = []
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    after_id = 0
    while True:
        query_string = CSR_service_mesh_map.api_brand_ambassador_referral_codes + "?after_id=" + str(after_id) + "&limit=200&scope=paginated"
        referral_codes_response = requests.get(query_string, headers=headers)
        referral_codes_response_json = referral_codes_response.json()
        print(referral_codes_response_json)
        if isinstance(referral_codes_response_json, str):
            logging.error("is string") #debugging
            referral_codes_response_json = eval(referral_codes_response_json)
            logging.error(referral_codes_response_json) #debugging
            logging.error(type(referral_codes_response_json)) #debugging
            logging.error(len(referral_codes_response_json)) #debugging

        if len(referral_codes_response_json) < 200:
            for referral_codes_row in referral_codes_response_json:
                print(referral_codes_row)
                list_of_referral_codes_strings.append(referral_codes_row[1])
            return list_of_referral_codes_strings    
        else:
            for referral_codes_row in referral_codes_response_json:
                list_of_referral_codes_strings.append(referral_codes_row[1])
            after_id = referral_codes_response_json[-1][0]

def build_api_key_metadata_list(user_id, exchange, timezone, api_gateway_api_key):
    logging.critical("build_api_key_metadata_list() called") #debugging
    meta_api_response = get_api_keys_metadata(user_id, exchange, api_gateway_api_key)
    if isinstance(meta_api_response, str):
        logging.error("is string") #debugging
        meta_api_response = eval(meta_api_response)
        logging.error(meta_api_response) #debugging
        logging.error(type(meta_api_response)) #debugging
        logging.error(len(meta_api_response)) #debugging

    if meta_api_response:
        logging.error("list not empty") #debugging
        meta_data_to_return_to_user = []           
        
        utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(meta_api_response[1])))
        timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(timezone))
        human_readable_time = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
        #human_readable_time = datetime.datetime.fromtimestamp(int(meta_api_response[1])).strftime('%Y-%m-%d %H:%M:%S')
        meta_data_to_return_to_user.append("API Key set at: %s" % str(human_readable_time))

        if int(meta_api_response[2]) == 0:
            meta_data_to_return_to_user.append("API Key never expires")
        elif int(meta_api_response[2]) != 0:
            utc_datetime_from_epoch = pytz.utc.localize(datetime.datetime.fromtimestamp(int(meta_api_response[2])))
            timezone_adjusted_now = utc_datetime_from_epoch.astimezone(pytz.timezone(timezone))
            human_readable_time = timezone_adjusted_now.strftime('%Y-%m-%d %H:%M:%S')
            #human_readable_time = datetime.datetime.fromtimestamp(int(meta_api_response[2])).strftime('%Y-%m-%d %H:%M:%S')
            meta_data_to_return_to_user.append("API Key expires at: %s" % str(human_readable_time))
        
        return meta_data_to_return_to_user

    elif not meta_api_response:
        logging.error("list empty - elif") #debugging
        meta_data_to_return_to_user = None
        return meta_data_to_return_to_user
    else:
        logging.error("list empty - else") #debugging
        meta_data_to_return_to_user = None
        return meta_data_to_return_to_user

def get_list_of_users_from_email_address(email_address, api_gateway_api_key):
    logging.critical("get_list_of_users_from_email_address() called")
    email_address = urllib.parse.quote_plus(email_address)
    query_string = CSR_service_mesh_map.users_api + "?email_address=" + str(email_address)
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    users_response_object = requests.get(query_string, headers=headers)
    if users_response_object.status_code == 200:
        logging.error("status code 200") #debugging
        users_response_object_json = users_response_object.json()
        
        if isinstance(users_response_object_json, list):
            return users_response_object_json
        
        elif isinstance(users_response_object_json, str):
            logging.error("is string") #debugging
            users_response_object_json = eval(users_response_object.json())
            logging.error(users_response_object_json) #debugging
            logging.error(type(users_response_object_json)) #debugging
            logging.error(len(users_response_object_json)) #debugging
            return users_response_object_json

    else:
        logging.error("status code not 200") #debugging
        return users_response_object.json()

def get_list_of_users_from_user_id(user_id, api_gateway_api_key):
    logging.critical("get_list_of_users_from_user_id() called")
    query_string = CSR_service_mesh_map.users_api + "?user_id=" + str(user_id)
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    users_response_object = requests.get(query_string, headers=headers)
    if users_response_object.status_code == 200:
        logging.error("status code 200") #debugging
        users_response_object_json = users_response_object.json()
        
        if isinstance(users_response_object_json, list):
            logging.error("is list") #debugging
            return users_response_object_json
        
        elif isinstance(users_response_object_json, str):
            logging.error("is string") #debugging
            users_response_object_json = eval(users_response_object.json())
            logging.error(users_response_object_json) #debugging
            logging.error(type(users_response_object_json)) #debugging
            logging.error(len(users_response_object_json)) #debugging
            return users_response_object_json

    else:
        logging.error("status code not 200") #debugging
        return users_response_object.json()

def create_csr_price_map(api_gateway_api_key):
    logging.critical("create_csr_price_map() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_pricing_tier + "?scope=allprices"
    users_response_object = requests.get(query_string, headers=headers)
    users_response_object_json = users_response_object.json()
    logging.error(users_response_object_json) #debugging
    csr_pricing_map = {}
    csr_pricing_map["2"] = {}
    csr_pricing_map["3"] = {}
    csr_pricing_map["2"]["1"] = str(users_response_object_json[0][2])
    csr_pricing_map["2"]["3"] = str(users_response_object_json[1][2])
    csr_pricing_map["2"]["6"] = str(users_response_object_json[2][2])
    csr_pricing_map["2"]["12"] = str(users_response_object_json[3][2])
    csr_pricing_map["2"]["1200"] = str(users_response_object_json[4][2])
    csr_pricing_map["3"]["1"] = str(users_response_object_json[5][2])
    csr_pricing_map["3"]["3"] = str(users_response_object_json[6][2])
    csr_pricing_map["3"]["6"] = str(users_response_object_json[7][2])
    csr_pricing_map["3"]["12"] = str(users_response_object_json[8][2])
    csr_pricing_map["3"]["1200"] = str(users_response_object_json[9][2])
    return csr_pricing_map

def get_subscription_tiers(api_gateway_api_key):
    logging.critical("get_subscription_tiers() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_subscription_tier + "?scope=allsubscriptions"
    api_response = requests.get(query_string, headers=headers)
    logging.error(api_response.json()) #debugging - should be; [[1, 10, 100], [2, 1000, 10000], [3, 500000000, 500000000]]
    return api_response.json()

def create_csr_tier_limits_map(api_gateway_api_key):
    logging.critical("create_csr_tier_limits_map() called")
    subscription_tiers = get_subscription_tiers(api_gateway_api_key)
    csr_tier_limits_map = {}
    csr_tier_limits_map["tier1"] = {}
    csr_tier_limits_map["tier2"] = {}
    csr_tier_limits_map["tier3"] = {}
    csr_tier_limits_map["tier1"]["transaction_limit"] = subscription_tiers[0][1]
    csr_tier_limits_map["tier1"]["dollar_limit"] = subscription_tiers[0][2]
    csr_tier_limits_map["tier2"]["transaction_limit"] = subscription_tiers[1][1]
    csr_tier_limits_map["tier2"]["transaction_limit"] = "{:,}".format(int(csr_tier_limits_map["tier2"]["transaction_limit"]))
    csr_tier_limits_map["tier2"]["dollar_limit"] = subscription_tiers[1][2]
    csr_tier_limits_map["tier2"]["dollar_limit"] = "{:,}".format(int(csr_tier_limits_map["tier2"]["dollar_limit"]))
    csr_tier_limits_map["tier3"]["transaction_limit"] = subscription_tiers[2][1]
    csr_tier_limits_map["tier3"]["dollar_limit"] = subscription_tiers[2][2]
    logging.error(csr_tier_limits_map) #debugging
    return csr_tier_limits_map

def create_csr_price_and_per_month_map_dict(api_gateway_api_key):
    logging.critical("create_csr_price_and_per_month_map_dict() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_pricing_tier + "?scope=allprices"
    users_response_object = requests.get(query_string, headers=headers)
    users_response_object_json = users_response_object.json()
    logging.error(users_response_object_json) #debugging
    csr_price_and_per_month_map_dict = {} #example: {'tier2': {'1months': {'total_price': 10, 'price_per_month': 10}, '3months': {'total_price': 24, 'price_per_month': 8}, '6months': {'total_price': 42, 'price_per_month': 7}, '12months': {'total_price': 72, 'price_per_month': 6}, '1200months': {'total_price': 200, 'price_per_month': 0}}, 'tier3': {'1months': {'total_price': 50, 'price_per_month': 50}, '3months': {'total_price': 120, 'price_per_month': 40}, '6months': {'total_price': 180, 'price_per_month': 30}, '12months': {'total_price': 240, 'price_per_month': 20}, '1200months': {'total_price': 650, 'price_per_month': 0}}}
    csr_price_and_per_month_map_dict["tier2"] = {}
    csr_price_and_per_month_map_dict["tier2"]["1months"] = {}
    csr_price_and_per_month_map_dict["tier2"]["1months"]["total_price"] = users_response_object_json[0][2]
    csr_price_and_per_month_map_dict["tier2"]["1months"]["price_per_month"] = int(users_response_object_json[0][2] / users_response_object_json[0][1])
    csr_price_and_per_month_map_dict["tier2"]["3months"] = {}
    csr_price_and_per_month_map_dict["tier2"]["3months"]["total_price"] = users_response_object_json[1][2]
    csr_price_and_per_month_map_dict["tier2"]["3months"]["price_per_month"] = int(users_response_object_json[1][2] / users_response_object_json[1][1])
    csr_price_and_per_month_map_dict["tier2"]["6months"] = {}
    csr_price_and_per_month_map_dict["tier2"]["6months"]["total_price"] = users_response_object_json[2][2]
    csr_price_and_per_month_map_dict["tier2"]["6months"]["price_per_month"] = int(users_response_object_json[2][2] / users_response_object_json[2][1])
    csr_price_and_per_month_map_dict["tier2"]["12months"] = {}
    csr_price_and_per_month_map_dict["tier2"]["12months"]["total_price"] = users_response_object_json[3][2]
    csr_price_and_per_month_map_dict["tier2"]["12months"]["price_per_month"] = int(users_response_object_json[3][2] / users_response_object_json[3][1])
    csr_price_and_per_month_map_dict["tier2"]["1200months"] = {}
    csr_price_and_per_month_map_dict["tier2"]["1200months"]["total_price"] = users_response_object_json[4][2]
    csr_price_and_per_month_map_dict["tier2"]["1200months"]["price_per_month"] = int(users_response_object_json[4][2] / users_response_object_json[4][1])
    csr_price_and_per_month_map_dict["tier3"] = {}
    csr_price_and_per_month_map_dict["tier3"]["1months"] = {}
    csr_price_and_per_month_map_dict["tier3"]["1months"]["total_price"] = users_response_object_json[5][2]
    csr_price_and_per_month_map_dict["tier3"]["1months"]["price_per_month"] = int(users_response_object_json[5][2] / users_response_object_json[5][1])
    csr_price_and_per_month_map_dict["tier3"]["3months"] = {}
    csr_price_and_per_month_map_dict["tier3"]["3months"]["total_price"] = users_response_object_json[6][2]
    csr_price_and_per_month_map_dict["tier3"]["3months"]["price_per_month"] = int(users_response_object_json[6][2] / users_response_object_json[6][1])
    csr_price_and_per_month_map_dict["tier3"]["6months"] = {}
    csr_price_and_per_month_map_dict["tier3"]["6months"]["total_price"] = users_response_object_json[7][2]
    csr_price_and_per_month_map_dict["tier3"]["6months"]["price_per_month"] = int(users_response_object_json[7][2] / users_response_object_json[7][1])
    csr_price_and_per_month_map_dict["tier3"]["12months"] = {}
    csr_price_and_per_month_map_dict["tier3"]["12months"]["total_price"] = users_response_object_json[8][2]
    csr_price_and_per_month_map_dict["tier3"]["12months"]["price_per_month"] = int(users_response_object_json[8][2] / users_response_object_json[8][1])
    csr_price_and_per_month_map_dict["tier3"]["1200months"] = {}
    csr_price_and_per_month_map_dict["tier3"]["1200months"]["total_price"] = users_response_object_json[9][2]
    csr_price_and_per_month_map_dict["tier3"]["1200months"]["price_per_month"] = int(users_response_object_json[9][2] / users_response_object_json[9][1])
    return csr_price_and_per_month_map_dict

def set_timezone_and_geo_location_service_mesh(identity_provider_sub_id, timezone, geo_location, api_gateway_api_key):
    logging.critical("set_timezone_and_geo_location_service_mesh() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.users_api + "?identity_provider_sub_id=" + str(identity_provider_sub_id) + "&timezone=" + str(timezone) + "&geo_location=" + str(geo_location) + "&update=geolocation_and_timezone"
    api_get_response = requests.post(query_string, headers=headers)
    logging.error(api_get_response.json()) #debugging
    return api_get_response.json()

def api_key_submission_counter_return_bool(user_id, threshold, api_gateway_api_key):
    logging.critical("api_key_submission_counter_return_bool() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_api_key_submission_counter + "?user_id=" + str(user_id) + "&scope=get_api_key_submission_counter_row"
    api_get_response = requests.get(query_string, headers=headers)
    api_get_response_json = api_get_response.json()
    logging.error(api_get_response_json) #debugging
    if int(api_get_response_json[1]) > int(threshold): #if hourly greater than threshold return True
        return True
    if int(api_get_response_json[1]) < int(threshold): #if hourly less than threshold return False
        return False

def increment_api_key_submission_counter(user_id, api_gateway_api_key):
    logging.critical("increment_api_key_submission_counter() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_api_key_submission_counter + "?user_id=" + str(user_id) + "&scope=increment_counter_by_user_id"
    api_get_response = requests.post(query_string, headers=headers)
    api_get_response_json = api_get_response.json()
    logging.error(api_get_response_json) #debugging

def set_referral_code_service_mesh(user_id, referral_code, api_gateway_api_key):
    logging.critical("set_referral_code_service_mesh() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_user_subscription_status + "?user_id=" + str(user_id) + "&referral_code=" + str(referral_code) + "&scope=referral_code"
    api_get_response = requests.post(query_string, headers=headers)
    logging.error(api_get_response.json()) #debugging
    return api_get_response.json()

def get_account_created_epoch_from_users(user_id, api_gateway_api_key):
    logging.critical("get_account_created_epoch_from_users() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.users_api + "?user_id=" + str(user_id)
    api_get_response = requests.get(query_string, headers=headers)
    logging.error(api_get_response.json()) #debugging
    return int(api_get_response.json()[10])

def get_referral_code_from_user_subscription_status(user_id, api_gateway_api_key):
    logging.critical("get_referral_code_from_user_subscription_status() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_user_subscription_status + "?user_id=" + str(user_id) + "&scope=user_id"
    api_get_response = requests.get(query_string, headers=headers)
    logging.error(api_get_response.json()) #debugging
    return api_get_response.json()[1]

def get_user_subscription_status_row_by_user_id(user_id, api_gateway_api_key):
    logging.critical("get_user_subscription_status_row_by_user_id() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_user_subscription_status + "?user_id=" + str(user_id) + "&scope=user_id"
    api_get_response = requests.get(query_string, headers=headers)
    api_get_response_json = api_get_response.json()
    logging.error(api_get_response_json) #debugging
    if isinstance(api_get_response_json, str):
        if api_get_response_json == "[]":
            api_get_response_json = eval(api_get_response.json())
    return api_get_response_json

def get_brand_ambassador_referral_code_row_from_referral_code(referral_code, api_gateway_api_key):
    """
    Used by first time login landing page to validate referral codes
    """
    logging.critical("get_brand_ambassador_referral_code_row_from_referral_code() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    if referral_code == "":
        return ["valid_referral_code"]
    query_string = CSR_service_mesh_map.api_brand_ambassador_referral_codes + "?referral_code=" + str(referral_code) + "&scope=referral_code"
    logging.error("query_string set to: %s" % query_string) #debugging
    api_get_response = requests.get(query_string, headers=headers)
    api_get_response_json = api_get_response.json()
    logging.error(api_get_response_json) #debugging
    if isinstance(api_get_response_json, str):
        if api_get_response_json == "[]":
            api_get_response_json = eval(api_get_response.json())
        else:
            api_get_response_json = eval(api_get_response.json())
    if not isinstance(api_get_response_json, type(list())):
        api_get_response_json = []
    return api_get_response_json

def get_brand_ambassador_referral_code_row_from_referral_code_subscribe(referral_code, api_gateway_api_key):
    """
    Used by /subscribe/<user_determined_tier>/<user_determinted_months> to validate referral codes
    """
    logging.critical("get_brand_ambassador_referral_code_row_from_referral_code_subscribe() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_brand_ambassador_referral_codes + "?referral_code=" + str(referral_code) + "&scope=referral_code"
    logging.error("query_string set to: %s" % query_string) #debugging
    api_get_response = requests.get(query_string, headers=headers)
    api_get_response_json = api_get_response.json()
    logging.error(api_get_response_json) #debugging
    if isinstance(api_get_response_json, str):
        if api_get_response_json == "[]":
            api_get_response_json = eval(api_get_response.json())
        else:
            api_get_response_json = eval(api_get_response.json())
    if not isinstance(api_get_response_json, type(list())):
        api_get_response_json = []
    return api_get_response_json

def set_tier_and_admin_lock_user_subscription_status(user_id, subscription_tier, tier_locked_by_admin, api_gateway_api_key):
    logging.critical("set_tier_and_admin_lock_user_subscription_status() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_user_subscription_status + "?user_id=" + str(user_id) + "&subscription_tier=" + str(subscription_tier) + "&scope=subscription_tier"
    set_tier_api_response = requests.post(query_string, headers=headers)

    query_string = CSR_service_mesh_map.api_user_subscription_status + "?user_id=" + str(user_id) + "&tier_locked_by_admin=" + str(tier_locked_by_admin) + "&scope=tier_locked_by_admin"
    tier_locked_api_response = requests.post(query_string, headers=headers)

    logging.error(set_tier_api_response.json()) #debugging
    logging.error(tier_locked_api_response.json()) #debugging
    return set_tier_api_response.json(), tier_locked_api_response.json()

def delete_user_by_email(email_address, api_gateway_api_key):
    logging.critical("delete_user_by_email() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_delete_users_everywhere + "?email_address=" + str(email_address) + "&deleteoptions=deleteauth0"
    logging.error(query_string)
    try:
        delete_response = requests.delete(query_string, headers=headers, timeout=5)
    except:
        pass

def delete_user_by_user_id(user_id, api_gateway_api_key):
    logging.critical("delete_user_by_user_id() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_delete_users_everywhere + "?user_id=" + str(user_id) + "&deleteoptions=deleteauth0"
    logging.error(query_string)
    try:
        delete_response = requests.delete(query_string, headers=headers, timeout=5)
    except:
        pass

def delete_and_block_user_by_email(email_address, api_gateway_api_key):
    logging.critical("delete_and_block_user_by_email() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_delete_users_everywhere + "?email_address=" + str(email_address) + "&deleteoptions=blockauth0"
    logging.error(query_string)
    try:
        delete_response = requests.delete(query_string, headers=headers, timeout=5)
    except:
        pass

def delete_and_block_user_by_user_id(user_id, api_gateway_api_key):
    logging.critical("delete_and_block_user_by_user_id() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_delete_users_everywhere + "?user_id=" + str(user_id) + "&deleteoptions=blockauth0"
    logging.error(query_string)
    try:
        delete_response = requests.delete(query_string, headers=headers, timeout=5)
    except:
        pass

def set_brand_ambassador_referral_code(user_id, referral_code, revenue_share_percentage, api_gateway_api_key):
    logging.critical("set_brand_ambassador_referral_code() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_brand_ambassador_referral_codes + "?user_id=" + str(user_id) + "&referral_code=" + str(referral_code) + "&revenue_share_percentage=" + str(revenue_share_percentage)
    logging.error("query_string set to: %s" % query_string) #debugging
    api_get_response = requests.post(query_string, headers=headers)
    api_get_response_json = api_get_response.json()
    logging.error(api_get_response_json) #debugging
    return api_get_response_json

def delete_brand_ambassador_referral_code_by_user_id(user_id, api_gateway_api_key):
    logging.critical("delete_brand_ambassador_referral_code_by_user_id() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_brand_ambassador_referral_codes + "?user_id=" + str(user_id)
    logging.error("query_string set to: %s" % query_string) #debugging
    api_get_response = requests.delete(query_string, headers=headers)
    api_get_response_json = api_get_response.json()
    logging.error(api_get_response_json) #debugging
    return api_get_response_json

def delete_all_dca_logs_for_user_id(user_id, api_gateway_api_key):
    logging.critical("delete_all_dca_logs_for_user_id() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.api_dca_purchase_logs + "?user_id=" + str(user_id) + "&delete=deleteoneuserall"
    logging.error("query_string set to: %s" % query_string) #debugging
    api_get_response = requests.delete(query_string, headers=headers)
    api_get_response_json = api_get_response.json()
    logging.error(api_get_response_json) #debugging
    return api_get_response_json

def set_brand_ambassador_site_metrics_viewer_email_verified(user_id, brand_ambassador, site_metrics_viewer, email_verified, api_gateway_api_key):
    logging.critical("set_brand_ambassador_site_metrics_viewer_email_verified() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    query_string = CSR_service_mesh_map.users_api + "?user_id=" + str(user_id) + "&brand_ambassador=" + str(brand_ambassador) + "&site_metrics_viewer=" + str(site_metrics_viewer) + "&email_verified=" + str(email_verified) + "&update=userroles_by_user_id"
    logging.error("query_string set to: %s" % query_string) #debugging
    api_get_response = requests.post(query_string, headers=headers)
    api_get_response_json = api_get_response.json()
    logging.error(api_get_response_json) #debugging
    return api_get_response_json

def get_brand_ambassador_metrics(user_id, api_gateway_api_key):
    logging.critical("get_brand_ambassador_metrics() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    api_call_results_dictionary = {}

    def get_associated_referral_code(user_id, headers):
        logging.critical("get_associated_referral_code() called")
        query_string = CSR_service_mesh_map.api_brand_ambassador_referral_codes + "?user_id=" + str(user_id) + "&scope=user_id"
        api_response = requests.get(query_string, headers=headers)
        #api_call_results_dictionary["get_associated_referral_code"] = api_response.json()
        logging.error(api_response.json()) #debugging
        return api_response.json()
        #[1,"lyra",50]
    
    def get_total_users_with_referral_code(referral_code, headers, api_call_results_dictionary):
        logging.critical("get_total_users_with_referral_code() called")
        query_string = CSR_service_mesh_map.api_user_subscription_status + "?referral_code=" + str(referral_code) + "&scope=count_single_referral_code"
        api_response = requests.get(query_string, headers=headers)
        api_call_results_dictionary["get_total_users_with_referral_code"] = api_response.json()
        logging.error(api_response.json()) #debugging
    
    def get_gross_revenue_from_referral_code(referral_code, headers, api_call_results_dictionary):
        logging.critical("get_gross_revenue_from_referral_code() called")
        query_string = CSR_service_mesh_map.api_user_payments + "?referral_code=" + str(referral_code) + "&scope=gross_revenue_from_referral_code"
        api_response = requests.get(query_string, headers=headers)
        api_call_results_dictionary["get_gross_revenue_from_referral_code"] = api_response.json()
        logging.error(api_response.json()) #debugging

    def get_gross_revenue_from_referral_code_previous_quarter(referral_code, headers, api_call_results_dictionary):
        logging.critical("get_gross_revenue_from_referral_code_previous_quarter() called")
        
        first_day_of_the_previous_quarter_datetime = datetime_plus_months(get_first_day_of_the_quarter(datetime.datetime.now()), -3)
        last_day_of_the_previous_quarter_datetime = datetime_plus_months(get_last_day_of_the_quarter(datetime.datetime.now()), -3)
        first_day_of_the_previous_quarter_epoch = first_day_of_the_previous_quarter_datetime.strftime('%s')
        last_day_of_the_previous_quarter_epoch = last_day_of_the_previous_quarter_datetime.strftime('%s')

        query_string = CSR_service_mesh_map.api_user_payments + "?referral_code=" + str(referral_code) + "&beginning_epoch=" + str(first_day_of_the_previous_quarter_epoch) + "&ending_epoch=" + str(last_day_of_the_previous_quarter_epoch) + "&scope=get_gross_revenue_from_referral_code_epoch_time_range"
        api_response = requests.get(query_string, headers=headers)
        api_call_results_dictionary["get_gross_revenue_from_referral_code_previous_quarter"] = api_response.json()
        logging.error(api_response.json()) #debugging

    def get_gross_revenue_from_referral_code_quarter_to_date(referral_code, headers, api_call_results_dictionary):
        logging.critical("get_gross_revenue_from_referral_code_quarter_to_date() called")
        
        first_day_of_the_current_quarter_datetime = get_first_day_of_the_quarter(datetime.datetime.now())
        last_day_of_the_current_quarter_datetime = get_last_day_of_the_quarter(datetime.datetime.now())
        first_day_of_the_current_quarter_epoch = first_day_of_the_current_quarter_datetime.strftime('%s')
        last_day_of_the_current_quarter_epoch = last_day_of_the_current_quarter_datetime.strftime('%s')

        query_string = CSR_service_mesh_map.api_user_payments + "?referral_code=" + str(referral_code) + "&beginning_epoch=" + str(first_day_of_the_current_quarter_epoch) + "&ending_epoch=" + str(last_day_of_the_current_quarter_epoch) + "&scope=get_gross_revenue_from_referral_code_epoch_time_range"
        api_response = requests.get(query_string, headers=headers)
        api_call_results_dictionary["get_gross_revenue_from_referral_code_quarter_to_date"] = api_response.json()
        logging.error(api_response.json()) #debugging
        
    def get_count_of_unique_paying_users_with_specific_referral_code(referral_code, headers, api_call_results_dictionary):
        logging.critical("get_count_of_unique_paying_users_with_specific_referral_code() called")
        
        query_string = CSR_service_mesh_map.api_user_payments + "?referral_code=" + str(referral_code) + "&scope=count_unique_paying_users_with_referral_code"
        api_response = requests.get(query_string, headers=headers)
        api_call_results_dictionary["get_count_of_unique_paying_users_with_specific_referral_code"] = api_response.json()
        logging.error(api_response.json()) #debugging
    
    associated_referral_code_response = get_associated_referral_code(user_id, headers) #[1,"lyra",50]
    brand_ambassador_referral_code = associated_referral_code_response[1]
    brand_ambassador_percentage = float(float(associated_referral_code_response[2]) / float(100))

    thread1 = threading.Thread(target=get_total_users_with_referral_code, args=(brand_ambassador_referral_code, headers, api_call_results_dictionary, ))
    thread2 = threading.Thread(target=get_gross_revenue_from_referral_code, args=(brand_ambassador_referral_code, headers, api_call_results_dictionary, ))
    thread3 = threading.Thread(target=get_gross_revenue_from_referral_code_previous_quarter, args=(brand_ambassador_referral_code, headers, api_call_results_dictionary, ))
    thread4 = threading.Thread(target=get_gross_revenue_from_referral_code_quarter_to_date, args=(brand_ambassador_referral_code, headers, api_call_results_dictionary, ))
    thread5 = threading.Thread(target=get_count_of_unique_paying_users_with_specific_referral_code, args=(brand_ambassador_referral_code, headers, api_call_results_dictionary, ))

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()

    total_users_with_referral_code = api_call_results_dictionary["get_total_users_with_referral_code"]
    gross_revenue_from_referral_code = api_call_results_dictionary["get_gross_revenue_from_referral_code"]
    gross_revenue_from_referral_code_previous_quarter = api_call_results_dictionary["get_gross_revenue_from_referral_code_previous_quarter"]
    gross_revenue_from_referral_code_quarter_to_date = api_call_results_dictionary["get_gross_revenue_from_referral_code_quarter_to_date"]
    count_of_unique_paying_users_with_specific_referral_code = api_call_results_dictionary["get_count_of_unique_paying_users_with_specific_referral_code"]

    logging.error("Stats 1:")
    logging.error(total_users_with_referral_code) #['Lyra', 11] #empty: []
    logging.error(gross_revenue_from_referral_code) #[130] #empty: []
    logging.error(gross_revenue_from_referral_code_previous_quarter) #[120] #empty: []
    logging.error(gross_revenue_from_referral_code_quarter_to_date) #[10] #empty: []
    logging.error(count_of_unique_paying_users_with_specific_referral_code) #[3] #empty: [0]

    if not total_users_with_referral_code:
        total_users_with_referral_code = 0
    else:
        total_users_with_referral_code = total_users_with_referral_code[1]

    if not gross_revenue_from_referral_code:
        gross_revenue_from_referral_code = 0
    else:
        gross_revenue_from_referral_code = gross_revenue_from_referral_code[0]

    if not gross_revenue_from_referral_code_previous_quarter:
        gross_revenue_from_referral_code_previous_quarter = 0
    else:
        gross_revenue_from_referral_code_previous_quarter = gross_revenue_from_referral_code_previous_quarter[0]

    if not gross_revenue_from_referral_code_quarter_to_date:
        gross_revenue_from_referral_code_quarter_to_date = 0
    else:
        gross_revenue_from_referral_code_quarter_to_date = gross_revenue_from_referral_code_quarter_to_date[0]

    count_of_unique_paying_users_with_specific_referral_code = count_of_unique_paying_users_with_specific_referral_code[0] #this should always return a value in index 0 so no need to build a conditional for empty lists
    gross_revenue_from_referral_code_brand_ambassador_share = float(gross_revenue_from_referral_code) * float(brand_ambassador_percentage)
    gross_revenue_from_referral_code_previous_quarter_ambassador_share = float(gross_revenue_from_referral_code_previous_quarter) * float(brand_ambassador_percentage)
    gross_revenue_from_referral_code_quarter_to_date_ambassador_share = float(gross_revenue_from_referral_code_quarter_to_date) * float(brand_ambassador_percentage)
    
    logging.error("Stats 2:")
    logging.error(total_users_with_referral_code) #
    logging.error(gross_revenue_from_referral_code) #
    logging.error(gross_revenue_from_referral_code_previous_quarter) #
    logging.error(gross_revenue_from_referral_code_quarter_to_date) #
    logging.error(count_of_unique_paying_users_with_specific_referral_code) #
    #
    logging.error(gross_revenue_from_referral_code_brand_ambassador_share) #
    logging.error(gross_revenue_from_referral_code_previous_quarter_ambassador_share) #
    logging.error(gross_revenue_from_referral_code_quarter_to_date_ambassador_share) #

    #printing to gather mock data
    debugging_tuple_object = (brand_ambassador_referral_code, int(float(brand_ambassador_percentage)*100), total_users_with_referral_code, gross_revenue_from_referral_code, gross_revenue_from_referral_code_previous_quarter, gross_revenue_from_referral_code_quarter_to_date, count_of_unique_paying_users_with_specific_referral_code, gross_revenue_from_referral_code_brand_ambassador_share, gross_revenue_from_referral_code_previous_quarter_ambassador_share, gross_revenue_from_referral_code_quarter_to_date_ambassador_share)
    logging.error(debugging_tuple_object)

    return brand_ambassador_referral_code, int(float(brand_ambassador_percentage)*100), total_users_with_referral_code, gross_revenue_from_referral_code, gross_revenue_from_referral_code_previous_quarter, gross_revenue_from_referral_code_quarter_to_date, count_of_unique_paying_users_with_specific_referral_code, gross_revenue_from_referral_code_brand_ambassador_share, gross_revenue_from_referral_code_previous_quarter_ambassador_share, gross_revenue_from_referral_code_quarter_to_date_ambassador_share

def get_active_subscription_tier(user_id, api_gateway_api_key):
    logging.critical("get_active_subscription_tier() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    
    query_string = CSR_service_mesh_map.api_user_subscription_status + "?user_id=" + str(user_id) + "&scope=user_id"
    api_response = requests.get(query_string, headers=headers)
    user_subscription_status = api_response.json()
    logging.error(user_subscription_status) #debugging

    query_string = CSR_service_mesh_map.api_user_payments + "?user_id=" + str(user_id) + "&scope=single_active"
    api_response = requests.get(query_string, headers=headers)
    user_payments = api_response.json()
    logging.error(user_payments) #debugging

    active_tier = "1"
    if user_payments: #if user_payments isn't empty
        logging.error("user payments isn't empty") #debugging
        active_tier = str(user_payments[8])
    elif not user_payments: #if user_payments is empty
        logging.error("user payments is empty") #debugging
        if user_subscription_status[3] == "True": #if tier locked = True
            logging.error("tier_locked_by_admin True") #debugging
            active_tier = str(user_subscription_status[2])
        elif user_subscription_status[3] == "False": #if tier locked = False
            logging.error("tier_locked_by_admin False") #debugging
            active_tier = str("1")
    return active_tier

def get_active_subscription_tier_transaction_stats_exceeded_bool(user_id, api_gateway_api_key):
    logging.critical("get_active_subscription_tier_transaction_stats_exceeded_bool() called")
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    api_call_results_dictionary = {}
    
    def api_user_subscription_status(user_id, headers, api_call_results_dictionary):
        logging.critical("api_user_subscription_status() called")
        query_string = CSR_service_mesh_map.api_user_subscription_status + "?user_id=" + str(user_id) + "&scope=user_id"
        api_response = requests.get(query_string, headers=headers)
        api_call_results_dictionary["user_subscription_status"] = api_response.json()
        logging.error(api_response.json()) #debugging

    def api_user_payments(user_id, headers, api_call_results_dictionary):
        logging.critical("api_user_payments() called")
        query_string = CSR_service_mesh_map.api_user_payments + "?user_id=" + str(user_id) + "&scope=single_active"
        api_response = requests.get(query_string, headers=headers)
        api_call_results_dictionary["user_payments"] = api_response.json()
        logging.error(api_response.json()) #debugging

    def api_subscription_tier(headers, api_call_results_dictionary):
        logging.critical("api_subscription_tier() called")
        query_string = CSR_service_mesh_map.api_subscription_tier + "?scope=allsubscriptions"
        api_response = requests.get(query_string, headers=headers)
        api_call_results_dictionary["subscription_tier"] = api_response.json()
        logging.error(api_response.json()) #debugging

    def api_user_payments_many(user_id, headers, api_call_results_dictionary):
        logging.critical("api_user_payments_many() called")
        query_string = CSR_service_mesh_map.api_user_payments + "?user_id=" + str(user_id) + "&limit=12&scope=multiple_latest"
        api_response = requests.get(query_string, headers=headers)
        api_response_json = api_response.json()
        if isinstance(api_response_json, str):
            api_response_json = eval(api_response_json)
        if not isinstance(api_response_json, type([])):
            api_response_json = eval(api_response_json)
        if api_response_json == "[]":
            api_response_json = []
        print(api_response_json)
        api_call_results_dictionary["user_payments_many"] = api_response_json
        logging.error(api_response.json()) #debugging

    def api_pending_payments_many(user_id, headers, api_call_results_dictionary):
        logging.critical("api_pending_payments_many() called")
        query_string = CSR_service_mesh_map.api_pending_payments + "?user_id=" + str(user_id) + "&limit=5&after_id=0&scope=singleuserpaginated"
        api_response = requests.get(query_string, headers=headers)
        api_response_json = api_response.json()
        if isinstance(api_response_json, str):
            api_response_json = eval(api_response_json)
        if not isinstance(api_response_json, type([])):
            api_response_json = eval(api_response_json)
        api_call_results_dictionary["pending_payments_many"] = api_response_json
        logging.error(api_response.json()) #debugging


    thread1 = threading.Thread(target=api_user_subscription_status, args=(user_id, headers, api_call_results_dictionary, ))
    thread2 = threading.Thread(target=api_user_payments, args=(user_id, headers, api_call_results_dictionary, ))
    thread3 = threading.Thread(target=api_subscription_tier, args=(headers, api_call_results_dictionary, ))
    thread4 = threading.Thread(target=api_user_payments_many, args=(user_id, headers, api_call_results_dictionary, ))
    thread5 = threading.Thread(target=api_pending_payments_many, args=(user_id, headers, api_call_results_dictionary, ))

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()

    user_subscription_status = api_call_results_dictionary["user_subscription_status"]
    user_payments = api_call_results_dictionary["user_payments"]
    subscription_tier = api_call_results_dictionary["subscription_tier"]
    user_payments_many = api_call_results_dictionary["user_payments_many"]
    pending_payments_many = api_call_results_dictionary["pending_payments_many"]
    tier_map = {"1": [], "2": [], "3": []}
    tier_map["1"] = subscription_tier[0][1:]
    tier_map["2"] = subscription_tier[1][1:]
    tier_map["3"] = subscription_tier[2][1:]
    logging.error(tier_map) #debugging

    exceeded_tier_limit = False
    active_tier = "1"
    if user_payments: #if user_payments isn't empty
        logging.error("user payments ins't empty") #debugging
        active_tier = str(user_payments[8])
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
            active_tier = str(user_subscription_status[2])
            if user_subscription_status[4] > tier_limits[0]: #if number of transactions this month is greater than tier limit
                logging.error("number of transactions exceeds tier") #debugging
                exceeded_tier_limit = True
            if user_subscription_status[5] > tier_limits[1]: #if dollar amount of transactions this month is greater than tier limit
                logging.error("dollar amount of transactions exceeds tier") #debugging
                exceeded_tier_limit = True
        elif user_subscription_status[3] == "False": #if tier locked = False
            logging.error("tier_locked_by_admin False") #debugging
            active_tier = str("1")
            paid_tier = str("1")
            tier_limits = tier_map[paid_tier]
            logging.error(tier_limits) #debugging
            if user_subscription_status[4] > tier_limits[0]: #if number of transactions this month is greater than tier limit
                logging.error("number of transactions exceeds tier") #debugging
                exceeded_tier_limit = True
            if user_subscription_status[5] > tier_limits[1]: #if dollar amount of transactions this month is greater than tier limit
                logging.error("dollar amount of transactions exceeds tier") #debugging
                exceeded_tier_limit = True

    logging.error("exceeded_tier_limit:") #debugging
    logging.error(exceeded_tier_limit) #debugging
    return exceeded_tier_limit, active_tier, user_subscription_status[4], user_subscription_status[5], user_subscription_status[6], user_subscription_status[7], user_payments_many, user_subscription_status, pending_payments_many
    #return user_subscription_status, user_payments, subscription_tier

def set_dca_schedule_next_run_time_n_seconds(user_id, digital_asset, seconds_input, api_gateway_api_key):
    """
    input: event_body_dict, dictionary created from SQS event, CSR-cron-events-btc lambda creates this message
    input: the exchange name that last ran, output from exchange function or can be mapped to a list of strings "priority_order_reference_list"
    output: no output
    """
    logging.critical("set_dca_schedule_next_run_time_n_seconds() called")

    top_of_the_current_minute_int = top_of_the_current_minute()
    next_run_epoch_int = top_of_the_current_minute_int + int(seconds_input)

    query_string = CSR_service_mesh_map.api_dca_schedule + "?user_id=" + str(user_id) + "&digital_asset=" + str(digital_asset) + "&next_run_epoch=" + str(next_run_epoch_int) + "&updatenextrunonly=updatenextrunonly"
    logging.debug(query_string) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    requests.post(query_string, headers=headers)

def log_to_dca_purchase_logs(event_body_dict, function_result, exchange_returned):
    pass
    #user_id	epoch_time	was_successful	coin_purchased	fiat_amount	exchange_used	interval_time_in_seconds	high_availability_type	exchange_order_id	failure_reason