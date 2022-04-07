#pip install mysql-connector-python
from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
import json
import CSR_service_mesh_map
import CSR_toolkit

def get_all_prices(RDS_secret_host, RDS_secret_user, RDS_secret_pass):
    #http method GET
    logging.critical("get_all_prices() called") #debugging
    limit_max = 200
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_pricing_tier_query = """
            SELECT *
            FROM pricing_tier
            """

            with connection.cursor() as cursor:
                cursor.execute(select_pricing_tier_query)
                sql_query_result = cursor.fetchmany(size=limit_max)
                #logging.error(sql_query_result) #debugging

        return sql_query_result

    except Error as e:
        print(e)


def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

    responseObject = {}
    responseObject["statusCode"] = 200
    responseObject["headers"] = {}
    responseObject["headers"]["Content-Type"] = "application/json" 
    #print(responseObject) #debugging

    logging.error("retrieve RDS secrets")
    RDS_secret_return = aws_functions_for_lambda.get_aws_secret("CSR-primary-serverless-db-1-tf")
    RDS_secret_dict = eval(RDS_secret_return)
    RDS_secret_user = RDS_secret_dict["username"]
    RDS_secret_pass = RDS_secret_dict["password"]
    RDS_secret_host = RDS_secret_dict["host"]
    if RDS_secret_host: #debugging
        logging.error("RDS host set") #debugging
        logging.error(RDS_secret_host) #debugging

    #IF GET
    if event["httpMethod"] == "GET":
        logging.error("httpMethod: GET") #debugging
        if "scope" in event["queryStringParameters"]:
            logging.error("scope provided") #debugging
            
            if event["queryStringParameters"]["scope"] == "allprices":
                logging.error("scope: allprices") #debugging
                sql_query_result = get_all_prices(RDS_secret_host, RDS_secret_user, RDS_secret_pass)
                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject
        
        else:          
            logging.error("queryStringParameters missing") #debugging
            responseObject["statusCode"] = 400
            responseObject["body"] = json.dumps("queryStringParameters missing")
            return responseObject


#########################
##### query params ######
#########################

#GET - 
#?scope=allprices
