#pip install mysql-connector-python
from mysql.connector import connect, Error
import logging

import requests
import aws_functions_for_lambda
import json
import datetime
import concurrent.futures
import CSR_service_mesh_map
import CSR_toolkit
import auth0_lib
#import pytz
import urllib.parse #remove later

def deleteauth0_function_order(user_id, identity_provider_sub_id, api_gateway_api_key, auth0_client_id, auth0_client_secret):
    logging.critical("deleteauth0_function_order() called") #debugging
    access_token = auth0_lib.get_bearer_token(auth0_client_id, auth0_client_secret)
    
    auth0_lib.blockuser(identity_provider_sub_id, access_token)
    delete_user_from_all_internal_services(user_id, api_gateway_api_key)

    auth0_lib.deleteuser(identity_provider_sub_id, access_token)

def blockauth0_function_order(user_id, identity_provider_sub_id, api_gateway_api_key, auth0_client_id, auth0_client_secret):
    logging.critical("blockauth0_function_order() called") #debugging
    access_token = auth0_lib.get_bearer_token(auth0_client_id, auth0_client_secret)

    auth0_lib.blockuser(identity_provider_sub_id, access_token)
    delete_user_from_all_internal_services(user_id, api_gateway_api_key)

def delete_user_from_all_internal_services(user_id, api_gateway_api_key):
    #make this function faster with threading: todo
    logging.critical("delete_user_from_all_internal_services() called") #debugging
    logging.error(user_id) #debugging
    headers = {}
    headers["X-API-Key"] = api_gateway_api_key
    
    #delete user from "user" table
    logging.error("deleting user from user table") #debugging
    #query_string = "https://rnywj5tnv4.execute-api.us-east-2.amazonaws.com/prod/users?user_id=" + str(user_id)
    query_string = CSR_service_mesh_map.users_api + "?user_id=" + str(user_id)
    delete_response = requests.delete(query_string, headers=headers)
    logging.error(delete_response) #debugging
    logging.error(delete_response.json()) #debugging

    #delete api_keys_write
    logging.error("deleting api_keys_write") #debugging
    for exchange in CSR_toolkit.supported_exchanges_list_without_notset:
        query_string = CSR_service_mesh_map.api_keys_write + "?user_id=" + str(user_id) + "&exchange=" + str(exchange) + "&delete=delete"
        delete_response = requests.post(query_string, headers=headers)
        logging.error(delete_response) #debugging
        logging.error(delete_response.json()) #debugging

    #delete api_dca_schedule
    logging.error("deleting api_dca_schedule") #debugging
    for coin in CSR_toolkit.supported_coins_list:
        query_string = CSR_service_mesh_map.api_dca_schedule + "?user_id=" + str(user_id) + "&digital_asset=" + str(coin) + "&delete=delete"
        delete_response = requests.post(query_string, headers=headers)
        logging.error(delete_response) #debugging
        logging.error(delete_response.json()) #debugging

    #delete api_dca_purchase_logs
    logging.error("deleting api_dca_purchase_logs") #debugging
    query_string = CSR_service_mesh_map.api_dca_purchase_logs + "?user_id=" + str(user_id) + "&delete=deleteoneuserall"
    delete_response = requests.delete(query_string, headers=headers)
    logging.error(delete_response) #debugging
    logging.error(delete_response.json()) #debugging

    #delete api_user_subscription_status
    logging.error("deleting api_user_subscription_status") #debugging
    query_string = CSR_service_mesh_map.api_user_subscription_status + "?user_id=" + str(user_id)
    delete_response = requests.delete(query_string, headers=headers)
    logging.error(delete_response) #debugging
    logging.error(delete_response.json()) #debugging


def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

    responseObject = {}
    responseObject["statusCode"] = 200
    responseObject["headers"] = {}
    responseObject["headers"]["Content-Type"] = "application/json" 

    logging.error("retrieve RDS secrets")
    RDS_secret_return = aws_functions_for_lambda.get_aws_secret("CSR-primary-serverless-db-1-tf")
    RDS_secret_dict = eval(RDS_secret_return)
    RDS_secret_user = RDS_secret_dict["username"]
    RDS_secret_pass = RDS_secret_dict["password"]
    RDS_secret_host = RDS_secret_dict["host"]

    logging.error("retrieve service mesh secret for API calls")
    service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF"))

    auth0_secret = eval(aws_functions_for_lambda.get_aws_secret("CSR-auth0-api-keys-2-tf"))
    auth0_client_id = auth0_secret["AUTH0_CLIENT_ID"]
    auth0_client_secret = auth0_secret["AUTH0_CLIENT_SECRET"]

    #IF DELETE
    if event["httpMethod"] == "DELETE":
        logging.error("httpMethod: DELETE")
        if "user_id" in event["queryStringParameters"] and "deleteoptions" in event["queryStringParameters"] and "email_address" not in event["queryStringParameters"]:
            user_id = event["queryStringParameters"]["user_id"]
            deleteoptions = event["queryStringParameters"]["deleteoptions"]
            users_response_object = CSR_toolkit.get_list_of_users_from_user_id(user_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
            
            logging.error(users_response_object) #debugging
            if not users_response_object:
                logging.error("empty list, user doesn't exist or already deleted") #debugging
                responseObject["body"] = json.dumps("empty list, user doesn't exist or already deleted")
                return responseObject
            
            if deleteoptions == "deleteauth0":
                user_id = users_response_object[0]
                identity_provider_sub_id = users_response_object[1]
                deleteauth0_function_order(user_id, identity_provider_sub_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], auth0_client_id, auth0_client_secret)
            
            elif deleteoptions == "blockauth0":
                user_id = users_response_object[0]
                identity_provider_sub_id = users_response_object[1]
                blockauth0_function_order(user_id, identity_provider_sub_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], auth0_client_id, auth0_client_secret)
        
            else:
                responseObject["body"] = json.dumps("queryStringParameters: invalid deleteoptions param")
                responseObject["statusCode"] = 400
                return responseObject
                
            responseObject["body"] = json.dumps("deleted user")
            return responseObject

        elif "email_address" in event["queryStringParameters"] and "user_id" not in event["queryStringParameters"] and "deleteoptions" in event["queryStringParameters"]:    
            email_address = event["queryStringParameters"]["email_address"]
            deleteoptions = event["queryStringParameters"]["deleteoptions"]
            users_response_object = CSR_toolkit.get_list_of_users_from_email_address(email_address, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])

            logging.error(users_response_object) #debugging
            
            if not users_response_object[0]:
                logging.error("empty list, user doesn't exist or already deleted") #debugging
                responseObject["body"] = json.dumps("empty list, user doesn't exist or already deleted")
                return responseObject
            
            if deleteoptions == "deleteauth0":
                for user_row in users_response_object:
                    user_id = user_row[0]
                    identity_provider_sub_id = user_row[1]
                    deleteauth0_function_order(user_id, identity_provider_sub_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], auth0_client_id, auth0_client_secret)
                
            elif deleteoptions == "blockauth0":
                for user_row in users_response_object:
                    user_id = user_row[0]
                    identity_provider_sub_id = user_row[1]
                    blockauth0_function_order(user_id, identity_provider_sub_id, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], auth0_client_id, auth0_client_secret)
            
            else:
                responseObject["body"] = json.dumps("queryStringParameters: invalid deleteoptions param")
                responseObject["statusCode"] = 400
                return responseObject
                
            responseObject["body"] = json.dumps("deleted user")
            return responseObject

        else:
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject
