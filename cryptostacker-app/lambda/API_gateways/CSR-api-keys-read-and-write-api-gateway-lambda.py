#pip install mysql-connector-python
from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
import json
import datetime
import CSR_service_mesh_map
import CSR_toolkit

def get_api_keys(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, exchange):
    #http method GET
    logging.critical("get_api_keys() called") #debugging
    logging.error("exchange: %s" % exchange) #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            if exchange == "coinbase_pro":
                logging.error("coinbase_pro query") #debugging
                select_user_query = """
                SELECT *
                FROM coinbase_pro_api_keys
                WHERE user_id = %s
                """

            if exchange == "coinbase":
                logging.error("coinbase query") #debugging
                select_user_query = """
                SELECT *
                FROM coinbase_api_keys
                WHERE user_id = %s
                """

            if exchange == "kraken":
                logging.error("kraken query") #debugging
                select_user_query = """
                SELECT *
                FROM kraken_api_keys
                WHERE user_id = %s
                """

            if exchange == "bittrex":
                logging.error("bittrex query") #debugging
                select_user_query = """
                SELECT *
                FROM bittrex_api_keys
                WHERE user_id = %s
                """

            if exchange == "gemini":
                logging.error("gemini query") #debugging
                select_user_query = """
                SELECT *
                FROM gemini_api_keys
                WHERE user_id = %s
                """

            if exchange == "binance_us":
                logging.error("binance_us query") #debugging
                select_user_query = """
                SELECT *
                FROM binance_us_api_keys
                WHERE user_id = %s
                """

            if exchange == "crypto_com":
                logging.error("crypto_com query") #debugging
                select_user_query = """
                SELECT *
                FROM crypto_com_api_keys
                WHERE user_id = %s
                """

            if exchange == "ftx_us":
                logging.error("ftx_us query") #debugging
                select_user_query = """
                SELECT *
                FROM ftx_us_api_keys
                WHERE user_id = %s
                """

            select_user_tuple = (user_id, )

            #logging.error(select_user_query) #debugging
            #logging.error(select_user_tuple) #debugging

            logging.error("sql query begin")
            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchone() 
                #logging.error(sql_query_result) #debugging
        
        logging.error("sql query complete, returning")
        return sql_query_result

    except Error as e:
        logging.error(e)


