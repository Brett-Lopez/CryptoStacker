#cron syntax:
# DAILY - 1am-ish pacific
# 0 9 * * ? *

#standard library
import datetime
import logging
import json
import urllib.parse
import time

#third party
import boto3
import requests

#iternal libraries
import aws_functions_for_lambda
import CSR_service_mesh_map
import CSR_toolkit

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def lambda_handler(event, context):
    logging.error("lambda_handler begins") #debugging

    logging.error("retrieve service mesh secret for API calls")
    service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF")) #{'CSR_Service_Mesh_Secret_1': 'test12345'}  
    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]

    #map to be used when creating metric record/row
    metric_record_dict = {
        "total_users": "0",
        "user_subscription_status_users": "0",
        "verified_users": "0",
        "paying_users": "0",
        "payments_1_month": "0",
        "payments_3_month": "0",
        "payments_6_month": "0",
        "payments_12_month": "0",
        "payments_1200_month": "0",
        "payments_tier_2": "0",
        "payments_tier_3": "0",
        "users_logged_in_past_24_hours": "0",
        "users_logged_in_past_48_hours": "0",
        "users_logged_in_past_168_hours": "0",
        "users_logged_in_past_336_hours": "0",
        "users_logged_in_past_720_hours": "0",
        "active_schedules_btc": "0",
        "active_schedules_eth": "0",
        "active_schedules_ltc": "0",
        "active_schedules_ha_type_failover": 0,
        "active_schedules_ha_type_round_robin": 0,
        "active_schedules_ha_type_simultaneous": 0,
        "active_schedules_ha_type_single_exchange": 0,
        "active_schedules_dca_logs_past_30_days": "0"
    }

    #count unique total users
    query_string = CSR_service_mesh_map.users_api + "?scope=count_unique_users"
    logging.error(query_string)
    logging.error("calling service: count unique total users")
    #query_response = requests.get(query_string, headers=headers)
    while True:
        query_response = requests.get(query_string, headers=headers)
        if query_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(query_response.json())
    count_json = query_response.json()
    logging.error(query_response.json())
    if isinstance(query_response.json(), str):
        count_json = eval(query_response.json())
    logging.error(count_json)
    metric_record_dict["total_users"] = str(count_json[0])

    #count unique user_subscription_status
    query_string = CSR_service_mesh_map.api_user_subscription_status + "?scope=count_unique_users"
    logging.error(query_string)
    logging.error("calling service: count unique user_subscription_status")
    #query_response = requests.get(query_string, headers=headers)
    while True:
        query_response = requests.get(query_string, headers=headers)
        if query_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    count_json = query_response.json()
    logging.error(query_response.json())
    if isinstance(query_response.json(), str):
        count_json = eval(query_response.json())
    logging.error(count_json)
    metric_record_dict["user_subscription_status_users"] = str(count_json[0])

    #count verified users
    query_string = CSR_service_mesh_map.users_api + "?scope=count_verified_users"
    logging.error(query_string)
    logging.error("calling service: count verified users in users")
    #query_response = requests.get(query_string, headers=headers)
    while True:
        query_response = requests.get(query_string, headers=headers)
        if query_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    count_json = query_response.json()
    logging.error(query_response.json())
    if isinstance(query_response.json(), str):
        count_json = eval(query_response.json())
    logging.error(count_json)
    if not count_json:
        metric_record_dict["verified_users"] = str(0)
    if count_json:
        metric_record_dict["verified_users"] = str(count_json[0])

    #count unique user_ids in paid_payments | where Subscription expiration date is greater than current time
    query_string = CSR_service_mesh_map.api_user_payments + "?scope=count_unique_users"
    logging.error(query_string)
    logging.error("calling service: count unique user_ids in paid_payments")
    #query_response = requests.get(query_string, headers=headers)
    while True:
        query_response = requests.get(query_string, headers=headers)
        if query_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    count_json = query_response.json()
    logging.error(query_response.json())
    if isinstance(query_response.json(), str):
        count_json = eval(query_response.json())
    logging.error(count_json)
    metric_record_dict["paying_users"] = str(count_json[0])

    #count number of paid_payments for each number of months | where Subscription expiration date is greater than current time
    for number_of_months_int in [1, 3, 6, 12, 1200]:
        #pass
        query_string = CSR_service_mesh_map.api_user_payments + "?scope=number_of_months_paid_for&number_of_months_paid_for=" + str(number_of_months_int)
        logging.error(query_string)
        logging.error("calling service: count number_of_months_paid_for in paid_payments")
        #query_response = requests.get(query_string, headers=headers)
        while True:
            query_response = requests.get(query_string, headers=headers)
            if query_response.status_code != 429:
                break
            time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
        count_json = query_response.json()
        logging.error(query_response.json())
        if isinstance(query_response.json(), str):
            count_json = eval(query_response.json())
        logging.error(count_json)
        metric_record_dict["payments_" + str(number_of_months_int) + "_month"] = str(count_json[0])
        #above should be iterative loop for [1, 3, 6, 12, 1200]
    
    #count number of paid_payments for each tier | where Subscription expiration date is greater than current time
    for tier_paid_int in [2, 3]:
        #pass
        query_string = CSR_service_mesh_map.api_user_payments + "?scope=count_tier_paid_for&tier_paid_for=" + str(tier_paid_int)
        logging.error(query_string)
        logging.error("calling service: count tier_paid_for in paid_payments")
        #query_response = requests.get(query_string, headers=headers)
        while True:
            query_response = requests.get(query_string, headers=headers)
            if query_response.status_code != 429:
                break
            time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
        count_json = query_response.json()
        logging.error(query_response.json())
        if isinstance(query_response.json(), str):
            count_json = eval(query_response.json())
        logging.error(count_json)
        metric_record_dict["payments_tier_" + str(tier_paid_int)] = str(count_json[0])
        #above should be iterative loop for [2, 3]

    #count users by last login
    for hours_since_log_on in [24, 48, 168, 336, 720]:
        query_string = CSR_service_mesh_map.users_api + "?scope=count_users_logged_in_last_n_hours&last_n_hours=" + str(hours_since_log_on)
        logging.error(query_string)
        logging.error("calling service: count user logons in last n hours")
        #query_response = requests.get(query_string, headers=headers)
        while True:
            query_response = requests.get(query_string, headers=headers)
            if query_response.status_code != 429:
                break
            time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
        count_json = query_response.json()
        logging.error(query_response.json())
        if isinstance(query_response.json(), str):
            count_json = eval(query_response.json())
        logging.error(count_json)
        metric_record_dict["users_logged_in_past_" + str(hours_since_log_on) + "_hours"] = str(count_json[0])
        #above should query [24, 48, 168, 336, 720]


    # count_active_schedules_btc | ?scope=count_active_schedules&digital_asset=btc
    # count_active_schedules_eth | ?scope=count_active_schedules&digital_asset=eth
    # count_active_schedules_ltc | ?scope=count_active_schedules&digital_asset=ltc
    for digital_asset in ["btc", "eth", "ltc"]:
        scope_string = "?scope=count_active_schedules&digital_asset=" + str(digital_asset)
        query_string = CSR_service_mesh_map.api_dca_schedule + scope_string
        logging.error(query_string)
        #query_response = requests.get(query_string, headers=headers)
        while True:
            query_response = requests.get(query_string, headers=headers)
            if query_response.status_code != 429:
                break
            time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
        count_json = query_response.json()
        metric_record_dict["active_schedules_" + str(digital_asset)] = count_json[0]


    # active_schedules_ha_type_failover         | ?scope=count_ha_types&digital_asset=btc&ha_type=failover
    # active_schedules_ha_type_round_robin      | ?scope=count_ha_types&digital_asset=btc&ha_type=round_robin
    # active_schedules_ha_type_simultaneous     | ?scope=count_ha_types&digital_asset=btc&ha_type=simultaneous
    # active_schedules_ha_type_single_exchange  | ?scope=count_ha_types&digital_asset=btc&ha_type=single_exchange
    logging.error("counting active_schedules_ha_type")
    for ha_type in ["failover", "round_robin", "simultaneous", "single_exchange"]:
        for digital_asset in ["btc", "eth", "ltc"]:
            scope_string = "?scope=count_ha_types&digital_asset=" + str(digital_asset) + "&ha_type=" + str(ha_type)
            query_string = CSR_service_mesh_map.api_dca_schedule + scope_string
            logging.error(query_string)
            #query_response = requests.get(query_string, headers=headers)
            while True:
                query_response = requests.get(query_string, headers=headers)
                if query_response.status_code != 429:
                    break
                time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
            count_json = query_response.json()
            metric_record_dict["active_schedules_ha_type_" + str(ha_type)] += int(count_json[0])


    # active_schedules_dca_logs_past_30_days
    query_string = CSR_service_mesh_map.api_dca_purchase_logs + "?scope=count_unique_user_ids_rolling_30_days"
    logging.error(query_string)
    logging.error("calling service: count unique user_ids in dca_purchase_logs rolling 30 days")
    #query_response = requests.get(query_string, headers=headers)
    while True:
        query_response = requests.get(query_string, headers=headers)
        if query_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    count_json = query_response.json()
    logging.error(query_response.json())
    if isinstance(query_response.json(), str):
        count_json = eval(query_response.json())
    logging.error(count_json)
    if count_json:
        metric_record_dict["active_schedules_dca_logs_past_30_days"] = str(count_json[0])


    logging.error(metric_record_dict) #debugging


    #post to daily_user_metrics 
    #query results dictionary is used as input for a call to the CSR-daily-metrics-api-gateway-lambda
    query_string = CSR_service_mesh_map.api_daily_user_metrics + "?total_users=" + str(metric_record_dict["total_users"]) + "&user_subscription_status_users=" + str(metric_record_dict["user_subscription_status_users"]) + "&verified_users=" + str(metric_record_dict["verified_users"]) + "&paying_users=" + str(metric_record_dict["paying_users"]) + "&payments_1_month=" + str(metric_record_dict["payments_1_month"]) + "&payments_3_month=" + str(metric_record_dict["payments_3_month"]) + "&payments_6_month=" + str(metric_record_dict["payments_6_month"]) + "&payments_12_month=" + str(metric_record_dict["payments_12_month"]) + "&payments_1200_month=" + str(metric_record_dict["payments_1200_month"]) + "&payments_tier_2=" + str(metric_record_dict["payments_tier_2"]) + "&payments_tier_3=" + str(metric_record_dict["payments_tier_3"]) + "&users_logged_in_past_24_hours=" + str(metric_record_dict["users_logged_in_past_24_hours"]) + "&users_logged_in_past_48_hours=" + str(metric_record_dict["users_logged_in_past_48_hours"]) + "&users_logged_in_past_168_hours=" + str(metric_record_dict["users_logged_in_past_168_hours"]) + "&users_logged_in_past_336_hours=" + str(metric_record_dict["users_logged_in_past_336_hours"]) + "&users_logged_in_past_720_hours=" + str(metric_record_dict["users_logged_in_past_720_hours"]) + "&active_schedules_btc=" + str(metric_record_dict["active_schedules_btc"]) + "&active_schedules_eth=" + str(metric_record_dict["active_schedules_eth"]) + "&active_schedules_ltc=" + str(metric_record_dict["active_schedules_ltc"]) + "&active_schedules_ha_type_failover=" + str(metric_record_dict["active_schedules_ha_type_failover"]) + "&active_schedules_ha_type_round_robin=" + str(metric_record_dict["active_schedules_ha_type_round_robin"]) + "&active_schedules_ha_type_simultaneous=" + str(metric_record_dict["active_schedules_ha_type_simultaneous"]) + "&active_schedules_ha_type_single_exchange=" + str(metric_record_dict["active_schedules_ha_type_single_exchange"]) + "&active_schedules_dca_logs_past_30_days=" + str(metric_record_dict["active_schedules_dca_logs_past_30_days"])
    logging.error(query_string)
    logging.error("calling service: posting to daily-user-metrics")
    #query_response = requests.post(query_string, headers=headers)
    while True:
        query_response = requests.post(query_string, headers=headers)
        if query_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(query_response.json())
    
    logging.error("lambda_handler ends") #debugging

