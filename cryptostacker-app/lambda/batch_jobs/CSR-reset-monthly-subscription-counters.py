#triggered by cloudwatch event cron job at 12:00AM on the first of the month - pacific time
#cron syntax:
# 0 8 1 * ? *

#standard libraries
import logging
import time

#third party libraries
import requests

#import custom libraries
import aws_functions_for_lambda
import CSR_service_mesh_map
import CSR_toolkit

def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s', level=CSR_toolkit.logging_level_var)
    logging.error("lambda_handler beginning")
    logging.error("retrieve service mesh secret for API calls")
    service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF")) #{'CSR_Service_Mesh_Secret_1': 'test12345'}
    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    query_string = CSR_service_mesh_map.api_user_subscription_status + "?scope=reset_monthly_counters"
    logging.error(query_string)
    logging.error("resetting monthly stats")
    #query_response = requests.post(query_string, headers=headers)
    while True:
        query_response = requests.post(query_string, headers=headers)
        if query_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(query_response.json())
    logging.error("lambda_handler ends")