def set_api_keys(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, exchange, api_key, api_secret, api_key_version, keys_created_time_epoch, keys_expiration_epoch, api_passphrase=None):
    KMS_KEY_ID = CSR_service_mesh_map.api_kms_key
    logging.critical("set_api_keys() called")
    logging.error("exchange: %s" % exchange) #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            if exchange == "coinbase_pro":
                insert_api_keys_query = """
                INSERT INTO coinbase_pro_api_keys
                (user_id,
                api_key_a,
                api_secret_a,
                api_passphrase_a, 
                api_key_a_version,
                api_key_b,
                api_secret_b,
                api_passphrase_b,
                api_key_b_version,
                keys_created_time_epoch,
                keys_expiration_epoch)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
                """

            if exchange == "coinbase":
                insert_api_keys_query = """
                INSERT INTO coinbase_api_keys
                (user_id,
                api_key_a,
                api_secret_a,
                api_passphrase_a, 
                api_key_a_version,
                api_key_b,
                api_secret_b,
                api_passphrase_b,
                api_key_b_version,
                keys_created_time_epoch,
                keys_expiration_epoch)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
                """

            if exchange == "kraken":
                insert_api_keys_query = """
                INSERT INTO kraken_api_keys
                (user_id,
                api_key_a,
                api_secret_a,
                api_key_a_version,
                api_key_b,
                api_secret_b,
                api_key_b_version,
                keys_created_time_epoch,
                keys_expiration_epoch)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )
                """

            if exchange == "bittrex":
                insert_api_keys_query = """
                INSERT INTO bittrex_api_keys
                (user_id,
                api_key_a,
                api_secret_a,
                api_key_a_version,
                api_key_b,
                api_secret_b,
                api_key_b_version,
                keys_created_time_epoch,
                keys_expiration_epoch)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )
                """

            if exchange == "gemini":
                insert_api_keys_query = """
                INSERT INTO gemini_api_keys
                (user_id,
                api_key_a,
                api_secret_a,
                api_key_a_version,
                api_key_b,
                api_secret_b,
                api_key_b_version,
                keys_created_time_epoch,
                keys_expiration_epoch)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )
                """

            if exchange == "binance_us":
                insert_api_keys_query = """
                INSERT INTO binance_us_api_keys
                (user_id,
                api_key_a,
                api_secret_a,
                api_key_a_version,
                api_key_b,
                api_secret_b,
                api_key_b_version,
                keys_created_time_epoch,
                keys_expiration_epoch)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )
                """

            if exchange == "crypto_com":
                insert_api_keys_query = """
                INSERT INTO crypto_com_api_keys
                (user_id,
                api_key_a,
                api_secret_a,
                api_key_a_version,
                api_key_b,
                api_secret_b,
                api_key_b_version,
                keys_created_time_epoch,
                keys_expiration_epoch)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )
                """

            if exchange == "ftx_us":
                insert_api_keys_query = """
                INSERT INTO ftx_us_api_keys
                (user_id,
                api_key_a,
                api_secret_a,
                api_key_a_version,
                api_key_b,
                api_secret_b,
                api_key_b_version,
                keys_created_time_epoch,
                keys_expiration_epoch)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )
                """
            
            #logging.error(insert_api_keys_query) #debugging
            if api_passphrase:
                api_key = aws_functions_for_lambda.encrypt_string_with_kms(api_key, KMS_KEY_ID) 
                api_secret = aws_functions_for_lambda.encrypt_string_with_kms(api_secret, KMS_KEY_ID) 
                api_passphrase = aws_functions_for_lambda.encrypt_string_with_kms(api_passphrase, KMS_KEY_ID) 
                api_records_tuple = (user_id, api_key, api_secret, api_passphrase, api_key_version, api_key, api_secret, api_passphrase, api_key_version, keys_created_time_epoch, keys_expiration_epoch, )
                #logging.error(api_records_tuple) #debugging
            elif not api_passphrase:
                api_key = aws_functions_for_lambda.encrypt_string_with_kms(api_key, KMS_KEY_ID) 
                api_secret = aws_functions_for_lambda.encrypt_string_with_kms(api_secret, KMS_KEY_ID) 
                api_records_tuple = (user_id, api_key, api_secret, api_key_version, api_key, api_secret, api_key_version, keys_created_time_epoch, keys_expiration_epoch, )
                #logging.error(api_records_tuple) #debugging

            with connection.cursor() as cursor:
                cursor.execute(insert_api_keys_query, api_records_tuple)
                connection.commit()
            
            logging.error("returning: success")
            return "success"

    except Error as e:
        logging.error(e)


