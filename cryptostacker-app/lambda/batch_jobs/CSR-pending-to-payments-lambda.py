#- build cron lambda (update user_payments)
#- checking pending_payments order_id status
#- creating rows in user_payments for successfully paid orders
#- set eventbridge schedule to every 5 minutes
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
import opennode_lib

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

def lambda_handler(event, context):
	logging.error("lambda_handler begins") #debugging 

	logging.error("retrieve service mesh secret for API calls") 
	service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF")) #{'CSR_Service_Mesh_Secret_1': 'test12345'}
	headers = {}
	headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]
	logging.error("retrieve opennode_api_key") 
	opennode_api_key = eval(aws_functions_for_lambda.get_aws_secret("CSR-opennode_api_key-TF"))

    #retrieve all pending payments
	logging.error("retrieve all pending payments")
	after_id = 0
	for loop_counter in range(0,180):
		query_string = CSR_service_mesh_map.api_pending_payments + "?limit=200&after_id=" + str(after_id) +"&scope=alluserspaginated"
		#api_get_response = requests.get(query_string, headers=headers)
		while True:
			api_get_response = requests.get(query_string, headers=headers)
			if api_get_response.status_code != 429:
				break
			time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
		api_get_response_json = api_get_response.json()
		after_id += 200
		logging.error(api_get_response_json) #debugging

		for row in api_get_response_json:
			user_id = row[1]
			order_id = row[2]
			current_us_state = row[3]
			epoch_time_created = row[4]
			purchased_tier = row[5]
			purchased_months = row[6]
			payment_amount_in_usd = row[7]
			logging.error("user_id: %s" % str(user_id)) #debugging
			logging.error("order_id: %s" % str(order_id)) #debugging
			logging.error("current_us_state: %s" % str(current_us_state)) #debugging
			logging.error("epoch_time_created: %s" % str(epoch_time_created)) #debugging
			opennode_response = opennode_lib.charge_info(opennode_api_key["api_key"], order_id)
			if "failed" not in opennode_response:
				logging.error(opennode_response) #debugging
				logging.error(opennode_response['data']['status']) #debugging
				description = opennode_response["data"]["description"] #AL:T2:1M: Tier 2 for 1 month
				tier_string = str(purchased_tier)
				months_string = str(purchased_months)
				
				if opennode_response['data']['status'] == "paid":
					#post to user_payments service/table
					logging.error("posting to user_payments")
					query_string = CSR_service_mesh_map.api_user_payments + "?user_id=" + str(user_id) + "&payment_provider=" + str("opennode") + "&crypto_or_fiat_gateway=" + str("crypto") + "&order_id=" + str(order_id) + "&payment_amount_in_usd=" + str(payment_amount_in_usd) + "&number_of_months_paid_for=" + str(months_string) + "&tier_paid_for=" + str(tier_string) + "&description=" + str(description) + "&current_us_state=" + str(current_us_state)
					#api_get_response = requests.post(query_string, headers=headers)
					while True:
						api_get_response = requests.post(query_string, headers=headers)
						if api_get_response.status_code != 429:
							break
						time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
					api_get_response_json = api_get_response.json()

					#delete from pending payments
					query_string = CSR_service_mesh_map.api_pending_payments + "?order_id=" + str(order_id)
					#api_get_response = requests.delete(query_string, headers=headers)
					while True:
						api_get_response = requests.delete(query_string, headers=headers)
						if api_get_response.status_code != 429:
							break
						time.sleep(CSR_toolkit.lambda_throttle_sleep_time)
					api_get_response_json = api_get_response.json()
					
		if len(api_get_response_json) < 200:
			break

	logging.error("lambda_handler ends") #debugging