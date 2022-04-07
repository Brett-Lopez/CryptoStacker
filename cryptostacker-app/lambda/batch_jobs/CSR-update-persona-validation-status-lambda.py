#cron syntax:
# */15 * * * ? *

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
import persona_lib

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def lambda_handler(event, context):
    logging.error("lambda_handler begins") #debugging

    logging.error("retrieve service mesh secret for API calls")
    service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF")) #{'CSR_Service_Mesh_Secret_1': 'test12345'}
    persona_secrets = eval(aws_functions_for_lambda.get_aws_secret("CSR-persona-secrets-TF"))
    
    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]

    hours_before_ignore = -6 #if user last login epoch is greater than n hours ignore user

    while_loop_counter = 1
    while True:
        if while_loop_counter == 1:
            query_string = CSR_service_mesh_map.users_api + "?scope=retrieve_users_by_verification_status_paginated&user_id=0&limit=200&verification_status_threshold=3"
            logging.error(query_string)
            #query_response = requests.get(query_string, headers=headers)
            while True:
                query_response = requests.get(query_string, headers=headers)
                if query_response.status_code != 429:
                    break
                time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
            users_by_verification_status_json = query_response.json()
            if isinstance(query_response.json(), str):
                users_by_verification_status_json = eval(query_response.json())
            logging.error(users_by_verification_status_json)
            if users_by_verification_status_json:
                if not isinstance(users_by_verification_status_json[0], list):
                    after_id = 0
                elif isinstance(users_by_verification_status_json[0], list):
                    after_id = users_by_verification_status_json[-1][0]

            for user in users_by_verification_status_json:
                
                #if user last login epoch is greater than n hours ignore user
                epoch_last_login_n_hours_ago = CSR_toolkit.epoch_plus_hours_epoch(CSR_toolkit.current_time_epoch(), hours_before_ignore) #if the user hasn't logged in for n hours then skip them so we don't hammer the persona API with calls for users who abandoned the verification process
                logging.error("epoch debug:")
                logging.error(str(user[9]))
                if int(epoch_last_login_n_hours_ago) > int(user[9]):
                    break
                
                persona_response = persona_lib.retrieve_inquiry_by_uuid(persona_secrets["persona_api_secret"], user[14])
                if persona_response.status_code == 429: #if rate limited sleep and break for loop
                    time.sleep(80)
                    break
                persona_response_object = persona_response.json()

                approved_counter = 0
                pending_counter = 0
                failed_counter = 0
                unknown_counter = 0

                if persona_response_object["data"]:
                    for inquiry in persona_response_object["data"]:
                        if inquiry["attributes"]["status"].lower() == "approved":
                            approved_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "completed":
                            approved_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "finished":
                            approved_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "pending":
                            pending_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "created":
                            pending_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "started":
                            pending_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "failed":
                            failed_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "fail":
                            failed_counter += 1
                        elif "fail" in inquiry["attributes"]["status"].lower():
                            failed_counter += 1
                        else:
                            unknown_counter += 1

                    if approved_counter > 0:
                        persona_verification_status = 3
                    elif approved_counter == 0 and failed_counter > 0:
                        persona_verification_status = 9
                    elif approved_counter == 0 and pending_counter > 0:
                        persona_verification_status = 2
                    else:
                        persona_verification_status = 0
                    
                    if int(user[15]) == persona_verification_status:
                        logging.error("status already correct in DB, skipping call to users service")
                    else:
                        logging.error("status not correct in DB, making call to users service")
                        query_string = CSR_service_mesh_map.users_api + "?update=persona_verification_status&user_id=" + str(user[0]) + "&persona_verification_status=" + str(persona_verification_status)
                        logging.error(query_string)
                        #query_response = requests.post(query_string, headers=headers)
                        while True:
                            query_response = requests.post(query_string, headers=headers)
                            if query_response.status_code != 429:
                                break
                            time.sleep(CSR_toolkit.lambda_throttle_sleep_time)


        elif while_loop_counter > 1:
            query_string = CSR_service_mesh_map.users_api + "?scope=retrieve_users_by_verification_status_paginated&user_id=" + str(after_id) + "&limit=200&verification_status_threshold=3"
            logging.error(query_string)
            #query_response = requests.get(query_string, headers=headers)
            while True:
                query_response = requests.get(query_string, headers=headers)
                if query_response.status_code != 429:
                    break
                time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
            users_by_verification_status_json = query_response.json()
            if isinstance(query_response.json(), str):
                users_by_verification_status_json = eval(query_response.json())
            logging.error(users_by_verification_status_json)
            if users_by_verification_status_json:
                if not isinstance(users_by_verification_status_json[0], list):
                    after_id = 0
                elif isinstance(users_by_verification_status_json[0], list):
                    after_id = users_by_verification_status_json[-1][0]

            for user in users_by_verification_status_json:
                
                #if user last login epoch is greater than n hours ignore user
                epoch_last_login_n_hours_ago = CSR_toolkit.epoch_plus_hours_epoch(CSR_toolkit.current_time_epoch(), hours_before_ignore) #if the user hasn't logged in for n hours then skip them so we don't hammer the persona API with calls for users who abandoned the verification process
                logging.error("epoch debug:")
                logging.error(str(user[9]))
                if int(epoch_last_login_n_hours_ago) > int(user[9]):
                    break
                
                persona_response = persona_lib.retrieve_inquiry_by_uuid(persona_secrets["persona_api_secret"], user[14])
                if persona_response.status_code == 429: #if rate limited sleep and break for loop
                    time.sleep(80)
                    break
                persona_response_object = persona_response.json()

                approved_counter = 0
                pending_counter = 0
                failed_counter = 0
                unknown_counter = 0

                if persona_response_object["data"]:
                    for inquiry in persona_response_object["data"]:
                        if inquiry["attributes"]["status"].lower() == "approved":
                            approved_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "completed":
                            approved_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "finished":
                            approved_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "pending":
                            pending_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "created":
                            pending_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "started":
                            pending_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "failed":
                            failed_counter += 1
                        elif inquiry["attributes"]["status"].lower() == "fail":
                            failed_counter += 1
                        elif "fail" in inquiry["attributes"]["status"].lower():
                            failed_counter += 1
                        else:
                            unknown_counter += 1

                    if approved_counter > 0:
                        persona_verification_status = 3
                    elif approved_counter == 0 and failed_counter > 0:
                        persona_verification_status = 9
                    elif approved_counter == 0 and pending_counter > 0:
                        persona_verification_status = 2
                    else:
                        persona_verification_status = 0
                    
                    if int(user[15]) == persona_verification_status:
                        logging.error("status already correct in DB, skipping call to users service")
                    else:
                        logging.error("status not correct in DB, making call to users service")
                        query_string = CSR_service_mesh_map.users_api + "?update=persona_verification_status&user_id=" + str(user[0]) + "&persona_verification_status=" + str(persona_verification_status)
                        logging.error(query_string)
                        #query_response = requests.post(query_string, headers=headers)
                        while True:
                            query_response = requests.post(query_string, headers=headers)
                            if query_response.status_code != 429:
                                break
                            time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
            
        while_loop_counter += 1
        if len(users_by_verification_status_json) < 200: #if API doesn't return at least as many rows as the query limit then its the last loop
            logging.error("retrieve_users_from_by_verification_status_paginated length of: %s.  Breaking while loop." % len(users_by_verification_status_json)) #debugging
            break
            
    logging.error("lambda_handler ends") #debugging
