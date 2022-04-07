#- set eventbridge schedule to every 1 minutes
#cron syntax:
# */1 * * * ? *

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

    # create get scope "warming" if there isn't an existing GET method scope that can be used for warming

    # API key submission counter
    logging.error("api_api_key_submission_counter")
    query_string = CSR_service_mesh_map.api_api_key_submission_counter + "?user_id=1&scope=get_api_key_submission_counter_row"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    # API keys metadata
    logging.error("api_keys_metadata")
    query_string = CSR_service_mesh_map.api_keys_metadata + "?user_id=1&exchange=coinbase_pro"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    # auth0 token
    logging.error("api_auth0_token_response")
    query_string = CSR_service_mesh_map.api_auth0_token_response + "?scope=warming"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    # auth0
    logging.error("api_auth0")
    query_string = CSR_service_mesh_map.api_auth0 + "?scope=warming"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    # brand ambassador referral codes
    logging.error("api_brand_ambassador_referral_codes")
    query_string = CSR_service_mesh_map.api_brand_ambassador_referral_codes + "?user_id=1&scope=user_id"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    # dca-purchase-logs
    logging.error("api_dca_purchase_logs")
    query_string = CSR_service_mesh_map.api_dca_purchase_logs + "?user_id=1&limit=1&after_id=0"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    # opennode
    logging.error("api_opennode")
    query_string = CSR_service_mesh_map.api_opennode + "?scope=warming"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    # pending-payments
    logging.error("api_pending_payments")
    query_string = CSR_service_mesh_map.api_pending_payments + "?user_id=1&scope=singleuser"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    # pricing-tier
    logging.error("api_pricing_tier")
    query_string = CSR_service_mesh_map.api_pricing_tier + "?scope=allprices"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    # subscription-tier
    logging.error("api_subscription_tier")
    query_string = CSR_service_mesh_map.api_subscription_tier + "?scope=allsubscriptions"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    # user-payments
    logging.error("api_user_payments")
    query_string = CSR_service_mesh_map.api_user_payments + "?user_id=1&scope=single_latest"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    # user-subscription-status
    logging.error("api_user_subscription_status")
    query_string = CSR_service_mesh_map.api_user_subscription_status + "?user_id=1&scope=user_id"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    # users
    logging.error("users_api")
    query_string = CSR_service_mesh_map.users_api + "?user_id=1"
    #api_get_response = requests.get(query_string, headers=headers)
    while True:
        api_get_response = requests.get(query_string, headers=headers)
        if api_get_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(api_get_response.json())

    logging.error("lambda_handler ends") #debugging