def update_api_keys(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, exchange, api_key, api_secret, api_key_version, keys_created_time_epoch, keys_expiration_epoch, api_passphrase=None):
    logging.critical("update_api_keys() called")
    logging.error("exchange: %s" % exchange) #debugging
    #different KMS key on each end?
    KMS_KEY_ID = CSR_service_mesh_map.api_kms_key
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging
            
            if exchange == "coinbase_pro":
                update_api_keys_query = """
                UPDATE coinbase_pro_api_keys
                SET api_key_a = %s,
                api_secret_a = %s,
                api_passphrase_a = %s,
                api_key_a_version = %s,
                api_key_b = %s,
                api_secret_b = %s,
                api_passphrase_b = %s,
                api_key_b_version = %s,
                keys_created_time_epoch = %s,
                keys_expiration_epoch = %s
                WHERE user_id = %s
                """

            if exchange == "coinbase":
                update_api_keys_query = """
                UPDATE coinbase_api_keys
                SET api_key_a = %s,
                api_secret_a = %s,
                api_passphrase_a = %s,
                api_key_a_version = %s,
                api_key_b = %s,
                api_secret_b = %s,
                api_passphrase_b = %s,
                api_key_b_version = %s,
                keys_created_time_epoch = %s,
                keys_expiration_epoch = %s
                WHERE user_id = %s
                """

            if exchange == "kraken":
                update_api_keys_query = """
                UPDATE kraken_api_keys
                SET api_key_a = %s,
                api_secret_a = %s,
                api_key_a_version = %s,
                api_key_b = %s,
                api_secret_b = %s,
                api_key_b_version = %s,
                keys_created_time_epoch = %s,
                keys_expiration_epoch = %s
                WHERE user_id = %s
                """

            if exchange == "bittrex":
                update_api_keys_query = """
                UPDATE bittrex_api_keys
                SET api_key_a = %s,
                api_secret_a = %s,
                api_key_a_version = %s,
                api_key_b = %s,
                api_secret_b = %s,
                api_key_b_version = %s,
                keys_created_time_epoch = %s,
                keys_expiration_epoch = %s
                WHERE user_id = %s
                """

            if exchange == "gemini":
                update_api_keys_query = """
                UPDATE gemini_api_keys
                SET api_key_a = %s,
                api_secret_a = %s,
                api_key_a_version = %s,
                api_key_b = %s,
                api_secret_b = %s,
                api_key_b_version = %s,
                keys_created_time_epoch = %s,
                keys_expiration_epoch = %s
                WHERE user_id = %s
                """

            if exchange == "binance_us":
                update_api_keys_query = """
                UPDATE binance_us_api_keys
                SET api_key_a = %s,
                api_secret_a = %s,
                api_key_a_version = %s,
                api_key_b = %s,
                api_secret_b = %s,
                api_key_b_version = %s,
                keys_created_time_epoch = %s,
                keys_expiration_epoch = %s
                WHERE user_id = %s
                """

            if exchange == "crypto_com":
                update_api_keys_query = """
                UPDATE crypto_com_api_keys
                SET api_key_a = %s,
                api_secret_a = %s,
                api_key_a_version = %s,
                api_key_b = %s,
                api_secret_b = %s,
                api_key_b_version = %s,
                keys_created_time_epoch = %s,
                keys_expiration_epoch = %s
                WHERE user_id = %s
                """

            if exchange == "ftx_us":
                update_api_keys_query = """
                UPDATE ftx_us_api_keys
                SET api_key_a = %s,
                api_secret_a = %s,
                api_key_a_version = %s,
                api_key_b = %s,
                api_secret_b = %s,
                api_key_b_version = %s,
                keys_created_time_epoch = %s,
                keys_expiration_epoch = %s
                WHERE user_id = %s
                """

            #logging.error(update_api_keys_query) #debugging
            if api_passphrase:
                api_key = aws_functions_for_lambda.encrypt_string_with_kms(api_key, KMS_KEY_ID) 
                api_secret = aws_functions_for_lambda.encrypt_string_with_kms(api_secret, KMS_KEY_ID) 
                api_passphrase = aws_functions_for_lambda.encrypt_string_with_kms(api_passphrase, KMS_KEY_ID) 
                api_keys_record_tuple = (api_key, api_secret, api_passphrase, api_key_version, api_key, api_secret, api_passphrase, api_key_version, keys_created_time_epoch, keys_expiration_epoch, user_id, )
                #logging.error(api_keys_record_tuple) #debugging
            elif not api_passphrase:
                api_key = aws_functions_for_lambda.encrypt_string_with_kms(api_key, KMS_KEY_ID) 
                api_secret = aws_functions_for_lambda.encrypt_string_with_kms(api_secret, KMS_KEY_ID) 
                api_keys_record_tuple = (api_key, api_secret, api_key_version, api_key, api_secret, api_key_version, keys_created_time_epoch, keys_expiration_epoch, user_id, )
                #logging.error(api_keys_record_tuple) #debugging

            with connection.cursor() as cursor:
                cursor.execute(update_api_keys_query, api_keys_record_tuple)
                connection.commit()
            
            logging.error("update_api_keys returning success")
            return "success"

    except Error as e:
        logging.error(e)


def delete_api_keys(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, exchange):
    logging.critical("delete_api_keys() called")
    logging.error("exchange: %s" % exchange) #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging
            
            if exchange == "coinbase_pro":
                delete_api_keys_query = """
                Delete
                FROM coinbase_pro_api_keys
                WHERE user_id = %s
                """

            if exchange == "coinbase":
                delete_api_keys_query = """
                Delete
                FROM coinbase_api_keys
                WHERE user_id = %s
                """

            if exchange == "kraken":
                delete_api_keys_query = """
                Delete
                FROM kraken_api_keys
                WHERE user_id = %s
                """

            if exchange == "bittrex":
                delete_api_keys_query = """
                Delete
                FROM bittrex_api_keys
                WHERE user_id = %s
                """

            if exchange == "gemini":
                delete_api_keys_query = """
                Delete
                FROM gemini_api_keys
                WHERE user_id = %s
                """

            if exchange == "binance_us":
                delete_api_keys_query = """
                Delete
                FROM binance_us_api_keys
                WHERE user_id = %s
                """

            if exchange == "crypto_com":
                delete_api_keys_query = """
                Delete
                FROM crypto_com_api_keys
                WHERE user_id = %s
                """

            if exchange == "ftx_us":
                delete_api_keys_query = """
                Delete
                FROM ftx_us_api_keys
                WHERE user_id = %s
                """

            api_keys_record = (user_id, )

            with connection.cursor() as cursor:
                cursor.execute(delete_api_keys_query, api_keys_record)
                connection.commit()

            logging.error("returning: success")
            return "success"

    except Error as e:
        logging.error(e)


