# if the cron events job for some reason misses a schedule then the next run time will be in the past, 
# since lambda's can run for 15 minutes and SQS queues can potentially end up with a lot of events a buffer is used when retrieving missed dca events
#cron syntax:
# 0 * * * ? *


#standard library
import datetime
import logging
import json
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

    for coin in CSR_toolkit.supported_coins_list:
        while_loop_counter = 1

        while True:
            if while_loop_counter == 1:
                query_url = CSR_service_mesh_map.api_dca_schedule + "?scope=get_missed_dca_schedules_paginated&limit=200&after_id=0&digital_asset=" + str(coin)
                logging.error(query_url)
                #missed_schedules_response = requests.get(query_url, headers=headers)
                while True:
                    missed_schedules_response = requests.get(query_url, headers=headers)
                    if missed_schedules_response.status_code != 429:
                        break
                    time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
                missed_schedules_response_json = missed_schedules_response.json()
                if isinstance(missed_schedules_response.json(), str):
                    missed_schedules_response_json = eval(missed_schedules_response.json())
                logging.error(missed_schedules_response_json)
                if missed_schedules_response_json:
                    after_id = missed_schedules_response_json[-1][0]
                for schedule in missed_schedules_response_json:
                    logging.error("schedule missed for user: %s" % str(schedule[0]))
                    CSR_toolkit.set_dca_schedule_next_run_time_n_seconds(schedule[0], coin, 300, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]) #set a new next run time
                
            elif while_loop_counter > 1:
                query_url = CSR_service_mesh_map.api_dca_schedule + "?scope=get_missed_dca_schedules_paginated&limit=200&after_id=" + str(after_id) + "&digital_asset=" + str(coin)
                logging.error(query_url)
                #missed_schedules_response = requests.get(query_url, headers=headers)
                while True:
                    missed_schedules_response = requests.get(query_url, headers=headers)
                    if missed_schedules_response.status_code != 429:
                        break
                    time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
                missed_schedules_response_json = missed_schedules_response.json()
                if isinstance(missed_schedules_response.json(), str):
                    missed_schedules_response_json = eval(missed_schedules_response.json())
                logging.error(missed_schedules_response_json)
                if missed_schedules_response_json:
                    after_id = missed_schedules_response_json[-1][0]
                for schedule in missed_schedules_response_json:
                    logging.error("schedule missed for user: %s" % str(schedule[0]))
                    CSR_toolkit.set_dca_schedule_next_run_time_n_seconds(schedule[0], coin, 300, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]) #set a new next run time

            while_loop_counter += 1
            
            if len(missed_schedules_response_json) < 200: #if API doesn't return at least as many rows as the query limit then then is the last loop
                logging.error("missed_schedules_response_json length of: %s.  Breaking while loop." % len(missed_schedules_response_json)) #debugging
                break
        