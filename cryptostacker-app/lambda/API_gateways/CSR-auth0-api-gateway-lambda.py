#pip install mysql-connector-python
#from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
import json
import CSR_service_mesh_map
import CSR_toolkit
import requests
import urllib.parse
import auth0_lib

def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)
    
    # Endpoint discovery
    def get_auth0_provider_cfg():
        return requests.get(AUTH0_DISCOVERY_URL).json()

    responseObject = {}
    responseObject["statusCode"] = 200
    responseObject["headers"] = {}
    responseObject["headers"]["Content-Type"] = "application/json" 
    #print(responseObject) #debugging

    logging.error("retrieve auth0_secret")
    auth0_secret = eval(aws_functions_for_lambda.get_aws_secret("CSR-auth0-api-keys-2-tf"))
    # AUTH0 oauth2.0 Configuration
    AUTH0_CLIENT_ID = auth0_secret["AUTH0_CLIENT_ID"]
    AUTH0_CLIENT_SECRET = auth0_secret["AUTH0_CLIENT_SECRET"]
    AUTH0_DISCOVERY_URL = auth0_secret["AUTH0_DISCOVERY_URL"]

    #IF GET
    if event["httpMethod"] == "GET":
        logging.error("httpMethod: GET") #debugging
        if "scope" in event["queryStringParameters"]:
            logging.error("required scope set") #debugging
            if event["queryStringParameters"]["scope"] == "warming":
                logging.error("scope: get_failed_dca_counter_row") #debugging
                responseObject["statusCode"] = 200
                responseObject["body"] = json.dumps("warming success!")
                return responseObject

            else:
                logging.error("queryStringParameters missing 1") #debugging
                responseObject["statusCode"] = 400
                responseObject["body"] = json.dumps("queryStringParameters missing")
                return responseObject
        else:
            logging.error("queryStringParameters missing 2") #debugging
            responseObject["statusCode"] = 400
            responseObject["body"] = json.dumps("queryStringParameters missing")
            return responseObject

    #IF POST
    if event["httpMethod"] == "POST":
        logging.error("httpMethod: POST") #debugging
        if "scope" in event["queryStringParameters"]:
            if event["queryStringParameters"]["scope"] == "reset_mfa":
                logging.error("scope: reset_mfa") #debugging
                if "identity_provider_sub_id" in event["queryStringParameters"]:
                    identity_provider_sub_id = urllib.parse.unquote(event["queryStringParameters"]["identity_provider_sub_id"])

                    access_token = auth0_lib.get_bearer_token(AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET)
                    reset_resposne = auth0_lib.reset_google_mfa(identity_provider_sub_id, access_token)

                    responseObject["body"] = json.dumps(reset_resposne)
                    return responseObject

                else:
                    logging.error("queryStringParameters missing 1") #debugging
                    responseObject["body"] = json.dumps("queryStringParameters missing 1")
                    responseObject["statusCode"] = 400
                    return responseObject
            
            else:
                logging.error("scope missing 1") #debugging
                responseObject["body"] = json.dumps("scope missing 1")
                responseObject["statusCode"] = 400
                return responseObject
        else:
            logging.error("scope missing 2") #debugging
            responseObject["body"] = json.dumps("scope missing 2")
            responseObject["statusCode"] = 400
            return responseObject

    #IF DELETE
    if event["httpMethod"] == "DELETE":
        logging.error("httpMethod: DELETE") #debugging
        if "user_id" in event["queryStringParameters"]:
            user_id = event["queryStringParameters"]["user_id"]
            sql_query_result = ""
            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject
        else:
            logging.error("queryStringParameters missing") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject


#########################
##### query params ######
#########################

#POST - 
#?scope=reset_mfa&identity_provider_sub_id=auth0|uthe


#=================================================================
