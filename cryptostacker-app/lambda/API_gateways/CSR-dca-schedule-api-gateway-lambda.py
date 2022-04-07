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

def delete_dca_schedule(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, digital_asset):
    #http method POST
    logging.critical("delete_dca_schedule() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            if digital_asset == "btc":
                logging.error("digital asset btc delete") #debugging
                delete_row_query = """
                Delete
                FROM dca_schedule_btc
                WHERE user_id = %s
                """

            if digital_asset == "ltc":
                logging.error("digital asset ltc delete") #debugging
                delete_row_query = """
                Delete
                FROM dca_schedule_ltc
                WHERE user_id = %s
                """

            if digital_asset == "eth":
                logging.error("digital asset eth delete") #debugging
                delete_row_query = """
                Delete
                FROM dca_schedule_eth
                WHERE user_id = %s
                """

            select_user_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(delete_row_query, select_user_tuple)
                connection.commit()
                logging.error("Row Deleted") #debugging

        return "Row Deleted"

    except Error as e:
        print(e)


def get_dca_schedule(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, digital_asset):
    #http method GET
    logging.critical("get_dca_schedule() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            if digital_asset == "btc":
                logging.error("digital asset query btc") #debugging
                select_user_query = """
                SELECT *
                FROM dca_schedule_btc
                WHERE user_id = %s
                """

            if digital_asset == "ltc":
                logging.error("digital asset query ltc") #debugging
                select_user_query = """
                SELECT *
                FROM dca_schedule_ltc
                WHERE user_id = %s
                """

            if digital_asset == "eth":
                logging.error("digital asset query eth") #debugging
                select_user_query = """
                SELECT *
                FROM dca_schedule_eth
                WHERE user_id = %s
                """

            select_user_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchone() 

        return sql_query_result

    except Error as e:
        print(e)

def get_dca_schedule_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, after_id, digital_asset, limit, next_run_epoch):
    #http method GET
    logging.critical("get_dca_schedule_paginated() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            if digital_asset == "btc":
                logging.error("digital asset query btc") #debugging
                select_schedules_query = """
                SELECT *
                FROM dca_schedule_btc
                WHERE user_id > %s AND next_run_epoch = %s
                LIMIT %s
                """

            if digital_asset == "ltc":
                logging.error("digital asset query ltc") #debugging
                select_schedules_query = """
                SELECT *
                FROM dca_schedule_ltc
                WHERE user_id > %s AND next_run_epoch = %s
                LIMIT %s
                """

            if digital_asset == "eth":
                logging.error("digital asset query eth") #debugging
                select_schedules_query = """
                SELECT *
                FROM dca_schedule_eth
                WHERE user_id > %s AND next_run_epoch = %s
                LIMIT %s
                """

            select_schedules_tuple = (int(after_id), int(next_run_epoch), int(limit), )

            with connection.cursor() as cursor:
                cursor.execute(select_schedules_query, select_schedules_tuple)
                sql_query_result = cursor.fetchall() 

        return sql_query_result

    except Error as e:
        print(e)
    

def get_missed_dca_schedules_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, after_id, digital_asset, limit):
    #http method GET
    logging.critical("get_missed_dca_schedules_paginated() called") #debugging
    current_time_epoch = CSR_toolkit.current_time_epoch()
    seconds_in_a_minute = 60
    seconds_in_an_hour = seconds_in_a_minute * 60
    next_run_epoch_in_the_past = current_time_epoch - (seconds_in_a_minute * 70)
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

            if digital_asset == "btc":
                logging.error("digital asset query btc") #debugging
                select_schedules_query = """
                SELECT *
                FROM dca_schedule_btc
                WHERE user_id > %s AND next_run_epoch < %s
                LIMIT %s
                """

            if digital_asset == "ltc":
                logging.error("digital asset query ltc") #debugging
                select_schedules_query = """
                SELECT *
                FROM dca_schedule_ltc
                WHERE user_id > %s AND next_run_epoch < %s
                LIMIT %s
                """

            if digital_asset == "eth":
                logging.error("digital asset query eth") #debugging
                select_schedules_query = """
                SELECT *
                FROM dca_schedule_eth
                WHERE user_id > %s AND next_run_epoch < %s
                LIMIT %s
                """

            select_schedules_tuple = (int(after_id), int(next_run_epoch_in_the_past), int(limit), )

            with connection.cursor() as cursor:
                cursor.execute(select_schedules_query, select_schedules_tuple)
                sql_query_result = cursor.fetchall() 

        return sql_query_result

    except Error as e:
        print(e)
    

def count_unique_user_ids_per_digital_asset(RDS_secret_host, RDS_secret_user, RDS_secret_pass, digital_asset):
    logging.critical("count_unique_user_ids_per_digital_asset()")
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            if digital_asset.lower() == "btc":
                logging.error("digital asset query btc") #debugging
                select_query = """
                SELECT COUNT(DISTINCT user_id) unique_users
                FROM dca_schedule_btc
                """

            if digital_asset.lower() == "eth":
                logging.error("digital asset query eth") #debugging
                select_query = """
                SELECT COUNT(DISTINCT user_id) unique_users
                FROM dca_schedule_eth
                """

            if digital_asset.lower() == "ltc":
                logging.error("digital asset query ltc") #debugging
                select_query = """
                SELECT COUNT(DISTINCT user_id) unique_users
                FROM dca_schedule_ltc
                """

            with connection.cursor() as cursor:
                cursor.execute(select_query)
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


def count_unique_user_ids_per_digital_asset_and_ha_type(RDS_secret_host, RDS_secret_user, RDS_secret_pass, digital_asset, ha_type):
    logging.critical("count_unique_user_ids_per_digital_asset_and_ha_type()")
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            if digital_asset.lower() == "btc":
                logging.error("digital asset query btc") #debugging
                select_query = """
                SELECT COUNT(*)
                FROM dca_schedule_btc
                WHERE high_availability_type = %s
                """

            if digital_asset.lower() == "eth":
                logging.error("digital asset query eth") #debugging
                select_query = """
                SELECT COUNT(*)
                FROM dca_schedule_eth
                WHERE high_availability_type = %s
                """

            if digital_asset.lower() == "ltc":
                logging.error("digital asset query ltc") #debugging
                select_query = """
                SELECT COUNT(*)
                FROM dca_schedule_ltc
                WHERE high_availability_type = %s
                """

            select_tuple = (str(ha_type).lower(), )

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
        if "user_id" in event["queryStringParameters"] and "digital_asset" in event["queryStringParameters"] and "limit" not in event["queryStringParameters"] and "after_id" not in event["queryStringParameters"]:
            logging.error("required queryStringParameters set") #debugging
            logging.error("query of a single DCA schedule") #debugging
            if event["queryStringParameters"]["digital_asset"] not in CSR_toolkit.supported_coins_list:
                logging.error('["queryStringParameters"]["digital_asset"] contains invalid coin!') #debugging
            if event["queryStringParameters"]["digital_asset"] in CSR_toolkit.supported_coins_list:
                user_id = event["queryStringParameters"]["user_id"]
                digital_asset = event["queryStringParameters"]["digital_asset"]
                sql_query_result = get_dca_schedule(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, digital_asset)
                if not sql_query_result:
                    responseObject["body"] = json.dumps("[]")
                    return responseObject

                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject
        
        elif "user_id" not in event["queryStringParameters"] and "digital_asset" in event["queryStringParameters"] and "limit" in event["queryStringParameters"] and "after_id" in event["queryStringParameters"] and "next_run_epoch" in event["queryStringParameters"]:
            logging.error("required queryStringParameters set") #debugging
            logging.error("query of multiple DCA schedules") #debugging
            if event["queryStringParameters"]["digital_asset"] not in CSR_toolkit.supported_coins_list:
                logging.error('["queryStringParameters"]["digital_asset"] contains invalid coin!') #debugging
                responseObject["body"] = json.dumps("[]")
                return responseObject
            elif event["queryStringParameters"]["digital_asset"] in CSR_toolkit.supported_coins_list:
                limit = event["queryStringParameters"]["limit"]
                after_id = event["queryStringParameters"]["after_id"]
                digital_asset = event["queryStringParameters"]["digital_asset"]
                next_run_epoch = event["queryStringParameters"]["next_run_epoch"]

                limit_limit = 100
                if int(event["queryStringParameters"]["limit"]) > limit_limit:
                    logging.error("limit size too large - not continuing with query") #debugging
                    responseObject["statusCode"] = 400
                    responseObject["body"] = json.dumps("limit too large")
                    return responseObject
                elif int(event["queryStringParameters"]["limit"]) <= limit_limit:
                    logging.error("limit size within limit - continuing with query") #debugging
                    sql_query_result = get_dca_schedule_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, after_id, digital_asset, limit, next_run_epoch)
                    if not sql_query_result:
                        responseObject["body"] = json.dumps("[]") #return empty list
                        return responseObject

                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
            
                else:
                    logging.error("unexpected limit issue") #debugging
        
        elif "scope" in event["queryStringParameters"]:
            if event["queryStringParameters"]["scope"] == "get_missed_dca_schedules_paginated":
                logging.error("scope: get_missed_dca_schedules_paginated") #debugging
                limit = event["queryStringParameters"]["limit"]
                after_id = event["queryStringParameters"]["after_id"]
                digital_asset = event["queryStringParameters"]["digital_asset"]
                sql_query_result = get_missed_dca_schedules_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, after_id, digital_asset, limit)
                if not sql_query_result:
                    responseObject["body"] = json.dumps("[]") #return empty list
                    return responseObject

                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject

            elif event["queryStringParameters"]["scope"] == "count_active_schedules":
                logging.error("scope: count_active_schedules") #debugging
                digital_asset = event["queryStringParameters"]["digital_asset"]
                sql_query_result = count_unique_user_ids_per_digital_asset(RDS_secret_host, RDS_secret_user, RDS_secret_pass, digital_asset)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject

            elif event["queryStringParameters"]["scope"] == "count_ha_types":
                logging.error("scope: count_ha_types") #debugging
                digital_asset = event["queryStringParameters"]["digital_asset"]
                ha_type = event["queryStringParameters"]["ha_type"]
                sql_query_result = count_unique_user_ids_per_digital_asset_and_ha_type(RDS_secret_host, RDS_secret_user, RDS_secret_pass, digital_asset, ha_type)
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

        else:
            logging.error("queryStringParameters missing")
            responseObject["statusCode"] = 400
            responseObject["body"] = json.dumps("queryStringParameters missing")
            return responseObject

    #IF POST
    if event["httpMethod"] == "POST":
        logging.error("httpMethod: POST") #debugging
        if "user_id" in event["queryStringParameters"] and "digital_asset" in event["queryStringParameters"] and "interval_time" in event["queryStringParameters"] and "interval_denomination" in event["queryStringParameters"] and "fiat_amount" in event["queryStringParameters"] and "fiat_denomination" in event["queryStringParameters"] and "high_availability_type" in event["queryStringParameters"] and "exchange_priority_1" in event["queryStringParameters"] and "exchange_priority_2" in event["queryStringParameters"] and "exchange_priority_3" in event["queryStringParameters"] and "exchange_priority_4" in event["queryStringParameters"] and "exchange_priority_5" in event["queryStringParameters"] and "exchange_priority_6" in event["queryStringParameters"] and "exchange_priority_7" in event["queryStringParameters"] and "exchange_priority_8" in event["queryStringParameters"] and "exchange_priority_9" in event["queryStringParameters"] and "exchange_priority_10" in event["queryStringParameters"] and "exchange_priority_11" in event["queryStringParameters"] and "exchange_priority_12" in event["queryStringParameters"] and "exchange_priority_13" in event["queryStringParameters"] and "exchange_priority_14" in event["queryStringParameters"] and "exchange_priority_15" in event["queryStringParameters"] and "exchange_priority_16" in event["queryStringParameters"] and "exchange_priority_17" in event["queryStringParameters"] and "exchange_priority_18" in event["queryStringParameters"] and "exchange_priority_19" in event["queryStringParameters"] and "exchange_priority_20" in event["queryStringParameters"] and "delete" not in event["queryStringParameters"] and "update" not in event["queryStringParameters"]:
            logging.error("POST if") #debugging
            
            #assign queryStringParameters to variables, these will be used to update or create a row
            user_id = event["queryStringParameters"]["user_id"]
            digital_asset = event["queryStringParameters"]["digital_asset"]
            interval_time = event["queryStringParameters"]["interval_time"]
            interval_denomination = event["queryStringParameters"]["interval_denomination"]
            fiat_amount = event["queryStringParameters"]["fiat_amount"]
            fiat_denomination = event["queryStringParameters"]["fiat_denomination"]
            high_availability_type = event["queryStringParameters"]["high_availability_type"]
            exchange_priority_1 = event["queryStringParameters"]["exchange_priority_1"]
            exchange_priority_2 = event["queryStringParameters"]["exchange_priority_2"]
            exchange_priority_3 = event["queryStringParameters"]["exchange_priority_3"]
            exchange_priority_4 = event["queryStringParameters"]["exchange_priority_4"]
            exchange_priority_5 = event["queryStringParameters"]["exchange_priority_5"]
            exchange_priority_6 = event["queryStringParameters"]["exchange_priority_6"]
            exchange_priority_7 = event["queryStringParameters"]["exchange_priority_7"]
            exchange_priority_8 = event["queryStringParameters"]["exchange_priority_8"]
            exchange_priority_9 = event["queryStringParameters"]["exchange_priority_9"]
            exchange_priority_10 = event["queryStringParameters"]["exchange_priority_10"]
            exchange_priority_11 = event["queryStringParameters"]["exchange_priority_11"]
            exchange_priority_12 = event["queryStringParameters"]["exchange_priority_12"]
            exchange_priority_13 = event["queryStringParameters"]["exchange_priority_13"]
            exchange_priority_14 = event["queryStringParameters"]["exchange_priority_14"]
            exchange_priority_15 = event["queryStringParameters"]["exchange_priority_15"]
            exchange_priority_16 = event["queryStringParameters"]["exchange_priority_16"]
            exchange_priority_17 = event["queryStringParameters"]["exchange_priority_17"]
            exchange_priority_18 = event["queryStringParameters"]["exchange_priority_18"]
            exchange_priority_19 = event["queryStringParameters"]["exchange_priority_19"]
            exchange_priority_20 = event["queryStringParameters"]["exchange_priority_20"]
            
            #check to make sure digital_asset is correct
            if digital_asset not in CSR_toolkit.supported_coins_list:
                logging.error('["queryStringParameters"]["digital_asset"] contains invalid coin!') #debugging
                responseObject["body"] = json.dumps('["queryStringParameters"]["digital_asset"] contains invalid coin!')
                responseObject["statusCode"] = 400
                return responseObject

            #set variables which the user doesn't provide, these will be used to update or create a row
            if digital_asset.lower() == "btc":
                first_run_time_buffer_in_seconds = 300
            elif digital_asset.lower() == "eth":
                first_run_time_buffer_in_seconds = 360
            elif digital_asset.lower() == "ltc":
                first_run_time_buffer_in_seconds = 420
            else:
                first_run_time_buffer_in_seconds = 300
            datetime_now_object = datetime.datetime.now()
            datetime_now_object_epoch = datetime_now_object.strftime('%s')

            if interval_denomination == "minutes":
                interval_time_in_seconds = int(interval_time) * 60
            if interval_denomination == "hours":
                interval_time_in_seconds = int(interval_time) * 60 * 60

            date_schedule_created_epoch = datetime_now_object_epoch
            first_run_epoch = 0 #must be int, this field in SQL is an int, this value is reset everytime a schedule is changed, this value is subsequently set by the DCA lambda
            next_run_time_build = datetime_now_object + datetime.timedelta(seconds=first_run_time_buffer_in_seconds)
            next_run_time = next_run_time_build.replace(second=00, microsecond=00)
            next_run_epoch = next_run_time.strftime('%s')
            last_run_epoch = 0 #this value is reset everytime a schedule is changed, this value is subsequently set by the DCA lambda
            exchange_last_run = "None" #this value is reset everytime a schedule is changed, this value is subsequently set by the DCA lambda
            
            #create result object to check to see if schedule already exists
            get_user_id_and_digital_asset_result = get_dca_schedule(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, digital_asset)

            if get_user_id_and_digital_asset_result:
                #if user already exists, update user
                try:
                    with connect(
                        host=RDS_secret_host,
                        user=RDS_secret_user,
                        password=RDS_secret_pass,
                        database="CSR",
                    ) as connection:
                        print(connection) #debugging

                        if digital_asset == "btc":
                            update_dca_schedule_query = """
                            UPDATE dca_schedule_btc
                            SET interval_time = %s,
                            interval_denomination = %s,
                            interval_time_in_seconds = %s,
                            fiat_amount = %s,
                            fiat_denomination = %s,
                            date_schedule_created_epoch = %s,
                            first_run_epoch = %s,
                            last_run_epoch = %s,
                            next_run_epoch = %s,
                            high_availability_type = %s,
                            exchange_priority_1 = %s,
                            exchange_priority_2 = %s,
                            exchange_priority_3 = %s,
                            exchange_priority_4 = %s,
                            exchange_priority_5 = %s,
                            exchange_priority_6 = %s,
                            exchange_priority_7 = %s,
                            exchange_priority_8 = %s,
                            exchange_priority_9 = %s,
                            exchange_priority_10 = %s,
                            exchange_priority_11 = %s,
                            exchange_priority_12 = %s,
                            exchange_priority_13 = %s,
                            exchange_priority_14 = %s,
                            exchange_priority_15 = %s,
                            exchange_priority_16 = %s,
                            exchange_priority_17 = %s,
                            exchange_priority_18 = %s,
                            exchange_priority_19 = %s,
                            exchange_priority_20 = %s,
                            exchange_last_run = %s
                            WHERE user_id = %s
                            """

                        if digital_asset == "ltc":
                            update_dca_schedule_query = """
                            UPDATE dca_schedule_ltc
                            SET interval_time = %s,
                            interval_denomination = %s,
                            interval_time_in_seconds = %s,
                            fiat_amount = %s,
                            fiat_denomination = %s,
                            date_schedule_created_epoch = %s,
                            first_run_epoch = %s,
                            last_run_epoch = %s,
                            next_run_epoch = %s,
                            high_availability_type = %s,
                            exchange_priority_1 = %s,
                            exchange_priority_2 = %s,
                            exchange_priority_3 = %s,
                            exchange_priority_4 = %s,
                            exchange_priority_5 = %s,
                            exchange_priority_6 = %s,
                            exchange_priority_7 = %s,
                            exchange_priority_8 = %s,
                            exchange_priority_9 = %s,
                            exchange_priority_10 = %s,
                            exchange_priority_11 = %s,
                            exchange_priority_12 = %s,
                            exchange_priority_13 = %s,
                            exchange_priority_14 = %s,
                            exchange_priority_15 = %s,
                            exchange_priority_16 = %s,
                            exchange_priority_17 = %s,
                            exchange_priority_18 = %s,
                            exchange_priority_19 = %s,
                            exchange_priority_20 = %s,
                            exchange_last_run = %s
                            WHERE user_id = %s
                            """

                        if digital_asset == "eth":
                            update_dca_schedule_query = """
                            UPDATE dca_schedule_eth
                            SET interval_time = %s,
                            interval_denomination = %s,
                            interval_time_in_seconds = %s,
                            fiat_amount = %s,
                            fiat_denomination = %s,
                            date_schedule_created_epoch = %s,
                            first_run_epoch = %s,
                            last_run_epoch = %s,
                            next_run_epoch = %s,
                            high_availability_type = %s,
                            exchange_priority_1 = %s,
                            exchange_priority_2 = %s,
                            exchange_priority_3 = %s,
                            exchange_priority_4 = %s,
                            exchange_priority_5 = %s,
                            exchange_priority_6 = %s,
                            exchange_priority_7 = %s,
                            exchange_priority_8 = %s,
                            exchange_priority_9 = %s,
                            exchange_priority_10 = %s,
                            exchange_priority_11 = %s,
                            exchange_priority_12 = %s,
                            exchange_priority_13 = %s,
                            exchange_priority_14 = %s,
                            exchange_priority_15 = %s,
                            exchange_priority_16 = %s,
                            exchange_priority_17 = %s,
                            exchange_priority_18 = %s,
                            exchange_priority_19 = %s,
                            exchange_priority_20 = %s,
                            exchange_last_run = %s
                            WHERE user_id = %s
                            """

                        update_variables_tuple = (int(interval_time), interval_denomination, int(interval_time_in_seconds), int(fiat_amount), fiat_denomination, int(date_schedule_created_epoch), int(first_run_epoch), int(last_run_epoch), int(next_run_epoch), high_availability_type, exchange_priority_1, exchange_priority_2, exchange_priority_3, exchange_priority_4, exchange_priority_5, exchange_priority_6, exchange_priority_7, exchange_priority_8, exchange_priority_9, exchange_priority_10, exchange_priority_11, exchange_priority_12, exchange_priority_13, exchange_priority_14, exchange_priority_15, exchange_priority_16, exchange_priority_17, exchange_priority_18, exchange_priority_19, exchange_priority_20, exchange_last_run, int(user_id), )

                        with connection.cursor() as cursor:
                            cursor.execute(update_dca_schedule_query, update_variables_tuple)
                            connection.commit()
                            print(cursor.rowcount, "record(s) affected") #debugging

                except Error as e:
                    print(e)
                
                logging.error("schedule already exists, schedule updated")
                responseObject["body"] = json.dumps("schedule already exists, schedule updated")
                return responseObject

            if not get_user_id_and_digital_asset_result:
                #if user doesn't already exist, create user
                try:
                    with connect(
                        host=RDS_secret_host,
                        user=RDS_secret_user,
                        password=RDS_secret_pass,
                        database="CSR",
                    ) as connection:
                        print(connection) #debugging

                        if digital_asset == "btc":
                            insert_dca_schedule_query = """
                            INSERT INTO dca_schedule_btc
                            (user_id,
                            interval_time,
                            interval_denomination,
                            interval_time_in_seconds,
                            fiat_amount,
                            fiat_denomination,
                            date_schedule_created_epoch,
                            first_run_epoch,
                            last_run_epoch,
                            next_run_epoch,
                            high_availability_type,
                            exchange_priority_1,
                            exchange_priority_2,
                            exchange_priority_3,
                            exchange_priority_4,
                            exchange_priority_5,
                            exchange_priority_6,
                            exchange_priority_7,
                            exchange_priority_8,
                            exchange_priority_9,
                            exchange_priority_10,
                            exchange_priority_11,
                            exchange_priority_12,
                            exchange_priority_13,
                            exchange_priority_14,
                            exchange_priority_15,
                            exchange_priority_16,
                            exchange_priority_17,
                            exchange_priority_18,
                            exchange_priority_19,
                            exchange_priority_20,
                            exchange_last_run)
                            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s  )
                            """
                        
                        if digital_asset == "ltc":
                            insert_dca_schedule_query = """
                            INSERT INTO dca_schedule_ltc
                            (user_id,
                            interval_time,
                            interval_denomination,
                            interval_time_in_seconds,
                            fiat_amount,
                            fiat_denomination,
                            date_schedule_created_epoch,
                            first_run_epoch,
                            last_run_epoch,
                            next_run_epoch,
                            high_availability_type,
                            exchange_priority_1,
                            exchange_priority_2,
                            exchange_priority_3,
                            exchange_priority_4,
                            exchange_priority_5,
                            exchange_priority_6,
                            exchange_priority_7,
                            exchange_priority_8,
                            exchange_priority_9,
                            exchange_priority_10,
                            exchange_priority_11,
                            exchange_priority_12,
                            exchange_priority_13,
                            exchange_priority_14,
                            exchange_priority_15,
                            exchange_priority_16,
                            exchange_priority_17,
                            exchange_priority_18,
                            exchange_priority_19,
                            exchange_priority_20,                            
                            exchange_last_run)
                            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s  )
                            """
                        
                        if digital_asset == "eth":
                            insert_dca_schedule_query = """
                            INSERT INTO dca_schedule_eth
                            (user_id,
                            interval_time,
                            interval_denomination,
                            interval_time_in_seconds,
                            fiat_amount,
                            fiat_denomination,
                            date_schedule_created_epoch,
                            first_run_epoch,
                            last_run_epoch,
                            next_run_epoch,
                            high_availability_type,
                            exchange_priority_1,
                            exchange_priority_2,
                            exchange_priority_3,
                            exchange_priority_4,
                            exchange_priority_5,
                            exchange_priority_6,
                            exchange_priority_7,
                            exchange_priority_8,
                            exchange_priority_9,
                            exchange_priority_10,
                            exchange_priority_11,
                            exchange_priority_12,
                            exchange_priority_13,
                            exchange_priority_14,
                            exchange_priority_15,
                            exchange_priority_16,
                            exchange_priority_17,
                            exchange_priority_18,
                            exchange_priority_19,
                            exchange_priority_20,                            
                            exchange_last_run)
                            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
                            """
                        
                        execute_variables_tuple = (int(user_id), int(interval_time), interval_denomination, int(interval_time_in_seconds), int(fiat_amount), fiat_denomination, int(date_schedule_created_epoch), int(first_run_epoch), int(last_run_epoch), int(next_run_epoch), high_availability_type, exchange_priority_1, exchange_priority_2, exchange_priority_3, exchange_priority_4, exchange_priority_5, exchange_priority_6, exchange_priority_7, exchange_priority_8, exchange_priority_9, exchange_priority_10, exchange_priority_11, exchange_priority_12, exchange_priority_13, exchange_priority_14, exchange_priority_15, exchange_priority_16, exchange_priority_17, exchange_priority_18, exchange_priority_19, exchange_priority_20, exchange_last_run, )

                        with connection.cursor() as cursor:
                            cursor.execute(insert_dca_schedule_query, execute_variables_tuple)
                            connection.commit()

                except Error as e:
                    print(e)

            logging.error("Schedule didn't already exist, schedule created")
            responseObject["body"] = json.dumps("Schedule didn't already exist, schedule created")
            return responseObject

        elif "user_id" in event["queryStringParameters"] and "digital_asset" in event["queryStringParameters"] and "update" in event["queryStringParameters"]:
            logging.error("POST elif update") #debugging
            user_id = event["queryStringParameters"]["user_id"]
            digital_asset = event["queryStringParameters"]["digital_asset"]
            last_run_epoch = event["queryStringParameters"]["last_run_epoch"]
            next_run_epoch = event["queryStringParameters"]["next_run_epoch"]
            exchange_last_run = event["queryStringParameters"]["exchange_last_run"]
            first_run_epoch = event["queryStringParameters"]["first_run_epoch"]

            try:
                with connect(
                    host=RDS_secret_host,
                    user=RDS_secret_user,
                    password=RDS_secret_pass,
                    database="CSR",
                ) as connection:
                    print(connection) #debugging

                    if digital_asset == "btc":
                        update_dca_schedule_query = """
                        UPDATE dca_schedule_btc
                        SET first_run_epoch = %s,
                        last_run_epoch = %s,
                        next_run_epoch = %s,
                        exchange_last_run = %s
                        WHERE user_id = %s
                        """

                    if digital_asset == "ltc":
                        update_dca_schedule_query = """
                        UPDATE dca_schedule_ltc
                        SET first_run_epoch = %s,
                        last_run_epoch = %s,
                        next_run_epoch = %s,
                        exchange_last_run = %s
                        WHERE user_id = %s
                        """

                    if digital_asset == "eth":
                        update_dca_schedule_query = """
                        UPDATE dca_schedule_eth
                        SET first_run_epoch = %s,
                        last_run_epoch = %s,
                        next_run_epoch = %s,
                        exchange_last_run = %s
                        WHERE user_id = %s
                        """

                    update_variables_tuple = (int(first_run_epoch), int(last_run_epoch), int(next_run_epoch), str(exchange_last_run), int(user_id), )

                    with connection.cursor() as cursor:
                        cursor.execute(update_dca_schedule_query, update_variables_tuple)
                        connection.commit()
                        print(cursor.rowcount, "record(s) affected") #debugging

            except Error as e:
                print(e)
            
            logging.error("schedule already exists, schedule updated")
            responseObject["body"] = json.dumps("schedule already exists, schedule updated")
            return responseObject

        elif "user_id" in event["queryStringParameters"] and "digital_asset" in event["queryStringParameters"] and "updatenextrunonly" in event["queryStringParameters"]:
            logging.error("POST elif update") #debugging
            user_id = event["queryStringParameters"]["user_id"]
            digital_asset = event["queryStringParameters"]["digital_asset"]
            next_run_epoch = event["queryStringParameters"]["next_run_epoch"]

            try:
                with connect(
                    host=RDS_secret_host,
                    user=RDS_secret_user,
                    password=RDS_secret_pass,
                    database="CSR",
                ) as connection:
                    print(connection) #debugging

                    if digital_asset == "btc":
                        update_dca_schedule_query = """
                        UPDATE dca_schedule_btc
                        SET next_run_epoch = %s
                        WHERE user_id = %s
                        """

                    if digital_asset == "ltc":
                        update_dca_schedule_query = """
                        UPDATE dca_schedule_ltc
                        SET next_run_epoch = %s
                        WHERE user_id = %s
                        """

                    if digital_asset == "eth":
                        update_dca_schedule_query = """
                        UPDATE dca_schedule_eth
                        SET next_run_epoch = %s
                        WHERE user_id = %s
                        """

                    update_variables_tuple = (int(next_run_epoch), int(user_id), )

                    with connection.cursor() as cursor:
                        cursor.execute(update_dca_schedule_query, update_variables_tuple)
                        connection.commit()
                        print(cursor.rowcount, "record(s) affected") #debugging

            except Error as e:
                print(e)
            
            logging.error("schedule already exists, schedule updated")
            responseObject["body"] = json.dumps("schedule already exists, schedule updated")
            return responseObject


        elif "user_id" in event["queryStringParameters"] and "digital_asset" in event["queryStringParameters"] and "delete" in event["queryStringParameters"]:
            logging.error("POST elif delete") #debugging
            user_id = event["queryStringParameters"]["user_id"]
            digital_asset = event["queryStringParameters"]["digital_asset"]

            #check to make sure digital_asset is correct
            if digital_asset not in CSR_toolkit.supported_coins_list:
                #log error in error DB and/or suspicious DB, could be IOC
                logging.error('["queryStringParameters"]["digital_asset"] contains invalid coin!') #debugging
                responseObject["body"] = json.dumps('["queryStringParameters"]["digital_asset"] contains invalid coin!')
                responseObject["statusCode"] = 400
                return responseObject

            #if delete=delete in query string then delete row
            if "delete" == event["queryStringParameters"]["delete"]:
                delete_result = delete_dca_schedule(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, digital_asset)
                #assign queryStringParameters to variables, these will be used to update or create a row
                responseObject["body"] = json.dumps(delete_result) #todo: switch to a fixed string literal
                return responseObject

        else:
            logging.error("POST else") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject


