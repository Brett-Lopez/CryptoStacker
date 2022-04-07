#reset api key counter
#runs hourly
#cron syntax:
# 0 * * * ? *


#standard;
import logging
import time

#third party;
import requests

#internal;
import aws_functions_for_lambda
import CSR_service_mesh_map
import CSR_toolkit

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def lambda_handler(event, context):
    logging.error("lambda_handler beginning")

    logging.error("retrieve service mesh secret for API calls")
    service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF")) #{'CSR_Service_Mesh_Secret_1': 'test12345'}
    
    query_url = CSR_service_mesh_map.api_api_key_submission_counter + "?scope=reset_hour_counter_for_all_users"
    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    #reset_response = requests.post(query_url, headers=headers)
    while True:
        reset_response = requests.post(query_url, headers=headers)
        if reset_response.status_code != 429:
            break
        time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
    logging.error(reset_response.json())