def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)

    responseObject = {}
    responseObject["statusCode"] = 200
    responseObject["headers"] = {}
    responseObject["headers"]["Content-Type"] = "application/json" 
    logging.error(responseObject)

    logging.error("retrieve RDS secrets")
    RDS_secret_return = aws_functions_for_lambda.get_aws_secret("CSR-primary-serverless-db-2-tf")
    RDS_secret_dict = eval(RDS_secret_return)
    RDS_secret_user = RDS_secret_dict["username"]
    RDS_secret_pass = RDS_secret_dict["password"]
    RDS_secret_host = RDS_secret_dict["host"]

    logging.error("retrieve service mesh secret for API calls")
    service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF"))

    #IF GET
    if event["httpMethod"] == "GET":
        logging.error("httpMethod: GET") #debugging
        #user_id, exchange
        if "user_id" in event["queryStringParameters"] and "exchange" in event["queryStringParameters"]:
            if event["queryStringParameters"]["exchange"] in CSR_toolkit.supported_exchanges_list:
                logging.error("all params provided") #debugging
                user_id = event["queryStringParameters"]["user_id"]
                exchange = event["queryStringParameters"]["exchange"]
                logging.error("exchange: %s" % exchange) #debugging
                sql_query_result = get_api_keys(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, exchange)
                if not sql_query_result:
                    logging.error("Returning: []") #debugging
                    responseObject["body"] = json.dumps("[]")
                    return responseObject

                logging.error("Returning: SQL result") #debugging
                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject
            
            else:
                responseObject["body"] = json.dumps("error: incorrect exchange")
                return responseObject

    #IF POST
    if event["httpMethod"] == "POST":
        logging.error("httpMethod: POST") #debugging
        if "user_id" in event["queryStringParameters"] and "exchange" in event["queryStringParameters"] and "api_key" in event["queryStringParameters"] and "api_secret" in event["queryStringParameters"] and "keys_expiration_epoch" in event["queryStringParameters"] and "delete" not in event["queryStringParameters"]:
            if event["queryStringParameters"]["exchange"] in CSR_toolkit.supported_exchanges_list:
                logging.error("all params provided") #debugging
                user_id = event["queryStringParameters"]["user_id"] #define variable to be passed to SQL query
                exchange = event["queryStringParameters"]["exchange"] #define variable to be passed to SQL query
                logging.error("exchange: %s" % exchange) #debugging
                api_key_a = event["queryStringParameters"]["api_key"] #define variable to be passed to SQL query
                api_secret_a = event["queryStringParameters"]["api_secret"] #define variable to be passed to SQL query
                keys_expiration_epoch = event["queryStringParameters"]["keys_expiration_epoch"] #define variable to be passed to SQL query
                api_key_a_version = "latest" #define variable to be passed to SQL query
                if "api_passphrase" in event["queryStringParameters"]:
                    api_passphrase = event["queryStringParameters"]["api_passphrase"] #define variable to be passed to SQL query
                elif "api_passphrase" not in event["queryStringParameters"]:
                    api_passphrase = None #define variable to be passed to SQL query
                
                datetime_now_object = datetime.datetime.now()
                datetime_now_object_epoch = datetime_now_object.strftime('%s')
                keys_created_time_epoch = str(datetime_now_object_epoch) #define variable to be passed to SQL query
                
                #create result object to check to see if user already exists
                logging.error("check if user exists")
                get_api_keys_result = get_api_keys(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, exchange)

                #if user already exists, update user
                if get_api_keys_result:
                    logging.error("api key already exists, update api key") #debugging
                    update_api_keys_result = update_api_keys(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, exchange, api_key_a, api_secret_a, api_key_a_version, keys_created_time_epoch, keys_expiration_epoch, api_passphrase=api_passphrase)
                    
                    #UPDATE API KEY METADATA
                    set_api_keys_metadata_response = CSR_toolkit.set_api_keys_metadata(user_id, exchange, keys_expiration_epoch, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    if update_api_keys_result == "success":
                        logging.error("success, api key already exists, updated api key") #debugging
                        responseObject["body"] = json.dumps("api key already exists, api key updated - metadata response: %s" % set_api_keys_metadata_response)
                        return responseObject
                    else:
                        logging.error("error, api key already exists, error updating api key") #debugging
                        responseObject["statusCode"] = 409
                        responseObject["body"] = json.dumps("error: api key already exists, error updating api key - metadata response: %s" % set_api_keys_metadata_response)
                        return responseObject

                #if api doesn't already exist, create api
                if not get_api_keys_result:
                    logging.error("api key doesn't exist, create api key") #debugging
                    set_api_keys_result = set_api_keys(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, exchange, api_key_a, api_secret_a, api_key_a_version, keys_created_time_epoch, keys_expiration_epoch, api_passphrase=api_passphrase)
                    
                    #SET API KEY METADATA
                    set_api_keys_metadata_response = CSR_toolkit.set_api_keys_metadata(user_id, exchange, keys_expiration_epoch, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    if set_api_keys_result == "success":
                        logging.error("success, api key metadata didn't already exist, api key metadata created") #debugging
                        responseObject["body"] = json.dumps("api key didn't already exist, api key created - metadata response: %s" % set_api_keys_metadata_response)
                        return responseObject
                    else:
                        logging.error("error, api key metadata didn't already exist, error creating api key metadata") #debugging
                        responseObject["statusCode"] = 409
                        responseObject["body"] = json.dumps("error: api key didn't already exist, error creating api key - metadata response: %s" % set_api_keys_metadata_response)
                        return responseObject
            else:
                logging.error("returning: error: incorrect exchange")
                responseObject["body"] = json.dumps("error: incorrect exchange")
                return responseObject
        
        #if contains delete
        if "user_id" in event["queryStringParameters"] and "exchange" in event["queryStringParameters"] and "delete" in event["queryStringParameters"]:
            if event["queryStringParameters"]["exchange"] in CSR_toolkit.supported_exchanges_list:
                if event["queryStringParameters"]["delete"] == "delete":
                    user_id = event["queryStringParameters"]["user_id"]
                    exchange = event["queryStringParameters"]["exchange"]
                    delete_api_keys_result = delete_api_keys(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, exchange)
                    
                    #DELETE API KEY METADATA
                    delete_api_keys_metadata_response = CSR_toolkit.delete_api_keys_metadata(user_id, exchange, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"])
                    if delete_api_keys_result == "success":
                        logging.error("returning: success")
                        responseObject["body"] = json.dumps("row deleted - metadata response: %s" % delete_api_keys_metadata_response)
                        return responseObject
                    else:
                        logging.error("returning: error: Row not deleted")
                        responseObject["body"] = json.dumps("error: Row not deleted - metadata response: %s" % delete_api_keys_metadata_response)
                        return responseObject
            else:
                logging.error("returning: error: incorrect exchange")
                responseObject["body"] = json.dumps("error: incorrect exchange")
                return responseObject
        
####################################
##### QUERY PARAMS FOR TESTING #####
####################################

# http method GET
#
# user_id 
# exchange
# /prod/api-keys-read-write?user_id=5&exchange=coinbase_pro

# http method POST
#
# create new user
# user_id
# exchange
# api_key
# api_secret
# keys_expiration_epoch

## COINBASE & COINBASE PRO:
# /prod/api-keys-read-write?user_id=5&exchange=coinbase_pro&api_key=api_key_12345&api_secret=api_secret_12345&api_passphrase=api_passphrase_12345&keys_expiration_epoch=0

## OTHER EXCHANGES:
# /prod/api-keys-read-write?user_id=5&exchange=kraken&api_key=api_key_12345&api_secret=api_secret_12345&keys_expiration_epoch=0

# http method POST
# delete user
#
# user_id
# exchange
# delete=delete
# /prod/api-keys-read-write?user_id=5&exchange=coinbase_pro&delete=delete
