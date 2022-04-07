#cron syntax:
# 0 * * * ? *

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

    current_time_epoch_int = CSR_toolkit.current_time_epoch()

    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
    
    for exchange_string in CSR_toolkit.supported_exchanges_list_without_notset:
        while_loop_counter = 1

        while True:
            if while_loop_counter == 1:
                query_string = CSR_service_mesh_map.api_keys_metadata + "?epoch_time=" + str(current_time_epoch_int) + "&exchange=" + str(exchange_string) + "&after_id=0&limit=200"
                logging.error(query_string)
                #expired_api_keys_metadata_response = requests.get(query_string, headers=headers)
                while True:
                    expired_api_keys_metadata_response = requests.get(query_string, headers=headers)
                    if expired_api_keys_metadata_response.status_code != 429:
                        break
                    time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
                expired_api_keys_metadata_response_json = expired_api_keys_metadata_response.json()
                if isinstance(expired_api_keys_metadata_response.json(), str):
                    expired_api_keys_metadata_response_json = eval(expired_api_keys_metadata_response.json())
                logging.error(expired_api_keys_metadata_response_json)
                if expired_api_keys_metadata_response_json:
                    after_id = expired_api_keys_metadata_response_json[-1][0]
                for api_key_metadata in expired_api_keys_metadata_response_json:
                    logging.error("deleting API key for user: %s on exchange: %s" % (str(api_key_metadata[0]), str(exchange_string)))
                    CSR_toolkit.delete_users_exchange_api_key_write_only(str(api_key_metadata[0]), str(exchange_string), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                
            elif while_loop_counter > 1:
                query_string = CSR_service_mesh_map.api_keys_metadata + "?epoch_time=" + str(current_time_epoch_int) + "&exchange=" + str(exchange_string) + "&after_id=" + str(after_id) + "&limit=200"
                logging.error(query_string)
                #expired_api_keys_metadata_response = requests.get(query_string, headers=headers)
                while True:
                    expired_api_keys_metadata_response = requests.get(query_string, headers=headers)
                    if expired_api_keys_metadata_response.status_code != 429:
                        break
                    time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
                expired_api_keys_metadata_response_json = expired_api_keys_metadata_response.json()
                if isinstance(expired_api_keys_metadata_response.json(), str):
                    expired_api_keys_metadata_response_json = eval(expired_api_keys_metadata_response.json())
                logging.error(expired_api_keys_metadata_response_json)
                if expired_api_keys_metadata_response_json:
                    after_id = expired_api_keys_metadata_response_json[-1][0]
                for api_key_metadata in expired_api_keys_metadata_response_json:
                    logging.error("deleting API key for user: %s on exchange: %s" % (str(api_key_metadata[0]), str(exchange_string)))
                    CSR_toolkit.delete_users_exchange_api_key_write_only(str(api_key_metadata[0]), str(exchange_string), service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])

            while_loop_counter += 1
            
            if len(expired_api_keys_metadata_response_json) < 200: #if API doesn't return at least as many rows as the query limit then then is the last loop
                logging.error("expired_api_keys_metadata_response_json length of: %s.  Breaking while loop." % len(expired_api_keys_metadata_response_json)) #debugging
                break
        