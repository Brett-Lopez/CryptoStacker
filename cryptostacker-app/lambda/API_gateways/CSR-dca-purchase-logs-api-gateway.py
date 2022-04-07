#pip install mysql-connector-python
from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
#import mysql.connector
import json
import datetime
import CSR_service_mesh_map
import CSR_toolkit

def TopOfNextHour(datatimeobject):
    logging.critical("TopOfNextHour() called") #debugging
    """
    Pass a datatime object as an argument to return the top of the following hour.  
    If you want to run a particular function at or after the top of an/every hour this function will be useful for determining that time.
    """
    current_plus_one = (datatimeobject.hour + 1) % 24
    return datatimeobject.replace(hour=current_plus_one, minute=00, second=00, microsecond=00)

def set_dca_purchase_log(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, epoch_time, was_successful, coin_purchased, fiat_amount, fiat_denomination, exchange_used, interval_time_in_seconds, high_availability_type, exchange_order_id, failure_reason):
    logging.critical("set_dca_purchase_log() called") #debugging
    #POST
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            insert_dca_purchase_log_query = """
            INSERT INTO dca_purchase_logs
            (user_id,
            epoch_time,
            was_successful,
            coin_purchased,
            fiat_amount,
            fiat_denomination,
            exchange_used,
            interval_time_in_seconds,
            high_availability_type,
            exchange_order_id,
            failure_reason)
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
            """
            
            execute_variables_tuple = (int(user_id), int(epoch_time), str(was_successful), str(coin_purchased), int(fiat_amount), str(fiat_denomination), str(exchange_used), int(interval_time_in_seconds), str(high_availability_type), str(exchange_order_id), str(failure_reason), )

            with connection.cursor() as cursor:
                cursor.execute(insert_dca_purchase_log_query, execute_variables_tuple)
                connection.commit()
            return "success"

    except Error as e:
        print(e)
        return "error"

