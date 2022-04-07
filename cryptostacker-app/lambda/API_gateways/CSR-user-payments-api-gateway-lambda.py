#pip install mysql-connector-python
from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
import json
import CSR_service_mesh_map
import CSR_toolkit
import datetime
#import threading

def get_single_latest_purchase(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    #http method GET
    logging.critical("get_single_latest_purchase() called") #debugging
    limit_max = 1
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_query = """
            SELECT *
            FROM user_payments
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT %s
            """

            select_tuple = (int(user_id), int(limit_max), )

            with connection.cursor() as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchone()

        return sql_query_result

    except Error as e:
        print(e)

def get_future_expire_purchase(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    #http method GET
    logging.critical("get_future_expire_purchase() called") #debugging
    limit_max = 1
    current_time_epoch = CSR_toolkit.current_time_epoch()
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_query = """
            SELECT *
            FROM user_payments
            WHERE user_id = %s AND epoch_expiration > %s
            ORDER BY id DESC
            LIMIT %s
            """

            select_tuple = (int(user_id), int(current_time_epoch), int(limit_max), )

            with connection.cursor(buffered=True) as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchone()

        return sql_query_result

    except Error as e:
        print(e)

def get_multiple_latest_purchase(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, limit):
    logging.critical("get_multiple_latest_purchase() called") #debugging
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

            select_query = """
            SELECT *
            FROM user_payments
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT %s
            """

            select_tuple = (int(user_id), int(limit), )

            with connection.cursor() as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchall()

        return sql_query_result

    except Error as e:
        print(e)

def get_gross_revenue_from_referral_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, referral_code):
    logging.critical("get_gross_revenue_from_referral_code() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_query = """
            SELECT SUM(payment_amount_in_usd) gross_revenue_from_referral_code 
            FROM user_payments
            WHERE referral_code = %s
            """

            select_tuple = (str(referral_code), )

            with connection.cursor() as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchone()

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

def get_gross_revenue_from_referral_code_epoch_time_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, referral_code, beginning_epoch, ending_epoch):
    logging.critical("get_gross_revenue_from_referral_code_epoch_time_range() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_query = """
            SELECT SUM(payment_amount_in_usd) gross_revenue_from_referral_code 
            FROM user_payments
            WHERE referral_code = %s
            AND epoch_of_payment >= %s
            AND epoch_of_payment <= %s
            """

            select_tuple = (str(referral_code), int(beginning_epoch), int(ending_epoch), )

            with connection.cursor() as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchone()

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

def get_unique_paying_users_with_referral_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, referral_code):
    logging.critical("get_unique_paying_users_with_referral_code() called") #debugging
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
            FROM user_payments
            WHERE referral_code = %s
            """

            select_tuple = (str(referral_code), )

            with connection.cursor() as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchone()

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


def get_count_unique_users(RDS_secret_host, RDS_secret_user, RDS_secret_pass):
    logging.critical("get_count_unique_users() called") #debugging
    current_epoch = CSR_toolkit.current_time_epoch()
    
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
            FROM user_payments
            WHERE epoch_expiration > %s
            """

            select_tuple = (int(current_epoch), )

            with connection.cursor() as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchone()

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


def get_count_tier_paid_for(RDS_secret_host, RDS_secret_user, RDS_secret_pass, tier_paid_for):
    logging.critical("get_count_tier_paid_for() called") #debugging
    current_epoch = CSR_toolkit.current_time_epoch()
    
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_query = """
            SELECT COUNT(*) as count
            FROM user_payments
            WHERE epoch_expiration > %s AND tier_paid_for = %s 
            """

            select_tuple = (int(current_epoch), int(tier_paid_for), )

            with connection.cursor() as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchone()

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


def get_count_number_of_months_paid_for(RDS_secret_host, RDS_secret_user, RDS_secret_pass, number_of_months_paid_for):
    logging.critical("get_count_number_of_months_paid_for() called") #debugging
    current_epoch = CSR_toolkit.current_time_epoch()
    
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_query = """
            SELECT COUNT(*) as count
            FROM user_payments
            WHERE epoch_expiration > %s AND number_of_months_paid_for = %s 
            """

            select_tuple = (int(current_epoch), int(number_of_months_paid_for), )

            with connection.cursor() as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchone()

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


def create_payment_record(RDS_secret_host, RDS_secret_user, RDS_secret_pass, api_gateway_api_key, user_id, payment_provider, crypto_or_fiat_gateway, order_id, payment_amount_in_usd, number_of_months_paid_for, tier_paid_for, description, current_us_state):
    logging.critical("create_payment_record() called") #debugging
    epoch_of_payment = CSR_toolkit.current_time_epoch()
    epoch_expiration = CSR_toolkit.epoch_plus_months_epoch(epoch_of_payment, number_of_months_paid_for)
    account_created_epoch = CSR_toolkit.get_account_created_epoch_from_users(user_id, api_gateway_api_key)
    
    if int(account_created_epoch) > int(CSR_toolkit.epoch_plus_months_epoch(CSR_toolkit.current_time_epoch(), -12)):
        logging.error("user's account was created less than 12 months ago, referral will be used")
        referral_code = CSR_toolkit.get_referral_code_from_user_subscription_status(user_id, api_gateway_api_key)
        referral_code = referral_code.lower()
    else:
        referral_code = "None"

    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection) #debugging

            insert_query = """
            INSERT INTO user_payments
            (user_id,
            epoch_of_payment,
            payment_provider,
            crypto_or_fiat_gateway,
            order_id,
            payment_amount_in_usd,
            number_of_months_paid_for,
            tier_paid_for,
            epoch_expiration,
            description,
            referral_code,
            account_created_epoch,
            current_us_state)
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
            """
        
            insert_tuple = (int(user_id), int(epoch_of_payment), str(payment_provider), str(crypto_or_fiat_gateway), str(order_id), int(payment_amount_in_usd), int(number_of_months_paid_for), int(tier_paid_for), int(epoch_expiration), str(description), str(referral_code), int(account_created_epoch), str(current_us_state), )

            with connection.cursor() as cursor:
                cursor.execute(insert_query, insert_tuple)
                connection.commit()

        return "inserted order_id"

    except Error as e:
        print(e)

def delete_row_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, row_id):
    logging.critical("delete_row_id() called") #debugging
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
            FROM user_payments
            WHERE id = %s
            """

            sql_tuple = (int(row_id), )

            with connection.cursor() as cursor:
                cursor.execute(delete_row_query, sql_tuple)
                connection.commit()
                logging.error("Row(s) Deleted") #debugging

        return "Row(s) Deleted"

    except Error as e:
        print(e)

def delete_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    logging.critical("delete_user_id() called") #debugging
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
            FROM user_payments
            WHERE user_id = %s
            """

            sql_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(delete_row_query, sql_tuple)
                connection.commit()
                logging.error("Row(s) Deleted") #debugging

        return "Row(s) Deleted"

    except Error as e:
        print(e)

def get_all_payments_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch):
    logging.critical("get_all_payments_between_date_range() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_query = """
            SELECT *
            FROM user_payments
            WHERE epoch_of_payment >= %s AND epoch_of_payment <= %s
            ORDER BY id DESC
            """

            select_tuple = (int(beginning_epoch), int(ending_epoch), )

            with connection.cursor() as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchall()

        return sql_query_result

    except Error as e:
        print(e)

def get_gross_revenue_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch):
    logging.critical("get_gross_revenue_between_date_range() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_query = """
            SELECT SUM(payment_amount_in_usd) gross_revenue_between_n_and_y_epoch
            FROM user_payments
            WHERE epoch_of_payment >= %s AND epoch_of_payment <= %s
            """

            select_tuple = (int(beginning_epoch), int(ending_epoch), )

            with connection.cursor() as cursor:
                cursor.execute(select_query, select_tuple)
                sql_query_result = cursor.fetchone()

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
    
    logging.error("retrieve service mesh secret for API calls")
    service_mesh_secret_1 = eval(aws_functions_for_lambda.get_aws_secret("CSR-Service-Mesh-Secret_1-TF"))
    
    #IF GET
    if event["httpMethod"] == "GET":
        logging.error("httpMethod: GET") #debugging
        if "scope" in event["queryStringParameters"]:
            logging.error("required scope set") #debugging
            
            if event["queryStringParameters"]["scope"] == "single_latest":
                logging.error("scope: single_latest") #debugging
                if "user_id" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                user_id = event["queryStringParameters"]["user_id"]
                sql_query_result = get_single_latest_purchase(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            elif event["queryStringParameters"]["scope"] == "single_active":
                logging.error("scope: single_active") #debugging
                if "user_id" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                user_id = event["queryStringParameters"]["user_id"]
                sql_query_result = get_future_expire_purchase(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "gross_revenue_from_referral_code":
                logging.error("scope: gross_revenue_from_referral_code") #debugging
                if "referral_code" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                referral_code = event["queryStringParameters"]["referral_code"]
                sql_query_result = get_gross_revenue_from_referral_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, referral_code)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "get_gross_revenue_from_referral_code_epoch_time_range":
                logging.error("scope: get_gross_revenue_from_referral_code_epoch_time_range") #debugging
                if "referral_code" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                if "beginning_epoch" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                if "ending_epoch" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                referral_code = event["queryStringParameters"]["referral_code"]
                beginning_epoch = event["queryStringParameters"]["beginning_epoch"]
                ending_epoch = event["queryStringParameters"]["ending_epoch"]
                sql_query_result = get_gross_revenue_from_referral_code_epoch_time_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, referral_code, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "count_unique_paying_users_with_referral_code":
                logging.error("scope: count_unique_paying_users_with_referral_code") #debugging
                if "referral_code" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                referral_code = event["queryStringParameters"]["referral_code"]
                sql_query_result = get_unique_paying_users_with_referral_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, referral_code)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "count_unique_users":
                logging.error("scope: count_unique_users") #debugging
                sql_query_result = get_count_unique_users(RDS_secret_host, RDS_secret_user, RDS_secret_pass)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "count_tier_paid_for":
                logging.error("scope: count_tier_paid_for") #debugging
                if "tier_paid_for" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                tier_paid_for = event["queryStringParameters"]["tier_paid_for"]
                sql_query_result = get_count_tier_paid_for(RDS_secret_host, RDS_secret_user, RDS_secret_pass, tier_paid_for)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "number_of_months_paid_for":
                logging.error("scope: number_of_months_paid_for") #debugging
                if "number_of_months_paid_for" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                number_of_months_paid_for = event["queryStringParameters"]["number_of_months_paid_for"]
                sql_query_result = get_count_number_of_months_paid_for(RDS_secret_host, RDS_secret_user, RDS_secret_pass, number_of_months_paid_for)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "multiple_latest":
                logging.error("scope: multiple_latest") #debugging
                if "user_id" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                if "limit" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                user_id = event["queryStringParameters"]["user_id"]
                limit = event["queryStringParameters"]["limit"]
                sql_query_result = get_multiple_latest_purchase(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, limit)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "previous_month_payments":
                logging.error("scope: previous_month_payments") #debugging
                first_and_last_day = CSR_toolkit.get_first_and_last_day_of_the_last_month()
                beginning_epoch = first_and_last_day[0].strftime('%s')
                ending_epoch = first_and_last_day[1].strftime('%s')
                sql_query_result = get_all_payments_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "month_to_date_payments":
                logging.error("scope: month_to_date_payments") #debugging
                first_and_last_day = CSR_toolkit.get_first_and_last_day_of_the_month()
                beginning_epoch = first_and_last_day[0].strftime('%s')
                ending_epoch = first_and_last_day[1].strftime('%s')
                sql_query_result = get_all_payments_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "previous_quarter_payments":
                logging.error("scope: previous_quarter_payments") #debugging
                first_and_last_day = CSR_toolkit.get_first_and_last_day_of_the_last_quarter()
                beginning_epoch = first_and_last_day[0].strftime('%s')
                ending_epoch = first_and_last_day[1].strftime('%s')
                sql_query_result = get_all_payments_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "quarter_to_date_payments":
                logging.error("scope: quarter_to_date_payments") #debugging
                date_time_object_now = datetime.datetime.now()
                beginning_epoch = CSR_toolkit.get_first_day_of_the_quarter(date_time_object_now).strftime('%s')
                ending_epoch = CSR_toolkit.get_last_day_of_the_quarter(date_time_object_now).strftime('%s')
                sql_query_result = get_all_payments_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "previous_year_payments":
                logging.error("scope: previous_year_payments") #debugging
                first_and_last_day = CSR_toolkit.get_first_and_last_day_of_the_last_year()
                beginning_epoch = first_and_last_day[0].strftime('%s')
                ending_epoch = first_and_last_day[1].strftime('%s')
                sql_query_result = get_all_payments_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "year_to_date_payments":
                logging.error("scope: year_to_date_payments") #debugging
                first_and_last_day = CSR_toolkit.get_first_and_last_day_of_the_year()
                beginning_epoch = first_and_last_day[0].strftime('%s')
                ending_epoch = first_and_last_day[1].strftime('%s')
                sql_query_result = get_all_payments_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "gross_revenue_past_24_hours":
                logging.error("scope: gross_revenue_past_24_hours") #debugging
                date_time_object_now = datetime.datetime.now()
                first_day = CSR_toolkit.datetime_plus_days(date_time_object_now, -1)
                beginning_epoch = first_day.strftime('%s')
                ending_epoch = date_time_object_now.strftime('%s')
                sql_query_result = get_gross_revenue_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "gross_revenue_past_7_days":
                logging.error("scope: gross_revenue_past_7_days") #debugging
                date_time_object_now = datetime.datetime.now()
                first_day = CSR_toolkit.datetime_plus_days(date_time_object_now, -7)
                beginning_epoch = first_day.strftime('%s')
                ending_epoch = date_time_object_now.strftime('%s')
                sql_query_result = get_gross_revenue_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "gross_revenue_past_rolling_30_days":
                logging.error("scope: gross_revenue_past_rolling_30_days") #debugging
                date_time_object_now = datetime.datetime.now()
                first_day = CSR_toolkit.datetime_plus_days(date_time_object_now, -30)
                beginning_epoch = first_day.strftime('%s')
                ending_epoch = date_time_object_now.strftime('%s')
                sql_query_result = get_gross_revenue_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "gross_revenue_past_previous_month":
                logging.error("scope: gross_revenue_past_previous_month") #debugging
                first_and_last_day = CSR_toolkit.get_first_and_last_day_of_the_last_month()
                beginning_epoch = first_and_last_day[0].strftime('%s')
                ending_epoch = first_and_last_day[1].strftime('%s')
                sql_query_result = get_gross_revenue_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "gross_revenue_past_month_to_date":
                logging.error("scope: gross_revenue_past_month_to_date") #debugging
                first_and_last_day = CSR_toolkit.get_first_and_last_day_of_the_month()
                beginning_epoch = first_and_last_day[0].strftime('%s')
                ending_epoch = first_and_last_day[1].strftime('%s')
                sql_query_result = get_gross_revenue_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "gross_revenue_past_previous_quarter":
                logging.error("scope: gross_revenue_past_previous_quarter") #debugging
                first_and_last_day = CSR_toolkit.get_first_and_last_day_of_the_last_quarter()
                beginning_epoch = first_and_last_day[0].strftime('%s')
                ending_epoch = first_and_last_day[1].strftime('%s')
                sql_query_result = get_gross_revenue_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "gross_revenue_past_quarter_to_date":
                logging.error("scope: gross_revenue_past_quarter_to_date") #debugging
                date_time_object_now = datetime.datetime.now()
                beginning_epoch = CSR_toolkit.get_first_day_of_the_quarter(date_time_object_now).strftime('%s')
                ending_epoch = CSR_toolkit.get_last_day_of_the_quarter(date_time_object_now).strftime('%s')
                sql_query_result = get_gross_revenue_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "gross_revenue_past_previous_year":
                logging.error("scope: gross_revenue_past_previous_year") #debugging
                first_and_last_day = CSR_toolkit.get_first_and_last_day_of_the_last_year()
                beginning_epoch = first_and_last_day[0].strftime('%s')
                ending_epoch = first_and_last_day[1].strftime('%s')
                sql_query_result = get_gross_revenue_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject

            elif event["queryStringParameters"]["scope"] == "gross_revenue_past_year_to_date":
                logging.error("scope: gross_revenue_past_year_to_date") #debugging
                first_and_last_day = CSR_toolkit.get_first_and_last_day_of_the_year()
                beginning_epoch = first_and_last_day[0].strftime('%s')
                ending_epoch = first_and_last_day[1].strftime('%s')
                sql_query_result = get_gross_revenue_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject

            elif event["queryStringParameters"]["scope"] == "gross_revenue_past_rolling_1_year":
                logging.error("scope: gross_revenue_past_rolling_1_year") #debugging
                date_time_object_now = datetime.datetime.now()
                first_day = CSR_toolkit.datetime_plus_days(date_time_object_now, -365)
                beginning_epoch = first_day.strftime('%s')
                ending_epoch = date_time_object_now.strftime('%s')
                sql_query_result = get_gross_revenue_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject

            elif event["queryStringParameters"]["scope"] == "gross_revenue_past_all_time":
                logging.error("scope: gross_revenue_past_all_time") #debugging
                beginning_epoch = 0
                ending_epoch = 4800809334
                sql_query_result = get_gross_revenue_between_date_range(RDS_secret_host, RDS_secret_user, RDS_secret_pass, beginning_epoch, ending_epoch)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject

            elif event["queryStringParameters"]["scope"] == "all_by_referral_code": #todo, finish this conditional
                logging.error("scope: all_by_referral_code") #debugging
                if "referral_code" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                sql_query_result = get_future_expire_purchase(RDS_secret_host, RDS_secret_user, RDS_secret_pass)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            
            elif event["queryStringParameters"]["scope"] == "all_by_current_us_state": #todo, finish this conditional
                logging.error("scope: all_by_current_us_state") #debugging
                if "current_us_state" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                sql_query_result = get_future_expire_purchase(RDS_secret_host, RDS_secret_user, RDS_secret_pass)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
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
        if "user_id" in event["queryStringParameters"] and "payment_provider" in event["queryStringParameters"] and "crypto_or_fiat_gateway" in event["queryStringParameters"] and "order_id" in event["queryStringParameters"] and "payment_amount_in_usd" in event["queryStringParameters"] and "number_of_months_paid_for" in event["queryStringParameters"] and "tier_paid_for" in event["queryStringParameters"] and "description" in event["queryStringParameters"] and "current_us_state" in event["queryStringParameters"]:
            user_id = event["queryStringParameters"]["user_id"]
            payment_provider = event["queryStringParameters"]["payment_provider"]
            crypto_or_fiat_gateway = event["queryStringParameters"]["crypto_or_fiat_gateway"]
            order_id = event["queryStringParameters"]["order_id"]
            payment_amount_in_usd = event["queryStringParameters"]["payment_amount_in_usd"]
            number_of_months_paid_for = event["queryStringParameters"]["number_of_months_paid_for"]
            tier_paid_for = event["queryStringParameters"]["tier_paid_for"]
            description = event["queryStringParameters"]["description"]
            current_us_state = event["queryStringParameters"]["current_us_state"]
            sql_query_result = create_payment_record(RDS_secret_host, RDS_secret_user, RDS_secret_pass, service_mesh_secret_1["CSR_Service_Mesh_Secret_1"], user_id, payment_provider, crypto_or_fiat_gateway, order_id, payment_amount_in_usd, number_of_months_paid_for, tier_paid_for, description, current_us_state)
            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject

        else:
            logging.error("queryStringParameters missing") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject
    
    #IF DELETE
    elif event["httpMethod"] == "DELETE":
        logging.error("httpMethod: DELETE") #debugging
        if "row_id" in event["queryStringParameters"]:
            row_id = event["queryStringParameters"]["row_id"]
            sql_query_result = delete_row_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, row_id)
            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject
        
        elif "user_id" in event["queryStringParameters"]:
            user_id = event["queryStringParameters"]["user_id"]
            sql_query_result = delete_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject
        
        else:
            logging.error("queryStringParameters missing") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject
    
    else:
        logging.error("queryStringParameters missing") #debugging
        responseObject["body"] = json.dumps("queryStringParameters missing")
        responseObject["statusCode"] = 400
        return responseObject


#########################
##### query params ######
#########################

#GET - single latest purchase of a user_id - 
#?user_id=1&scope=single_latest

#GET - single purchase of a user_id with epoch_expiration in the future - 
#?user_id=1&scope=single_active

#GET - multiple purchases of a user_id, sorted by newest, limit (max 200)
#?user_id=1&limit=12&scope=multiple_latest

#GET - dollar amount sum of all payments made using n referral_code
#?referral_code=lyra&scope=gross_revenue_from_referral_code

#GET - dollar amount sum of all payments made in n time frame using n referral_code
#?referral_code=lyra&beginning_epoch=100&ending_epoch=10000000000&scope=get_gross_revenue_from_referral_code_epoch_time_range

#GET - count the number of unique paying users with a specific referral code
#?referral_code=lyra&scope=count_unique_paying_users_with_referral_code

#GET - count unique user_ids with an expiration epoch greater than current epoch
#?scope=count_unique_users

#GET - count number of payments with matching tier_paid_for parameter & an expiration epoch greater than current epoch
#?scope=count_tier_paid_for&tier_paid_for=2

#GET - count number of payments with matching number_of_months_paid_for parameter & an expiration epoch greater than current epoch
#?scope=number_of_months_paid_for&number_of_months_paid_for=1

#GET - all purchases matching referral code - 
#todo requires pagination
#all_by_referral_code

#GET - all purchases matching current_us_state - 
#todo requires pagination
#

#GET - retrieve every payment from the previous month
#?scope=previous_month_payments

#GET - retrieve every payment month to date
#?scope=month_to_date_payments

#GET - retrieve every payment from the previous quarter
#?scope=previous_quarter_payments

#GET - retrieve every payment quarter to date
#?scope=quarter_to_date_payments

#GET - retrieve every payment from the previous year
#?scope=previous_year_payments

#GET - retrieve every payment year to date
#?scope=year_to_date_payments


#GET - sum payment_amount_in_usd past 24 hours
#?scope=gross_revenue_past_24_hours

#GET - sum payment_amount_in_usd rolling 7 days
#?scope=gross_revenue_past_7_days

#GET - sum payment_amount_in_usd rolling 30 days
#?scope=gross_revenue_past_rolling_30_days

#GET - sum payment_amount_in_usd from the previous month
#?scope=gross_revenue_past_previous_month

#GET - sum payment_amount_in_usd month to date
#?scope=gross_revenue_past_month_to_date

#GET - sum payment_amount_in_usd from the previous quarter
#?scope=gross_revenue_past_previous_quarter

#GET - sum payment_amount_in_usd quarter to date
#?scope=gross_revenue_past_quarter_to_date

#GET - sum payment_amount_in_usd from the previous year
#?scope=gross_revenue_past_previous_year

#GET - sum payment_amount_in_usd year to date
#?scope=gross_revenue_past_year_to_date

#GET - sum payment_amount_in_usd rolling 1 year
#?scope=gross_revenue_past_rolling_1_year

#GET - sum payment_amount_in_usd ALL
#?scope=gross_revenue_past_all_time




#POST - create payment row - working
#?user_id=1&payment_provider=opennode&crypto_or_fiat_gateway=crypto&order_id=abc1234abc&payment_amount_in_usd=9&number_of_months_paid_for=1&tier_paid_for=2&description=AL:T2:1M:-Tier-2-for-1-month&current_us_state=AL

#DELETE - delete single payment of row_id - 
#?row_id=1

#DELETE - delete all payments of user_id - 
#?user_id=1





#=========================
#user_id	epoch_of_payment	payment_provider	crypto_or_fiat_gateway	order_id	payment_amount_in_usd	number_of_months_paid_for	tier_paid_for	epoch_expiration	description	referral_code	account_created_epoch	current_us_state

#GET:
#single latest purchase of a user_id
#single purchase of a user_id with epoch_expiration in the future
#all purchases matching referral code
#all purchases matching current_us_state


#param input:
# user_id
# payment_provider
# crypto_or_fiat_gateway
# order_id
# payment_amount_in_usd
# number_of_months_paid_for	
# tier_paid_for
# description
# current_us_state

#calculated by function:
# epoch_of_payment
# epoch_expiration

#retrieved from users table:
# account_created_epoch

#retrieved from user_subscription_status table:
# referral_code