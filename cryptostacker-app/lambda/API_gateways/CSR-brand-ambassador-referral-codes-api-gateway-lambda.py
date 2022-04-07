#pip install mysql-connector-python
from mysql.connector import connect, Error
import logging
import aws_functions_for_lambda
import json
import CSR_service_mesh_map
import CSR_toolkit

def get_row_from_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
    logging.critical("get_row_from_user_id() called") #debugging
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
            FROM brand_ambassador_referral_codes
            WHERE user_id = %s
            """

            select_user_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchone()

        return sql_query_result

    except Error as e:
        print(e)

def get_row_from_referral_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, referral_code):
    logging.critical("get_row_from_referral_code() called") #debugging
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
            FROM brand_ambassador_referral_codes
            WHERE referral_code = %s
            """

            select_user_tuple = (str(referral_code), )

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchone()

        return sql_query_result

    except Error as e:
        print(e)

def get_all_rows_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, after_id, limit):
    logging.critical("get_all_rows_paginated() called") #debugging
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

            select_user_query = """
            SELECT *
            FROM brand_ambassador_referral_codes
            WHERE user_id > %s
            LIMIT %s
            """

            select_user_tuple = (int(after_id), int(limit))

            with connection.cursor() as cursor:
                cursor.execute(select_user_query, select_user_tuple)
                sql_query_result = cursor.fetchall()

        return sql_query_result

    except Error as e:
        print(e)

def insert_or_update_referral_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, referral_code, revenue_share_percentage):
    logging.critical("insert_or_update_referral_code() called") #debugging

    if not get_row_from_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id):
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
                INSERT INTO brand_ambassador_referral_codes
                (user_id,
                referral_code,
                revenue_share_percentage)
                VALUES ( %s, %s, %s )
                """
            
                order_id_tuple = (int(user_id), str(referral_code), int(revenue_share_percentage), )

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
                UPDATE brand_ambassador_referral_codes
                SET referral_code = %s,
                revenue_share_percentage = %s
                WHERE user_id = %s
                """

                order_id_tuple = (str(referral_code), int(revenue_share_percentage), int(user_id), )

                with connection.cursor() as cursor:
                    cursor.execute(insert_order_id_query, order_id_tuple)
                    connection.commit()

            return "updated referral_code"

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
            FROM brand_ambassador_referral_codes
            WHERE user_id = %s
            """

            sql_tuple = (int(user_id), )

            with connection.cursor() as cursor:
                cursor.execute(sql_query, sql_tuple)
                connection.commit()

        return "row deleted"

    except Error as e:
        print(e)

def delete_row_by_referral_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, referral_code):
    logging.critical("delete_row_by_referral_code() called") #debugging
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
            FROM brand_ambassador_referral_codes
            WHERE referral_code = %s
            """

            sql_tuple = (str(referral_code), )

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
                    responseObject["body"] = json.dumps("queryStringParameters missing - user_id")
                    return responseObject
                user_id = event["queryStringParameters"]["user_id"]
                sql_query_result = get_row_from_user_id(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            elif event["queryStringParameters"]["scope"] == "referral_code":
                logging.error("scope: referral_code") #debugging
                if "referral_code" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing - referral_code")
                    return responseObject
                referral_code = event["queryStringParameters"]["referral_code"]
                sql_query_result = get_row_from_referral_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, referral_code)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            elif event["queryStringParameters"]["scope"] == "paginated":
                logging.error("scope: paginated") #debugging
                if "after_id" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing - paginated")
                    return responseObject
                if "limit" not in event["queryStringParameters"]:
                    responseObject["body"] = json.dumps("queryStringParameters missing - paginated")
                    return responseObject
                after_id = event["queryStringParameters"]["after_id"]
                limit = event["queryStringParameters"]["limit"]
                sql_query_result = get_all_rows_paginated(RDS_secret_host, RDS_secret_user, RDS_secret_pass, after_id, limit)
                if sql_query_result:
                    responseObject["body"] = json.dumps(sql_query_result)
                    return responseObject
                else:
                    responseObject["body"] = json.dumps([])
                    return responseObject
            else:
                logging.error("queryStringParameters missing 1") #debugging
                responseObject["statusCode"] = 400
                responseObject["body"] = json.dumps("queryStringParameters missing 1")
                return responseObject
        else:
            logging.error("queryStringParameters missing 2") #debugging
            responseObject["statusCode"] = 400
            responseObject["body"] = json.dumps("queryStringParameters missing 2")
            return responseObject

    #IF POST
    if event["httpMethod"] == "POST":
        logging.error("httpMethod: POST") #debugging
        if "user_id" in event["queryStringParameters"] and "referral_code" in event["queryStringParameters"] and "revenue_share_percentage" in event["queryStringParameters"]:
            user_id = event["queryStringParameters"]["user_id"]
            referral_code = event["queryStringParameters"]["referral_code"]
            referral_code = referral_code.lower()
            revenue_share_percentage = event["queryStringParameters"]["revenue_share_percentage"]
            sql_query_result = insert_or_update_referral_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, user_id, referral_code, revenue_share_percentage)
            responseObject["body"] = json.dumps(sql_query_result)
            return responseObject
        else:
            logging.error("queryStringParameters missing 2") #debugging
            responseObject["body"] = json.dumps("queryStringParameters missing 2")
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
        elif "referral_code" in event["queryStringParameters"]:
            referral_code = event["queryStringParameters"]["referral_code"]
            sql_query_result = delete_row_by_referral_code(RDS_secret_host, RDS_secret_user, RDS_secret_pass, referral_code)
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

#GET - retrieve entire row by referral_code (single row) - working
#?referral_code=lyra&scope=referral_code

#GET - multiple rows paginated - working
#?after_id=0&limit=100&scope=paginated

#POST - insert/update - working
#?user_id=1&referral_code=lyra&revenue_share_percentage=50

#DELETE - entire row by user_id - working
#?user_id=1

#DELETE - entire row by referral_code - working
#?referral_code=lyra