#########################
### test query params ###
#########################
#this service needs to be completely refactored, its fucking ridiculous

#GET - get schedule - single
#?user_id=50&digital_asset=btc

#GET - get multiple paginated schedules
#?digital_asset=btc&limit=20&after_id=0&next_run_epoch=1637513940

#GET - get schedules which have past due next run epochs - paginated
#?scope=get_missed_dca_schedules_paginated&limit=200&after_id=0&digital_asset=btc

#GET - count active schedules by digial asset
#?scope=count_active_schedules&digital_asset=btc

#GET - count active schedules by digital asset & ha type
#?scope=count_ha_types&digital_asset=btc&ha_type=failover

#POST - create or overwrite schedule
#?user_id=50&digital_asset=btc&interval_time=10&interval_denomination=minutes&fiat_amount=10&fiat_denomination=USD&high_availability_type=failover&exchange_priority_1=coinbase_pro&exchange_priority_2=coinbase_pro&exchange_priority_3=coinbase_pro&exchange_priority_4=coinbase_pro&exchange_priority_5=coinbase_pro&exchange_priority_6=coinbase_pro&exchange_priority_7=coinbase_pro&exchange_priority_8=coinbase_pro&exchange_priority_9=coinbase_pro&exchange_priority_10=coinbase_pro&exchange_priority_11=coinbase_pro&exchange_priority_12=coinbase_pro&exchange_priority_13=coinbase_pro&exchange_priority_14=coinbase_pro&exchange_priority_15=coinbase_pro&exchange_priority_16=coinbase_pro&exchange_priority_17=coinbase_pro&exchange_priority_18=coinbase_pro&exchange_priority_19=coinbase_pro&exchange_priority_20=coinbase_pro

#POST - update existing schedule (initiated from DCA purchaser)
#?user_id=3&digital_asset=btc&last_run_epoch=1000000&next_run_epoch=10000000&exchange_last_run=coinbase_pro&first_run_epoch=10000&update=update

#POST - update next run only 
#?user_id=3&digital_asset=btc&next_run_epoch=10000000&updatenextrunonly=updatenextrunonly

#POST - delete schedule
#?user_id=50&digital_asset=btc&delete=delete
