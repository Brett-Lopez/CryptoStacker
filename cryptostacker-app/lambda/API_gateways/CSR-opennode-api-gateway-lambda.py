import logging
import aws_functions_for_lambda
import json
import CSR_service_mesh_map
import CSR_toolkit
import requests
import urllib.parse
import opennode_lib

def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)
    
    responseObject = {}
    responseObject["statusCode"] = 200
    responseObject["headers"] = {}
    responseObject["headers"]["Content-Type"] = "application/json" 
    #print(responseObject) #debugging

    logging.error("retrieve opennode secret")
    opennode_api_key = eval(aws_functions_for_lambda.get_aws_secret("CSR-opennode_api_key-TF"))

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
            if event["queryStringParameters"]["scope"] == "create_charge":
                logging.error("scope: token_response") #debugging
                if "dollar_amount" and "fiat_denomination" and "email_address" and "description" in event["queryStringParameters"]:
                    dollar_amount = int(event["queryStringParameters"]["dollar_amount"])
                    fiat_denomination = event["queryStringParameters"]["fiat_denomination"]
                    email_address = event["queryStringParameters"]["email_address"]
                    description = urllib.parse.unquote(event["queryStringParameters"]["description"])

                    charge_response = opennode_lib.create_charge(opennode_api_key["api_key"], dollar_amount, fiat_denomination, email_address, description)

                    responseObject["statusCode"] = 200
                    responseObject["body"] = json.dumps(charge_response)
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
            sql_query_result = "delete_row_by_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)"
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
#?scope=create_charge&dollar_amount=10&fiat_denomination=USD&email_address=brettlopez639@gmail.com&description=TESTING123