def delete_dca_purchase_log_deleteoneusertime(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, epoch_time):
    #http method POST
    logging.critical("delete_dca_purchase_log_deleteoneusertime called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            delete_row_query = """
            Delete
            FROM dca_purchase_logs
            WHERE user_id = %s AND epoch_time < %s
            """

            select_user_tuple = (int(user_id), int(epoch_time), )

            with connection.cursor() as cursor:
                cursor.execute(delete_row_query, select_user_tuple)
                connection.commit()
                logging.error("Row Deleted") #debugging

        return "Rows deleted"

    except Error as e:
        print(e)
        return "error"

def delete_dca_purchase_log_deletemultiusertime(RDS_secret_host, RDS_secret_user, RDS_secret_pass, epoch_time):
    #http method POST
    logging.critical("delete_dca_purchase_log_deletemultiusertime() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            delete_row_query = """
            Delete
            FROM dca_purchase_logs
            WHERE epoch_time < %s
            """

            select_user_tuple = (int(epoch_time), )

            with connection.cursor() as cursor:
                cursor.execute(delete_row_query, select_user_tuple)
                connection.commit()
                logging.error("Row Deleted") #debugging

        return "Rows deleted"

    except Error as e:
        print(e)
        return "error"

def delete_dca_purchase_log_deleteoneuserall(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    #http method POST
    logging.critical("delete_dca_purchase_log_deleteoneuserall() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            delete_row_query = """
            Delete
            FROM dca_purchase_logs
            WHERE user_id = %s
            """

            select_user_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(delete_row_query, select_user_tuple)
                connection.commit()
                logging.error("Row Deleted") #debugging

        return "Rows deleted"

    except Error as e:
        print(e)
        return "error"

def get_dca_purchase_log(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, limit, was_successful, coin_purchased, exchange_used):
    #http method GET
    logging.critical("get_dca_purchase_log() called") #debugging
    limit_max = 200
    limit = int(limit)
    if limit >= limit_max:
        limit = int(limit_max)
    logging.error("limit: %s" % str(limit)) #debugging

    if was_successful == "all":
        was_successful = "%"
    elif was_successful == "success":
        was_successful = "True"
    elif was_successful == "failed":
        was_successful = "False"
    else:
        was_successful = "%"

    if coin_purchased == "all":
        coin_purchased = "%"
    elif coin_purchased == "btc":
        coin_purchased = "btc"
    elif coin_purchased == "eth":
        coin_purchased = "eth"
    elif coin_purchased == "ltc":
        coin_purchased = "ltc"
    else:
        coin_purchased = "%"

    if exchange_used == "all":
        exchange_used = "%"
    elif exchange_used == "coinbase_pro":
        exchange_used = "coinbase_pro"
    elif exchange_used == "bittrex":
        exchange_used = "bittrex"
    elif exchange_used == "kraken":
        exchange_used = "kraken"
    elif exchange_used == "binance_us":
        exchange_used = "binance_us"
    elif exchange_used == "gemini":
        exchange_used = "gemini"
    elif exchange_used == "ftx_us":
        exchange_used = "ftx_us"
    else:
        exchange_used = "%"
    
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_dca_purchase_logs_query = """
            SELECT *
            FROM dca_purchase_logs
            WHERE user_id = %s AND was_successful like %s AND coin_purchased like %s AND exchange_used like %s
            ORDER BY id DESC
            LIMIT %s
            """

            select_user_tuple = (int(user_id), str(was_successful), str(coin_purchased), str(exchange_used), int(limit), )

            debug_select_user_tuple = (str(user_id), str(was_successful), str(coin_purchased), str(exchange_used), str(limit), )

            with connection.cursor() as cursor:
                cursor.execute(select_dca_purchase_logs_query, select_user_tuple)
                sql_query_result = cursor.fetchmany(size=limit_max)

        return sql_query_result

    except Error as e:
        print(e)

def get_dca_purchase_log_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, limit, after_id):
    #http method GET
    logging.critical("get_dca_purchase_log_paginated() called") #debugging
    limit_max = 200
    limit = int(limit)
    if limit >= limit_max:
        limit = int(limit_max)

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_dca_purchase_logs_query = """
            SELECT *
            FROM dca_purchase_logs
            WHERE user_id = %s AND id < %s
            ORDER BY id DESC
            LIMIT %s
            """
            
            select_user_tuple = (int(user_id), int(after_id), int(limit), )

            with connection.cursor() as cursor:
                cursor.execute(select_dca_purchase_logs_query, select_user_tuple)
                sql_query_result = cursor.fetchmany(size=limit_max)

        return sql_query_result

    except Error as e:
        print(e)

def count_unique_user_ids_rolling_30_days(RDS_secret_host, RDS_secret_user, RDS_secret_pass):
    logging.critical("count_unique_user_ids_rolling_30_days()")
    date_time_object_now = datetime.datetime.now()
    rolling_30_days_datetime = CSR_toolkit.datetime_plus_days(date_time_object_now, -30)
    rolling_30_days_epoch = int(rolling_30_days_datetime.strftime('%s'))

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_query = """
            SELECT COUNT(DISTINCT user_id) unique_users
            FROM dca_purchase_logs
            WHERE epoch_time >= %s
            """

            select_tuple = (int(rolling_30_days_epoch), )

            with connection.cursor() as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchone()
                logging.error(sql_query_result) #debugging
        
        if sql_query_result[0] == None: #if None return empty list
            sql_query_result = []
            return sql_query_result
        elif isinstance(sql_query_result[0], type(None)): #if None return empty list
            sql_query_result = []
            return sql_query_result
        else:
            try:
                return [int(float(sql_query_result[0]))]
            except:
                return sql_query_result

    except Error as e:
        print(e)

def lambda_handler(event, context):
    #configure logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s', level=CSR_toolkit.logging_level_var)

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

    #IF GET
    if event["httpMethod"] == "GET":
        logging.error("httpMethod: GET") #debugging
        
        if "scope" in event["queryStringParameters"]:
            logging.error("queryStringParameters scope") #debugging
            if event["queryStringParameters"]["scope"] == "count_unique_user_ids_rolling_30_days":
                logging.error("scope: count_unique_user_ids_rolling_30_days") #debugging
                sql_query_result = count_unique_user_ids_rolling_30_days(RDS_secret_host, RDS_secret_user, RDS_secret_pass)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            else:
                responseObject["statusCode"] = 400
                logging.error("queryStringParameters missing - incorrect scope") #debugging
                responseObject["body"] = json.dumps("queryStringParameters missing - incorrect scope")
                return responseObject

        elif "user_id" in event["queryStringParameters"] and "limit" in event["queryStringParameters"] and "was_successful" in event["queryStringParameters"] and "coin_purchased" in event["queryStringParameters"] and "exchange_used" in event["queryStringParameters"] and "after_id" not in event["queryStringParameters"]:
            logging.error("required queryStringParameters set") #debugging
            logging.error("query of a list of DCA logs WITHOUT pagination") #debugging
            user_id = event["queryStringParameters"]["user_id"]
            limit = event["queryStringParameters"]["limit"]
            was_successful = event["queryStringParameters"]["was_successful"]
            coin_purchased = event["queryStringParameters"]["coin_purchased"]
            exchange_used = event["queryStringParameters"]["exchange_used"]

            sql_query_result = get_dca_purchase_log(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, limit, was_successful, coin_purchased, exchange_used)
            logging.debug(sql_query_result) #debugging
            if not sql_query_result:
                logging.error("returning empty list") #debugging
                responseObject["body"] = json.dumps("[]")
                return responseObject

            responseObject["body"] = json.dumps(sql_query_result)
            logging.error("returning list of results") #debugging
            return responseObject
    
        elif "user_id" in event["queryStringParameters"] and "limit" in event["queryStringParameters"] and "after_id" in event["queryStringParameters"]:
            logging.error("required queryStringParameters set") #debugging
            logging.error("query of a list of DCA logs WITH pagination") #debugging
            logging.error(event["queryStringParameters"]) #debugging
            user_id = event["queryStringParameters"]["user_id"]
            limit = event["queryStringParameters"]["limit"]
            after_id = event["queryStringParameters"]["after_id"]

            sql_query_result = get_dca_purchase_log_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, limit, after_id)
            logging.debug(sql_query_result) #debugging
            if not sql_query_result:
                logging.error("returning empty list") #debugging
                responseObject["body"] = json.dumps("[]") #return empty list
                return responseObject

            responseObject["body"] = json.dumps(sql_query_result)
            logging.error("returning list of results") #debugging
            return responseObject

        else:
            responseObject["statusCode"] = 400
            logging.error("queryStringParameters missing") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            return responseObject

    #IF POST
    elif event["httpMethod"] == "POST":
        logging.error("httpMethod: POST") #debugging
        if "user_id" in event["queryStringParameters"] and "epoch_time" in event["queryStringParameters"] and "was_successful" in event["queryStringParameters"] and "coin_purchased" in event["queryStringParameters"] and "fiat_amount" in event["queryStringParameters"] and "fiat_denomination" in event["queryStringParameters"] and "exchange_used" in event["queryStringParameters"] and "interval_time_in_seconds" in event["queryStringParameters"] and "high_availability_type" in event["queryStringParameters"] and "exchange_order_id" in event["queryStringParameters"] and "failure_reason" in event["queryStringParameters"] and "delete" not in event["queryStringParameters"]:
            logging.error("POST if") #debugging
            user_id = event["queryStringParameters"]["user_id"]
            epoch_time = event["queryStringParameters"]["epoch_time"]
            was_successful = event["queryStringParameters"]["was_successful"]
            coin_purchased = event["queryStringParameters"]["coin_purchased"]
            fiat_amount = event["queryStringParameters"]["fiat_amount"]
            fiat_denomination = event["queryStringParameters"]["fiat_denomination"]
            exchange_used = event["queryStringParameters"]["exchange_used"]
            interval_time_in_seconds = event["queryStringParameters"]["interval_time_in_seconds"]
            high_availability_type = event["queryStringParameters"]["high_availability_type"]
            exchange_order_id = event["queryStringParameters"]["exchange_order_id"]
            failure_reason = event["queryStringParameters"]["failure_reason"]
            
            set_dca_purchase_log_result = set_dca_purchase_log(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, epoch_time, was_successful, coin_purchased, fiat_amount, fiat_denomination, exchange_used, interval_time_in_seconds, high_availability_type, exchange_order_id, failure_reason)
            if set_dca_purchase_log_result == "success":
                logging.error("dca purchase log event created successfully")
                responseObject["body"] = json.dumps("dca purchase log event created successfully")
                return responseObject

        else:
            logging.error("POST else: queryStringParameters missing") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject
    
    #IF DELETE
    elif event["httpMethod"] == "DELETE":
        logging.error("httpMethod: DELETE") #debugging
        if "delete" in event["queryStringParameters"]:
            logging.error("delete in queryStringParameters") #debugging
            
            if "deleteoneusertime" == event["queryStringParameters"]["delete"]: #delete multiple events from a single user older than passed epoch time
                if "user_id" in event["queryStringParameters"] and "epoch_time" in event["queryStringParameters"]:
                    user_id = event["queryStringParameters"]["user_id"]
                    epoch_time = event["queryStringParameters"]["epoch_time"]
                    delete_result = delete_dca_purchase_log_deleteoneusertime(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, epoch_time)
                    responseObject["body"] = json.dumps(delete_result)
                    return responseObject
                else:
                    logging.error("POST else: queryStringParameters missing") #debugging
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    responseObject["statusCode"] = 400
                    return responseObject

            elif "deletemultiusertime" == event["queryStringParameters"]["delete"]: #delete multiple users events older than passed epoch time
                if "epoch_time" in event["queryStringParameters"]:
                    epoch_time = event["queryStringParameters"]["epoch_time"]
                    delete_result = delete_dca_purchase_log_deletemultiusertime(RDS_secret_host, RDS_secret_user, RDS_secret_pass, epoch_time)
                    responseObject["body"] = json.dumps(delete_result)
                    return responseObject
                else:
                    logging.error("POST else: queryStringParameters missing") #debugging
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    responseObject["statusCode"] = 400
                    return responseObject

            elif "deleteoneuserall" == event["queryStringParameters"]["delete"]: #delete all rows for a single user
                if "user_id" in event["queryStringParameters"]:
                    user_id = event["queryStringParameters"]["user_id"]
                    delete_result = delete_dca_purchase_log_deleteoneuserall(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
                    responseObject["body"] = json.dumps(delete_result)
                    return responseObject
                else:
                    logging.error("POST else: queryStringParameters missing") #debugging
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    responseObject["statusCode"] = 400
                    return responseObject

    else:
        logging.error("queryStringParameters missing - httpmethod") #debugging
        responseObject["body"] = json.dumps("queryStringParameters missing - httpmethod")
        responseObject["statusCode"] = 400
        return responseObject


#########################
### test query params ###
#########################

#GET - dca logs without after_id
#?user_id=50&limit=100&was_successful=all&coin_purchased=all&exchange_used=all
#&was_successful=all, "success", "failed"
#&coin_purchased=all, "btc", "eth", "ltc"
#&exchange_used=all, 'coinbase_pro', 'bittrex', 'kraken', 'binance_us', 'gemini', 'ftx_us'

#GET - dca logs with after_id
#?user_id=50&limit=100&after_id=50000

#GET - count unique user IDs in DCA logs rolling 30 days
#?scope=count_unique_user_ids_rolling_30_days

#POST - create dca log
#?user_id=1&epoch_time=10000000&was_successful=True&coin_purchased=btc&fiat_amount=10&fiat_denomination=USD&exchange_used=coinbase_pro&interval_time_in_seconds=4800&high_availability_type=failover&exchange_order_id=ab1354345bsdfbsd&failure_reason=n/a

#DELETE - delete logs
#?user_id=50&epoch_time=10000000&delete=deleteoneusertime
#?epoch_time=10000000&delete=deletemultiusertime
#?user_id=50&delete=deleteoneuserall
