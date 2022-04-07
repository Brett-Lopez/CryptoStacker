#pip install mysql-connector-python
from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
import json
import CSR_service_mesh_map
import CSR_toolkit

def get_user_status_row(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    logging.critical("get_user_status_row() called") #debugging
    limit_max = 200
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_user_query = """
            SELECT *
            FROM user_subscription_status
            WHERE user_id = %s
            """

            select_user_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchone()

        return sql_query_result

    except Error as e:
        print(e)

def insert_referral_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, referral_code):
    logging.critical("insert_referral_code() called") #debugging
   
    if not get_user_status_row(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
        logging.error("attempting insert") #debugging
        try:
            with connect(
                host=RDS_secret_host,
                user=RDS_secret_user,
                password=RDS_secret_pass,
                database="CSR",
            ) as connection:
                print(connection) #debugging

                insert_order_id_query = """
                INSERT INTO user_subscription_status
                (user_id,
                referral_code)
                VALUES ( %s, %s )
                """
            
                order_id_tuple = (int(user_id), str(referral_code), )

                with connection.cursor() as cursor:
                    cursor.execute(insert_order_id_query, order_id_tuple)
                    connection.commit()

            return "inserted referral_code"

        except Error as e:
            print(e)
    else:
        logging.error("attempting update") #debugging
        try:
            with connect(
                host=RDS_secret_host,
                user=RDS_secret_user,
                password=RDS_secret_pass,
                database="CSR",
            ) as connection:
                print(connection) #debugging

                insert_order_id_query = """
                UPDATE user_subscription_status
                SET referral_code = %s
                WHERE user_id = %s
                """

                order_id_tuple = (str(referral_code), int(user_id), )

                with connection.cursor() as cursor:
                    cursor.execute(insert_order_id_query, order_id_tuple)
                    connection.commit()

            return "updated referral_code"

        except Error as e:
            print(e)

def update_tier_locked_by_admin(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, tier_locked_by_admin):
    logging.critical("update_tier_locked_by_admin() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection) #debugging

            update_query = """
            UPDATE user_subscription_status
            SET tier_locked_by_admin = %s
            WHERE user_id = %s
            """

            param_tuple = (str(tier_locked_by_admin), int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(update_query, param_tuple)
                connection.commit()

        return "updated tier_locked_by_admin"

    except Error as e:
        print(e)

def update_subscription_tier(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, subscription_tier):
    logging.critical("update_subscription_tier() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection) #debugging

            update_query = """
            UPDATE user_subscription_status
            SET subscription_tier = %s
            WHERE user_id = %s
            """

            param_tuple = (int(subscription_tier), int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(update_query, param_tuple)
                connection.commit()

        return "updated subscription_tier"

    except Error as e:
        print(e)

def update_transaction_stats(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, number_of_transactions_this_month, dollar_amount_of_transactions_this_month, total_number_of_transactions, total_dollar_amount_of_transactions):
    logging.critical("update_transaction_stats() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection) #debugging

            update_query = """
            UPDATE user_subscription_status
            SET number_of_transactions_this_month = %s,
            dollar_amount_of_transactions_this_month = %s,
            total_number_of_transactions = %s,
            total_dollar_amount_of_transactions = %s
            WHERE user_id = %s
            """

            param_tuple = (int(number_of_transactions_this_month), int(dollar_amount_of_transactions_this_month), int(total_number_of_transactions), int(total_dollar_amount_of_transactions), int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(update_query, param_tuple)
                connection.commit()

        return "updated subscription_tier"

    except Error as e:
        print(e)

def count_rows_by_all_referral_codes(RDS_secret_host, RDS_secret_user, RDS_secret_pass):
    logging.critical("count_rows_by_all_referral_codes() called") #debugging
    limit_max = 200
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_user_query = """
            select referral_code,COUNT(*) as count
            from user_subscription_status
            GROUP BY referral_code
            order by count DESC;
            """

            with connection.cursor() as cursor:
                cursor.execute(select_user_query)
                sql_query_result = cursor.fetchmany(size=limit_max)

        return sql_query_result

    except Error as e:
        print(e)

def count_referral_codes_by_specific_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, referral_code):
    logging.critical("count_referral_codes_by_specific_code() called") #debugging
    limit_max = 200
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_user_query = """
            select referral_code,COUNT(*) as count
            from user_subscription_status
            WHERE referral_code = %s
            GROUP BY referral_code
            order by count DESC;
            """

            select_user_tuple = (str(referral_code), )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchone()

        return sql_query_result

    except Error as e:
        print(e)

def count_rows_by_subscription_tier(RDS_secret_host, RDS_secret_user, RDS_secret_pass):
    logging.critical("count_rows_by_subscription_tier() called") #debugging
    limit_max = 200
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_user_query = """
            select subscription_tier,COUNT(*) as count
            from user_subscription_status
            GROUP BY subscription_tier
            order by count DESC;
            """

            with connection.cursor() as cursor:
                cursor.execute(select_user_query)
                sql_query_result = cursor.fetchmany(size=limit_max)

        return sql_query_result

    except Error as e:
        print(e)

def count_unique_users(RDS_secret_host, RDS_secret_user, RDS_secret_pass):
    logging.critical("count_unique_users() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            select_user_query = """
            SELECT COUNT(DISTINCT user_id) unique_users
            FROM user_subscription_status
            """

            with connection.cursor() as cursor:
                cursor.execute(select_user_query)
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

def reset_monthly_counters(RDS_secret_host, RDS_secret_user, RDS_secret_pass):
    logging.critical("reset_monthly_counters() called") #debugging
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            print(connection) #debugging

            update_query = """
            UPDATE user_subscription_status
            SET number_of_transactions_this_month = 0,
            dollar_amount_of_transactions_this_month = 0
            """

            with connection.cursor() as cursor:
                cursor.execute(update_query)
                connection.commit()

        return "reset monthly counters"

    except Error as e:
        print(e)

def delete_row_by_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    logging.critical("delete_row_by_user_id() called") #debugging
    limit_max = 200
    try:
        with connect(
            host=RDS_secret_host,
            user=RDS_secret_user,
            password=RDS_secret_pass,
            database="CSR",
        ) as connection:
            logging.error(connection) #debugging

            sql_query = """
            Delete
            FROM user_subscription_status
            WHERE user_id = %s
            """

            sql_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(sql_query, sql_tuple)
                connection.commit()

        return "row deleted"

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
            logging.error("required scope set") #debugging
            if event["queryStringParameters"]["scope"] == "user_id":
                logging.error("scope: user_id") #debugging
                if "user_id" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing")
                    return responseObject
                user_id = event["queryStringParameters"]["user_id"]
                sql_query_result = get_user_status_row(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            elif event["queryStringParameters"]["scope"] == "count_by_all_referral_codes":
                logging.error("scope: count_by_all_referral_codes") #debugging
                sql_query_result = count_rows_by_all_referral_codes(RDS_secret_host, RDS_secret_user, RDS_secret_pass)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            elif event["queryStringParameters"]["scope"] == "count_single_referral_code":
                logging.error("scope: count_single_referral_code") #debugging
                referral_code = event["queryStringParameters"]["referral_code"]
                sql_query_result = count_referral_codes_by_specific_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, referral_code)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            elif event["queryStringParameters"]["scope"] == "count_subscription_tier":
                logging.error("scope: count_subscription_tier") #debugging
                sql_query_result = count_rows_by_subscription_tier(RDS_secret_host, RDS_secret_user, RDS_secret_pass)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            elif event["queryStringParameters"]["scope"] == "count_unique_users":
                logging.error("scope: count_unique_users") #debugging
                sql_query_result = count_unique_users(RDS_secret_host, RDS_secret_user, RDS_secret_pass)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
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
        if "user_id" in event["queryStringParameters"] and "scope" in event["queryStringParameters"]:
            if event["queryStringParameters"]["scope"] == "referral_code":
                logging.error("scope: referral_code") #debugging
                user_id = event["queryStringParameters"]["user_id"]
                referral_code = event["queryStringParameters"]["referral_code"]
                referral_code = referral_code.lower()
                sql_query_result = insert_referral_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, referral_code)
                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject
            elif event["queryStringParameters"]["scope"] == "subscription_tier":
                logging.error("scope: subscription_tier") #debugging
                user_id = event["queryStringParameters"]["user_id"]
                subscription_tier = event["queryStringParameters"]["subscription_tier"]
                sql_query_result = update_subscription_tier(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, subscription_tier)
                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject
            elif event["queryStringParameters"]["scope"] == "tier_locked_by_admin":
                logging.error("scope: tier_locked_by_admin") #debugging
                user_id = event["queryStringParameters"]["user_id"]
                tier_locked_by_admin = event["queryStringParameters"]["tier_locked_by_admin"]
                sql_query_result = update_tier_locked_by_admin(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, tier_locked_by_admin)
                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject
            elif event["queryStringParameters"]["scope"] == "transaction_stats":
                logging.error("scope: transaction_stats") #debugging
                user_id = event["queryStringParameters"]["user_id"]
                number_of_transactions_this_month = event["queryStringParameters"]["number_of_transactions_this_month"]
                dollar_amount_of_transactions_this_month = event["queryStringParameters"]["dollar_amount_of_transactions_this_month"]
                total_number_of_transactions = event["queryStringParameters"]["total_number_of_transactions"]
                total_dollar_amount_of_transactions = event["queryStringParameters"]["total_dollar_amount_of_transactions"]
                sql_query_result = update_transaction_stats(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, number_of_transactions_this_month, dollar_amount_of_transactions_this_month, total_number_of_transactions, total_dollar_amount_of_transactions)
                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject
            else:
                logging.error("queryStringParameters missing 1") #debugging
                responseObject["body"] = json.dumps("queryStringParameters missing")
                responseObject["statusCode"] = 400
                return responseObject
        elif "scope" in event["queryStringParameters"]:
            if event["queryStringParameters"]["scope"] == "reset_monthly_counters":
                logging.error("scope: reset_monthly_counters") #debugging
                sql_query_result = reset_monthly_counters(RDS_secret_host, RDS_secret_user, RDS_secret_pass)
                responseObject["body"] = json.dumps(sql_query_result)
                return responseObject
            else:
                logging.error("queryStringParameters missing 2") #debugging
                responseObject["body"] = json.dumps("queryStringParameters missing")
                responseObject["statusCode"] = 400
                return responseObject
        else:
            logging.error("queryStringParameters missing 3") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing")
            responseObject["statusCode"] = 400
            return responseObject
    
    #IF DELETE
    if event["httpMethod"] == "DELETE":
        logging.error("httpMethod: DELETE") #debugging
        if "user_id" in event["queryStringParameters"]:
            user_id = event["queryStringParameters"]["user_id"]
            sql_query_result = delete_row_by_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
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

#GET - retrieve entire row by user_id (single row) - working
#?user_id=1&scope=user_id

#GET - count rows containing referral_code - working
#?scope=count_by_all_referral_codes

#GET - count rows containing referral_code - working
#?referral_code=influencer4&scope=count_single_referral_code

#GET - count rows by subscription_tier - working
#?scope=count_subscription_tier

#GET - count unique user_ids - 
#?scope=count_unique_users

#POST - insert/update referral_code - working
#?user_id=1&referral_code=influencer4&scope=referral_code

#POST - update subscription_tier - working
#?user_id=1&subscription_tier=2&scope=subscription_tier

#POST - update tier_locked_by_admin - working
#?user_id=1&tier_locked_by_admin=True&scope=tier_locked_by_admin

#POST - update number_of_transactions_this_month, dollar_amount_of_transactions_this_month, total_number_of_transactions, total_dollar_amount_of_transactions
#?user_id=1&number_of_transactions_this_month=10&dollar_amount_of_transactions_this_month=10&total_number_of_transactions=10&total_dollar_amount_of_transactions=10&scope=transaction_stats

#POST - reset monthly counters
#?scope=reset_monthly_counters

#DELETE - entire row by user_id - working
#?user_id=1

#=================================================================
