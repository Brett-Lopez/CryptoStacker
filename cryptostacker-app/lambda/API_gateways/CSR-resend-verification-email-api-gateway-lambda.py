import logging
import aws_functions_for_lambda
import json
import CSR_service_mesh_map
import CSR_toolkit
import auth0_lib
import sendgrid_lib

def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

    responseObject = {}
    responseObject["statusCode"] = 200
    responseObject["headers"] = {}
    responseObject["headers"]["Content-Type"] = "application/json" 
    logging.error(responseObject)

    logging.error("retrieve service mesh secret for API calls")
    service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF"))

    auth0_secret = eval(aws_functions_for_lambda.get_aws_secret("CSR-auth0-api-keys-2-tf"))
    auth0_client_id = auth0_secret["AUTH0_CLIENT_ID"]
    auth0_client_secret = auth0_secret["AUTH0_CLIENT_SECRET"]
    access_token = auth0_lib.get_bearer_token(auth0_client_id, auth0_client_secret)

    sendgrid_secret = eval(aws_functions_for_lambda.get_aws_secret("CSR-sendgrid_api_key-TF"))
    sendgrid_api_key = sendgrid_secret["SENDGRID_API_KEY"]

    #IF POST
    if event["httpMethod"] == "POST":
        logging.error("httpMethod: POST") #debugging
        if "email_address" in event["queryStringParameters"] and "identity_provider_sub_id" in event["queryStringParameters"]:
            email_address = event["queryStringParameters"]["email_address"]
            identity_provider_sub_id = event["queryStringParameters"]["identity_provider_sub_id"]
            #generate verification URL
            generate_verification_link_response = auth0_lib.generate_verification_link(identity_provider_sub_id, access_token)
            if "https" in generate_verification_link_response:
                #send verification link via sendgrid
                send_email_response = sendgrid_lib.send_an_http_verification_email(sendgrid_api_key, "support@cryptostacker.io", str(email_address), generate_verification_link_response)
                if "success" in send_email_response:
                    responseObject["body"] = json.dumps("success: new verification link sent")
                    return responseObject
                else:
                    responseObject["body"] = json.dumps("error: failed to send verification link")
                    responseObject["statusCode"] = 400
                    return responseObject
            else:
                responseObject["body"] = json.dumps("error: failed to generate verification link")
                responseObject["statusCode"] = 400
                return responseObject
        else:
            logging.error("queryStringParameters missing") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject
    