#pip install mysql-connector-python
#from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
import json
import CSR_service_mesh_map
import CSR_toolkit
import requests
from oauthlib.oauth2 import WebApplicationClient
from flask import request
import urllib.parse

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

    # OAuth 2 client setup for each identity provider
    auth0_client = WebApplicationClient(AUTH0_CLIENT_ID)

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    auth0_provider_cfg = get_auth0_provider_cfg()
    token_endpoint = auth0_provider_cfg["token_endpoint"]


    #IF GET
    if event["httpMethod"] == "GET":
        logging.error("httpMethod: GET") #debugging
        if "scope" in event["queryStringParameters"]:
            logging.error("required scope set") #debugging
            if event["queryStringParameters"]["scope"] == "warming":
                logging.error("scope: warming") #debugging
                responseObject["statusCode"] = 200
                responseObject["body"] = json.dumps("warming success")
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
            if event["queryStringParameters"]["scope"] == "token_response":
                logging.error("scope: token_response") #debugging
                if "request_url" and "request_base_url" and "code_auth0" in event["queryStringParameters"]:
                    request_url = event["queryStringParameters"]["request_url"]
                    request_base_url = event["queryStringParameters"]["request_base_url"]
                    code_auth0 = event["queryStringParameters"]["code_auth0"]

                    # Prepare and send a request to get tokens!
                    token_url, headers, body = auth0_client.prepare_token_request(
                        token_endpoint,
                        authorization_response=urllib.parse.unquote(request_url),
                        redirect_url=urllib.parse.unquote(request_base_url),
                        code=urllib.parse.unquote(code_auth0)
                    )

                    token_response = requests.post(
                        token_url,
                        headers=headers,
                        data=body,
                        auth=(AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET),
                    )

                    auth0_client.parse_request_body_response(json.dumps(token_response.json()))

                    userinfo_endpoint = auth0_provider_cfg["userinfo_endpoint"]
                    uri, headers, body = auth0_client.add_token(userinfo_endpoint)
                    userinfo_response = requests.get(uri, headers=headers, data=body)

                    responseObject["body"] = json.dumps(userinfo_response.json())
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

#POST - auth0 token response - working
#?scope=token_response&request_url=http&request_base_url=http&code_auth0=oijsfdgsfg


#=================================================================
