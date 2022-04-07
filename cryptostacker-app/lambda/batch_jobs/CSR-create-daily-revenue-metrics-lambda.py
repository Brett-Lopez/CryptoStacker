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
        "gross_revenue_past_24_hours": 0,
        "gross_revenue_past_7_days": 0,
        "gross_revenue_past_rolling_30_days": 0,
        "gross_revenue_past_previous_month": 0,
        "gross_revenue_past_month_to_date": 0,
        "gross_revenue_past_previous_quarter": 0,
        "gross_revenue_past_quarter_to_date": 0,
        "gross_revenue_past_previous_year": 0,
        "gross_revenue_past_year_to_date": 0,
        "gross_revenue_past_rolling_1_year": 0,
        "gross_revenue_past_all_time": 0
    }

    #gross_revenue_past_24_hours
    query_string = CSR_service_mesh_map.api_user_payments + "?scope=gross_revenue_past_24_hours"
    logging.error(query_string)
    
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
    if count_json:
        metric_record_dict["gross_revenue_past_24_hours"] = str(count_json[0])

    #gross_revenue_past_7_days
    query_string = CSR_service_mesh_map.api_user_payments + "?scope=gross_revenue_past_7_days"
    logging.error(query_string)
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
    if count_json:
        metric_record_dict["gross_revenue_past_7_days"] = str(count_json[0])

    #gross_revenue_past_rolling_30_days
    query_string = CSR_service_mesh_map.api_user_payments + "?scope=gross_revenue_past_rolling_30_days"
    logging.error(query_string)
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
    if count_json:
        metric_record_dict["gross_revenue_past_rolling_30_days"] = str(count_json[0])

    #gross_revenue_past_previous_month
    query_string = CSR_service_mesh_map.api_user_payments + "?scope=gross_revenue_past_previous_month"
    logging.error(query_string)
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
    if count_json:
        metric_record_dict["gross_revenue_past_previous_month"] = str(count_json[0])
    
    #gross_revenue_past_month_to_date
    query_string = CSR_service_mesh_map.api_user_payments + "?scope=gross_revenue_past_month_to_date"
    logging.error(query_string)
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
    if count_json:
        metric_record_dict["gross_revenue_past_month_to_date"] = str(count_json[0])
    
    #gross_revenue_past_previous_quarter
    query_string = CSR_service_mesh_map.api_user_payments + "?scope=gross_revenue_past_previous_quarter"
    logging.error(query_string)
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
    if count_json:
        metric_record_dict["gross_revenue_past_previous_quarter"] = str(count_json[0])
    
    #gross_revenue_past_quarter_to_date
    query_string = CSR_service_mesh_map.api_user_payments + "?scope=gross_revenue_past_quarter_to_date"
    logging.error(query_string)
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
    if count_json:
        metric_record_dict["gross_revenue_past_quarter_to_date"] = str(count_json[0])
    
    #gross_revenue_past_previous_year
    query_string = CSR_service_mesh_map.api_user_payments + "?scope=gross_revenue_past_previous_year"
    logging.error(query_string)
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
    if count_json:
        metric_record_dict["gross_revenue_past_previous_year"] = str(count_json[0])
    
    #gross_revenue_past_year_to_date
    query_string = CSR_service_mesh_map.api_user_payments + "?scope=gross_revenue_past_year_to_date"
    logging.error(query_string)
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
    if count_json:
        metric_record_dict["gross_revenue_past_year_to_date"] = str(count_json[0])
    
    #gross_revenue_past_rolling_1_year
    query_string = CSR_service_mesh_map.api_user_payments + "?scope=gross_revenue_past_rolling_1_year"
    logging.error(query_string)
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
    if count_json:
        metric_record_dict["gross_revenue_past_rolling_1_year"] = str(count_json[0])
    
    #gross_revenue_past_all_time
    query_string = CSR_service_mesh_map.api_user_payments + "?scope=gross_revenue_past_all_time"
    logging.error(query_string)
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
    if count_json:
        metric_record_dict["gross_revenue_past_all_time"] = str(count_json[0])

    logging.error(metric_record_dict) #debugging


    #post to daily-revenue-metrics 
    #query results dictionary is used as input for a call to the CSR-create-daily-revenue-metrics-lambda
    logging.error("posting to daily-revenue-metrics")
    query_string = CSR_service_mesh_map.api_daily_revenue_metrics + "?gross_revenue_past_24_hours=" + str(metric_record_dict["gross_revenue_past_24_hours"]) + "&gross_revenue_past_7_days=" + str(metric_record_dict["gross_revenue_past_7_days"]) + "&gross_revenue_past_rolling_30_days=" + str(metric_record_dict["gross_revenue_past_rolling_30_days"]) + "&gross_revenue_past_previous_month=" + str(metric_record_dict["gross_revenue_past_previous_month"]) + "&gross_revenue_past_month_to_date=" + str(metric_record_dict["gross_revenue_past_month_to_date"]) + "&gross_revenue_past_previous_quarter=" + str(metric_record_dict["gross_revenue_past_previous_quarter"]) + "&gross_revenue_past_quarter_to_date=" + str(metric_record_dict["gross_revenue_past_quarter_to_date"]) + "&gross_revenue_past_previous_year=" + str(metric_record_dict["gross_revenue_past_previous_year"]) + "&gross_revenue_past_year_to_date=" + str(metric_record_dict["gross_revenue_past_year_to_date"]) + "&gross_revenue_past_rolling_1_year=" + str(metric_record_dict["gross_revenue_past_rolling_1_year"]) + "&gross_revenue_past_all_time=" + str(metric_record_dict["gross_revenue_past_all_time"])
    logging.error(query_string)
    #query_response = requests.post(query_string, headers=headers)
    while True:
        query_response = requests.post(query_string, headers=headers)
        if query_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(query_response.json())
    
    logging.error("lambda_handler ends") #debugging

