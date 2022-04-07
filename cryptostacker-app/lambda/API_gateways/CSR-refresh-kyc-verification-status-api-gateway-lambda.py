#pip install mysql-connector-python
from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
import json
import CSR_service_mesh_map
import CSR_toolkit
import requests
import time
import persona_lib
#import threading


def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

    responseObject = {}
    responseObject["statusCode"] = 200
    responseObject["headers"] = {}
    responseObject["headers"]["Content-Type"] = "application/json" 
    #print(responseObject) #debugging

    logging.error("retrieve service mesh secret for API calls")
    service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF"))
    persona_secrets = eval(aws_functions_for_lambda.get_aws_secret("CSR-persona-secrets-TF"))
    headers = {}
    headers["X-API-Key"] = service_mesh_secret_1["CSR_Service_Mesh_Secret_1"]

    #IF GET
    if event["httpMethod"] == "GET":
        logging.error("httpMethod: GET") #debugging
        if "scope" in event["queryStringParameters"]:
            logging.error("required scope set") #debugging
            
            if event["queryStringParameters"]["scope"] == "get_latest_kyc_status":
                logging.error("scope: single_latest") #debugging
                if "user_id" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                user_id = event["queryStringParameters"]["user_id"]
                query_string = CSR_service_mesh_map.users_api + "?user_id=" + str(user_id)
                logging.error(query_string)
                query_response = requests.get(query_string, headers=headers)
                user = query_response.json()

                persona_response = persona_lib.retrieve_inquiry_by_uuid(persona_secrets["persona_api_secret"], user[14])
                if persona_response.status_code == 429:
                    responseObject["body"] = json.dumps("persona rate limit reached")
                    return responseObject 
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
                        responseObject["body"] = json.dumps("verification status hasn't changed, no update")
                        return responseObject
                    else:
                        logging.error("status not correct in DB, making call to users service")
                        query_string = CSR_service_mesh_map.users_api + "?update=persona_verification_status&user_id=" + str(user[0]) + "&persona_verification_status=" + str(persona_verification_status)
                        logging.error(query_string)
                        query_response = requests.post(query_string, headers=headers)

                        responseObject["body"] = json.dumps("verification status has changed, status field updated")
                        return responseObject
                
                else:
                    responseObject["body"] = json.dumps("user hasn't submitted verification inquiry yet")
                    return responseObject

            else:
                logging.error("queryStringParameters missing") #debugging
                responseObject["statusCode"] = 400
                responseObject["body"] = json.dumps("queryStringParameters missing")
                return responseObject
            
        else:
            logging.error("queryStringParameters missing") #debugging
            responseObject["statusCode"] = 400
            responseObject["body"] = json.dumps("queryStringParameters missing")
            return responseObject

    #IF POST
    elif event["httpMethod"] == "POST":
        logging.error("httpMethod: POST") #debugging
    
    #IF DELETE
    elif event["httpMethod"] == "DELETE":
        logging.error("httpMethod: DELETE") #debugging
        
    else:
        logging.error("queryStringParameters missing httpMethod") #debugging
        responseObject["body"] = json.dumps("queryStringParameters missing httpMethod")
        responseObject["statusCode"] = 400
        return responseObject


#########################
##### query params ######
#########################

#GET - multiple metrics - 
#?scope=get_latest_kyc_status&user_id=1

