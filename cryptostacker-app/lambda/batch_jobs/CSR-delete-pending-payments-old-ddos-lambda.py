#cron syntax:
# */5 * * * ? *

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

	#delete older than threshold
	current_epoch_time = CSR_toolkit.current_time_epoch()
	seconds_in_a_minute = 60
	seconds_in_an_hour = seconds_in_a_minute * 60
	seconds_in_a_day = seconds_in_an_hour * 24
	epoch_delete_threshold = current_epoch_time - (seconds_in_a_day * 1.5)
	headers = {}
	headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
	logging.error("deleting expired payments")
	query_string = CSR_service_mesh_map.api_pending_payments + "?epoch_time_created=" + str(epoch_delete_threshold)
	#api_get_response = requests.delete(query_string, headers=headers)
	while True:
		api_get_response = requests.delete(query_string, headers=headers)
		if api_get_response.status_code != 429:
			break
		time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
	logging.error(api_get_response.json())

	#retrieve all users with pending payments above threshold;
	logging.error("retrieving list of abusers")
	query_string = CSR_service_mesh_map.api_pending_payments + "?threshold=50&scope=ddos"
	#api_get_response = requests.get(query_string, headers=headers)
	while True:
		api_get_response = requests.get(query_string, headers=headers)
		if api_get_response.status_code != 429:
			break
		time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
	api_get_response_json = api_get_response.json()
	#example; [[1,75]]
	logging.error(api_get_response_json) #debugging
	logging.error("found %s payment abusers" % str(len(api_get_response_json)))
	logging.error("deleting abusers")
	for abuser in api_get_response_json:
		logging.error("deleting pending payments for user_id: %s" % str(abuser[0])) #debugging
		query_string = CSR_service_mesh_map.api_pending_payments + "?user_id=" + str(abuser[0])
		#api_get_response = requests.delete(query_string, headers=headers)
		while True:
			api_get_response = requests.delete(query_string, headers=headers)
			if api_get_response.status_code != 429:
				break
			time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
	
	logging.error("lambda_handler ends") #debugging